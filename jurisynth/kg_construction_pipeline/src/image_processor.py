"""Opt-in visual-description and FAISS indexing stage for batch image artefacts.

The document preprocessors already download images and persist a per-document
JSON manifest in ``image_store``.  This module deliberately runs *after* that
stage: visual calls are expensive and must never be an implicit side effect of
ordinary KG construction.

It creates ``<batch>/image_index`` containing:

* ``descriptions.jsonl``: provenance-preserving description records;
* ``image.index``: a cosine-similarity FAISS index over those descriptions;
* ``metadata.json``: index-to-record lookup and embedding provenance.

Descriptions are auxiliary retrieval evidence.  They are not assertions and
must not be treated as a source for legal propositions without opening the
underlying image/document.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import random
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Protocol

import faiss
import numpy as np
import openai
from sentence_transformers import SentenceTransformer

from llm_utils import DEFAULT_REQUESTS_PER_SECOND, MAX_BACKOFF, wait_for_rate_limit
from vision_llm_utils import DEFAULT_IMAGE_MODEL_ID, VisionNIMConfig, create_vision_client


DEFAULT_EMBEDDING_MODEL_ID = "all-MiniLM-L6-v2"
SUPPORTED_IMAGE_MIME_TYPES = frozenset({"image/jpeg", "image/png", "image/webp"})

DESCRIPTION_PROMPT = """You describe an image extracted from an EU legal document.
Return only one JSON object with exactly these string fields:
{
  "description": "concise retrieval-ready visual description",
  "image_type": "one of: photograph, diagram, chart, scan, logo, illustration, other",
  "legible_text": "salient text visible in the image, or an empty string"
}

