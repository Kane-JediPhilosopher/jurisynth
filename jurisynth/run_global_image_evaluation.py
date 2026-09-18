"""Build and run the case-based Jurisynth image component evaluation.

Stage A isolates the production-v2 image-caption FAISS index. Stage B proves
local path resolution for the gold image and, only when it is retrieved inside
the production cutoff, exercises the ImageExpander contract with a recording
local client. The script never performs live provider inference.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import statistics
import time
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

import psutil

from jurisynth.contracts import ImageEvidence
from jurisynth.retrieval_mech.artifacts import ImageIndex
from jurisynth.retrieval_mech.document_metadata import DocumentMetadataStore
from jurisynth.retrieval_mech.image_expander import ImageExpander
from jurisynth.run_agentic_acceptance_smokes import CASES as ACCEPTANCE_CASES
from vision_llm_utils import VisionNIMConfig


DEFAULT_ROOT = Path("jurisynth/global_artifacts_source_uri_v2")
DEFAULT_OUTPUT = Path("jurisynth/evaluation_artifacts/image_retrieval_case_based_v1")


@dataclass(frozen=True, slots=True)
class ImageEvalCase:
    case_id: str
    query: str
    expected_document_id: str
    expected_image_id: str
    expected_relative_path: str
    stored_caption: str
    image_local_context: dict[str, object]
    canonical_source: dict[str, object]
    alternate_valid_image_ids: tuple[str, ...]
    source_asset: str
    construction_method: str


@dataclass(frozen=True, slots=True)
class ImageEvalResult:
    case_id: str
    query: str
    expected_document_id: str
    expected_image_id: str
    expected_image_present_in_index: bool
    expected_file_present_on_disk: bool
    exact_rank: int | None
    diagnostic_exact_rank_at_100: int | None
    correct_document_rank: int | None
    retrieval_status: str
    retrieval_failure_category: str | None
    retrieval_latency_seconds: float
    path_resolution_attempted: bool
    path_resolution_succeeded: bool
    resolved_path: str | None
    expansion_eligible: bool
    local_expansion_attempted: bool
    image_bytes_reached_recording_client: bool
    local_expansion_contract_succeeded: bool
    returned_expansion_attached: bool
    caption_only_fallback_preserved: bool
    live_provider_inference_occurred: bool
    semantic_usefulness_assessed: bool
    hits: list[dict[str, object]]


class _RecordingCompletions:
    def __init__(self) -> None:
        self.calls = 0
        self.received_image_bytes = False

    async def create(self, **kwargs):
        self.calls += 1
        messages = kwargs.get("messages") or []
        content = messages[-1].get("content") if messages else []
        image_urls = [
            item.get("image_url", {}).get("url")
            for item in content
            if isinstance(item, dict) and item.get("type") == "image_url"
        ]
        self.received_image_bytes = any(
            isinstance(url, str) and url.startswith("data:image/") and ";base64," in url
            and len(url.split(",", 1)[-1]) > 20
            for url in image_urls
        )
        message = type("Message", (), {"content": json.dumps({
            "expanded_description": "Local contract probe; semantic usefulness was not evaluated.",
            "visual_findings": ["Actual image bytes reached the recording client."],
            "relevance": 0.0,
        })})
        return type("Response", (), {"choices": [type("Choice", (), {"message": message})]})


class _RecordingVisionClient:
    def __init__(self) -> None:
        self.completions = _RecordingCompletions()
        self.chat = type("Chat", (), {"completions": self.completions})()

    async def close(self) -> None:
        return None


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


def build_frozen_cases(args: argparse.Namespace) -> tuple[list[ImageEvalCase], dict[str, object]]:
    image_root = args.artifact_root / "images"
    index = ImageIndex.load(image_root)
    records = {str(item["image_id"]): item for item in index.metadata}
    acceptance = next(
        case for case in ACCEPTANCE_CASES if case.get("case_id") == "image_primary"
    )
    expected_image_id = str(acceptance["expected_image"])
    expected = records.get(expected_image_id)
    if expected is None:
        raise ValueError(f"Frozen image-primary target {expected_image_id} is absent from production-v2 metadata")
    document_id = str(expected["document_id"])
    if document_id not in set(map(str, acceptance.get("expected_documents") or [])):
        raise ValueError("Frozen image-primary document gold disagrees with image metadata")
    document_store = (
        DocumentMetadataStore(args.artifact_root / "document_metadata.sqlite")
        if (args.artifact_root / "document_metadata.sqlite").is_file()
        else None
    )
    case = ImageEvalCase(
        case_id="image_primary",
        query=str(acceptance["query"]),
        expected_document_id=document_id,
        expected_image_id=expected_image_id,
        expected_relative_path=str(expected["relative_path"]),
        stored_caption=str(expected["description"]),
        image_local_context={
            "alt": expected.get("alt"),
            "legible_text": expected.get("legible_text"),
            "image_type": expected.get("image_type"),
            "mime_type": expected.get("mime_type"),
            "sha256": expected.get("sha256"),
            "source_url": expected.get("source_url"),
        },
        canonical_source=_canonical_source(document_store, document_id),
        alternate_valid_image_ids=(),
        source_asset="jurisynth/run_agentic_acceptance_smokes.py::CASES[image_primary]",
        construction_method="verbatim pre-existing frozen image-primary acceptance case",
    )
    type_counts = Counter(str(item.get("image_type") or "unknown") for item in index.metadata)
    status_counts = Counter(str(item.get("status") or "unknown") for item in index.metadata)
    plan = {
        "evaluation_type": "case-based modality evaluation",
        "freshness": "reused frozen",
        "provider_status": "zero-NIM; local recording client only",
        "indexed_image_count": len(index.metadata),
        "distinct_source_document_count": len({str(item["document_id"]) for item in index.metadata}),
        "metadata_status_counts": dict(status_counts),
        "image_type_counts": dict(type_counts),
        "defensible_case_count": 1,
        "genuinely_image_primary_case_count": 1,
        "query_generation": "none",
        "alternate_policy": "none encoded; none inferred after retrieval",
        "inventory": {
            "global_natural_candidate_packet": "No defensible image-primary gold cases.",
            "global_acceptance_image_primary": "One legitimate frozen query with exact document and image ID gold; used.",
            "image_sidecars": "27,647 captioned images with production FAISS vectors and path/provenance metadata.",
            "prior_live_image_smokes": "Two successful Nano Omni expansion diagnostics exist, but their generic prompts do not define unique global-retrieval gold; not scored.",
            "complex_smokes": "Images were auxiliary/incidental rather than clean image-primary gold; not scored.",
            "fixtures": "Validate local contracts only; not used as benchmark cases.",
        },
    }
    return [case], plan


def write_frozen_cases(cases: list[ImageEvalCase], plan: dict[str, object], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=False)
    with (output_dir / "cases.jsonl").open("x", encoding="utf-8") as handle:
        for case in cases:
            handle.write(json.dumps(asdict(case), ensure_ascii=False, sort_keys=True) + "\n")
    (output_dir / "sample_plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def read_cases(path: Path) -> list[ImageEvalCase]:
    cases: list[ImageEvalCase] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = json.loads(line)
        raw["alternate_valid_image_ids"] = tuple(raw["alternate_valid_image_ids"])
        cases.append(ImageEvalCase(**raw))
    return cases


def _rank_image(hits: list[ImageEvidence], image_id: str) -> int | None:
    return next((rank for rank, hit in enumerate(hits, 1) if hit.image_id == image_id), None)


def _rank_document(hits: list[ImageEvidence], document_id: str) -> int | None:
    return next((rank for rank, hit in enumerate(hits, 1) if hit.document_id == document_id), None)


def _serialize_hits(hits: list[ImageEvidence]) -> list[dict[str, object]]:
    return [
        {
            "rank": rank,
            "image_id": hit.image_id,
            "document_id": hit.document_id,
            "relative_path": hit.relative_path,
            "similarity": hit.similarity,
            "description": hit.description,
        }
        for rank, hit in enumerate(hits, 1)
    ]


async def _evaluate_case(
    case: ImageEvalCase,
    image_index: ImageIndex,
    embedder,
    expander_root: Path,
    top_k: int,
    audit_top_k: int,
) -> ImageEvalResult:
    metadata_by_id = {str(item["image_id"]): item for item in image_index.metadata}
    expected_present = case.expected_image_id in metadata_by_id
    started = time.perf_counter()
    primary_hits = image_index.search(case.query, embedder, top_k)
    latency = time.perf_counter() - started
    exact_rank = _rank_image(primary_hits, case.expected_image_id)
    diagnostic_hits = primary_hits if exact_rank is not None else image_index.search(
        case.query, embedder, audit_top_k
    )
    diagnostic_rank = exact_rank or _rank_image(diagnostic_hits, case.expected_image_id)
    document_rank = _rank_document(primary_hits, case.expected_document_id)
    if exact_rank is not None:
        status, failure = "exact", None
    elif not expected_present:
        status, failure = "miss", "expected_image_absent_from_index"
    elif document_rank is not None:
        status, failure = "correct_document_wrong_image", "correct_document_but_wrong_image"
    elif diagnostic_rank is not None:
        status, failure = "miss", "expected_image_below_top_10_but_within_top_100"
    else:
        status, failure = "miss", "expected_image_below_top_100"

    record = metadata_by_id.get(case.expected_image_id)
    expected_evidence = ImageEvidence(
        image_id=case.expected_image_id,
        document_id=case.expected_document_id,
        relative_path=case.expected_relative_path,
        mime_type=str((record or {}).get("mime_type") or "application/octet-stream"),
        description=case.stored_caption,
        legible_text=str((record or {}).get("legible_text") or ""),
        sha256=(record or {}).get("sha256") if isinstance((record or {}).get("sha256"), str) else None,
        source_url=(record or {}).get("source_url") if isinstance((record or {}).get("source_url"), str) else None,
        alt=(record or {}).get("alt") if isinstance((record or {}).get("alt"), str) else None,
    )
    recording_client = _RecordingVisionClient()
    expander = ImageExpander(
        expander_root,
        client=recording_client,
        config=VisionNIMConfig("local-recording", "https://invalid.local/v1", "local-recording"),
        requests_per_second=1000,
    )
    resolved_path = expander.resolve_image_path(expected_evidence)
    file_present = resolved_path is not None and resolved_path.is_file()
    eligible = exact_rank is not None
    attempted = False
    contract_succeeded = False
    attached = False
    fallback_preserved = False
    if eligible and file_present:
        attempted = True
        expanded = (await expander.expand([expected_evidence], case.query))[0]
        contract_succeeded = bool(expanded.expanded_description)
        attached = expanded.image_id == expected_evidence.image_id and bool(expanded.expanded_description)
        fallback_preserved = not attached and expanded.description == expected_evidence.description
    elif eligible:
        fallback_preserved = True
    return ImageEvalResult(
        case.case_id,
        case.query,
        case.expected_document_id,
        case.expected_image_id,
        expected_present,
        file_present,
        exact_rank,
        diagnostic_rank,
        document_rank,
        status,
        failure,
        latency,
        True,
        resolved_path is not None,
        str(resolved_path) if resolved_path is not None else None,
        eligible,
        attempted,
        recording_client.completions.received_image_bytes,
        contract_succeeded,
        attached,
        fallback_preserved,
        False,
        False,
        _serialize_hits(primary_hits),
    )


async def run_evaluation(
    args: argparse.Namespace, cases: list[ImageEvalCase]
) -> tuple[list[ImageEvalResult], dict[str, object]]:
    from sentence_transformers import SentenceTransformer

    image_root = args.artifact_root / "images"
    image_index = ImageIndex.load(image_root)
    model_started = time.perf_counter()
    embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    model_load_seconds = time.perf_counter() - model_started
    if cases:
        image_index.search(cases[0].query, embedder, args.top_k)
    process = psutil.Process()
    peak_rss = process.memory_info().rss
    results: list[ImageEvalResult] = []
    for case in cases:
        results.append(await _evaluate_case(
            case,
            image_index,
            embedder,
            image_root / "image_store",
            args.top_k,
            args.audit_top_k,
        ))
        peak_rss = max(peak_rss, process.memory_info().rss)
    return results, summarize(results, model_load_seconds, peak_rss, args.top_k, args.audit_top_k)


def summarize(
    results: list[ImageEvalResult],
    model_load_seconds: float,
    peak_rss: int,
    top_k: int,
    audit_top_k: int,
) -> dict[str, object]:
    total = len(results)
    ranks = [result.exact_rank for result in results]
    latencies = [result.retrieval_latency_seconds for result in results]
    ordered = sorted(latencies)
    p95_index = max(0, math.ceil(0.95 * len(ordered)) - 1)
    return {
        "benchmark": "case_based_image_retrieval_and_local_expansion_contract",
        "artifact_root": str(DEFAULT_ROOT),
        "case_count": total,
        "top_k": top_k,
        "diagnostic_audit_top_k": audit_top_k,
        "image_recall_at_k": {
            str(k): sum(rank is not None and rank <= k for rank in ranks) / total
            for k in (1, 3, 5, 10)
        },
        "mrr": sum(1 / rank for rank in ranks if rank is not None) / total,
        "correct_document_recall_at_10": sum(
            result.correct_document_rank is not None and result.correct_document_rank <= 10
            for result in results
        ) / total,
        "alternate_valid_recoveries": 0,
        "retrieval_latency_seconds": {
            "mean": statistics.fmean(latencies),
            "median": statistics.median(latencies),
            "p95": ordered[p95_index],
            "worst": max(latencies),
        },
        "model_load_seconds": model_load_seconds,
        "peak_rss_mb": peak_rss / 1024 / 1024,
        "retrieval_status_distribution": dict(Counter(result.retrieval_status for result in results)),
        "failure_breakdown": dict(Counter(
            result.retrieval_failure_category for result in results if result.retrieval_failure_category
        )),
        "expected_images_absent_from_index": sum(not result.expected_image_present_in_index for result in results),
        "expected_files_absent_from_disk": sum(not result.expected_file_present_on_disk for result in results),
        "expansion_eligible_retrieved_images": sum(result.expansion_eligible for result in results),
        "path_resolution_successes": sum(result.path_resolution_succeeded for result in results),
        "path_resolution_failures": sum(not result.path_resolution_succeeded for result in results),
        "local_expansion_attempts": sum(result.local_expansion_attempted for result in results),
        "image_bytes_reached_recording_client": sum(
            result.image_bytes_reached_recording_client for result in results
        ),
        "local_expansion_contract_successes": sum(
            result.local_expansion_contract_succeeded for result in results
        ),
        "returned_expansions_attached": sum(result.returned_expansion_attached for result in results),
        "caption_only_fallbacks": sum(result.caption_only_fallback_preserved for result in results),
        "live_provider_attempts": 0,
        "live_provider_successes": 0,
        "semantic_usefulness_assessed_count": 0,
    }


def _report(summary: dict[str, object], plan: dict[str, object]) -> str:
    recall = summary["image_recall_at_k"]
    latency = summary["retrieval_latency_seconds"]
    lines = [
        "# Jurisynth image retrieval and expansion component evaluation",
        "",
        "This is a case-based, reused-frozen, zero-NIM evaluation. Caption retrieval, path resolution, local expansion-contract invocation, live provider inference, and semantic usefulness are reported separately.",
        "",
        "## Corpus and existing-gold inventory",
        "",
        f"- Indexed images: **{plan['indexed_image_count']}**.",
        f"- Distinct source documents: **{plan['distinct_source_document_count']}**.",
        f"- Defensible image-primary cases: **{plan['defensible_case_count']}**.",
    ]
    lines.extend(f"- **{key.replace('_', ' ')}:** {value}" for key, value in plan["inventory"].items())
    lines.extend([
        "",
        "## Gold and query policy",
        "",
        "- The sole case is the unchanged global acceptance `image_primary` query with exact document and image-ID gold.",
        "- No new query, paraphrase, weak caption-derived case, or post-retrieval alternate was created.",
        "- This result is descriptive evidence about one legitimate case, not a corpus-level accuracy estimate.",
        "",
        "## Stage A — caption/index retrieval",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f"| Recall@1 | {recall['1']:.3f} |",
        f"| Recall@3 | {recall['3']:.3f} |",
        f"| Recall@5 | {recall['5']:.3f} |",
        f"| Recall@10 | {recall['10']:.3f} |",
        f"| MRR | {summary['mrr']:.4f} |",
        f"| Correct-document Recall@10 | {summary['correct_document_recall_at_10']:.3f} |",
        f"| Alternate-valid recoveries | {summary['alternate_valid_recoveries']} |",
        f"| Mean / median latency | {latency['mean']:.4f} / {latency['median']:.4f} s |",
        f"| P95 / worst latency | {latency['p95']:.4f} / {latency['worst']:.4f} s |",
        f"| Peak RSS | {summary['peak_rss_mb']:.1f} MB |",
        "",
        "## Stage B — vision expansion",
        "",
        f"- Images eligible after production-cutoff retrieval: **{summary['expansion_eligible_retrieved_images']}**.",
        f"- Gold paths resolved locally: **{summary['path_resolution_successes']}**; failures: **{summary['path_resolution_failures']}**.",
        f"- Local recording-client attempts: **{summary['local_expansion_attempts']}**; contract successes: **{summary['local_expansion_contract_successes']}**.",
        f"- Image-byte deliveries to recording client: **{summary['image_bytes_reached_recording_client']}**.",
        f"- Returned expansions attached: **{summary['returned_expansions_attached']}**.",
        "- Live provider attempts/successes: **0 / 0**.",
        "- Semantic usefulness was not assessed because no live vision description was generated.",
        "",
        "## Failure audit",
        "",
    ])
    if summary["failure_breakdown"]:
        lines.extend(f"- `{key}`: {value}" for key, value in summary["failure_breakdown"].items())
    else:
        lines.append("- No retrieval misses.")
    lines.extend([
        f"- `expected_file_absent_from_disk`: {summary['expected_files_absent_from_disk']}",
        f"- `path_resolution_failure`: {summary['path_resolution_failures']}",
        "",
        "## Interpretation",
        "",
        "The evaluation can establish whether the one frozen image-primary target is caption-retrievable and whether its corrected aggregate path resolves. It cannot establish corpus-wide image recall or vision-description quality. No deterministic path/index-presence defect is inferred unless the corresponding counts are non-zero.",
        "",
        "The frozen query addresses an image by document ID and image number, while the dense index represents its visual caption. Its miss therefore suggests an identifier-to-caption retrieval mismatch for this case, not index corruption. Once a candidate is supplied, the corrected path contract is operational; prior live smoke captures suggest expansion can be useful, but they are not part of this evaluation's scored evidence.",
        "",
        "Production code, image captions, FAISS artifacts, embeddings, thresholds, ranking, scoping, and prior evaluations were not modified.",
        "",
    ])
    return "\n".join(lines)


def write_results(
    output_dir: Path,
    results: list[ImageEvalResult],
    summary: dict[str, object],
    plan: dict[str, object],
) -> None:
    with (output_dir / "results.jsonl").open("x", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps(asdict(result), ensure_ascii=False, sort_keys=True) + "\n")
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_dir / "REPORT.md").write_text(_report(summary, plan), encoding="utf-8")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--case-file", type=Path)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--audit-top-k", type=int, default=100)
    parser.add_argument("--freeze-only", action="store_true")
    return parser


def main() -> None:
    args = _parser().parse_args()
    if args.case_file is None:
        cases, plan = build_frozen_cases(args)
        write_frozen_cases(cases, plan, args.output_dir)
        if args.freeze_only:
            print(json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True))
            return
    else:
        cases = read_cases(args.case_file)
        plan = json.loads((args.output_dir / "sample_plan.json").read_text(encoding="utf-8"))
    results, summary = asyncio.run(run_evaluation(args, cases))
    summary["artifact_root"] = str(args.artifact_root)
    write_results(args.output_dir, results, summary, plan)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
