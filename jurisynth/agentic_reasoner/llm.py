"""OpenAI-compatible NIM boundary and evidence-grounded leaf generation."""

from __future__ import annotations

import asyncio
import json
import os
import random
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol
from uuid import uuid4

from jurisynth.agentic_reasoner.models import Claim, LeafAnswer, LeafNode
from jurisynth.contracts import EvidenceBundle


class ChatModel(Protocol):
    async def complete(self, *, system: str, user: str, max_tokens: int | None = None, response_schema: dict[str, object] | None = None) -> str: ...


def _exception_chain_types(exc: BaseException) -> list[dict[str, str]]:
    """Record exception classes only, never messages, headers or request bodies."""
    result = []
    seen = {id(exc)}
    for _ in range(8):
        nested = exc.__cause__
        link = 'cause'
        if nested is None and not exc.__suppress_context__:
            nested = exc.__context__
            link = 'context'
        if nested is None or id(nested) in seen:
            break
        seen.add(id(nested))
        result.append({'link': link, 'type': type(nested).__name__, 'module': type(nested).__module__})
        exc = nested
    return result


@dataclass(frozen=True, slots=True)
class NIMConfig:
    api_key: str
    base_url: str
    model: str = "nemotron-3-ultra"
    # NIM's retry policy deliberately handles transient provider failures
    # without a fixed attempt budget.  Keep the transport deadline disabled by
    # default so a long but valid completion is not converted into a local
    # timeout; deployments may opt into a positive bound through the env var.
    request_timeout_seconds: float | None = None
    max_attempts: int | None = None
    reasoning_effort: str | None = "none"

    @classmethod
    def from_environment(cls, *, dotenv_path: str | Path | None = None) -> "NIMConfig":
        """Load the local Agentic Reasoner dotenv file without logging secrets."""
        try:
            from dotenv import load_dotenv
        except ModuleNotFoundError as exc:
            raise RuntimeError("Install 'python-dotenv' to load the local NIM configuration.") from exc
        load_dotenv(dotenv_path or Path(__file__).with_name(".env"), override=False)
        api_key = os.environ.get("JURISYNTH_NIM_API_KEY", "")
        base_url = os.environ.get("JURISYNTH_NIM_BASE_URL", "")
        model = os.environ.get("JURISYNTH_NIM_MODEL", "nemotron-3-ultra")
        timeout_text = os.environ.get("JURISYNTH_NIM_TIMEOUT_SECONDS", "0").strip().lower()
        max_attempts_text = os.environ.get("JURISYNTH_NIM_MAX_ATTEMPTS", "").strip()
        reasoning_effort = os.environ.get("JURISYNTH_NIM_REASONING_EFFORT", "none").strip() or None
        if reasoning_effort == "omit":
            reasoning_effort = None
        if not api_key or not base_url:
            raise RuntimeError("Set JURISYNTH_NIM_API_KEY and JURISYNTH_NIM_BASE_URL before using NVIDIA NIM.")
        if not base_url.startswith(("https://", "http://")):
            raise RuntimeError("JURISYNTH_NIM_BASE_URL must be a plain http(s) URL, not Markdown formatting.")
        try:
            request_timeout_seconds = None if timeout_text in {"0", "none", "off"} else float(timeout_text)
        except ValueError as exc:
            raise RuntimeError("JURISYNTH_NIM_TIMEOUT_SECONDS must be a positive number of seconds.") from exc
        if request_timeout_seconds is not None and request_timeout_seconds <= 0:
            raise RuntimeError("JURISYNTH_NIM_TIMEOUT_SECONDS must be a positive number of seconds, or 0/none to disable it.")
        try:
            max_attempts = int(max_attempts_text) if max_attempts_text else None
        except ValueError as exc:
            raise RuntimeError("JURISYNTH_NIM_MAX_ATTEMPTS must be a positive integer when set.") from exc
        if max_attempts is not None and max_attempts < 1:
            raise RuntimeError("JURISYNTH_NIM_MAX_ATTEMPTS must be a positive integer when set.")
        return cls(
            api_key=api_key,
            base_url=base_url,
            model=model,
            request_timeout_seconds=request_timeout_seconds,
            max_attempts=max_attempts,
            reasoning_effort=reasoning_effort,
        )


