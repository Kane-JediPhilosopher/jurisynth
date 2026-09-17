"""Trace controlled assertion misses through the frozen candidate path.

This is read-only diagnostic instrumentation.  It deliberately reuses the
production interpreter, E-R matcher, bounded quad scan, and evidence selector
without changing their configuration.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sqlite3
import time
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from jurisynth.contracts import RetrievalRequest
from jurisynth.main import _load_community_guidance
from jurisynth.retrieval_evaluation import RetrievalEvalCase, RetrievalEvalResult
from jurisynth.retrieval_mech.er_matcher import ERMatcher, PersistedERIndices
from jurisynth.retrieval_mech.global_artifacts import load_global_artifacts
from jurisynth.retrieval_mech.rdf_retriever import DirectRDFRetriever, LeafQueryInterpreter
from jurisynth.run_global_assertion_evaluation import ControlledAssertionInterpreter
from jurisynth.table_rdf_enricher import chunk_uri_candidates


def _read_cases(path: Path) -> list[RetrievalEvalCase]:
    cases = []
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = json.loads(line)
        raw["expected_assertion"] = tuple(raw["expected_assertion"])
        raw["expected_chunk_ids"] = tuple(raw["expected_chunk_ids"])
        cases.append(RetrievalEvalCase(**raw))
    return cases


def _read_results(path: Path) -> list[RetrievalEvalResult]:
    return [RetrievalEvalResult(**json.loads(line)) for line in path.read_text(encoding="utf-8").splitlines()]


def _label(uri: str) -> str:
    value = uri.rsplit("/", 1)[-1].rsplit("#", 1)[-1]
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.casefold()).split())


def _target_in_source_graph(case: RetrievalEvalCase, artifacts) -> tuple[bool, list[str]]:
    graph_ids = []
    for chunk_id in case.expected_chunk_ids:
        for candidate in chunk_uri_candidates(case.expected_document_id or "", chunk_id):
            source = artifacts.resolve_chunk(str(candidate))
            if source is not None and (source.document_id, source.chunk_id) == (case.expected_document_id, chunk_id):
                graph_ids.append(str(candidate))
    if not graph_ids:
        return False, []
    values = " ".join(f"<{value}>" for value in sorted(set(graph_ids)))
    rows = artifacts.dataset.select_rows(
        f"SELECT ?s ?p ?o ?g WHERE {{ VALUES ?g {{ {values} }} GRAPH ?g {{ ?s ?p ?o }} }}"
    )
    return any(tuple(row[:3]) == case.expected_assertion for row in rows), sorted(set(graph_ids))


def _indexed_components(case: RetrievalEvalCase, sqlite_path: Path) -> dict[str, bool]:
    subject, predicate, obj = case.expected_assertion
    with sqlite3.connect(sqlite_path) as connection:
        entity_uris = {subject}
        if obj.startswith(("http://", "https://", "urn:")):
            entity_uris.add(obj)
        placeholders = ",".join("?" for _ in entity_uris)
        found_entities = {
            str(row[0]) for row in connection.execute(
                f"SELECT uri FROM resources WHERE kind='entity' AND uri IN ({placeholders})",
                tuple(sorted(entity_uris)),
            )
        }
        predicate_exists = connection.execute(
            "SELECT 1 FROM resources WHERE kind='relation' AND uri=? LIMIT 1", (predicate,)
        ).fetchone() is not None
    return {
        "subject": subject in found_entities,
        "predicate": predicate_exists,
        "object": obj in found_entities if obj.startswith(("http://", "https://", "urn:")) else True,
    }


async def _trace_case(case: RetrievalEvalCase, retriever: DirectRDFRetriever, artifacts, er_db: Path) -> dict[str, object]:
    request = RetrievalRequest(case.case_id, case.query)
    entity_concepts, relation_concepts = await retriever.interpreter.interpret(request)
    matches = retriever.matcher.match(
        entity_concepts, relation_concepts,
        entity_top_k=retriever.entity_match_top_k,
        relation_top_k=retriever.relation_match_top_k,
        minimum_similarity=retriever.minimum_match_similarity,
    )
    subject, predicate, obj = case.expected_assertion
    target_uris = {subject, predicate, obj}
    matched_uris = {item.uri for item in (*matches.entity_matches, *matches.relation_matches)}
    source_exists, graph_ids = _target_in_source_graph(case, artifacts)
    indexed = _indexed_components(case, er_db)

    evidence = {}
    for quad_subject, quad_predicate, quad_object, graph_id in retriever._matching_quads(
        {match.uri for match in matches.entity_matches},
        {match.uri for match in matches.relation_matches},
    ):
        source = retriever._resolve_chunk(graph_id)
        if source is not None:
            retriever._add_evidence(
                evidence, quad_subject, quad_predicate, quad_object,
                source, matches, "direct", 1.0,
            )

    target_item = evidence.get(case.expected_assertion)
    concept_count = len({
        match.concept_id for match in (*matches.entity_matches, *matches.relation_matches)
    })
    minimum_coverage = 2 if concept_count > 1 else 1
    coverage_filtered = [
        item for item in evidence.values()
        if len(item.matched_concept_ids) >= minimum_coverage or "path" in item.retrieval_origins
    ]
    ranked = sorted(
        coverage_filtered,
        key=lambda item: (
            -len(item.matched_concept_ids),
            -(item.relevance_score if item.relevance_score is not None else -1.0),
            -(item.structural_score if item.structural_score is not None else -1.0),
            item.evidence_id,
        ),
    )
    ranked_keys = [
        (item.assertion.subject, item.assertion.predicate, item.assertion.object)
        for item in ranked
    ]
    target_rank = ranked_keys.index(case.expected_assertion) + 1 if case.expected_assertion in ranked_keys else None
    selected = ranked[:retriever.max_evidence_items]
    selected_keys = {
        (item.assertion.subject, item.assertion.predicate, item.assertion.object)
        for item in selected
    }

    normalized_query = " ".join(re.sub(r"[^a-z0-9]+", " ", case.query.casefold()).split())
    subject_cue = _label(subject) in normalized_query
    predicate_cue = _label(predicate) in normalized_query
    if not source_exists:
        category = "representation_mismatch"
    elif not indexed["subject"] or not indexed["predicate"]:
        # Index representation is the earliest defect even when the other
        # indexed component happens to seed a later candidate scan.
        category = "subject_predicate_missing_from_er_index"
    elif not target_uris.intersection(matched_uris):
        category = "er_grounding_failure_despite_indexed_target"
    elif target_item is None:
        category = "graph_candidate_generation_miss"
    elif target_item not in coverage_filtered:
        category = "candidate_filtering_pruning_miss"
    elif case.expected_assertion not in selected_keys:
        category = "ranking_only_miss"
    else:
        category = "target_reached_selected_pool"

    return {
        "case_id": case.case_id,
        "query": case.query,
        "expected_assertion": list(case.expected_assertion),
        "expected_document_id": case.expected_document_id,
        "expected_chunk_ids": list(case.expected_chunk_ids),
        "classification": category,
        "kg": {
            "exact_target_in_expected_source_graph": source_exists,
            "source_graph_ids": graph_ids,
            "indexed_component_existence": indexed,
            "index_representation_limitation": not indexed["subject"] or not indexed["predicate"],
        },
        "query_interpreter": {
            "entity_concepts": [asdict(item) for item in entity_concepts],
            "relation_concepts": [asdict(item) for item in relation_concepts],
            "subject_cue_present": subject_cue,
            "predicate_cue_present": predicate_cue,
        },
        "er": {
            "target_seed_hit": bool(target_uris.intersection(matched_uris)),
            "target_seed_uris": sorted(target_uris.intersection(matched_uris)),
            "entity_matches": [asdict(item) for item in matches.entity_matches],
            "relation_matches": [asdict(item) for item in matches.relation_matches],
            "metadata": matches.metadata,
        },
        "candidate_path": {
            "raw_candidate_count": len(evidence),
            "target_generated": target_item is not None,
            "coverage_filtered_count": len(coverage_filtered),
            "target_survived_filter": target_item in coverage_filtered if target_item is not None else False,
            "target_rank": target_rank,
            "selected_count": len(selected),
            "target_selected": case.expected_assertion in selected_keys,
        },
    }


async def run(args: argparse.Namespace) -> dict[str, object]:
    from sentence_transformers import SentenceTransformer

    cases = _read_cases(args.cases)
    results = _read_results(args.results)
    by_result = {item.case_id: item for item in results}
    if args.miss_mode == "exact":
        selected_misses = [case for case in cases if not by_result[case.case_id].assertion_recalled]
    else:
        selected_misses = [
            case for case in cases
            if not by_result[case.case_id].assertion_recalled
            and not by_result[case.case_id].subject_entity_recalled
            and not by_result[case.case_id].predicate_recalled
            and not by_result[case.case_id].object_entity_recalled
        ]
    successes = [case for case in cases if by_result[case.case_id].assertion_recalled][:args.success_sample]
    if args.expected_misses is not None and len(selected_misses) != args.expected_misses:
        raise RuntimeError(
            f"Expected {args.expected_misses} misses, found {len(selected_misses)}."
        )

    artifacts = load_global_artifacts(args.artifact_root)
    indices = PersistedERIndices.load(args.community_dir / "er_index")
    embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    selector, _orientation, _descriptors = _load_community_guidance(
        args.community_dir / "er_index", indices,
        hierarchy_path=args.community_dir / "community_hierarchy.json",
        descriptor_path=args.community_dir / "community_descriptors.json",
    )
    retriever = DirectRDFRetriever(
        artifacts.dataset,
        ERMatcher(indices, embedder),
        artifacts.resolve_chunk,
        interpreter=(
            ControlledAssertionInterpreter()
            if args.interpreter == "controlled-template"
            else LeafQueryInterpreter()
        ),
        community_selector=selector,
        max_quads_per_seed=50,
        path_expansion_limit=0,
        allow_three_hop_escalation=False,
    )
    er_db = args.community_dir / "er_index" / "er_metadata.sqlite"
    started = time.perf_counter()
    miss_traces = []
    for index, case in enumerate(selected_misses, 1):
        miss_traces.append(await _trace_case(case, retriever, artifacts, er_db))
        print(json.dumps({"completed": index, "total": len(selected_misses), "case_id": case.case_id}), flush=True)
    success_traces = [await _trace_case(case, retriever, artifacts, er_db) for case in successes]
    counts = Counter(item["classification"] for item in miss_traces)
    return {
        "protocol": {
            "cases": str(args.cases),
            "results": str(args.results),
            "artifact_root": str(args.artifact_root),
            "interpreter": args.interpreter,
            "miss_mode": args.miss_mode,
            "entity_top_k": retriever.entity_match_top_k,
            "relation_top_k": retriever.relation_match_top_k,
            "max_quads_per_seed": retriever.max_quads_per_seed,
            "path_expansion_limit": retriever.path_expansion_limit,
            "max_evidence_items": retriever.max_evidence_items,
            "retrieval_policy_changed": False,
            "elapsed_seconds": round(time.perf_counter() - started, 3),
        },
        "miss_count": len(miss_traces),
        "category_counts": dict(counts),
        "category_percentages": {
            key: round(value / len(miss_traces) * 100, 3) for key, value in counts.items()
        },
        "miss_traces": miss_traces,
        "success_sample": success_traces,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, default=Path("jurisynth/global_artifacts_source_uri_v2"))
    parser.add_argument("--community-dir", type=Path, default=Path("jurisynth/global_artifacts_source_uri_v2/community"))
    parser.add_argument("--cases", type=Path, default=Path("jurisynth/evaluation_artifacts/global_batch_stratified_subject-predicate_200_v2_cases.jsonl"))
    parser.add_argument("--results", type=Path, default=Path("jurisynth/evaluation_artifacts/global_batch_stratified_subject-predicate_200_post_retrieval_fix_results.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("jurisynth/evaluation_artifacts/assertion_candidate_diagnosis_92.json"))
    parser.add_argument("--expected-misses", type=int)
    parser.add_argument("--miss-mode", choices=("complete", "exact"), default="complete")
    parser.add_argument("--interpreter", choices=("raw-leaf", "controlled-template"), default="raw-leaf")
    parser.add_argument("--success-sample", type=int, default=5)
    args = parser.parse_args()
    result = asyncio.run(run(args))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "category_counts": result["category_counts"]}, indent=2))


if __name__ == "__main__":
    main()
