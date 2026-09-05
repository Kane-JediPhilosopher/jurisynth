"""Pilot CLI for running the Jurisynth Reasoner against persisted batch artifacts."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from dataclasses import asdict
from pathlib import Path
from uuid import uuid4

from jurisynth.agentic_reasoner.llm import NIMConfig, OpenAICompatibleNIM
from jurisynth.agentic_reasoner.qcompiler_translator import QCompilerTranslator
from jurisynth.agentic_reasoner.dependency_planner import SemanticDependencyPlanner
from jurisynth.agentic_reasoner.intake import NIMConversationIntake
from jurisynth.agentic_reasoner.reasoner import AgenticReasoner
from jurisynth.agentic_reasoner.reporting import FinalReportSynthesizer
from jurisynth.agentic_reasoner.workflow import AgenticWorkflow, NIMTaskAnalyzer
from jurisynth.agentic_reasoner.llm import EvidenceGroundedLeafGenerator
from jurisynth.agentic_reasoner.contradiction import ContradictionDetector, ExplicitNegationScorer
from jurisynth.reasoning_log import ReasoningLog
from jurisynth.retrieval_mech.er_matcher import ERMatcher, PersistedERIndices
from jurisynth.retrieval_mech.mechanism import RetrievalMechanism
from jurisynth.retrieval_mech.pilot_artifacts import load_pilot_batch
from jurisynth.retrieval_mech.query_interpreter import NIMQueryInterpreter
from jurisynth.retrieval_mech.rdf_retriever import DirectRDFRetriever
from jurisynth.retrieval_mech.community_hierarchy import CommunityOrientationBuilder, load_hierarchy_artifact
from jurisynth.retrieval_mech.community_selector import CommunitySelector


def build_pilot_workflow(
    *,
    processed_batch_dir: str | Path,
    raw_batch_dir: str | Path,
    er_index_dir: str | Path,
    model: OpenAICompatibleNIM,
    embedder: object,
    reasoning_log: ReasoningLog | None = None,
) -> AgenticWorkflow:
    """Compose the V1 opaque Retrieval Mech and Agentic Reasoner for one pilot batch."""
    artifacts = load_pilot_batch(processed_batch_dir, raw_batch_dir=raw_batch_dir)
    indices = PersistedERIndices.load(er_index_dir)
    matcher = ERMatcher(indices, embedder)
    community_selector, orientation_builder = _load_community_guidance(er_index_dir, indices)
    structured_retriever = DirectRDFRetriever(
        artifacts.dataset,
        matcher,
        artifacts.resolve_chunk,
        interpreter=NIMQueryInterpreter(model),
        community_selector=community_selector,
    )
    retrieval_mech = RetrievalMechanism(
        embedder,
        chunk_indices=[artifacts.chunk_index],
        table_indices=[artifacts.table_index] if artifacts.table_index is not None else [],
        structured_retriever=structured_retriever,
        community_orientation_builder=orientation_builder,
    )
    reasoner = AgenticReasoner(
        retrieval_mech,
        EvidenceGroundedLeafGenerator(model),
        reasoning_log=reasoning_log,
    )
    return AgenticWorkflow(
        analyzer=NIMTaskAnalyzer(model),
        reasoner=reasoner,
        translator=QCompilerTranslator(model),
        dependency_planner=SemanticDependencyPlanner(model),
        synthesizer=FinalReportSynthesizer(model),
        contradiction_detector=ContradictionDetector(ExplicitNegationScorer()),
        intake=NIMConversationIntake(model),
        reasoning_log=reasoning_log,
    )


def _load_community_guidance(
    er_index_dir: str | Path,
    indices: PersistedERIndices,
) -> tuple[CommunitySelector, CommunityOrientationBuilder | None]:
    """Load optional deterministic graph guidance without making it a hard dependency."""
    hierarchy_path = Path(er_index_dir) / "community_hierarchy.json"
    if not hierarchy_path.is_file():
        return CommunitySelector(), None
    hierarchy = load_hierarchy_artifact(hierarchy_path)
    labels = {
        record.uri: record.label
        for record in (*indices.entity_records, *indices.relation_records)
    }
    return CommunitySelector(hierarchy=hierarchy), CommunityOrientationBuilder(hierarchy, labels)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Jurisynth batch_0009 pilot workflow.")
    parser.add_argument("query", help="One legal-information question to process.")
    parser.add_argument("--processed-batch", type=Path, default=Path("jurisynth/kg_construction_pipeline/output/batch_0009"))
    parser.add_argument("--raw-batch", type=Path, default=Path("eu_legislation/batch_0009"))
    parser.add_argument("--er-index", type=Path, default=Path("jurisynth/pilot_artifacts/batch_0009/er_index"))
    parser.add_argument("--reasoning-log", type=Path, default=Path("jurisynth/reasoning_logs"))
    parser.add_argument("--output", type=Path, help="Write the JSON result as UTF-8 instead of printing it.")
    parser.add_argument("--full-output", action="store_true", help="Include the full retrieval bundles; use only with --output.")
    return parser


async def _run(args: argparse.Namespace):
    try:
        from sentence_transformers import SentenceTransformer
    except ModuleNotFoundError as exc:
        raise RuntimeError("Install sentence-transformers in the documented Python 3.12 environment.") from exc
    model = OpenAICompatibleNIM(NIMConfig.from_environment())
    try:
        embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
        run_id = uuid4().hex
        reasoning_log = ReasoningLog(args.reasoning_log / f"{run_id}.jsonl", run_id)
        workflow = build_pilot_workflow(
            processed_batch_dir=args.processed_batch,
            raw_batch_dir=args.raw_batch,
            er_index_dir=args.er_index,
            model=model,
            embedder=embedder,
            reasoning_log=reasoning_log,
        )
        return await workflow.run(args.query)
    finally:
        await model.aclose()


def main() -> None:
    args = _parser().parse_args()
    result = asyncio.run(_run(args))
    if args.full_output and args.output is None:
        raise ValueError("--full-output requires --output to avoid dumping full retrieval bundles to the console.")
    payload = asdict(result) if args.full_output else _compact_result(result)
    rendered = json.dumps(payload, ensure_ascii=False, default=str, indent=2)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(json.dumps({"output": str(args.output), "full_output": args.full_output}, indent=2))
        return
    _configure_utf8_stdout()
    print(rendered)


def _compact_result(result: object) -> dict[str, object]:
    """Render a terminal-safe summary; full evidence is retained in the reasoning log."""
    analysis = result.analysis
    node_results: dict[str, object] = {}
    for query_id, node_result in result.node_results.items():
        entry: dict[str, object] = {"status": str(node_result.status), "error": node_result.error}
        if node_result.answer is not None:
            answer = node_result.answer
            bundle = answer.evidence_bundle
            entry["answer"] = {
                "status": answer.status,
                "answer_text": answer.answer_text,
                "claims": [asdict(claim) for claim in answer.claims],
                "evidence_summary": {
                    "retrieval_status": bundle.status,
                    "evidence_item_count": len(bundle.evidence_items),
                    "table_evidence_count": len(bundle.table_evidence),
                    "evidence_ids": [item.evidence_id for item in bundle.evidence_items[:12]],
                    "warnings": list(bundle.retrieval_metadata.get("warnings", [])),
                },
            }
        node_results[query_id] = entry
    return {
        "analysis": asdict(analysis),
        "leaves": [asdict(leaf) for leaf in result.leaves],
        "node_results": node_results,
        "report": asdict(result.report) if result.report is not None else None,
        "contradictions": [asdict(item) for item in getattr(result, "contradictions", ())],
        "presentation": getattr(result, "presentation", None),
        "clarification": getattr(result, "clarification", None),
    }


def _configure_utf8_stdout() -> None:
    """Avoid Windows code-page failures when a report contains corpus Unicode."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")


if __name__ == "__main__":
    main()
