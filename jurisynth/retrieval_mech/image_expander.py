"""Lazy, query-aware visual inspection for already retrieved image candidates."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import logging
import random
import sys
import time
from dataclasses import replace
from pathlib import Path

from jurisynth.contracts import ImageEvidence
# The KG pipeline source remains a legacy flat module directory. Add only that
# explicit directory so the visual client is shared rather than duplicating its
# Nano Omni configuration inside retrieval.
_PIPELINE_SRC = Path(__file__).resolve().parents[1] / "kg_construction_pipeline" / "src"
if str(_PIPELINE_SRC) not in sys.path:
    sys.path.insert(0, str(_PIPELINE_SRC))
from vision_llm_utils import VisionNIMConfig, create_vision_client
from llm_utils import DEFAULT_REQUESTS_PER_SECOND, MAX_BACKOFF, wait_for_rate_limit


IMAGE_EXPANSION_SCHEMA = {
    "name": "jurisynth_image_expansion", "strict": True,
    "schema": {"type": "object", "properties": {
        "expanded_description": {"type": "string"},
        "visual_findings": {"type": "array", "items": {"type": "string"}},
        "relevance": {"type": "number", "minimum": 0, "maximum": 1},
    }, "required": ["expanded_description", "visual_findings", "relevance"], "additionalProperties": False},
}

_PROMPT = """Inspect this already retrieved image in relation to the user's question.
Return only the requested JSON. Describe visible structure, labels, fields, and
relationships relevant to the question. Do not infer legal effect, legal duties,
or facts not visible in the image. This is auxiliary visual context, not legal
evidence. Keep expanded_description under 140 words and each finding under 35 words."""

_LOGGER = logging.getLogger(__name__)


class ImageExpander:
    """Caches query-specific inspection without changing canonical FAISS scores."""

    def __init__(self, batch_root: str | Path, *, config: VisionNIMConfig | None = None, client=None, invalid_output_attempts: int = 2, requests_per_second: float = DEFAULT_REQUESTS_PER_SECOND) -> None:
        self.batch_root = Path(batch_root)
        self.config = config or VisionNIMConfig.from_environment()
        self.client = client or create_vision_client(self.config)
        self._cache: dict[tuple[str, str], ImageEvidence] = {}
        self._lock = asyncio.Lock()
        self.invalid_output_attempts = invalid_output_attempts
        self._rate_lock = asyncio.Lock()
        self._last_request_time = [0.0]
        self._cooldown_until = [0.0]
        self._current_rps = [requests_per_second]

    async def expand(self, images: list[ImageEvidence], query: str) -> list[ImageEvidence]:
        return [await self._expand_one(image, query) for image in images]

    def resolve_image_path(self, image: ImageEvidence) -> Path | None:
        """Resolve aggregate metadata paths without duplicating ``image_store``.

        The aggregate store root is the canonical base.  Current metadata may
        retain one legacy ``image_store`` component below its batch directory;
        that component is removed only when the exact stored path is absent
        and this expander is already rooted at an ``image_store`` directory.
        """
        root = self.batch_root.resolve()
        relative = Path(image.relative_path)
        if relative.is_absolute():
            return None
        candidates = [relative]
        if root.name.casefold() == "image_store":
            parts = list(relative.parts)
            for index, part in enumerate(parts):
                if part.casefold() == "image_store":
                    normalized = Path(*(parts[:index] + parts[index + 1 :]))
                    if normalized != relative:
                        candidates.append(normalized)
                    break
        for candidate in candidates:
            path = (root / candidate).resolve()
            if root not in path.parents or not path.is_file():
                continue
            return path
        return None

    async def _expand_one(self, image: ImageEvidence, query: str) -> ImageEvidence:
        cache_key = (image.sha256 or image.image_id, hashlib.sha256(query.encode("utf-8")).hexdigest())
        if cached := self._cache.get(cache_key):
            return cached
        path = self.resolve_image_path(image)
        if path is None:
            _LOGGER.warning(
                "image expansion skipped: artifact file missing",
                extra={"image_id": image.image_id, "relative_path": image.relative_path},
            )
            return image
        _LOGGER.debug("image expansion attempted", extra={"image_id": image.image_id, "path": str(path)})
        data_url = f"data:{image.mime_type};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"
        invalid_attempt = 0
        transient_attempt = 0
        while True:
            await wait_for_rate_limit(self._rate_lock, self._last_request_time, self._cooldown_until, self._current_rps)
            try:
                response = await self.client.chat.completions.create(
                    model=self.config.model_id,
                    messages=[{"role": "system", "content": _PROMPT}, {"role": "user", "content": [
                        {"type": "text", "text": f"Question: {query}"},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ]}], temperature=0, top_p=0.000001, stream=False,
                    reasoning_effort="none",
                    response_format={"type": "json_schema", "json_schema": IMAGE_EXPANSION_SCHEMA},
                )
                raw = response.choices[0].message.content
                payload = json.loads(raw or "")
                description = payload.get("expanded_description")
                findings = payload.get("visual_findings")
                relevance = payload.get("relevance")
                if not isinstance(description, str) or not isinstance(findings, list) or not all(isinstance(item, str) for item in findings) or not isinstance(relevance, (float, int)):
                    raise ValueError("Image expansion response does not match its schema.")
                expanded = replace(
                    image, expanded_description=" ".join(description.split()[:140]),
                    visual_findings=[" ".join(item.split()[:35]) for item in findings[:6]],
                    expansion_relevance=float(relevance),
                )
                async with self._lock:
                    self._cache[cache_key] = expanded
                _LOGGER.info("image expansion succeeded", extra={"image_id": image.image_id})
                return expanded
            except ValueError:
                invalid_attempt += 1
                if invalid_attempt > self.invalid_output_attempts:
                    _LOGGER.exception(
                        "image expansion failed: invalid structured output",
                        extra={"image_id": image.image_id},
                    )
                    raise
            except Exception as exc:
                if not _is_retryable(exc):
                    _LOGGER.exception(
                        "image expansion failed: non-retryable provider error",
                        extra={"image_id": image.image_id},
                    )
                    raise
                delay = _retry_delay(exc, transient_attempt)
                transient_attempt += 1
                async with self._rate_lock:
                    self._cooldown_until[0] = max(self._cooldown_until[0], time.monotonic() + delay)
                    self._current_rps[0] = max(0.25, self._current_rps[0] * 0.5)

    async def aclose(self) -> None:
        await self.client.close()


def _is_retryable(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(code in text for code in ("429", "404", "500", "502", "503", "504", "connection", "timeout"))


def _retry_delay(exc: Exception, attempt: int) -> float:
    if "404" in str(exc):
        return 30 + random.uniform(0, 5)
    return min(2 ** attempt, MAX_BACKOFF) + random.uniform(0, 1)