@dataclass(frozen=True, slots=True)
class NIMRetryPolicy:
    """Pipeline-aligned rate limiting and retry policy for one shared NIM client."""

    requests_per_second: float = 2.0
    min_requests_per_second: float = 0.25
    recovery_step: float = 0.10
    success_threshold: int = 20
    max_backoff_seconds: float = 30.0
    jitter_seconds: float = 1.0
    max_attempts: int | None = None

    def __post_init__(self) -> None:
        if self.requests_per_second <= 0 or self.min_requests_per_second <= 0:
            raise ValueError("NIM retry rates must be positive.")
        if self.min_requests_per_second > self.requests_per_second:
            raise ValueError("min_requests_per_second cannot exceed requests_per_second.")
        if self.max_attempts is not None and self.max_attempts < 1:
            raise ValueError("max_attempts must be positive or None for unbounded retries.")


class OpenAICompatibleNIM:
    """Thin async wrapper; import and network configuration remain runtime-only."""

    def __init__(self, config: NIMConfig, *, retry_policy: NIMRetryPolicy | None = None, client: Any | None = None, reasoning_log: Any | None = None) -> None:
        if client is None:
            try:
                from openai import AsyncOpenAI
            except ModuleNotFoundError as exc:
                raise RuntimeError("Install the 'openai' package to use the NIM client.") from exc
            client = AsyncOpenAI(
                base_url=config.base_url,
                api_key=config.api_key,
                max_retries=0,
                timeout=config.request_timeout_seconds,
            )
        self._client = client
        self._model = config.model
        self._reasoning_effort = config.reasoning_effort
        self._request_timeout_seconds = config.request_timeout_seconds
        self._retry_policy = retry_policy or NIMRetryPolicy(max_attempts=config.max_attempts)
        self._rate_lock = asyncio.Lock()
        self._last_request_time = 0.0
        self._cooldown_until = 0.0
        self._current_rps = self._retry_policy.requests_per_second
        self._success_count = 0
        self._reasoning_log = reasoning_log

    async def complete(self, *, system: str, user: str, max_tokens: int | None = None, response_schema: dict[str, object] | None = None) -> str:
        # Legacy adapter arguments remain compatible but are not transmitted.
        # Omitting the output limit uses the provider's default, not infinity.
        attempt = 0
        call_id = uuid4().hex
        while True:
            attempt += 1
            await self._wait_for_rate_limit()
            started = time.perf_counter()
            self._record_event("nim_request_started", call_id=call_id, attempt=attempt, model=self._model,
                               schema_name=response_schema.get("name") if response_schema else None, output_token_limit='provider_default',
                               request_timeout_seconds=self._request_timeout_seconds)
            try:
                request: dict[str, object] = {
                    "model": self._model,
                    "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                    "temperature": 0,
                    # Match the KG pipeline's near-greedy setting rather than
                    # relying on a provider default for top-p sampling.
                    "top_p": 0.000001,
                }
                if self._reasoning_effort is not None:
                    request["reasoning_effort"] = self._reasoning_effort
                if response_schema is not None:
                    request["response_format"] = {"type": "json_schema", "json_schema": response_schema}
                response = await self._client.chat.completions.create(**request)
                content = response.choices[0].message.content
                if not content:
                    raise RuntimeError("NIM returned an empty completion.")
                await self._record_success()
                usage = getattr(response, "usage", None)
                self._record_event("nim_request_completed", call_id=call_id, attempt=attempt,
                                   elapsed_seconds=round(time.perf_counter() - started, 3),
                                   finish_reason=getattr(response.choices[0], "finish_reason", None),
                                   output_chars=len(content),
                                   prompt_tokens=getattr(usage, "prompt_tokens", None),
                                   completion_tokens=getattr(usage, "completion_tokens", None))
                return content
            except asyncio.CancelledError:
                self._record_event("nim_request_cancelled", call_id=call_id, attempt=attempt,
                                   elapsed_seconds=round(time.perf_counter() - started, 3))
                raise
            except Exception as exc:
                diagnostics = {'elapsed_seconds': round(time.perf_counter() - started, 3),
                               'transport_exception_chain': _exception_chain_types(exc)}
                error_text = str(exc)
                status_code = getattr(exc, "status_code", None)
                # A real HTTP status takes precedence over numbers in its payload.
                if status_code is None:
                    match = re.search(r"^(?:Error code: |HTTP(?: status)? )?(404|429|500|502|503|504)\b", error_text.strip(), re.I)
                    status_code = int(match.group(1)) if match else None
                if status_code == 404:
                    delay = 30.0 + random.uniform(0, 5)
                elif status_code in {429, 500, 502, 503, 504}:
                    delay = min(2 ** min(attempt - 1, 30), self._retry_policy.max_backoff_seconds)
                    delay += random.uniform(0, self._retry_policy.jitter_seconds)
                elif isinstance(exc, (ConnectionError, TimeoutError)) or type(exc).__name__ in {"APIConnectionError", "APITimeoutError", "ConnectError", "ConnectTimeout", "ReadTimeout"}:
                    delay = min(2 ** min(attempt - 1, 30), self._retry_policy.max_backoff_seconds)
                    delay += random.uniform(0, self._retry_policy.jitter_seconds)
                else:
                    self._record_event("nim_request_failed", call_id=call_id, attempt=attempt,
                                       error_type=type(exc).__name__, status_code=status_code, **diagnostics)
                    raise
                if self._retry_policy.max_attempts is not None and attempt >= self._retry_policy.max_attempts:
                    self._record_event("nim_retries_exhausted", call_id=call_id, attempt=attempt, status_code=status_code, **diagnostics)
                    raise
                self._record_event("nim_retry_scheduled", call_id=call_id, attempt=attempt,
                                   status_code=status_code, error_type=type(exc).__name__, backoff_seconds=round(delay, 3), **diagnostics)
                await self._record_transient_failure(delay)

    def _record_event(self, event: str, **payload: object) -> None:
        if self._reasoning_log is not None:
            try:
                self._reasoning_log.record(event, **payload)
            except Exception:
                # Observability is auxiliary; unavailable log storage must not
                # convert a successful completion into a model-call failure.
                pass

    async def aclose(self) -> None:
        """Close the underlying asynchronous HTTP client at application shutdown."""
        await self._client.close()

    async def _wait_for_rate_limit(self) -> None:
        async with self._rate_lock:
            now = time.monotonic()
            if now < self._cooldown_until:
                await asyncio.sleep(self._cooldown_until - now)
                now = time.monotonic()
            wait_time = (1 / self._current_rps) - (now - self._last_request_time)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                now = time.monotonic()
            self._last_request_time = now

    async def _record_success(self) -> None:
        async with self._rate_lock:
            self._success_count += 1
            if self._success_count >= self._retry_policy.success_threshold:
                self._current_rps = min(self._retry_policy.requests_per_second, self._current_rps + self._retry_policy.recovery_step)
                self._success_count = 0

    async def _record_transient_failure(self, delay: float) -> None:
        async with self._rate_lock:
            self._cooldown_until = max(self._cooldown_until, time.monotonic() + delay)
            self._current_rps = max(self._retry_policy.min_requests_per_second, self._current_rps / 2)
            self._success_count = 0


