"""Retrieval-first, provenance-backed evaluation for a Jurisynth pilot batch."""

from __future__ import annotations

import json
import asyncio
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Iterable

from rdflib import URIRef

from jurisynth.contracts import EvidenceBundle, SourceChunk
from jurisynth.contracts import RetrievalRequest


@dataclass(frozen=True, slots=True)
class RetrievalEvalCase:
    case_id: str
    query: str
    expected_assertion: tuple[str, str, str]
    expected_chunk_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RetrievalEvalResult:
    case_id: str
    retrieval_status: str
    assertion_recalled: bool
    provenance_valid: bool
    direct_chunk_recalled: bool = False
    retrieved_evidence: list[dict[str, object]] = field(default_factory=list)
    expected_assertion_rank: int | None = None
    subject_entity_recalled: bool = False
    object_entity_recalled: bool = False
    predicate_recalled: bool = False


@dataclass(frozen=True, slots=True)
class RetrievalReviewItem:
    case: RetrievalEvalCase
    result: RetrievalEvalResult


@dataclass(frozen=True, slots=True)
class TableRetrievalEvalCase:
    case_id: str
    query: str
    document_id: str
    table_id: str
    row_id: int


@dataclass(frozen=True, slots=True)
class TableRetrievalEvalResult:
    case_id: str
    retrieval_status: str
    table_recalled: bool
    row_recalled: bool


@dataclass(frozen=True, slots=True)
class NaturalRetrievalEvalCase:
    """A human-authored, source-aligned question; not a general legal-QA gold answer."""

    case_id: str
    query: str
    expected_document_id: str
    expected_chunk_ids: tuple[str, ...]
    scope_note: str = ""


@dataclass(frozen=True, slots=True)
class NaturalRetrievalEvalResult:
    case_id: str
    retrieval_status: str
    expected_document_recalled: bool
    expected_chunk_recalled: bool
    retrieved_evidence: list[dict[str, object]] = field(default_factory=list)


def build_assertion_cases(
    dataset,
    chunk_resolver: Callable[[URIRef], SourceChunk | None],
    *,
    chunk_namespace: str = "http://jurisynth/source/chunk/",
    limit: int | None = None,
    query_style: str = "subject_predicate",
) -> list[RetrievalEvalCase]:
    """Build deterministic known-target retrieval probes from semantic chunk graphs only.

    These are controlled retrieval probes, not natural legal-QA questions.  The
    default includes the subject and predicate; the former subject/object-only
    template is retained solely to reproduce legacy pilot artifacts.
    """
    if query_style not in {"subject_predicate", "legacy_subject_object"}:
        raise ValueError("query_style must be 'subject_predicate' or 'legacy_subject_object'")
    cases: list[RetrievalEvalCase] = []
    for graph in sorted(dataset.graphs(), key=lambda item: str(item.identifier)):
        if not str(graph.identifier).startswith(chunk_namespace):
            continue
        source_chunk = chunk_resolver(graph.identifier)
        if source_chunk is None:
            continue
        for subject, predicate, obj in sorted(graph, key=lambda triple: tuple(map(str, triple))):
            assertion = (str(subject), str(predicate), str(obj))
            cases.append(
                RetrievalEvalCase(
                    case_id=f"assertion_{len(cases) + 1:05d}",
                    query=_query_for_assertion(*assertion, query_style=query_style),
                    expected_assertion=assertion,
                    expected_chunk_ids=(source_chunk.chunk_id,),
                )
            )
            if limit is not None and len(cases) >= limit:
                return cases
    return cases


def build_table_cases(table_index, *, limit: int | None = None) -> list[TableRetrievalEvalCase]:
    """Create deterministic row-echo integrity probes, not realistic user questions."""
    cases: list[TableRetrievalEvalCase] = []
    for table in sorted(table_index.table_metadata, key=lambda item: (item["doc_id"], item["table_id"])):
        source = table_index._load_table(table["doc_id"], table["table_id"])
        for row_id, row in enumerate(source.get("data") or []):
            text = " ".join(str(value).strip() for value in row if str(value).strip())
            if not text:
                continue
            cases.append(TableRetrievalEvalCase(
                case_id=f"table_row_{len(cases) + 1:05d}",
                query=f"Find the table row containing: {text}",
                document_id=table["doc_id"],
                table_id=table["table_id"],
                row_id=row_id,
            ))
            if limit is not None and len(cases) >= limit:
                return cases
    return cases


