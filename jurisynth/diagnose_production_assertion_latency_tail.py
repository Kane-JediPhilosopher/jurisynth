"""Read-only profile of the slowest fixed assertion benchmark cases."""

from __future__ import annotations

import argparse
import asyncio
import json
import time
from pathlib import Path

from jurisynth.contracts import RetrievalRequest
from jurisynth.main import _load_community_guidance
from jurisynth.retrieval_evaluation import RetrievalEvalCase
from jurisynth.retrieval_mech.config import GLOBAL_MAX_QUADS_PER_SEED
from jurisynth.retrieval_mech.er_matcher import ERMatcher, PersistedERIndices
from jurisynth.retrieval_mech.global_artifacts import load_global_artifacts
from jurisynth.retrieval_mech.mechanism import RetrievalMechanism
from jurisynth.retrieval_mech.rdf_retriever import DirectRDFRetriever
from jurisynth.run_global_assertion_evaluation import ControlledAssertionInterpreter


class ProfilingQuadStore:
    """Materialize bounded store iterators only to separate storage from consumers."""

    def __init__(self, inner):
        self.inner = inner
        self.calls: list[dict[str, object]] = []

    def reset(self) -> None:
        self.calls.clear()

    def matching_subject_predicate_quads(self, subject, predicate, *, limit):
        started = time.perf_counter()
        rows = list(self.inner.matching_subject_predicate_quads(subject, predicate, limit=limit))
        self.calls.append({
            "mode": "conjunctive", "subject": subject, "predicate": predicate,
            "limit": limit, "row_count": len(rows),
            "storage_seconds": round(time.perf_counter() - started, 6),
        })
        return iter(rows)

    def matching_quads(self, entities, relations, *, max_per_seed):
        started = time.perf_counter()
        rows = list(self.inner.matching_quads(entities, relations, max_per_seed=max_per_seed))
        self.calls.append({
            "mode": "independent_fallback", "entity_seed_count": len(entities),
            "relation_seed_count": len(relations), "limit": max_per_seed,
            "row_count": len(rows),
            "storage_seconds": round(time.perf_counter() - started, 6),
        })
        return iter(rows)

    def select_rows(self, query):
        return self.inner.select_rows(query)


def _read_cases(path: Path, selected_ids: set[str]) -> list[RetrievalEvalCase]:
    result = []
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = json.loads(line)
        if raw["case_id"] not in selected_ids:
            continue
        raw["expected_assertion"] = tuple(raw["expected_assertion"])
        raw["expected_chunk_ids"] = tuple(raw["expected_chunk_ids"])
        result.append(RetrievalEvalCase(**raw))
    return sorted(result, key=lambda item: item.case_id)


def _capped_cardinality(store, subject: str, predicate: str, cap: int = 1001) -> dict[str, object]:
    from pyoxigraph import NamedNode

    def count(pattern):
        started = time.perf_counter()
        value = 0
        for _quad in store.store.quads_for_pattern(*pattern):
            value += 1
            if value >= cap:
                break
        return {
            "observed": value,
            "censored_at_cap": value >= cap,
            "seconds": round(time.perf_counter() - started, 6),
        }

    subject_node, predicate_node = NamedNode(subject), NamedNode(predicate)
    return {
        "target_subject": count((subject_node, None, None, None)),
        "target_predicate": count((None, predicate_node, None, None)),
        "target_subject_predicate_pair": count((subject_node, predicate_node, None, None)),
    }


