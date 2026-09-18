"""Run a bounded, no-NIM global assertion-retrieval probe on Oxigraph.

This is a controlled retrieval integrity check, not natural legal-QA and not a
representative sample of every corpus assertion.  Seed graph URIs are drawn
from the independently sampled global source pool; Oxigraph performs the
bounded graph query without materialising the complete RDF corpus in Python.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import pickle
import random
import re
import time
import math
import statistics
from dataclasses import replace, asdict
from pathlib import Path

from jurisynth.main import _load_community_guidance
from jurisynth.retrieval_evaluation import (
    build_assertion_cases_from_quad_rows,
    RetrievalEvalCase,
    run_evaluation,
    write_cases_jsonl,
    write_results_jsonl,
    write_review_items_jsonl,
    select_review_items,
    write_summary_json,
)
from jurisynth.retrieval_mech.er_matcher import Concept, ERMatcher, PersistedERIndices
from jurisynth.retrieval_mech.config import GLOBAL_MAX_QUADS_PER_SEED
from jurisynth.retrieval_mech.global_artifacts import load_global_artifacts
from jurisynth.retrieval_mech.mechanism import RetrievalMechanism
from jurisynth.retrieval_mech.rdf_retriever import DirectRDFRetriever, LeafQueryInterpreter
from jurisynth.table_rdf_enricher import chunk_uri_candidates
import psutil


_CONTROLLED_ASSERTION_QUERY = re.compile(
    r"^According to the source, what is stated about '(.+?)' in relation to '(.+?)'\?$",
    re.IGNORECASE,
)


class ControlledAssertionInterpreter:
    """Deterministic parser for this benchmark's fixed synthetic template only."""

    async def interpret(self, request):
        match = _CONTROLLED_ASSERTION_QUERY.fullmatch(request.leaf_query.strip())
        if match is None:
            raise ValueError(
                "Controlled assertion query does not match the fixed subject/predicate template."
            )
        subject_label, predicate_label = match.groups()
        return [Concept("entity_1", subject_label)], [Concept("relation_1", predicate_label)]


class ExperimentalConjunctiveDirectRDFRetriever(DirectRDFRetriever):
    """Backward-compatible benchmark alias for the adopted production path."""


def _source_graph_uris(pool_path: Path, limit: int, artifacts) -> list[str]:
    pool = json.loads(pool_path.read_text(encoding="utf-8"))
    records = [item for values in pool["strata"].values() for item in values]
    seen: set[str] = set()
    result: list[str] = []
    for record in records:
        uri = next((
            str(candidate)
            for candidate in chunk_uri_candidates(record["document_id"], record["chunk_id"])
            if (source := artifacts.resolve_chunk(str(candidate))) is not None
            and (source.document_id, source.chunk_id) == (record["document_id"], record["chunk_id"])
        ), None)
        if uri is None:
            continue
        if uri not in seen:
            seen.add(uri)
            result.append(uri)
        if len(result) >= limit:
            break
    return result