def build_stratified_table_cases(
    table_index,
    *,
    limit: int = 20,
    query_style: str = "natural",
) -> list[TableRetrievalEvalCase]:
    """Sample rows across profiles/documents using natural or integrity-probe queries."""
    if limit < 1:
        raise ValueError("limit must be positive")
    if query_style not in {"natural", "integrity"}:
        raise ValueError("query_style must be 'natural' or 'integrity'")
    buckets: dict[str, list[TableRetrievalEvalCase]] = {"numeric": [], "mixed": [], "text": []}
    for table in sorted(table_index.table_metadata, key=lambda item: (item["doc_id"], item["table_id"])):
        source = table_index._load_table(table["doc_id"], table["table_id"])
        for row_id, row in enumerate(source.get("data") or []):
            text = " ".join(str(value).strip() for value in row if str(value).strip())
            if not text:
                continue
            query = _natural_table_query(source, row) if query_style == "natural" else f"Find the table row containing: {text}"
            buckets[_table_row_profile(text)].append(TableRetrievalEvalCase(
                case_id="",
                query=query,
                document_id=table["doc_id"],
                table_id=table["table_id"],
                row_id=row_id,
            ))
    selected: list[TableRetrievalEvalCase] = []
    seen_documents: set[str] = set()
    positions = {bucket: 0 for bucket in buckets}
    while len(selected) < limit:
        added = False
        for bucket in ("numeric", "mixed", "text"):
            candidates = buckets[bucket]
            while positions[bucket] < len(candidates) and candidates[positions[bucket]].document_id in seen_documents:
                positions[bucket] += 1
            if positions[bucket] >= len(candidates):
                continue
            selected.append(candidates[positions[bucket]])
            seen_documents.add(candidates[positions[bucket]].document_id)
            positions[bucket] += 1
            added = True
            if len(selected) == limit:
                break
        if not added:
            break
    return [
        TableRetrievalEvalCase(f"table_row_{index:05d}", case.query, case.document_id, case.table_id, case.row_id)
        for index, case in enumerate(selected, start=1)
    ]


def _table_row_profile(text: str) -> str:
    tokens = re.findall(r"\S+", text)
    numeric = sum(bool(re.fullmatch(r"[\d.,%+\-]+", token)) for token in tokens)
    if tokens and numeric / len(tokens) >= 0.6:
        return "numeric"
    if numeric:
        return "mixed"
    return "text"


def evaluate_bundle(case: RetrievalEvalCase, bundle: EvidenceBundle) -> RetrievalEvalResult:
    """Score exact-triple, entity, predicate, and source provenance separately."""
    ranked_items = sorted(
        bundle.evidence_items,
        key=lambda item: (
            -len(item.matched_concept_ids),
            -(item.relevance_score if item.relevance_score is not None else -1.0),
            -(item.structural_score if item.structural_score is not None else -1.0),
            item.evidence_id,
        ),
    )
    matching_items = [
        item for item in ranked_items
        if (item.assertion.subject, item.assertion.predicate, item.assertion.object) == case.expected_assertion
    ]
    retrieved_chunks = {chunk.chunk_id for item in matching_items for chunk in item.source_chunks}
    direct_chunk_ids = {
        str(item["chunk_id"])
        for item in bundle.retrieval_metadata.get("direct_chunk_matches", [])
        if isinstance(item, dict) and "chunk_id" in item
    }
    expected_subject, expected_predicate, expected_object = case.expected_assertion
    expected_rank = next(
        (index for index, item in enumerate(ranked_items, start=1)
         if (item.assertion.subject, item.assertion.predicate, item.assertion.object) == case.expected_assertion),
        None,
    )
    return RetrievalEvalResult(
        case_id=case.case_id,
        retrieval_status=bundle.status,
        assertion_recalled=bool(matching_items),
        provenance_valid=bool(matching_items) and set(case.expected_chunk_ids).issubset(retrieved_chunks),
        direct_chunk_recalled=set(case.expected_chunk_ids).issubset(direct_chunk_ids),
        retrieved_evidence=_review_evidence_preview(bundle),
        expected_assertion_rank=expected_rank,
        subject_entity_recalled=any(expected_subject in {item.assertion.subject, item.assertion.object} for item in ranked_items),
        object_entity_recalled=any(expected_object in {item.assertion.subject, item.assertion.object} for item in ranked_items),
        predicate_recalled=any(item.assertion.predicate == expected_predicate for item in ranked_items),
    )


