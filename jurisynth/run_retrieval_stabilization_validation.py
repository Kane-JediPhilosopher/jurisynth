"""Run the final local-only retrieval stabilization checks on global artifacts."""

from __future__ import annotations

import argparse
import asyncio
import json
import time
from collections import Counter
from dataclasses import asdict
from pathlib import Path

from jurisynth.contracts import RetrievalRequest
from jurisynth.main import _load_community_guidance
from jurisynth.retrieval_mech.config import GLOBAL_MAX_QUADS_PER_SEED
from jurisynth.retrieval_mech.er_matcher import Concept, ERMatcher, PersistedERIndices
from jurisynth.retrieval_mech.global_artifacts import load_global_artifacts
from jurisynth.retrieval_mech.mechanism import RetrievalMechanism
from jurisynth.retrieval_mech.rdf_retriever import DirectRDFRetriever


class CaseInterpreter:
    def __init__(self, concepts: dict[str, tuple[list[Concept], list[Concept]]]):
        self.concepts = concepts

    async def interpret(self, request: RetrievalRequest):
        return self.concepts[request.query_id]


def _concepts(values: list[dict[str, object]]) -> list[Concept]:
    return [
        Concept(str(item["concept_id"]), str(item["text"]), tuple(item.get("variants", [])))
        for item in values
    ]


def _cases(q003_capture: Path) -> tuple[list[RetrievalRequest], dict, dict]:
    capture = json.loads(q003_capture.read_text(encoding="utf-8-sig"))
    q003 = RetrievalRequest(**capture["request"])
    requests = [
        q003,
        RetrievalRequest(
            "single_instrument",
            "Under Regulation (EU) 2024/1689 (AI Act), what obligations apply to providers of high-risk AI systems?",
        ),
        RetrievalRequest(
            "cross_instrument",
            "How do provider obligations under Regulation (EU) 2024/1689 (AI Act) interact with manufacturer obligations under Regulation (EU) 2017/746 (IVDR) for an AI-enabled in vitro diagnostic device?",
        ),
        RetrievalRequest(
            "table_primary",
            "In L_2010041EN.01000801 table_10, how does the table distinguish Metier*Fleet segment (Cell), Metier, and Fleet segment across the displayed geographic aggregation levels?",
            constraints={"document_ids": ["L_2010041EN.01000801"]},
        ),
        RetrievalRequest(
            "non_table_control",
            "Under Regulation (EU) 2016/679 (GDPR), what does Article 13 require a controller to tell a data subject?",
        ),
    ]
    concepts = {
        q003.query_id: (_concepts(capture["entity_concepts"]), _concepts(capture["relation_concepts"])),
        "single_instrument": (
            [Concept("e1", "AI Act", ("Regulation (EU) 2024/1689",)), Concept("e2", "provider"), Concept("e3", "high-risk AI system")],
            [Concept("r1", "obligation", ("must",))],
        ),
        "cross_instrument": (
            [
                Concept("e1", "AI Act", ("Regulation (EU) 2024/1689",)),
                Concept("e2", "IVDR", ("Regulation (EU) 2017/746",)),
                Concept("e3", "provider"), Concept("e4", "manufacturer"),
                Concept("e5", "in vitro diagnostic medical device"),
            ],
            [Concept("r1", "obligation", ("must",)), Concept("r2", "place on the market", ("market",))],
        ),
        "table_primary": (
            [Concept("e1", "metier"), Concept("e2", "fleet segment"), Concept("e3", "geographic aggregation level")],
            [Concept("r1", "distinguish", ("map",))],
        ),
        "non_table_control": (
            [Concept("e1", "GDPR", ("Regulation (EU) 2016/679",)), Concept("e2", "controller"), Concept("e3", "data subject")],
            [Concept("r1", "provide information", ("tell", "inform"))],
        ),
    }
    expected = {
        q003.query_id: {"L_202401689EN"},
        "single_instrument": {"L_202401689EN"},
        "cross_instrument": {"L_202401689EN", "L_2017117EN.01017601"},
        "table_primary": {"L_2010041EN.01000801"},
        "non_table_control": {"L_2016119EN.01000101"},
    }
    return requests, concepts, expected


