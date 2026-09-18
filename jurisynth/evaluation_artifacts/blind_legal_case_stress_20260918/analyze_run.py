"""Produce deterministic structural statistics after the blind run is sealed."""

from __future__ import annotations

import json
from pathlib import Path


BASE = Path("jurisynth/evaluation_artifacts/blind_legal_case_stress_20260918")


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _modality(item: dict[str, object]) -> str:
    origins = item.get("retrieval_origins", [])
    return "chunk" if "chunk" in origins else "assertion"


def main() -> None:
    run = _read(BASE / "live_run" / "complete_run.json")
    traces = {
        str(item["query_id"]): item
        for item in run.get("prompt_selection_traces", [])
    }
    leaves: dict[str, object] = {}
    all_claims: list[dict[str, object]] = []
    all_documents: set[str] = set()
    for query_id, node in run["node_results"].items():
        answer = node.get("answer")
        if answer is None:
            leaves[query_id] = {"node_status": node["status"], "error": node["error"]}
            continue
        bundle = answer["evidence_bundle"]
        items = bundle["evidence_items"]
        by_id = {str(item["evidence_id"]): item for item in items}
        documents_by_modality = {"assertion": set(), "chunk": set()}
        for item in items:
            modality = _modality(item)
            for source in item["source_chunks"]:
                documents_by_modality[modality].add(str(source["document_id"]))
                all_documents.add(str(source["document_id"]))
        claims = []
        for claim in answer["claims"]:
            cited = [by_id[ref] for ref in claim["evidence_refs"] if ref in by_id]
            modalities = sorted({_modality(item) for item in cited})
            row = {
                "query_id": query_id,
                "claim_id": claim["claim_id"],
                "text": claim["text"],
                "status": claim["status"],
                "evidence_refs": claim["evidence_refs"],
                "cited_modalities": modalities,
                "all_references_resolve": len(cited) == len(claim["evidence_refs"]),
            }
            claims.append(row)
            all_claims.append(row)
        selected = traces.get(query_id, {}).get("selected", [])
        selected_details = []
        for selected_item in selected:
            item = by_id.get(str(selected_item["evidence_id"]))
            if item is None:
                continue
            selected_details.append(
                {
                    **selected_item,
                    "assertion": item["assertion"],
                    "sources": [
                        {
                            "document_id": source["document_id"],
                            "chunk_id": source["chunk_id"],
                            "text": source["text"][:1200],
                        }
                        for source in item["source_chunks"]
                    ],
                }
            )
        leaves[query_id] = {
            "node_status": node["status"],
            "answer_status": answer["status"],
            "answer_text": answer["answer_text"],
            "retrieval_status": bundle["status"],
            "evidence_count": len(items),
            "assertion_count": sum(_modality(item) == "assertion" for item in items),
            "chunk_count": sum(_modality(item) == "chunk" for item in items),
            "table_count": len(bundle.get("table_evidence", [])),
            "image_count": len(bundle.get("image_evidence", [])),
            "documents_by_modality": {
                key: sorted(value) for key, value in documents_by_modality.items()
            },
            "selected_assertion_count": sum(
                item.get("modality") == "assertion" for item in selected
            ),
            "selected_chunk_count": sum(item.get("modality") == "chunk" for item in selected),
            "selected_evidence": selected_details,
            "claims": claims,
            "retrieval_diagnostics": bundle.get("retrieval_diagnostics", {}),
            "community_summary": bundle.get("community_summary"),
        }

    reasoning_events = [
        json.loads(line)
        for line in (BASE / "live_run" / "reasoning.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    retrieval_seconds = {
        str(event["query_id"]): round(float(event["duration_ms"]) / 1000, 3)
        for event in reasoning_events
        if event.get("event") == "retrieval_completed"
    }
    leaf_seconds = {
        str(event["query_id"]): round(float(event["duration_ms"]) / 1000, 3)
        for event in reasoning_events
        if event.get("event") == "leaf_generation_completed"
    }
    summary = {
        "case_id": run["case_id"],
        "route": run["analysis"]["route"],
        "ast": run["ast"],
        "leaves_plan": run["leaves"],
        "dependency_edges": run["dependency_edges"],
        "leaf_results": leaves,
        "claim_counts": {
            "total": len(all_claims),
            "with_evidence": sum(bool(item["evidence_refs"]) for item in all_claims),
            "without_evidence": sum(not item["evidence_refs"] for item in all_claims),
            "assertion_only": sum(item["cited_modalities"] == ["assertion"] for item in all_claims),
            "chunk_only": sum(item["cited_modalities"] == ["chunk"] for item in all_claims),
            "both": sum(item["cited_modalities"] == ["assertion", "chunk"] for item in all_claims),
            "all_references_resolve": all(item["all_references_resolve"] for item in all_claims),
        },
        "all_retrieved_documents": sorted(all_documents),
        "expected_document_presence": {
            "eprivacy_32002L0058en": "32002L0058en" in all_documents,
            "gdpr_L_2016119EN.01000101": "L_2016119EN.01000101" in all_documents,
        },
        "contradictions": run["contradictions"],
        "contradiction_detector_status": "disabled_for_case_study_after_cpu_cost_gate",
        "final_report": run["final_report"],
        "latency_seconds": {
            "per_leaf_retrieval": retrieval_seconds,
            "per_leaf_generation": leaf_seconds,
            "nim_completed_total": run["nim"]["completed_seconds"],
            "total_wall": run["total_wall_seconds"],
        },
        "nim": run["nim"],
        "peak_rss_bytes": run["peak_rss_bytes"],
    }
    output = BASE / "structural_analysis.json"
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "claims": summary["claim_counts"]}, ensure_ascii=True))


if __name__ == "__main__":
    main()