def evaluate_table_bundle(case: TableRetrievalEvalCase, bundle: EvidenceBundle) -> TableRetrievalEvalResult:
    """Score table and row recovery independently, retaining the retrieval status."""
    matching_tables = [
        item for item in bundle.table_evidence
        if item.document_id == case.document_id and item.table_id == case.table_id
    ]
    return TableRetrievalEvalResult(
        case.case_id,
        bundle.status,
        bool(matching_tables),
        any(case.row_id in item.row_ids for item in matching_tables),
    )


def summarize_table_results(results: Iterable[TableRetrievalEvalResult]) -> dict[str, float | int]:
    values = list(results)
    total = len(values)
    return {
        "case_count": total,
        "table_recall": sum(item.table_recalled for item in values) / total if total else 0.0,
        "row_recall": sum(item.row_recalled for item in values) / total if total else 0.0,
        "success_count": sum(item.retrieval_status == "success" for item in values),
        "weak_count": sum(item.retrieval_status == "weak" for item in values),
        "empty_count": sum(item.retrieval_status == "empty" for item in values),
        "error_count": sum(item.retrieval_status == "error" for item in values),
    }


def summarize_results(results: Iterable[RetrievalEvalResult]) -> dict[str, float | int]:
    values = list(results)
    total = len(values)
    return {
        "case_count": total,
        "assertion_recall": sum(item.assertion_recalled for item in values) / total if total else 0.0,
        "provenance_validity": sum(item.provenance_valid for item in values) / total if total else 0.0,
        "direct_chunk_recall": sum(item.direct_chunk_recalled for item in values) / total if total else 0.0,
        "subject_entity_recall": sum(item.subject_entity_recalled for item in values) / total if total else 0.0,
        "object_entity_recall": sum(item.object_entity_recalled for item in values) / total if total else 0.0,
        "predicate_recall": sum(item.predicate_recalled for item in values) / total if total else 0.0,
        "assertion_mrr": sum(1 / item.expected_assertion_rank for item in values if item.expected_assertion_rank) / total if total else 0.0,
        "success_count": sum(item.retrieval_status == "success" for item in values),
        "weak_count": sum(item.retrieval_status == "weak" for item in values),
        "empty_count": sum(item.retrieval_status == "empty" for item in values),
        "error_count": sum(item.retrieval_status == "error" for item in values),
    }


def write_cases_jsonl(cases: Iterable[RetrievalEvalCase], destination: str | Path) -> None:
    """Persist cases as JSONL for reproducible later execution and manual review."""
    with Path(destination).open("w", encoding="utf-8") as handle:
        for case in cases:
            handle.write(json.dumps(asdict(case), ensure_ascii=False, sort_keys=True) + "\n")


def write_results_jsonl(results: Iterable[RetrievalEvalResult], destination: str | Path) -> None:
    """Persist per-case outcomes so aggregate metrics remain auditable."""
    with Path(destination).open("w", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps(asdict(result), ensure_ascii=False, sort_keys=True) + "\n")