Describe only visible content. Mention visual structure, labels, and subject matter
when legible. Do not infer legal duties, legal effect, or facts not visible in the
image. Keep description under 110 words and legible_text under 80 words."""


class ImageDescriber(Protocol):
    async def describe(self, asset: "ImageAsset") -> dict[str, str]: ...


@dataclass(frozen=True, slots=True)
class ImageAsset:
    image_id: str
    document_id: str
    filename: str
    path: Path
    mime_type: str
    sha256: str | None
    source_url: str | None
    alt: str | None


@dataclass(frozen=True, slots=True)
class ImageDescription:
    image_id: str
    document_id: str
    filename: str
    relative_path: str
    mime_type: str
    sha256: str | None
    source_url: str | None
    alt: str | None
    description: str
    image_type: str
    legible_text: str
    status: str = "success"
    error: str | None = None

    def retrieval_text(self) -> str:
        return " ".join(
            part for part in (self.description, self.image_type, self.legible_text) if part
        )


def load_image_assets(image_store: str | Path) -> list[ImageAsset]:
    """Read only successful, locally available, supported image artefacts."""
    store = Path(image_store)
    assets: list[ImageAsset] = []
    seen: set[tuple[str, str]] = set()
    for manifest_path in sorted(store.glob("*.json")):
        try:
            records = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(records, list):
            continue
        document_id = manifest_path.stem
        for position, raw in enumerate(records, start=1):
            if not isinstance(raw, dict) or raw.get("status") != "success":
                continue
            filename = raw.get("filename")
            mime_type = str(raw.get("mime_type") or "").lower()
            if not isinstance(filename, str) or mime_type not in SUPPORTED_IMAGE_MIME_TYPES:
                continue
            path = store / filename
            if not path.is_file():
                continue
            sha256 = raw.get("sha256") if isinstance(raw.get("sha256"), str) else None
            identity = (document_id, sha256 or filename)
            if identity in seen:
                continue
            seen.add(identity)
            assets.append(
                ImageAsset(
                    image_id=f"{document_id}:image:{position:03d}",
                    document_id=document_id,
                    filename=filename,
                    path=path,
                    mime_type=mime_type,
                    sha256=sha256,
                    source_url=raw.get("source_url") if isinstance(raw.get("source_url"), str) else None,
                    alt=raw.get("alt") if isinstance(raw.get("alt"), str) else None,
                )
            )
    return assets


class NIMImageDescriber:
    """Small OpenAI-compatible adapter with bounded invalid-output retries.

    Transport/rate-limit failures intentionally retry indefinitely, matching the
    existing Assertion Extractor policy. Invalid model payloads retry only a
    limited number of times and are recorded per image rather than halting a
    batch.
    """

    def __init__(
        self,
        client: openai.AsyncOpenAI,
        *,
        model_id: str | None = None,
        invalid_output_attempts: int = 2,
        requests_per_second: float = DEFAULT_REQUESTS_PER_SECOND,
    ) -> None:
        self.client = client
        self.model_id = model_id or DEFAULT_IMAGE_MODEL_ID
        self.invalid_output_attempts = invalid_output_attempts
        self.rate_lock = asyncio.Lock()
        self.last_request_time = [0.0]
        self.cooldown_until = [0.0]
        self.current_rps = [requests_per_second]

    async def describe(self, asset: ImageAsset) -> dict[str, str]:
        invalid_attempt = 0
        transient_attempt = 0
        while True:
            await wait_for_rate_limit(
                self.rate_lock, self.last_request_time, self.cooldown_until, self.current_rps
            )
            try:
                response = await self.client.chat.completions.create(
                    model=self.model_id,
                    messages=[
                        {"role": "system", "content": DESCRIPTION_PROMPT},
                        {"role": "user", "content": [
                            {"type": "text", "text": "Describe this extracted document image."},
                            {"type": "image_url", "image_url": {"url": _as_data_url(asset)}},
                        ]},
                    ],
                    temperature=0,
                    top_p=0.000001,
                    max_tokens=300,
                    stream=False,
                    reasoning_effort="none",
                )
                return _parse_description(response.choices[0].message.content)
            except ValueError:
                invalid_attempt += 1
                if invalid_attempt > self.invalid_output_attempts:
                    raise
            except Exception as exc:  # Existing pipeline policy: retry temporary NIM failures.
                if not _is_retryable(exc):
                    raise
                delay = _retry_delay(exc, transient_attempt)
                transient_attempt += 1
                async with self.rate_lock:
                    self.cooldown_until[0] = max(self.cooldown_until[0], time.monotonic() + delay)
                    self.current_rps[0] = max(0.25, self.current_rps[0] * 0.5)


def _as_data_url(asset: ImageAsset) -> str:
    encoded = base64.b64encode(asset.path.read_bytes()).decode("ascii")
    return f"data:{asset.mime_type};base64,{encoded}"


def _parse_description(raw: str | None) -> dict[str, str]:
    if not isinstance(raw, str):
        raise ValueError("Image model returned no description content.")
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError("Image model did not return valid JSON.") from exc
    if not isinstance(payload, dict):
        raise ValueError("Image model JSON must be an object.")
    fields = {key: payload.get(key) for key in ("description", "image_type", "legible_text")}
    if not all(isinstance(value, str) for value in fields.values()) or not fields["description"].strip():
        raise ValueError("Image model JSON is missing the required description fields.")
    normalized = {key: " ".join(value.split()) for key, value in fields.items()}
    # Model instructions are helpful but not a reliable context control. The
    # indexed payload must be bounded deterministically so repetitive OCR does
    # not drown out visual semantics during retrieval.
    normalized["description"] = _truncate_words(normalized["description"], 110)
    normalized["legible_text"] = _truncate_words(normalized["legible_text"], 80)
    return normalized


def _truncate_words(value: str, limit: int) -> str:
    words = value.split()
    return " ".join(words[:limit])


def _is_retryable(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(code in text for code in ("429", "404", "500", "502", "503", "504", "connection", "timeout"))


def _retry_delay(exc: Exception, attempt: int) -> float:
    if "404" in str(exc):
        return 30 + random.uniform(0, 5)
    return min(2 ** attempt, MAX_BACKOFF) + random.uniform(0, 1)


async def describe_assets(
    assets: Iterable[ImageAsset],
    describer: ImageDescriber,
    *,
    batch_dir: str | Path,
) -> list[ImageDescription]:
    """Describe assets serially to keep a vision job predictable and resumable."""
    root = Path(batch_dir).resolve()
    results: list[ImageDescription] = []
    for asset in assets:
        try:
            payload = await describer.describe(asset)
            results.append(_description_record(asset, root, payload))
        except Exception as exc:
            results.append(
                ImageDescription(
                    image_id=asset.image_id, document_id=asset.document_id, filename=asset.filename,
                    relative_path=_relative(asset.path, root), mime_type=asset.mime_type,
                    sha256=asset.sha256, source_url=asset.source_url, alt=asset.alt,
                    description="", image_type="", legible_text="", status="error", error=repr(exc),
                )
            )
    return results


def _description_record(asset: ImageAsset, root: Path, payload: dict[str, str]) -> ImageDescription:
    return ImageDescription(
        image_id=asset.image_id, document_id=asset.document_id, filename=asset.filename,
        relative_path=_relative(asset.path, root), mime_type=asset.mime_type, sha256=asset.sha256,
        source_url=asset.source_url, alt=asset.alt, description=payload["description"],
        image_type=payload["image_type"], legible_text=payload["legible_text"],
    )


def _relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return str(path)


def write_image_index(
    records: Iterable[ImageDescription],
    destination: str | Path,
    embedding_model: Any,
    *,
    embedding_model_id: str = DEFAULT_EMBEDDING_MODEL_ID,
) -> dict[str, int]:
    """Persist successful description records and their normalized FAISS vectors."""
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    ordered = list(records)
    with (destination / "descriptions.jsonl").open("w", encoding="utf-8") as handle:
        for record in ordered:
            handle.write(json.dumps(asdict(record), ensure_ascii=False, sort_keys=True) + "\n")
    successful = [record for record in ordered if record.status == "success" and record.retrieval_text()]
    metadata = [asdict(record) for record in successful]
    manifest: dict[str, Any] = {
        "artifact_version": "1.0", "embedding_model": embedding_model_id,
        "normalized": True, "record_count": len(ordered), "indexed_count": len(successful),
        "error_count": len(ordered) - len(successful), "metadata": metadata,
    }
    if successful:
        vectors = np.asarray(
            embedding_model.encode(
                [record.retrieval_text() for record in successful], normalize_embeddings=True,
                show_progress_bar=False,
            ), dtype=np.float32,
        )
        if vectors.ndim != 2 or vectors.shape[0] != len(successful):
            raise ValueError("Embedding model returned vectors with an unexpected shape.")
        index = faiss.IndexFlatIP(int(vectors.shape[1]))
        index.add(vectors)
        faiss.write_index(index, str(destination / "image.index"))
        manifest["embedding_dimension"] = int(vectors.shape[1])
    (destination / "metadata.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {"records": len(ordered), "indexed": len(successful), "errors": len(ordered) - len(successful)}


async def process_batch_images(
    batch_dir: str | Path,
    *,
    describer: ImageDescriber,
    embedding_model: Any,
    embedding_model_id: str = DEFAULT_EMBEDDING_MODEL_ID,
) -> dict[str, int]:
    """Run the opt-in stage for one preprocessed batch."""
    batch = Path(batch_dir)
    records = await describe_assets(load_image_assets(batch / "image_store"), describer, batch_dir=batch)
    return write_image_index(records, batch / "image_index", embedding_model, embedding_model_id=embedding_model_id)


def main() -> None:
    parser = argparse.ArgumentParser(description="Describe and FAISS-index extracted batch images.")
    parser.add_argument("batch_dir", type=Path, help="Preprocessed batch directory containing image_store")
    parser.add_argument("--embedding-model", default=DEFAULT_EMBEDDING_MODEL_ID)
    parser.add_argument("--model-id", default=None, help="Override NEMOTRON_NANO_OMNI_MODEL")
    args = parser.parse_args()
    config = VisionNIMConfig.from_environment()
    client = create_vision_client(config)
    describer = NIMImageDescriber(client, model_id=args.model_id or config.model_id)
    embedder = SentenceTransformer(args.embedding_model)
    outcome = asyncio.run(
        process_batch_images(
            args.batch_dir, describer=describer, embedding_model=embedder,
            embedding_model_id=args.embedding_model,
        )
    )
    print({**outcome, "destination": str(args.batch_dir / "image_index")})


if __name__ == "__main__":
    main()