async def run(args: argparse.Namespace) -> dict[str, object]:
    from sentence_transformers import SentenceTransformer

    artifacts = load_global_artifacts(args.artifact_root)
    if artifacts.document_metadata is None:
        raise RuntimeError("The global document_metadata.sqlite sidecar is required.")
    indices = PersistedERIndices.load(args.community_dir / "er_index")
    embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    selector, orientation, descriptors = _load_community_guidance(
        args.community_dir / "er_index", indices,
        hierarchy_path=args.community_dir / "community_hierarchy.json",
        descriptor_path=args.community_dir / "community_descriptors.json",
    )
    requests, concepts, expected = _cases(args.q003_capture)
    mechanism = RetrievalMechanism(
        embedder,
        chunk_indices=[artifacts.chunk_index],
        table_indices=[artifacts.table_index] if artifacts.table_index is not None else [],
        image_indices=[artifacts.image_index] if artifacts.image_index is not None else [],
        structured_retriever=DirectRDFRetriever(
            artifacts.dataset,
            ERMatcher(indices, embedder),
            artifacts.resolve_chunk,
            interpreter=CaseInterpreter(concepts),
            community_selector=selector,
            max_quads_per_seed=GLOBAL_MAX_QUADS_PER_SEED,
        ),
        community_orientation_builder=orientation,
        community_descriptors=descriptors,
        community_summarizer=None,
        document_metadata=artifacts.document_metadata,
    )
    results = []
    for request in requests:
        started = time.perf_counter()
        bundle = await mechanism.retrieve_evidence(request)
        seconds = time.perf_counter() - started
        evidence_documents = {
            chunk.document_id for item in bundle.evidence_items for chunk in item.source_chunks
        }
        table_documents = {item.document_id for item in bundle.table_evidence}
        covered = expected[request.query_id].intersection(evidence_documents | table_documents)
        metadata = bundle.retrieval_metadata
        scope = metadata.get("instrument_scope", {})
        modality = metadata.get("modality_retrieval", {})
        results.append({
            "case_id": request.query_id,
            "status": bundle.status,
            "latency_seconds": round(seconds, 3),
            "evidence_count": len(bundle.evidence_items),
            "table_count": len(bundle.table_evidence),
            "scope_counts": scope.get("evidence_counts", {}),
            "evidence_origin_counts": dict(Counter(
                origin
                for item in bundle.evidence_items
                for origin in item.retrieval_origins
            )),
            "instrument_source_recovery": scope.get("source_recovery", {}),
            "expected_source_documents": sorted(expected[request.query_id]),
            "covered_source_documents": sorted(covered),
            "source_coverage": len(covered) / len(expected[request.query_id]),
            "retrieved_source_documents": sorted(evidence_documents),
            "table_source_documents": sorted(table_documents),
            "useful_cross_instrument_evidence_survived": (
                request.query_id == "cross_instrument" and covered == expected[request.query_id]
            ),
            "unrelated_similarity_alone_determined_success": (
                bool(scope.get("explicitly_scoped"))
                and bundle.status == "success"
                and int(scope.get("evidence_counts", {}).get("in_scope", 0)) == 0
            ),
            "table_retrieval": {
                key: modality.get(key, 0)
                for key in (
                    "table_pass_one_raw_count", "table_pass_two_raw_count",
                    "table_merged_reranked_count",
                )
            },
            "table_hits": [
                {
                    "document_id": item.document_id, "table_id": item.table_id,
                    "row_ids": item.row_ids, "scope": item.instrument_scope,
                    "score": item.combined_score,
                }
                for item in bundle.table_evidence
            ],
            "provenance_pair_count": len({
                (chunk.document_id, chunk.chunk_id)
                for item in bundle.evidence_items for chunk in item.source_chunks
            }),
        })
    return {
        "mode": "local_only_fixed_concepts_no_nim",
        "artifact_root": str(args.artifact_root),
        "community_graph_modified": False,
        "cases": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, default=Path("jurisynth/global_artifacts_source_uri_v2"))
    parser.add_argument("--community-dir", type=Path, default=Path("jurisynth/global_artifacts_source_uri_v2/community"))
    parser.add_argument(
        "--q003-capture", type=Path,
        default=Path("jurisynth/evaluation_artifacts/chat_handoffs/architecture_fix_review_20260916/results/q003_interpretation_capture.json"),
    )
    parser.add_argument("--output", type=Path, default=Path("jurisynth/run_outputs/retrieval_stabilization_validation.json"))
    args = parser.parse_args()
    result = asyncio.run(run(args))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "case_count": len(result["cases"])}, indent=2))


if __name__ == "__main__":
    main()