def write_summary_json(results: Iterable[RetrievalEvalResult], destination: str | Path) -> dict[str, float | int]:
    """Write the aggregate metrics paired with the case-level JSONL results."""
    summary = summarize_results(results)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def select_review_items(
    cases: Iterable[RetrievalEvalCase],
    results: Iterable[RetrievalEvalResult],
    *,
    limit: int = 20,
) -> list[RetrievalReviewItem]:
    """Prioritize misses/weak outcomes, then choose a deterministic review sample."""
    if limit < 1:
        raise ValueError("limit must be positive")
    results_by_id = {result.case_id: result for result in results}
    paired = [RetrievalReviewItem(case, results_by_id[case.case_id]) for case in cases if case.case_id in results_by_id]
    priority = [
        item for item in paired
        if not item.result.assertion_recalled
        or not item.result.provenance_valid
        or item.result.retrieval_status in {"weak", "empty", "error"}
    ]
    priority_ids = {item.case.case_id for item in priority}
    remainder = [item for item in paired if item.case.case_id not in priority_ids]
    return sorted(priority, key=lambda item: item.case.case_id)[:limit] + sorted(remainder, key=lambda item: item.case.case_id)[:max(0, limit - len(priority))]


def write_review_items_jsonl(items: Iterable[RetrievalReviewItem], destination: str | Path) -> None:
    """Write a review queue with expected targets, retrieved excerpts, and label fields."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps({
                "case": asdict(item.case),
                "result": asdict(item.result),
                "human_review": {
                    "evidence_relevant": None,
                    "source_supports_assertion": None,
                    "status_appropriate": None,
                    "notes": "",
                },
            }, ensure_ascii=False, sort_keys=True) + "\n")


async def run_evaluation(cases: Iterable[RetrievalEvalCase], mechanism: object, *, max_concurrency: int = 4) -> list[RetrievalEvalResult]:
    """Run one opaque retrieval call per known-target case and score the results."""
    if max_concurrency < 1:
        raise ValueError("max_concurrency must be positive")
    semaphore = asyncio.Semaphore(max_concurrency)

    async def run_case(case: RetrievalEvalCase) -> RetrievalEvalResult:
        async with semaphore:
            bundle = await mechanism.retrieve_evidence(RetrievalRequest(case.case_id, case.query))
            return evaluate_bundle(case, bundle)

    return list(await asyncio.gather(*(run_case(case) for case in cases)))


async def run_table_evaluation(cases: Iterable[TableRetrievalEvalCase], mechanism: object, *, max_concurrency: int = 4) -> list[TableRetrievalEvalResult]:
    """Run one opaque table retrieval call per known-row evaluation case."""
    if max_concurrency < 1:
        raise ValueError("max_concurrency must be positive")
    semaphore = asyncio.Semaphore(max_concurrency)

    async def run_case(case: TableRetrievalEvalCase) -> TableRetrievalEvalResult:
        async with semaphore:
            bundle = await mechanism.retrieve_evidence(RetrievalRequest(case.case_id, case.query))
            return evaluate_table_bundle(case, bundle)

    return list(await asyncio.gather(*(run_case(case) for case in cases)))


async def run_natural_evaluation(cases: Iterable[NaturalRetrievalEvalCase], mechanism: object, *, max_concurrency: int = 1) -> list[NaturalRetrievalEvalResult]:
    """Measure source/chunk recovery for authored natural questions only."""
    if max_concurrency < 1:
        raise ValueError("max_concurrency must be positive")
    semaphore = asyncio.Semaphore(max_concurrency)

    async def run_case(case: NaturalRetrievalEvalCase) -> NaturalRetrievalEvalResult:
        async with semaphore:
            bundle = await mechanism.retrieve_evidence(RetrievalRequest(case.case_id, case.query))
            chunks = {
                (source.document_id, source.chunk_id)
                for item in bundle.evidence_items
                for source in item.source_chunks
            }
            return NaturalRetrievalEvalResult(
                case.case_id,
                bundle.status,
                any(document_id == case.expected_document_id for document_id, _chunk_id in chunks),
                all((case.expected_document_id, chunk_id) in chunks for chunk_id in case.expected_chunk_ids),
                _review_evidence_preview(bundle),
            )

    return list(await asyncio.gather(*(run_case(case) for case in cases)))


def read_natural_cases(source: str | Path) -> list[NaturalRetrievalEvalCase]:
    cases: list[NaturalRetrievalEvalCase] = []
    for line_number, line in enumerate(Path(source).read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        payload = json.loads(line)
        try:
            cases.append(NaturalRetrievalEvalCase(
                case_id=str(payload["case_id"]),
                query=str(payload["query"]),
                expected_document_id=str(payload["expected_document_id"]),
                expected_chunk_ids=tuple(str(value) for value in payload["expected_chunk_ids"]),
                scope_note=str(payload.get("scope_note", "")),
            ))
        except (KeyError, TypeError) as exc:
            raise ValueError(f"Malformed natural evaluation case at line {line_number}") from exc
    return cases


def summarize_natural_results(results: Iterable[NaturalRetrievalEvalResult]) -> dict[str, float | int]:
    values = list(results)
    total = len(values)
    return {
        "case_count": total,
        "expected_document_recall": sum(item.expected_document_recalled for item in values) / total if total else 0.0,
        "expected_chunk_recall": sum(item.expected_chunk_recalled for item in values) / total if total else 0.0,
        "success_count": sum(item.retrieval_status == "success" for item in values),
        "weak_count": sum(item.retrieval_status == "weak" for item in values),
        "empty_count": sum(item.retrieval_status == "empty" for item in values),
        "error_count": sum(item.retrieval_status == "error" for item in values),
    }


def write_table_results_jsonl(results: Iterable[TableRetrievalEvalResult], destination: str | Path) -> None:
    """Persist table-evaluation outcomes beside their assertion-evaluation counterparts."""
    with Path(destination).open("w", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps(asdict(result), ensure_ascii=False, sort_keys=True) + "\n")


def write_table_summary_json(results: Iterable[TableRetrievalEvalResult], destination: str | Path) -> dict[str, float | int]:
    summary = summarize_table_results(results)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary


def _query_for_assertion(subject: str, predicate: str, obj: str, *, query_style: str) -> str:
    """Produce transparent controlled probes without leaking RDF URI syntax."""
    if query_style == "legacy_subject_object":
        return f"What relationship is stated between '{_display_term(subject)}' and '{_display_term(obj)}'?"
    del obj
    return (
        f"According to the source, what is stated about '{_display_term(subject)}' "
        f"in relation to '{_display_term(predicate)}'?"
    )


def _display_term(value: str) -> str:
    """Turn a URI-shaped resource identifier into a minimally readable query term."""
    tail = value.rstrip("/#").rsplit("/", maxsplit=1)[-1].rsplit("#", maxsplit=1)[-1]
    return tail.replace("_", " ")


def _natural_table_query(table: dict[str, object], row: list[object]) -> str:
    """Use one row identifier and table context instead of leaking an entire target row."""
    values = [str(value).strip() for value in row]
    headers = [str(header).strip() for header in (table.get("header") or [])]
    anchor_index = next(
        (index for index, value in enumerate(values) if len(value) >= 3 and any(char.isalpha() for char in value)),
        next((index for index, value in enumerate(values) if value), 0),
    )
    anchor = _shorten(values[anchor_index] if anchor_index < len(values) else "entry", 120)
    label = headers[anchor_index] if anchor_index < len(headers) and headers[anchor_index] else f"column {anchor_index + 1}"
    context = _shorten(str(table.get("context") or ""), 140)
    context_clause = f" in the table about {context}" if context else " in this table"
    return f"What information is recorded{context_clause} for {label} '{anchor}'?"


def _shorten(value: str, limit: int) -> str:
    return value if len(value) <= limit else value[: limit - 1] + "…"


def _review_evidence_preview(bundle: EvidenceBundle) -> list[dict[str, object]]:
    """Expose a small auditable excerpt for human review, never a full retrieved payload."""
    preview: list[dict[str, object]] = []
    for item in sorted(
        bundle.evidence_items,
        key=lambda value: (-(value.relevance_score or -1.0), value.evidence_id),
    )[:5]:
        preview.append({
            "evidence_id": item.evidence_id,
            "assertion": asdict(item.assertion),
            "source_chunks": [
                {
                    "chunk_id": source.chunk_id,
                    "document_id": source.document_id,
                    "text_excerpt": _shorten(source.text, 500),
                }
                for source in item.source_chunks[:1]
            ],
        })
    return preview