@dataclass(slots=True)
class EvidenceGroundedLeafGenerator:
    """Generate Claim-bearing leaf answers without accepting invented evidence IDs."""

    model: ChatModel
    max_tokens: int = 800
    max_validation_attempts: int = 2
    max_evidence_items: int = 12
    max_sources_per_item: int = 1
    max_source_characters: int = 3_000
    max_assertion_field_characters: int = 1_000
    max_evidence_payload_characters: int = 50_000

    async def __call__(
        self,
        node: LeafNode,
        dependency_answers: list[LeafAnswer],
        evidence: EvidenceBundle,
    ) -> LeafAnswer:
        if evidence.status in {"empty", "error"}:
            return LeafAnswer(
                node.query_id,
                "insufficient_evidence",
                "The available sources do not provide sufficient evidence to answer this question.",
                [],
                evidence,
            )
        payload = {
            "query": node.query,
            "dependency_claims": [
                {"claim_id": claim.claim_id, "text": claim.text, "status": claim.status}
                for answer in dependency_answers for claim in answer.claims
            ],
            "retrieval_status": evidence.status,
            "evidence": self._bounded_evidence(evidence),
            "auxiliary_images": [
                {
                    "image_id": image.image_id,
                    "document_id": image.document_id,
                    "canonical_description": image.description,
                    "expanded_description": image.expanded_description,
                    "visual_findings": image.visual_findings,
                    "canonical_similarity": image.similarity,
                    "visual_relevance": image.expansion_relevance,
                }
                for image in evidence.image_evidence
            ],
        }
        if self.max_validation_attempts < 1:
            raise ValueError("max_validation_attempts must be positive")
        prompt = json.dumps(payload)
        response = ""
        for attempt in range(self.max_validation_attempts):
            from jurisynth.agentic_reasoner.schemas import LEAF_ANSWER_SCHEMA
            response = await self.model.complete(system=_LEAF_SYSTEM_PROMPT, user=prompt, max_tokens=self.max_tokens, response_schema=LEAF_ANSWER_SCHEMA)
            try:
                parsed = _parse_leaf_response(response)
                break
            except ValueError as exc:
                if attempt + 1 == self.max_validation_attempts:
                    raise
                prompt = json.dumps({"original_input": payload, "validation_error": str(exc)})
        claims = [
            Claim(None, item["text"], list(item.get("evidence_refs", [])), item.get("status", "supported"))
            for item in parsed["claims"]
        ]
        return LeafAnswer(node.query_id, parsed["status"], parsed["answer_text"], claims, evidence, raw_output=response)

    def _bounded_evidence(self, evidence: EvidenceBundle) -> list[dict[str, object]]:
        """Create a deterministic, prompt-safe evidence view without mutating logs."""
        if min(
            self.max_evidence_items,
            self.max_sources_per_item,
            self.max_source_characters,
            self.max_assertion_field_characters,
            self.max_evidence_payload_characters,
        ) < 1:
            raise ValueError("Evidence prompt-budget settings must be positive")

        remaining = self.max_evidence_payload_characters
        selected: list[dict[str, object]] = []
        ranked = sorted(
            evidence.evidence_items,
            key=lambda item: (
                -(item.relevance_score if item.relevance_score is not None else -1.0),
                -(item.structural_score if item.structural_score is not None else -1.0),
                item.evidence_id,
            ),
        )
        for item in ranked[: self.max_evidence_items]:
            candidate = {
                "evidence_id": item.evidence_id,
                "assertion": {
                    "subject": _truncate(item.assertion.subject, self.max_assertion_field_characters),
                    "predicate": _truncate(item.assertion.predicate, self.max_assertion_field_characters),
                    "object": _truncate(item.assertion.object, self.max_assertion_field_characters),
                },
                "source_chunks": [
                    {
                        "chunk_id": source.chunk_id,
                        "document_id": source.document_id,
                        "text": _truncate(source.text, self.max_source_characters),
                        "text_truncated": len(source.text) > self.max_source_characters,
                    }
                    for source in item.source_chunks[: self.max_sources_per_item]
                ],
            }
            serialized = json.dumps(candidate, ensure_ascii=False)
            if len(serialized) > remaining:
                continue
            selected.append(candidate)
            remaining -= len(serialized)
        return selected


