"""Replay captured Jurisynth upstream outputs through downstream contracts.

No prompt or model call is made.  The harness reuses a previously persisted
QCompiler plan, interpretation concepts, leaf answers, and final report while
running the current production retrieval, scheduler, validation, contradiction,
and presentation code.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import time
from dataclasses import asdict
from pathlib import Path

from jurisynth.agentic_reasoner.contradiction import ContradictionDetector, ExplicitNegationScorer
from jurisynth.agentic_reasoner.models import Claim, LeafAnswer, LeafNode
from jurisynth.agentic_reasoner.qcompiler_translator import QCompilerCompilation
from jurisynth.agentic_reasoner.reasoner import AgenticReasoner
from jurisynth.agentic_reasoner.reporting import _parse_report, progressive_disclosure_payload
from jurisynth.agentic_reasoner.scheduler import execute_dependency_plan
from jurisynth.contracts import RetrievalRequest
from jurisynth.main import _load_community_guidance
from jurisynth.retrieval_mech.config import GLOBAL_MAX_QUADS_PER_SEED
from jurisynth.retrieval_mech.er_matcher import Concept, ERMatcher, PersistedERIndices
from jurisynth.retrieval_mech.global_artifacts import load_global_artifacts
from jurisynth.retrieval_mech.mechanism import RetrievalMechanism
from jurisynth.retrieval_mech.rdf_retriever import DirectRDFRetriever


class CapturedConceptInterpreter:
    """Return persisted, valid NIM concept output; never call a provider."""

    def __init__(self, entities: list[Concept], relations: list[Concept], traces: list[dict]) -> None:
        self.entities = entities
        self.relations = relations
        self.traces = traces

    async def interpret(self, request: RetrievalRequest):
        self.traces.append({
            "query_id": request.query_id,
            "leaf_query": request.leaf_query,
            "entity_concepts": [asdict(item) for item in self.entities],
            "relation_concepts": [asdict(item) for item in self.relations],
            "source": "captured structured_output_smoke_v4",
        })
        return self.entities, self.relations


class CapturedLeafGenerator:
    """Return captured leaf output verbatim, attaching the newly retrieved bundle."""

    def __init__(self, answers: dict[str, dict]) -> None:
        self.answers = answers

    async def __call__(self, node: LeafNode, _dependencies, bundle) -> LeafAnswer:
        captured = self.answers[node.query_id]
        return LeafAnswer(
            query_id=node.query_id,
            status=captured["status"],
            answer_text=captured["answer_text"],
            claims=[Claim(**claim) for claim in captured["claims"]],
            evidence_bundle=bundle,
            raw_output={"replayed_from": "global_complex_ai_medical_organized.json"},
        )


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _concepts(values: list[dict]) -> list[Concept]:
    return [Concept(str(item["concept_id"]), str(item["text"]), tuple(item.get("variants", []))) for item in values]


def _bundle_summary(bundle) -> dict:
    metadata = bundle.retrieval_metadata
    scope = metadata.get("instrument_scope", {})
    modality = metadata.get("modality_retrieval", {})
    return {
        "status": bundle.status,
        "assertion_evidence": len(bundle.evidence_items),
        "table_evidence": len(bundle.table_evidence),
        "image_evidence": len(bundle.image_evidence),
        "source_documents": sorted({chunk.document_id for item in bundle.evidence_items for chunk in item.source_chunks}),
        "instrument_scope_counts": scope.get("evidence_counts", {}),
        "covered_instrument_keys": scope.get("covered_target_keys", []),
        "missing_instrument_keys": scope.get("missing_target_keys", []),
        "community_orientation": metadata.get("community_orientation"),
        "lazy_community_summary": metadata.get("lazy_community_summary"),
        "structured_timings_ms": metadata.get("timings_ms", {}),
        "modality_timings_ms": modality.get("timings_ms", {}),
        "escalation_stages": metadata.get("escalation_stages", []),
    }


async def run(args: argparse.Namespace) -> dict:
    from sentence_transformers import SentenceTransformer

    captured = _load_json(args.captured_result)["result"]
    structured = _load_json(args.captured_ast)["cases"][0]
    captured_answers = {
        query_id: value["answer"]
        for query_id, value in captured["node_results"].items()
        if value.get("answer") is not None
    }
    # The captured global run's q001 -> q002/q004 -> q003 subgraph has a real
    # dependency chain and a parallel ready layer.  It keeps the replay bounded.
    selected_ids = ("q001", "q002", "q003", "q004")
    leaves = [
        LeafNode(
            item["query_id"], item["query"], tuple(item["dependency_ids"]),
            tuple(item.get("contextual_facts", [])), item.get("constraints", {}),
            tuple(item.get("optional_dependency_ids", [])),
        )
        for item in captured["leaves"] if item["query_id"] in selected_ids
    ]
    ast = captured["ast"]
    artifacts = load_global_artifacts(args.artifact_root)
    indices = PersistedERIndices.load(args.community_dir / "er_index")
    embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    selector, orientation, descriptors = _load_community_guidance(
        args.community_dir / "er_index", indices,
        hierarchy_path=args.community_dir / "community_hierarchy.json",
        descriptor_path=args.community_dir / "community_descriptors.json",
    )
    traces: list[dict] = []
    interpreter = CapturedConceptInterpreter(
        _concepts(structured["entities"]), _concepts(structured["relations"]), traces
    )
    # A lazy summary would be a new NIM call.  This replay preserves the
    # production hierarchy/orientation work and records whether a summary would
    # have been required, without inventing one.
    mechanism = RetrievalMechanism(
        embedder,
        chunk_indices=[artifacts.chunk_index],
        table_indices=[artifacts.table_index] if artifacts.table_index is not None else [],
        image_indices=[artifacts.image_index] if artifacts.image_index is not None else [],
        structured_retriever=DirectRDFRetriever(
            artifacts.dataset, ERMatcher(indices, embedder), artifacts.resolve_chunk,
            interpreter=interpreter, community_selector=selector,
            max_quads_per_seed=GLOBAL_MAX_QUADS_PER_SEED,
        ),
        community_orientation_builder=orientation,
        community_descriptors=descriptors,
        community_summarizer=None,
        document_metadata=artifacts.document_metadata,
    )
    bundle_records: dict[str, dict] = {}

    class RecordingMechanism:
        async def retrieve_evidence(self, request: RetrievalRequest):
            started = time.perf_counter()
            bundle = await mechanism.retrieve_evidence(request)
            bundle_records[request.query_id] = {
                "request": asdict(request),
                "wall_seconds": round(time.perf_counter() - started, 3),
                "summary": _bundle_summary(bundle),
                "bundle": asdict(bundle),
            }
            return bundle

    reasoner = AgenticReasoner(RecordingMechanism(), CapturedLeafGenerator(captured_answers))
    started = time.perf_counter()
    node_results = await reasoner.execute_leaves(leaves)
    wall_seconds = round(time.perf_counter() - started, 3)
    completed = [
        result.answer for leaf in leaves
        if (result := node_results[leaf.query_id]).answer is not None
    ]
    detector = ContradictionDetector(ExplicitNegationScorer())
    contradictions = await detector.detect(completed)
    captured_report = captured["report"]
    claim_ids = {claim.claim_id for answer in completed for claim in answer.claims if claim.claim_id}
    report_result: dict[str, object]
    try:
        report = _parse_report(json.dumps(captured_report), claim_ids, {item.contradiction_id for item in contradictions})
        presentation = progressive_disclosure_payload(report, completed)
        report_result = {"status": "passed", "report": asdict(report), "presentation": presentation}
    except Exception as exc:
        report_result = {"status": "failed", "error": repr(exc)}

    results = {
        query_id: {
            "status": str(result.status),
            "error": result.error,
            "claims": [asdict(claim) for claim in result.answer.claims] if result.answer else [],
            "claim_provenance_valid": (
                all(
                    ref in {item.evidence_id for item in result.answer.evidence_bundle.evidence_items}
                    for claim in result.answer.claims for ref in claim.evidence_refs
                ) if result.answer else False
            ),
        }
        for query_id, result in node_results.items()
    }
    return {
        "mode": "zero_nim_replay",
        "sources": {
            "captured_qcompiler_ast": str(args.captured_ast),
            "captured_leaf_answers_and_report": str(args.captured_result),
            "captured_interpretation": "structured_output_smoke_v4 case[0]",
        },
        "qcompiler_ast": ast,
        "leaves": [asdict(leaf) for leaf in leaves],
        "dependency_edges": [
            {"from": dependency, "to": leaf.query_id}
            for leaf in leaves for dependency in leaf.dependency_ids
        ],
        "interpreter_traces": traces,
        "retrieval": bundle_records,
        "node_results": results,
        "contradictions": [asdict(item) for item in contradictions],
        "final_synthesis": report_result,
        "total_wall_seconds": wall_seconds,
        "limitations": [
            "Leaf answers and final report are historical model outputs; none were regenerated.",
            "The current production EvidenceBundles are live local retrieval results, not historical paired bundles.",
            "Lazy community summarization is intentionally not replayed because no matching captured lazy-summary output is available; hierarchy orientation still runs.",
            "Image expansion is not exercised because no selected leaf requests visual material; it would otherwise require a vision-model call.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, default=Path("jurisynth/global_artifacts_source_uri_v2"))
    parser.add_argument("--community-dir", type=Path, default=Path("jurisynth/global_artifacts_source_uri_v2/community"))
    parser.add_argument("--captured-result", type=Path, default=Path("jurisynth/run_outputs/global_complex_ai_medical_organized.json"))
    parser.add_argument("--captured-ast", type=Path, default=Path("jurisynth/run_outputs/structured_output_smoke_v4.json"))
    parser.add_argument("--output", type=Path, default=Path("jurisynth/run_outputs/zero_nim_replay_20260917.json"))
    args = parser.parse_args()
    payload = asyncio.run(run(args))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, default=str, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "wall_seconds": payload["total_wall_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