def _batch_stratified_cases(args, artifacts):
    excluded = set()
    for path in args.exclude_case_file:
        for line in path.read_text(encoding="utf-8").splitlines():
            raw = json.loads(line)
            excluded.add(tuple(raw["expected_assertion"]))
    batches = json.loads(args.manifest.read_text(encoding="utf-8"))["batches"]
    ordered = sorted(batches, key=lambda batch: batch["batch_id"])
    rng = random.Random(args.seed)
    rng.shuffle(ordered)
    cases, selections, skipped = [], [], []
    selected_assertions: set[tuple[str, str, str]] = set()
    for batch in ordered:
        with Path(batch["chunk_metadata"]).open("rb") as handle:
            metadata = pickle.load(handle)
        records = sorted(metadata.values(), key=lambda item: (item["doc_id"], item["chunk_id"]))
        rng.shuffle(records)
        selected = False
        for record in records[:args.chunk_trials_per_batch]:
            graph_id = next((
                str(candidate)
                for candidate in chunk_uri_candidates(record["doc_id"], record["chunk_id"])
                if (source := artifacts.resolve_chunk(str(candidate))) is not None
                and (source.document_id, source.chunk_id) == (record["doc_id"], record["chunk_id"])
            ), None)
            if graph_id is None:
                skipped.append({"batch_id": batch["batch_id"], "reason": "unresolved_source"})
                continue
            if artifacts.chunk_lookup.has_ambiguous_provenance(graph_id):
                skipped.append({"batch_id": batch["batch_id"], "reason": "ambiguous_graph_uri", "graph_uri": graph_id})
                continue
            source = artifacts.resolve_chunk(graph_id)
            if source is None or (source.document_id, source.chunk_id) != (record["doc_id"], record["chunk_id"]):
                skipped.append({"batch_id": batch["batch_id"], "reason": "unresolved_source"})
                continue
            query = f"SELECT ?s ?p ?o ?g WHERE {{ VALUES ?g {{ <{graph_id}> }} GRAPH ?g {{ ?s ?p ?o }} }} ORDER BY ?s ?p ?o LIMIT 16"
            candidates = build_assertion_cases_from_quad_rows(
                artifacts.dataset.select_rows(query), artifacts.resolve_chunk,
                query_style=args.query_style.replace("-", "_"),
            )
            # A held-out case is an assertion identity, not merely one of its
            # graph-qualified provenance occurrences.  Retaining duplicate
            # SPO targets would overweight it in exact-recall and MRR.
            candidates = [
                candidate for candidate in candidates
                if candidate.expected_assertion not in excluded
                and candidate.expected_assertion not in selected_assertions
            ]
            if not candidates:
                continue
            case = replace(rng.choice(candidates), case_id=f"global_assertion_{len(cases) + 1:05d}")
            cases.append(case)
            selected_assertions.add(case.expected_assertion)
            selections.append({"case_id": case.case_id, "batch_id": batch["batch_id"], "document_id": source.document_id,
                               "chunk_id": source.chunk_id, "graph_uri": graph_id})
            selected = True
            break
        del metadata, records
        if not selected:
            skipped.append({"batch_id": batch["batch_id"], "reason": "no_eligible_semantic_graph_in_trial_budget"})
        if len(cases) >= args.limit:
            break
    if len(cases) < args.limit:
        raise RuntimeError(f"Only {len(cases)} unambiguous source cases found for requested {args.limit}.")
    return cases, {"seed": args.seed, "sampling": "one source graph and unique assertion per sampled batch; bounded 16-triple prefix",
                   "excluded_assertion_count": len(excluded),
                   "unique_normalized_spo_count": len(selected_assertions),
                   "selections": selections, "skipped": skipped}