def _profile_record(bundle, wall_seconds: float, calls: list[dict[str, object]]) -> dict[str, object]:
    metadata = bundle.retrieval_metadata
    normal = metadata.get("timings_ms", {})
    broaden = metadata.get("broaden_candidates", {}).get("timings_ms", {})
    storage_seconds = sum(float(item["storage_seconds"]) for item in calls)
    direct_scan_ms = float(normal.get("direct_quad_scan_ms", 0.0)) + float(broaden.get("direct_quad_scan_ms", 0.0))
    return {
        "wall_seconds": round(wall_seconds, 6),
        "status": bundle.status,
        "evidence_count": len(bundle.evidence_items),
        "escalation_stages": metadata.get("escalation_stages", []),
        "normal_structured_timings_ms": normal,
        "broaden_structured_timings_ms": broaden,
        "modality_timings_ms": metadata.get("modality_retrieval", {}).get("timings_ms", {}),
        "store_calls": calls,
        "store_seconds": round(storage_seconds, 6),
        "direct_scan_ms": round(direct_scan_ms, 3),
        "candidate_materialization_resolution_ms": round(max(0.0, direct_scan_ms - storage_seconds * 1000), 3),
        "conjunctive_call_count": sum(item["mode"] == "conjunctive" for item in calls),
        "conjunctive_row_count": sum(int(item["row_count"]) for item in calls if item["mode"] == "conjunctive"),
        "fallback_call_count": sum(item["mode"] == "independent_fallback" for item in calls),
        "fallback_row_count": sum(int(item["row_count"]) for item in calls if item["mode"] == "independent_fallback"),
    }


async def run(args: argparse.Namespace) -> dict[str, object]:
    from sentence_transformers import SentenceTransformer

    selected_ids = set(args.case_ids.split(","))
    cases = _read_cases(args.cases, selected_ids)
    if {item.case_id for item in cases} != selected_ids:
        raise ValueError("One or more selected case IDs were not found.")
    artifacts = load_global_artifacts(args.artifact_root)
    indices = PersistedERIndices.load(args.community_dir / "er_index")
    embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    selector, orientation, descriptors = _load_community_guidance(
        args.community_dir / "er_index", indices,
        hierarchy_path=args.community_dir / "community_hierarchy.json",
        descriptor_path=args.community_dir / "community_descriptors.json",
    )
    profiled_store = ProfilingQuadStore(artifacts.dataset)
    mechanism = RetrievalMechanism(
        embedder, chunk_indices=[artifacts.chunk_index],
        table_indices=[artifacts.table_index] if artifacts.table_index is not None else [],
        structured_retriever=DirectRDFRetriever(
            profiled_store, ERMatcher(indices, embedder), artifacts.resolve_chunk,
            interpreter=ControlledAssertionInterpreter(), community_selector=selector,
            max_quads_per_seed=GLOBAL_MAX_QUADS_PER_SEED,
            path_expansion_limit=0,
            allow_three_hop_escalation=False,
        ),
        community_orientation_builder=orientation,
        community_descriptors=descriptors,
        community_summarizer=None,
        document_metadata=artifacts.document_metadata,
    )
    results = []
    for case in cases:
        runs = []
        for run_name in ("process_first", "immediate_repeat"):
            profiled_store.reset()
            started = time.perf_counter()
            bundle = await mechanism.retrieve_evidence(RetrievalRequest(case.case_id, case.query))
            record = _profile_record(bundle, time.perf_counter() - started, list(profiled_store.calls))
            record["run"] = run_name
            runs.append(record)
            print(json.dumps({"case_id": case.case_id, "run": run_name, "seconds": record["wall_seconds"]}), flush=True)
        subject, predicate, _obj = case.expected_assertion
        results.append({
            "case_id": case.case_id,
            "query": case.query,
            "target_cardinality": _capped_cardinality(artifacts.dataset, subject, predicate),
            "runs": runs,
        })
    return {
        "mode": "read_only_no_nim",
        "case_ids": sorted(selected_ids),
        "cardinality_cap": 1001,
        "cold_warm_caveat": "Process-first versus immediate repeat; operating-system cache may already be warm.",
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, default=Path("jurisynth/global_artifacts_source_uri_v2"))
    parser.add_argument("--community-dir", type=Path, default=Path("jurisynth/global_artifacts_source_uri_v2/community"))
    parser.add_argument("--cases", type=Path, default=Path("jurisynth/evaluation_artifacts/global_batch_stratified_subject-predicate_200_v2_cases.jsonl"))
    parser.add_argument("--case-ids", default="global_assertion_00033,global_assertion_00084,global_assertion_00096,global_assertion_00102,global_assertion_00124")
    parser.add_argument("--output", type=Path, default=Path("jurisynth/evaluation_artifacts/production_assertion_latency_tail.json"))
    args = parser.parse_args()
    result = asyncio.run(run(args))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "case_count": len(result["results"])}, indent=2))


if __name__ == "__main__":
    main()