_LEAF_SYSTEM_PROMPT = """You answer one legal-information subquestion from supplied evidence only.
Return JSON only: {"status":"supported|partially_supported|insufficient_evidence","answer_text":"...","claims":[{"text":"...","evidence_refs":["E..."],"status":"supported|partially_supported|insufficient_evidence"}]}.
Every substantive claim must cite one or more supplied evidence IDs. `text_truncated: true` means the supplied source is only an excerpt: do not infer omitted content, and use partially_supported or insufficient_evidence when the excerpt cannot establish the complete answer. Auxiliary image descriptions are contextual only and cannot independently support a legal claim. If evidence is weak, state the limitation rather than inventing support."""


def _truncate(value: str, limit: int) -> str:
    """Keep a visible truncation marker so the model never mistakes an excerpt for full text."""
    if len(value) <= limit:
        return value
    return value[: max(0, limit - 1)] + "…"


def _parse_leaf_response(response: str) -> dict[str, object]:
    candidate = _extract_json_object(response)
    try:
        payload = json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise ValueError("Leaf model response is not valid JSON.") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("answer_text"), str) or not isinstance(payload.get("claims"), list):
        raise ValueError("Leaf model response does not match the required shape.")
    if payload.get("status") not in {"supported", "partially_supported", "insufficient_evidence"}:
        raise ValueError("Leaf model response has an invalid status.")
    for claim in payload["claims"]:
        if not isinstance(claim, dict) or not isinstance(claim.get("text"), str) or not isinstance(claim.get("evidence_refs", []), list):
            raise ValueError("Leaf model response contains a malformed claim.")
    return payload


def _extract_json_object(response: str) -> str:
    """Tolerate harmless Markdown/prose around an otherwise valid JSON answer.

    The evidence/claim validator remains strict after parsing; this only avoids
    discarding a schema-compliant answer because a hosted model wrapped it in a
    code fence despite the JSON-only instruction.
    """
    candidate = response.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        candidate = "\n".join(lines).strip()
    if candidate.startswith("{") and candidate.endswith("}"):
        return candidate
    start, end = candidate.find("{"), candidate.rfind("}")
    return candidate[start:end + 1] if start >= 0 and end > start else candidate