async def run(args: argparse.Namespace) -> dict[str, object]:
    from sentence_transformers import SentenceTransformer

    artifacts = load_global_artifacts(args.artifact_root)
    if args.case_file is not None:
        cases = []
        for line in args.case_file.read_text(encoding="utf-8").splitlines():
            raw = json.loads(line)
            raw["expected_assertion"] = tuple(raw["expected_assertion"])
            raw["expected_chunk_ids"] = tuple(raw["expected_chunk_ids"])
            cases.append(RetrievalEvalCase(**raw))
        source_graph_count = len(cases)
        sample_plan = {"sampling": "fixed development case file", "source": str(args.case_file)}
    elif args.sample_mode == "batch-stratified":
        cases, sample_plan = _batch_stratified_cases(args, artifacts)
        source_graph_count = len(cases)
    else:
        graph_uris = _source_graph_uris(args.source_pool, args.source_graph_limit, artifacts)
        values = ", ".join(f"<{uri}>" for uri in graph_uris)
        rows = artifacts.dataset.select_rows(
            "SELECT ?s ?p ?o ?g WHERE { GRAPH ?g { ?s ?p ?o } "
            f"FILTER(?g IN ({values})) }} ORDER BY ?g ?s ?p ?o LIMIT {args.limit * 8}"
        )
        cases = build_assertion_cases_from_quad_rows(
            rows, artifacts.resolve_chunk, limit=args.limit, query_style=args.query_style.replace("-", "_"),
        )
        source_graph_count = len(graph_uris)
        sample_plan = {"sampling": "legacy source-pool prefix", "graph_uris": graph_uris}
    if not cases:
        raise RuntimeError("No semantic assertion cases resolved from the selected global source graphs.")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    scope = "batch_stratified" if args.sample_mode == "batch-stratified" else "source_sampled"
    prefix = args.run_tag or f"global_{scope}_{args.query_style}_{len(cases)}_v2"
    cases_path = args.output_dir / f"{prefix}_cases.jsonl"
    sample_plan_path = args.output_dir / f"{prefix}_sample_plan.json"
    # Freeze the selected cases before opening the model/index side of the
    # evaluation.  A subsequent --case-file run consumes this exact artifact;
    # it does not sample or replace individual cases.
    if args.case_file is None:
        write_cases_jsonl(cases, cases_path)
        sample_plan_path.write_text(json.dumps(sample_plan, indent=2) + "\n", encoding="utf-8")
    elif args.case_file.resolve() != cases_path.resolve():
        write_cases_jsonl(cases, cases_path)
        sample_plan_path.write_text(json.dumps(sample_plan, indent=2) + "\n", encoding="utf-8")
    if args.freeze_only:
        return {
            "status": "cases_frozen_no_evaluation",
            "case_count": len(cases),
            "cases_path": str(cases_path),
            "sample_plan_path": str(sample_plan_path),
            "sample_mode": args.sample_mode,
        }
    indices = PersistedERIndices.load(args.community_dir / "er_index")
    embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    selector, orientation, descriptors = _load_community_guidance(
        args.community_dir / "er_index", indices,
        hierarchy_path=args.community_dir / "community_hierarchy.json",
        descriptor_path=args.community_dir / "community_descriptors.json",
    )
    retriever_type = (
        ExperimentalConjunctiveDirectRDFRetriever
        if args.experimental_conjunctive_lookup
        else DirectRDFRetriever
    )
    mechanism = RetrievalMechanism(
        embedder, chunk_indices=[artifacts.chunk_index],
        table_indices=[artifacts.table_index] if artifacts.table_index is not None else [],
        structured_retriever=retriever_type(
            artifacts.dataset, ERMatcher(indices, embedder), artifacts.resolve_chunk,
            interpreter=(
                ControlledAssertionInterpreter()
                if args.controlled_template_interpreter
                else LeafQueryInterpreter()
            ),
            community_selector=selector, max_quads_per_seed=args.max_quads_per_seed,
            # This controlled metric scores direct assertion recovery.  Keeping
            # path expansion here would add unrelated work without changing
            # the expected direct-triple criterion.
            path_expansion_limit=20 if args.path_expansion else 0,
            allow_three_hop_escalation=args.path_expansion,
        ),
        community_orientation_builder=orientation,
        community_descriptors=descriptors,
        community_summarizer=None,
        document_metadata=artifacts.document_metadata,
    )
    results, timings = [], []
    peak_rss = psutil.Process().memory_info().rss
    with (args.output_dir / f"{prefix}_results.jsonl").open("w", encoding="utf-8") as handle:
        pool_handle = (args.output_dir / f"{prefix}_ranked_pool.jsonl").open("w", encoding="utf-8") if args.record_pool else None
        class RecordedMechanism:
            async def retrieve_evidence(self, request):
                bundle = await mechanism.retrieve_evidence(request)
                if pool_handle is not None:
                    ranked = sorted(bundle.evidence_items, key=lambda item: (
                        -len(item.matched_concept_ids), -(item.relevance_score if item.relevance_score is not None else -1),
                        -(item.structural_score if item.structural_score is not None else -1), item.evidence_id))
                    pool_handle.write(json.dumps({"case_id": request.query_id, "scoring_pool_count": len(ranked),
                        "assertions": [{"rank": rank, "assertion": asdict(item.assertion),
                            "source_chunks": [{"document_id": source.document_id, "chunk_id": source.chunk_id,
                                               "text_excerpt": source.text[:1200]} for source in item.source_chunks]}
                            for rank, item in enumerate(ranked, 1)],
                        "direct_chunk_matches": bundle.retrieval_metadata.get("direct_chunk_matches", [])}, ensure_ascii=False) + "\n")
                    pool_handle.flush()
                return bundle
        for case in cases:
            started = time.perf_counter()
            result = (await run_evaluation([case], RecordedMechanism(), max_concurrency=1))[0]
            timings.append(time.perf_counter() - started)
            results.append(result)
            handle.write(json.dumps(asdict(result), ensure_ascii=False) + "\n")
            handle.flush()
            peak_rss = max(peak_rss, psutil.Process().memory_info().rss,
                           getattr(indices.entity_index, "last_search_peak_rss_bytes", 0) or 0)
            print(json.dumps({"completed": len(results), "total": len(cases), "case_id": case.case_id,
                              "seconds": round(timings[-1], 3), "status": result.retrieval_status}), flush=True)
        if pool_handle is not None:
            pool_handle.close()
    write_review_items_jsonl(select_review_items(cases, results), args.output_dir / f"{prefix}_review_set.jsonl")
    summary = write_summary_json(results, args.output_dir / f"{prefix}_summary.json")
    recall_at = {
        f"assertion_recall_at_{cutoff}": sum(
            0 < (item.expected_assertion_rank or 0) <= cutoff for item in results
        ) / len(results)
        for cutoff in (1, 3, 5, 10, 20, 40)
    }
    summary.update({"case_kind": "controlled direct-assertion probe; not natural legal-QA", "source_graph_count": source_graph_count,
                    "provenance_identity": "document_id+chunk_id", "sample_mode": args.sample_mode,
                    "interpreter_mode": "controlled_subject_predicate_template" if args.controlled_template_interpreter else "raw_leaf_fallback",
                    "experimental_conjunctive_lookup": args.experimental_conjunctive_lookup,
                    "path_expansion": args.path_expansion, "max_quads_per_seed": args.max_quads_per_seed,
                    "mean_retrieval_seconds": round(statistics.mean(timings), 3),
                    "median_retrieval_seconds": round(statistics.median(timings), 3),
                    "p95_retrieval_seconds": round(sorted(timings)[math.ceil(0.95 * len(timings)) - 1], 3),
                    "worst_case_retrieval_seconds": round(max(timings), 3),
                    "observed_peak_rss_mb": round(peak_rss / 1024**2, 1)})
    summary.update(recall_at)
    (args.output_dir / f"{prefix}_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, default=Path("jurisynth/global_artifacts"))
    parser.add_argument("--community-dir", type=Path, default=Path("jurisynth/global_artifacts/community"))
    parser.add_argument("--source-pool", type=Path, default=Path("jurisynth/evaluation_artifacts/global_source_first_pool.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("jurisynth/evaluation_artifacts"))
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--source-graph-limit", type=int, default=24)
    parser.add_argument("--sample-mode", choices=("source-pool", "batch-stratified"), default="source-pool")
    parser.add_argument("--manifest", type=Path, default=Path("jurisynth/global_artifacts/manifest.json"))
    parser.add_argument("--seed", type=int, default=312)
    parser.add_argument("--chunk-trials-per-batch", type=int, default=8)
    parser.add_argument("--query-style", choices=("subject-predicate", "legacy-subject-object"), default="subject-predicate")
    parser.add_argument("--case-file", type=Path)
    parser.add_argument("--exclude-case-file", type=Path, action="append", default=[],
                        help="Immutable development/diagnostic case files whose exact assertions are excluded from sampling.")
    parser.add_argument("--run-tag", help="Unique artifact filename prefix for a fixed comparison.")
    parser.add_argument("--path-expansion", action="store_true")
    parser.add_argument("--max-quads-per-seed", type=int, default=GLOBAL_MAX_QUADS_PER_SEED)
    parser.add_argument("--record-pool", action="store_true")
    parser.add_argument(
        "--freeze-only",
        action="store_true",
        help="Persist a newly sampled immutable case file and stop before any retrieval result is produced.",
    )
    parser.add_argument(
        "--controlled-template-interpreter",
        action="store_true",
        help="Parse only the fixed benchmark's quoted subject and predicate fields; never used by production retrieval.",
    )
    parser.add_argument(
        "--experimental-conjunctive-lookup",
        action="store_true",
        help="Benchmark-only bounded subject+predicate lookup with the unchanged independent scan as fallback.",
    )
    args = parser.parse_args()
    if args.run_tag and (not args.run_tag.replace('_', '').replace('-', '').isalnum()):
        parser.error("--run-tag must contain only letters, digits, underscores or hyphens")
    if args.max_quads_per_seed < 1:
        parser.error("--max-quads-per-seed must be positive")
    if min(args.limit, args.source_graph_limit, args.chunk_trials_per_batch) < 1:
        parser.error("--limit and --source-graph-limit must be positive")
    print(json.dumps(asyncio.run(run(args)), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
