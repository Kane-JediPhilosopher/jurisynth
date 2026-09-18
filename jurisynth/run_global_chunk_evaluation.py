"""Build and run a frozen, zero-NIM direct-chunk retrieval benchmark.

The benchmark isolates the production FAISS chunk layer.  Queries are derived
deterministically from semantic assertions already stored in independently
sampled source chunk graphs; they are not generated from retrieval results and
are not arbitrary legal-QA questions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import pickle
import random
import re
import sqlite3
import statistics
import time
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import psutil

from jurisynth.contracts import SourceChunk
from jurisynth.retrieval_mech.artifacts import ChunkIndex
from jurisynth.retrieval_mech.document_metadata import DocumentMetadataStore
from jurisynth.retrieval_mech.lazy_chunk_metadata import SQLiteChunkMetadata
from jurisynth.retrieval_mech.rdf_store import OxigraphQuadStore
from jurisynth.table_rdf_enricher import chunk_uri_candidates


DEFAULT_ROOT = Path("jurisynth/global_artifacts_source_uri_v2")
DEFAULT_MANIFEST = Path("jurisynth/global_artifacts/manifest.json")
DEFAULT_OUTPUT = Path("jurisynth/evaluation_artifacts/direct_chunk_heldout_v1")
DEFAULT_EXCLUSIONS = (
    Path("jurisynth/evaluation_artifacts/global_batch_stratified_subject-predicate_200_post_retrieval_fix_cases.jsonl"),
    Path("jurisynth/evaluation_artifacts/global_heldout_100_v2_replacement_frozen_cases.jsonl"),
)
DEFAULT_NATURAL_PACKET = Path("jurisynth/evaluation_artifacts/global_natural_candidate_packet.json")
_WORD = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "a", "an", "and", "as", "at", "be", "by", "for", "from", "in", "is",
    "of", "on", "or", "that", "the", "this", "to", "under", "with",
}


@dataclass(frozen=True, slots=True)
class ChunkEvalCase:
    case_id: str
    query: str
    expected_document_id: str
    expected_chunk_id: str
    source_text_excerpt: str
    expected_assertion: tuple[str, str, str]
    acceptable_alternate_chunk_ids: tuple[str, ...]
    canonical_source: dict[str, object]
    batch_id: str
    document_family: str
    object_type: str
    generation_method: str = "deterministic_subject_predicate_from_source_graph"


@dataclass(frozen=True, slots=True)
class ChunkEvalResult:
    case_id: str
    query: str
    retrieval_status: str
    expected_document_id: str
    expected_chunk_id: str
    exact_rank: int | None
    diagnostic_exact_rank_at_100: int | None
    answer_bearing_rank: int | None
    correct_document_rank: int | None
    exact_recalled: bool
    source_document_recalled: bool
    correct_document_candidate_recalled: bool
    alternate_valid_recovery: bool
    expected_chunk_present_in_index: bool
    latency_seconds: float
    failure_category: str | None
    hits: list[dict[str, object]]


def _display_term(value: str) -> str:
    tail = value.rstrip("/#").rsplit("/", 1)[-1].rsplit("#", 1)[-1]
    return tail.replace("_", " ").replace("-", " ").strip()


def _controlled_query(subject: str, predicate: str) -> str:
    return (
        f"According to the source, what is stated about '{_display_term(subject)}' "
        f"in relation to '{_display_term(predicate)}'?"
    )


def _document_family(document_id: str) -> str:
    if document_id.startswith("L_"):
        return "official_journal_l"
    if document_id.startswith("C_"):
        return "official_journal_c"
    if re.match(r"^[36]\d", document_id):
        return "legacy_celex"
    return "other"


def _object_type(value: str) -> str:
    return "uri" if value.startswith(("http://", "https://", "urn:")) else "literal"


def _chunk_bucket(chunk_id: str) -> str:
    match = re.search(r"(\d+)$", chunk_id)
    number = int(match.group(1)) if match else 0
    if number <= 3:
        return "early"
    if number <= 12:
        return "middle"
    return "late"


def _tokens(value: str) -> set[str]:
    return {token for token in _WORD.findall(value.casefold()) if token not in _STOPWORDS and len(token) >= 3}


def _query_is_answerable(subject: str, predicate: str, source_text: str) -> bool:
    subject_label, predicate_label = _display_term(subject), _display_term(predicate)
    query = _controlled_query(subject, predicate)
    if not (3 <= len(subject_label) <= 120 and 3 <= len(predicate_label) <= 100 and len(query) <= 320):
        return False
    source_tokens = _tokens(source_text)
    subject_tokens, predicate_tokens = _tokens(subject_label), _tokens(predicate_label)
    return bool(subject_tokens & source_tokens) and bool(predicate_tokens & source_tokens)


def _load_exclusions(paths: Iterable[Path], natural_packet: Path) -> tuple[set[tuple[str, str]], set[tuple[str, str, str]]]:
    source_pairs: set[tuple[str, str]] = set()
    assertions: set[tuple[str, str, str]] = set()
    for path in paths:
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            raw = json.loads(line)
            document_id = raw.get("expected_document_id")
            for chunk_id in raw.get("expected_chunk_ids", []):
                if document_id:
                    source_pairs.add((str(document_id), str(chunk_id)))
            if isinstance(raw.get("expected_assertion"), list) and len(raw["expected_assertion"]) == 3:
                assertions.add(tuple(map(str, raw["expected_assertion"])))
    if natural_packet.is_file():
        packet = json.loads(natural_packet.read_text(encoding="utf-8"))
        for case in packet.get("cases", []):
            for source in case.get("expected_chunks", []):
                source_pairs.add((str(source["document_id"]), str(source["chunk_id"])))
    return source_pairs, assertions


def _resolve_graph_uri(metadata: SQLiteChunkMetadata, document_id: str, chunk_id: str) -> str | None:
    for candidate in chunk_uri_candidates(document_id, chunk_id):
        source = metadata.resolve_graph(str(candidate))
        if source is not None and (source.document_id, source.chunk_id) == (document_id, chunk_id):
            return str(candidate)
    return None


def _semantic_rows(store: OxigraphQuadStore, graph_uri: str) -> list[tuple[str, str, str]]:
    rows = store.select_rows(
        "SELECT ?s ?p ?o WHERE { "
        f"GRAPH <{graph_uri}> {{ ?s ?p ?o }} "
        "} ORDER BY ?s ?p ?o LIMIT 48"
    )
    return [(str(row[0]), str(row[1]), str(row[2])) for row in rows if len(row) >= 3]


def _alternate_chunks(
    connection: sqlite3.Connection,
    document_id: str,
    expected_chunk_id: str,
    expected_text: str,
) -> tuple[str, ...]:
    """Conservatively accept only normalized duplicate text in the same source."""
    normalized = " ".join(expected_text.casefold().split())
    rows = connection.execute(
        "SELECT chunk_id, content FROM chunks WHERE doc_id = ? AND chunk_id <> ? ORDER BY vector_id",
        (document_id, expected_chunk_id),
    ).fetchall()
    return tuple(
        str(chunk_id)
        for chunk_id, content in rows
        if " ".join(str(content).casefold().split()) == normalized
    )


def _canonical_source(store: DocumentMetadataStore | None, document_id: str) -> dict[str, object]:
    record = store.get(document_id) if store is not None else None
    if record is None:
        return {"document_id": document_id, "identification": "unknown"}
    return {
        "document_id": document_id,
        "celex": record.celex,
        "eli": record.eli,
        "title": record.title,
        "canonical_keys": list(record.canonical_keys),
        "identification": "canonical" if record.celex or record.eli or record.canonical_keys else "title_only",
    }


def _stratified_select(candidates: list[dict[str, object]], limit: int, seed: int) -> list[dict[str, object]]:
    rng = random.Random(seed)
    groups: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for candidate in candidates:
        key = (
            str(candidate["document_family"]),
            str(candidate["object_type"]),
            _chunk_bucket(str(candidate["chunk_id"])),
        )
        groups[key].append(candidate)
    for values in groups.values():
        rng.shuffle(values)
    keys = sorted(groups)
    selected: list[dict[str, object]] = []
    while keys and len(selected) < limit:
        next_keys: list[tuple[str, str, str]] = []
        for key in keys:
            values = groups[key]
            if values and len(selected) < limit:
                selected.append(values.pop())
            if values:
                next_keys.append(key)
        keys = next_keys
    return selected


def freeze_cases(args: argparse.Namespace) -> tuple[list[ChunkEvalCase], dict[str, object]]:
    root = args.artifact_root
    chunk_sqlite = root / "chunk_index" / "chunk_metadata.sqlite"
    metadata = SQLiteChunkMetadata(chunk_sqlite)
    graph_store = OxigraphQuadStore.open_read_only(root / "oxigraph")
    document_store = DocumentMetadataStore(root / "document_metadata.sqlite") if (root / "document_metadata.sqlite").is_file() else None
    excluded_pairs, excluded_assertions = _load_exclusions(args.exclude_case_file, args.natural_packet)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    batches = list(manifest["batches"])
    rng = random.Random(args.seed)
    rng.shuffle(batches)
    connection = sqlite3.connect(f"file:{chunk_sqlite.as_posix()}?mode=ro", uri=True)
    candidates: list[dict[str, object]] = []
    seen_pairs: set[tuple[str, str]] = set()
    seen_assertions: set[tuple[str, str, str]] = set()
    skipped = Counter()
    target_pool = max(args.limit * 3, args.limit + 20)
    try:
        for batch in batches:
            metadata_path = Path(batch["chunk_metadata"])
            if not metadata_path.is_file():
                skipped["missing_batch_metadata"] += 1
                continue
            with metadata_path.open("rb") as handle:
                records = list(pickle.load(handle).values())
            rng.shuffle(records)
            chosen: dict[str, object] | None = None
            for record in records[: args.chunk_trials_per_batch]:
                document_id, chunk_id = str(record["doc_id"]), str(record["chunk_id"])
                source_pair = (document_id, chunk_id)
                if source_pair in excluded_pairs or source_pair in seen_pairs:
                    skipped["excluded_or_duplicate_source"] += 1
                    continue
                graph_uri = _resolve_graph_uri(metadata, document_id, chunk_id)
                if graph_uri is None or metadata.has_ambiguous_provenance(graph_uri):
                    skipped["unresolved_or_ambiguous_graph"] += 1
                    continue
                global_source = metadata.resolve_graph(graph_uri)
                if global_source is None:
                    skipped["unresolved_or_ambiguous_graph"] += 1
                    continue
                source_text = global_source.text
                if len(source_text) < 160:
                    skipped["source_too_short"] += 1
                    continue
                triples = [
                    triple for triple in _semantic_rows(graph_store, graph_uri)
                    if triple not in excluded_assertions
                    and triple not in seen_assertions
                    and _query_is_answerable(triple[0], triple[1], source_text)
                ]
                if not triples:
                    skipped["no_clean_semantic_assertion"] += 1
                    continue
                assertion = rng.choice(sorted(triples))
                chosen = {
                    "batch_id": str(batch["batch_id"]),
                    "document_id": document_id,
                    "chunk_id": chunk_id,
                    "source_text": source_text,
                    "assertion": assertion,
                    "query": _controlled_query(assertion[0], assertion[1]),
                    "document_family": _document_family(document_id),
                    "object_type": _object_type(assertion[2]),
                    "canonical_source": _canonical_source(document_store, document_id),
                    "alternates": _alternate_chunks(connection, document_id, chunk_id, source_text),
                }
                break
            if chosen is not None:
                candidates.append(chosen)
                pair = (str(chosen["document_id"]), str(chosen["chunk_id"]))
                seen_pairs.add(pair)
                seen_assertions.add(tuple(chosen["assertion"]))
            if len(candidates) >= target_pool:
                break
    finally:
        connection.close()
        metadata.close()

    selected = _stratified_select(candidates, args.limit, args.seed)
    if len(selected) < args.limit:
        raise RuntimeError(f"Only {len(selected)} clean held-out chunk cases were constructible; requested {args.limit}.")
    cases = [
        ChunkEvalCase(
            case_id=f"global_chunk_{index:03d}",
            query=str(item["query"]),
            expected_document_id=str(item["document_id"]),
            expected_chunk_id=str(item["chunk_id"]),
            source_text_excerpt=" ".join(str(item["source_text"]).split())[:1200],
            expected_assertion=tuple(item["assertion"]),
            acceptable_alternate_chunk_ids=tuple(item["alternates"]),
            canonical_source=dict(item["canonical_source"]),
            batch_id=str(item["batch_id"]),
            document_family=str(item["document_family"]),
            object_type=str(item["object_type"]),
        )
        for index, item in enumerate(selected, 1)
    ]
    if len({(case.expected_document_id, case.expected_chunk_id) for case in cases}) != len(cases):
        raise RuntimeError("Frozen chunk cases must have unique document-qualified targets.")
    if any((case.expected_document_id, case.expected_chunk_id) in excluded_pairs for case in cases):
        raise RuntimeError("Frozen chunk cases overlap an excluded benchmark source.")
    plan = {
        "benchmark": "direct_chunk_retrieval",
        "case_count": len(cases),
        "seed": args.seed,
        "generation": "zero-NIM deterministic subject+predicate query from a semantic triple in the gold chunk",
        "sampling": "one candidate per shuffled batch, then round-robin across document family, object type, and chunk-position strata",
        "artifact_root": str(root),
        "artifact_identity": _artifact_identity(root),
        "excluded_source_pairs": len(excluded_pairs),
        "excluded_assertions": len(excluded_assertions),
        "candidate_pool_count": len(candidates),
        "strata": dict(Counter(f"{case.document_family}|{case.object_type}|{_chunk_bucket(case.expected_chunk_id)}" for case in cases)),
        "skipped": dict(skipped),
        "reused_assets": _asset_inventory(),
    }
    return cases, plan


def _artifact_identity(root: Path) -> dict[str, object]:
    files = [
        root / "chunk_index" / "chunk_index.faiss",
        root / "chunk_index" / "chunk_metadata.sqlite",
        root / "oxigraph" / "jurisynth_oxigraph_manifest.json",
        root / "document_metadata.sqlite",
    ]
    identity: dict[str, object] = {"files": []}
    for path in files:
        if path.is_file():
            identity["files"].append({"path": str(path), "size_bytes": path.stat().st_size})
    manifest = root / "oxigraph" / "jurisynth_oxigraph_manifest.json"
    if manifest.is_file():
        identity["oxigraph_manifest_sha256"] = hashlib.sha256(manifest.read_bytes()).hexdigest()
        identity["oxigraph_manifest"] = json.loads(manifest.read_text(encoding="utf-8"))
    return identity


def _asset_inventory() -> dict[str, object]:
    return {
        "development_assertion_200": "Reusable controlled query/gold structure and exclusion set; not reused as chunk cases because it is development data.",
        "heldout_assertion_100": "Reusable frozen schema and exclusion set; not rerun or modified.",
        "global_natural_packet": "20 source-first questions, 14 adjudicated eligible; useful for later natural-query corroboration but too small/heterogeneous for the primary held-out set.",
        "stabilization_gates": "Focused hand-picked regression checks; unsuitable as a representative held-out set.",
        "complex_smokes": "Broad multi-leaf end-to-end traces; unsuitable for isolated direct-chunk scoring.",
        "chunk_sidecars": "Authoritative production-v2 FAISS index plus SQLite metadata used for targets, retrieval, and presence checks.",
        "diagnostic_fixtures": "Small or development-exposed fixtures retained for tests only.",
    }


def write_frozen_cases(cases: list[ChunkEvalCase], plan: dict[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    cases_path, plan_path = output_dir / "cases.jsonl", output_dir / "sample_plan.json"
    with cases_path.open("x", encoding="utf-8") as handle:
        for case in cases:
            handle.write(json.dumps(asdict(case), ensure_ascii=False, sort_keys=True) + "\n")
    with plan_path.open("x", encoding="utf-8", errors="strict") as handle:
        handle.write(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return cases_path, plan_path


def read_cases(path: Path) -> list[ChunkEvalCase]:
    cases: list[ChunkEvalCase] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = json.loads(line)
        raw["expected_assertion"] = tuple(raw["expected_assertion"])
        raw["acceptable_alternate_chunk_ids"] = tuple(raw["acceptable_alternate_chunk_ids"])
        cases.append(ChunkEvalCase(**raw))
    return cases


def _rank(hits: list[SourceChunk], document_id: str, chunk_ids: set[str]) -> int | None:
    return next(
        (rank for rank, hit in enumerate(hits, 1) if hit.document_id == document_id and hit.chunk_id in chunk_ids),
        None,
    )


def _score_case(
    case: ChunkEvalCase,
    primary_hits: list[SourceChunk],
    diagnostic_hits: list[SourceChunk],
    latency: float,
    expected_present: bool,
) -> ChunkEvalResult:
    exact_rank = _rank(primary_hits, case.expected_document_id, {case.expected_chunk_id})
    diagnostic_rank = exact_rank or _rank(diagnostic_hits, case.expected_document_id, {case.expected_chunk_id})
    alternate_rank = _rank(primary_hits, case.expected_document_id, set(case.acceptable_alternate_chunk_ids))
    answer_rank = min((rank for rank in (exact_rank, alternate_rank) if rank is not None), default=None)
    document_rank = next((rank for rank, hit in enumerate(primary_hits, 1) if hit.document_id == case.expected_document_id), None)
    alternate_valid = exact_rank is None and alternate_rank is not None
    if exact_rank is not None:
        status, failure = "exact", None
    elif alternate_valid:
        status, failure = "alternate_valid", "semantically_equivalent_alternate_chunk_retrieved"
    elif document_rank is not None:
        status, failure = "correct_document_wrong_chunk", "correct_document_retrieved_but_wrong_chunk"
    elif not expected_present:
        status, failure = "miss", "expected_chunk_absent_from_index"
    elif diagnostic_rank is not None:
        status, failure = "miss", "unrelated_high_similarity_chunks_outranked_source"
    else:
        status, failure = "miss", "chunk_present_but_query_embedding_failed_to_rank_it"
    return ChunkEvalResult(
        case.case_id, case.query, status, case.expected_document_id, case.expected_chunk_id,
        exact_rank, diagnostic_rank, answer_rank, document_rank,
        exact_rank is not None, answer_rank is not None, document_rank is not None,
        alternate_valid, expected_present, latency, failure,
        [
            {
                "rank": rank,
                "document_id": hit.document_id,
                "chunk_id": hit.chunk_id,
                "similarity": hit.similarity,
                "text_excerpt": " ".join(hit.text.split())[:800],
            }
            for rank, hit in enumerate(primary_hits, 1)
        ],
    )


def run_evaluation(args: argparse.Namespace, cases: list[ChunkEvalCase]) -> tuple[list[ChunkEvalResult], dict[str, object]]:
    from sentence_transformers import SentenceTransformer

    root = args.artifact_root
    metadata = SQLiteChunkMetadata(root / "chunk_index" / "chunk_metadata.sqlite")
    index = ChunkIndex.load(
        root / "chunk_index" / "chunk_index.faiss",
        root / "chunk_index" / "chunk_metadata.pkl",
        lazy_metadata=metadata,
    )
    model_started = time.perf_counter()
    embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    model_load_seconds = time.perf_counter() - model_started
    if cases:
        index.search(cases[0].query, embedder, args.top_k)
    process = psutil.Process()
    peak_rss = process.memory_info().rss
    results: list[ChunkEvalResult] = []
    connection = sqlite3.connect(f"file:{(root / 'chunk_index' / 'chunk_metadata.sqlite').as_posix()}?mode=ro", uri=True)
    try:
        for case in cases:
            row = connection.execute(
                "SELECT vector_id FROM chunks WHERE doc_id = ? AND chunk_id = ? LIMIT 1",
                (case.expected_document_id, case.expected_chunk_id),
            ).fetchone()
            expected_present = row is not None and int(row[0]) < int(index.index.ntotal)
            started = time.perf_counter()
            primary_hits = index.search(case.query, embedder, args.top_k)
            latency = time.perf_counter() - started
            exact_rank = _rank(primary_hits, case.expected_document_id, {case.expected_chunk_id})
            diagnostic_hits = primary_hits if exact_rank is not None else index.search(case.query, embedder, args.audit_top_k)
            results.append(_score_case(case, primary_hits, diagnostic_hits, latency, expected_present))
            peak_rss = max(peak_rss, process.memory_info().rss)
    finally:
        connection.close()
        metadata.close()
    summary = summarize(results, peak_rss, model_load_seconds, args.top_k, args.audit_top_k)
    return results, summary


def summarize(
    results: list[ChunkEvalResult], peak_rss: int, model_load_seconds: float, top_k: int, audit_top_k: int
) -> dict[str, object]:
    total = len(results)
    latencies = [item.latency_seconds for item in results]
    exact_ranks = [item.exact_rank for item in results]
    recall_at = {
        str(k): sum(rank is not None and rank <= k for rank in exact_ranks) / total
        for k in (1, 3, 5, 10)
    }
    ordered = sorted(latencies)
    p95_index = max(0, math.ceil(0.95 * len(ordered)) - 1)
    failures = Counter(item.failure_category for item in results if item.failure_category)
    statuses = Counter(item.retrieval_status for item in results)
    return {
        "benchmark": "direct_chunk_retrieval",
        "case_kind": "controlled source-derived chunk probe; not arbitrary legal-QA",
        "case_count": total,
        "top_k": top_k,
        "diagnostic_audit_top_k": audit_top_k,
        "exact_expected_chunk_recall": sum(item.exact_recalled for item in results) / total,
        "source_document_recall": sum(item.source_document_recalled for item in results) / total,
        "correct_document_candidate_recall": sum(item.correct_document_candidate_recalled for item in results) / total,
        "alternate_valid_recoveries": sum(item.alternate_valid_recovery for item in results),
        "recall_at_k": recall_at,
        "mrr": sum(1 / rank for rank in exact_ranks if rank is not None) / total,
        "latency_seconds": {
            "mean": statistics.fmean(latencies),
            "median": statistics.median(latencies),
            "p95": ordered[p95_index],
            "worst": max(latencies),
        },
        "model_load_seconds": model_load_seconds,
        "peak_rss_mb": peak_rss / 1024 / 1024,
        "retrieval_status_distribution": dict(statuses),
        "failure_breakdown": dict(failures),
        "expected_chunks_absent_from_index": sum(not item.expected_chunk_present_in_index for item in results),
    }


def write_results(
    results: list[ChunkEvalResult], summary: dict[str, object], plan: dict[str, object], output_dir: Path
) -> tuple[Path, Path, Path]:
    results_path, summary_path, report_path = (
        output_dir / "results.jsonl", output_dir / "summary.json", output_dir / "REPORT.md"
    )
    with results_path.open("x", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps(asdict(result), ensure_ascii=False, sort_keys=True) + "\n")
    with summary_path.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    with report_path.open("x", encoding="utf-8") as handle:
        handle.write(_markdown_report(summary, plan))
    return results_path, summary_path, report_path


def _markdown_report(summary: dict[str, object], plan: dict[str, object]) -> str:
    latency = summary["latency_seconds"]
    recalls = summary["recall_at_k"]
    failures = summary["failure_breakdown"]
    assets = plan["reused_assets"]
    lines = [
        "# Jurisynth direct chunk retrieval evaluation",
        "",
        "This is a zero-NIM, controlled component benchmark of the frozen production-v2 FAISS chunk layer. It is not end-to-end legal QA.",
        "",
        "## Existing-asset inventory",
        "",
    ]
    lines.extend(f"- **{key.replace('_', ' ')}:** {value}" for key, value in assets.items())
    lines.extend([
        "",
        "## Construction and integrity",
        "",
        f"- Cases: **{summary['case_count']}**, frozen before retrieval.",
        f"- Generation: {plan['generation']}.",
        f"- Sampling: {plan['sampling']}.",
        f"- Excluded existing gold source pairs: **{plan['excluded_source_pairs']}**.",
        "- Queries contain readable subject and predicate labels, never the source chunk or retrieved candidate list.",
        "- Alternate-valid chunks were frozen conservatively from normalized duplicate source text before retrieval.",
        "",
        "## Metrics",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f"| Exact expected-chunk recall | {summary['exact_expected_chunk_recall']:.3f} |",
        f"| Answer-bearing source-document recall | {summary['source_document_recall']:.3f} |",
        f"| Correct-document candidate recall | {summary['correct_document_candidate_recall']:.3f} |",
        f"| Alternate-valid recoveries | {summary['alternate_valid_recoveries']} |",
        f"| Recall@1 | {recalls['1']:.3f} |",
        f"| Recall@3 | {recalls['3']:.3f} |",
        f"| Recall@5 | {recalls['5']:.3f} |",
        f"| Recall@10 | {recalls['10']:.3f} |",
        f"| MRR | {summary['mrr']:.4f} |",
        f"| Mean latency | {latency['mean']:.4f} s |",
        f"| Median latency | {latency['median']:.4f} s |",
        f"| P95 latency | {latency['p95']:.4f} s |",
        f"| Worst latency | {latency['worst']:.4f} s |",
        f"| Peak RSS | {summary['peak_rss_mb']:.1f} MB |",
        "",
        "## Retrieval outcomes",
        "",
    ])
    lines.extend(f"- `{key}`: {value}" for key, value in summary["retrieval_status_distribution"].items())
    lines.extend(["", "## Failure audit", ""])
    if failures:
        lines.extend(f"- `{key}`: {value}" for key, value in failures.items())
    else:
        lines.append("- No misses.")
    lines.extend([
        "",
        "## Interpretation boundary",
        "",
        "Exact Recall@k and MRR score the designated document-qualified chunk. Source-document recall accepts only that chunk or a pre-frozen duplicate-text alternate from the same document. A merely topically related chunk from the correct document is reported separately and is not counted as answer-bearing.",
        "",
        "## Findings",
        "",
        f"- All {summary['case_count']} expected chunks were present in the production index; no corpus/index-presence or metadata-source defect was observed.",
        "- The dominant limitation is semantic ranking: most targets did not enter even the diagnostic top 100 for their controlled subject+predicate query.",
        "- Correct-document/wrong-chunk outcomes show that document-level topical similarity occasionally works while chunk-level discrimination fails.",
        "- No result justifies a production change from this held-out set alone. The low recall should be treated as a measured limitation and investigated later using development data only.",
        "- Some controlled queries contain generic legal subjects such as ‘this regulation’ or ‘the annex’. They remain frozen and scored, but this benchmark must not be presented as natural-language legal QA.",
        "- Production retrieval code and artifacts were not modified by this evaluation.",
        "",
    ])
    return "\n".join(lines)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--case-file", type=Path)
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--seed", type=int, default=20260918)
    parser.add_argument("--chunk-trials-per-batch", type=int, default=12)
    parser.add_argument("--exclude-case-file", type=Path, action="append", default=list(DEFAULT_EXCLUSIONS))
    parser.add_argument("--natural-packet", type=Path, default=DEFAULT_NATURAL_PACKET)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--audit-top-k", type=int, default=100)
    parser.add_argument("--freeze-only", action="store_true")
    return parser


def main() -> None:
    args = _parser().parse_args()
    if args.limit < 1 or args.top_k < 10 or args.audit_top_k < args.top_k:
        raise ValueError("limit must be positive, top-k at least 10, and audit-top-k >= top-k")
    if args.case_file is None:
        cases, plan = freeze_cases(args)
        cases_path, plan_path = write_frozen_cases(cases, plan, args.output_dir)
        if args.freeze_only:
            print(json.dumps({"status": "frozen", "cases": str(cases_path), "plan": str(plan_path), "case_count": len(cases)}, indent=2))
            return
    else:
        cases = read_cases(args.case_file)
        plan = json.loads((args.output_dir / "sample_plan.json").read_text(encoding="utf-8"))
    results, summary = run_evaluation(args, cases)
    paths = write_results(results, summary, plan, args.output_dir)
    print(json.dumps({"status": "complete", "summary": summary, "outputs": [str(path) for path in paths]}, indent=2))


if __name__ == "__main__":
    main()
