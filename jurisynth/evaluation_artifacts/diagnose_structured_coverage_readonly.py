"""Read-only development-set diagnosis for frozen structured retrieval."""

from __future__ import annotations

import json
import sqlite3
from collections import Counter
from pathlib import Path

from pyoxigraph import NamedNode, Store


ROOT = Path("jurisynth/evaluation_artifacts")
V2 = Path("jurisynth/global_artifacts_source_uri_v2")
CHUNK_PREFIX = "http://jurisynth/source/chunk/"


def rows(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def object_kind(value: str) -> str:
    return "uri" if value.startswith(("http://", "https://", "urn:")) else "literal_or_non_uri"


def fallback_label(uri: str) -> str:
    return uri.rstrip("/#").rsplit("/", 1)[-1].rsplit("#", 1)[-1].replace("_", " ")


def main() -> None:
    cases = {item["case_id"]: item for item in rows(ROOT / "global_batch_stratified_subject-predicate_200_production_conjunctive_cases.jsonl")}
    results = {item["case_id"]: item for item in rows(ROOT / "global_batch_stratified_subject-predicate_200_production_conjunctive_results.jsonl")}
    historical = json.loads((ROOT / "assertion_candidate_diagnosis_corrected_interpreter.json").read_text(encoding="utf-8"))
    prior = {item["case_id"]: item for item in historical["miss_traces"]}

    misses = [cases[case_id] for case_id, result in results.items() if not result["assertion_recalled"]]
    database = sqlite3.connect(V2 / "community" / "er_index" / "er_metadata.sqlite")
    entities = {uri for (uri,) in database.execute("SELECT uri FROM resources WHERE kind = 'entity'")}
    relations = {uri for (uri,) in database.execute("SELECT uri FROM resources WHERE kind = 'relation'")}
    store = Store.read_only(str(V2 / "oxigraph"))
    rdfs_label = NamedNode("http://www.w3.org/2000/01/rdf-schema#label")

    traces = []
    categories = Counter()
    er_categories = Counter()
    for case in misses:
        case_id = case["case_id"]
        subject, predicate, obj = case["expected_assertion"]
        result = results[case_id]
        old = prior.get(case_id, {})
        old_er = old.get("er", {})
        subject_indexed = subject in entities
        predicate_indexed = predicate in relations
        subject_labels = [str(q.object) for q in store.quads_for_pattern(NamedNode(subject), rdfs_label, None, None)]
        predicate_labels = [str(q.object) for q in store.quads_for_pattern(NamedNode(predicate), rdfs_label, None, None)]

        record = {
            "case_id": case_id,
            "expected_assertion": case["expected_assertion"],
            "expected_document_id": case.get("expected_document_id"),
            "expected_chunk_ids": case.get("expected_chunk_ids"),
            "object_kind": object_kind(obj),
            "expected_target_in_source_graph": old.get("kg", {}).get("exact_target_in_expected_source_graph"),
            "subject_indexed": subject_indexed,
            "predicate_indexed": predicate_indexed,
            "subject_rdfs_labels": subject_labels,
            "predicate_rdfs_labels": predicate_labels,
            "subject_fallback_label": fallback_label(subject),
            "predicate_fallback_label": fallback_label(predicate),
            "historical_target_seed_hit": old_er.get("target_seed_hit"),
            "final_subject_recalled": result["subject_entity_recalled"],
            "final_predicate_recalled": result["predicate_recalled"],
        }

        if not subject_indexed or not predicate_indexed:
            # This is construction-time loss: build_resource_records skips
            # every triple whose object is not a URI, so its subject/predicate
            # never enter the E-R records if no URI-object occurrence exists.
            if object_kind(obj) == "literal_or_non_uri":
                cause = "literal_object_exclusion_in_er_index_builder"
            else:
                cause = "uri_component_missing_from_er_metadata"
            record["earliest_stage"] = "representation_index_coverage"
            record["cause"] = cause
            er_categories[cause] += 1
            categories[record["earliest_stage"]] += 1
            traces.append(record)
            continue

        # Current production direct conjunction: first 50 quads for the exact
        # grounded subject/predicate pair.  This exactly mirrors the frozen
        # `matching_subject_predicate_quads(..., limit=max_quads_per_seed)`.
        matched = []
        for quad in store.quads_for_pattern(NamedNode(subject), NamedNode(predicate), None, None):
            matched.append((str(quad.subject), str(quad.predicate), str(quad.object), str(quad.graph_name)))
            if len(matched) >= 50:
                break
        expected_in_direct_window = any(row[:3] == (subject, predicate, obj) and row[3].startswith(CHUNK_PREFIX) for row in matched)
        record["direct_conjunction_window_count"] = len(matched)
        record["expected_in_direct_conjunction_window"] = expected_in_direct_window
        record["direct_window_reached_cap"] = len(matched) == 50

        if old_er.get("target_seed_hit") is False:
            record["earliest_stage"] = "query_time_er_grounding"
            record["cause"] = "target_uri_not_among_diagnostic_top_k_seeds"
        elif not expected_in_direct_window:
            record["earliest_stage"] = "candidate_generation"
            record["cause"] = (
                "bounded_subject_predicate_window_censorship"
                if len(matched) == 50 else "direct_conjunction_did_not_surface_expected_target"
            )
        else:
            record["earliest_stage"] = "post_conjunction_pipeline"
            record["cause"] = "materialization_deduplication_or_prebundle_pruning"
        categories[record["earliest_stage"]] += 1
        traces.append(record)

    out = {
        "scope": "read-only diagnosis on pre-existing 200-case development artifacts; not a held-out correction",
        "production_artifact_root": str(V2),
        "direct_conjunction_limit": 50,
        "development_exact_misses": len(misses),
        "earliest_stage_counts": dict(categories),
        "er_coverage_causes": dict(er_categories),
        "traces": traces,
    }
    (ROOT / "DEVELOPMENT_STRUCTURED_RETRIEVAL_COVERAGE_DIAGNOSIS.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: out[key] for key in ("development_exact_misses", "earliest_stage_counts", "er_coverage_causes")}, indent=2))


if __name__ == "__main__":
    main()
