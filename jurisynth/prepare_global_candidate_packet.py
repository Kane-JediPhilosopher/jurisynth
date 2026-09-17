"""Prepare the source-first, self-contained global natural-question review packet.

The runner deliberately uses the deterministic LeafQueryInterpreter rather
than NIM: this records Retrieval Mech behaviour without making an answer,
decomposition, or source-selection call to a language model.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from collections import Counter
from pathlib import Path
from typing import Any

from jurisynth.contracts import RetrievalRequest
from jurisynth.main import _load_community_guidance
from jurisynth.retrieval_mech.er_matcher import ERMatcher, PersistedERIndices
from jurisynth.retrieval_mech.config import GLOBAL_MAX_QUADS_PER_SEED
from jurisynth.retrieval_mech.global_artifacts import load_global_artifacts
from jurisynth.retrieval_mech.mechanism import RetrievalMechanism
from jurisynth.retrieval_mech.rdf_retriever import DirectRDFRetriever, LeafQueryInterpreter


# These are source-first review candidates, not gold legal-QA answers. Their
# supporting chunk ids come from the independent deterministic source sample.
_TEXT_CASES: tuple[dict[str, Any], ...] = (
    {"category": "obligation_prohibition", "question": "What must an authority tell the applicant authority when it refuses or withholds requested assistance?", "sources": (("L_1994001EN.01000101", "chunk_50"),)},
    {"category": "obligation_prohibition", "question": "What interim protection may a judicial authority provide to prevent an imminent intellectual-property infringement?", "sources": (("L_2008289EN.01000101", "chunk_48"),)},
    {"category": "obligation_prohibition", "question": "Under the aquatic-toxicity testing procedure described in the source, what information must the test report contain?", "sources": (("L_2008142EN.01000101", "chunk_319"),)},
    {"category": "definition_scope", "question": "What level of free volatile acid is required for food preserved in vinegar or acetic acid to fall under heading 2001?", "sources": (("L_2008291EN.01000101", "chunk_112"),)},
    {"category": "definition_scope", "question": "When does wood powder qualify as wood flour for tariff-heading purposes?", "sources": (("L_2011282EN.01000101", "chunk_271"),)},
    {"category": "definition_scope", "question": "What is treated as water-pipe tobacco for the relevant tariff subheading?", "sources": (("L_2016294EN.01000101", "chunk_164"),)},
    {"category": "definition_scope", "question": "How is the country of origin determined for a good or part produced from a blank?", "sources": (("L_2015343EN.01000101", "chunk_129"),)},
    {"category": "procedure_deadline", "question": "When does the TIR Convention enter into force after the required States have completed the specified signature or ratification steps?", "sources": (("L_2009165EN.01000101", "chunk_10"),)},
    {"category": "procedure_deadline", "question": "Who may request a meeting of the Committee on Trade in Goods, and what is it meant to consider?", "sources": (("L_2011127EN.01000101", "chunk_8"),)},
    {"category": "procedure_deadline", "question": "When may customs authorities carry out a subsequent verification of a proof of origin?", "sources": (("L_2007345EN.01000101", "chunk_39"),)},
    {"category": "procedure_deadline", "question": "Which measurements must be collected during the road-load curve determination procedure?", "sources": (("L_2017175EN.01000101", "chunk_157"),)},
    {"category": "cross_document_dependent", "question": "In a customs-origin inquiry, how is a good's origin determined when it is made from a blank, and when may the importing authorities verify its proof of origin?", "sources": (("L_2015343EN.01000101", "chunk_129"), ("L_2007345EN.01000101", "chunk_39"))},
    {"category": "cross_document_dependent", "question": "For an import containing vinegar-preserved food and water-pipe tobacco, what classification criteria apply to each product?", "sources": (("L_2008291EN.01000101", "chunk_112"), ("L_2016294EN.01000101", "chunk_164"))},
    {"category": "cross_document_dependent", "question": "For an import containing vinegar-preserved food and wood powder, what separate tariff-classification criteria would the importer need to apply?", "sources": (("L_2008291EN.01000101", "chunk_112"), ("L_2011282EN.01000101", "chunk_271"))},
    {"category": "cross_document_dependent", "question": "In a cross-border customs matter, what must be communicated if mutual assistance is denied, and when may authorities recheck a proof of origin?", "sources": (("L_1994001EN.01000101", "chunk_50"), ("L_2007345EN.01000101", "chunk_39"))},
    {"category": "cross_document_dependent", "question": "Where a trade-in-goods issue and an alleged intellectual-property infringement arise under the applicable agreements, what institutional and interim-remedy mechanisms are described?", "sources": (("L_2011127EN.01000101", "chunk_8"), ("L_2008289EN.01000101", "chunk_48"))},
    {"category": "cross_document_dependent", "question": "For a technical compliance dossier, what belongs in the toxicology test report and what data must be recorded in the vehicle road-load procedure?", "sources": (("L_2008142EN.01000101", "chunk_319"), ("L_2017175EN.01000101", "chunk_157"))},
)

_TABLE_CASES: tuple[dict[str, Any], ...] = (
    {"category": "table", "question": "For the 2021–2025 allocation table, what annual and total allocation quantities are recorded for Audi Brussels?", "table": ("C_2022160EN.01002701", "table_1", 0)},
    {"category": "table", "question": "For the 2021–2025 allocation table, what amounts are recorded for the Lakeland Dairies Killeshandra Site?", "table": ("C_2022236EN.01000501", "table_11", 1)},
    {"category": "table", "question": "How does the fisheries table distinguish a metier from a fleet segment across its listed geographic aggregation levels?", "table": ("L_2010041EN.01000801", "table_10", (0, 1, 2))},
)

_ADJUDICATION: dict[str, dict[str, str]] = {
    "global_natural_001": {"verdict": "pass_alternate_source", "note": "Expected source is valid; an alternate source states the same decision-and-reasons rule."},
    "global_natural_002": {"verdict": "pass_alternate_source", "note": "An alternate IP-enforcement provision is answer-bearing."},
    "global_natural_003": {"verdict": "revised", "note": "Question narrowed to the identified testing procedure; re-review source scope."},
    "global_natural_004": {"verdict": "strong_pass", "note": "Expected source and equivalent later CN provisions are answer-bearing."},
    "global_natural_005": {"verdict": "clean_failure", "note": "Keep as a precise defining-rule retrieval miss."},
    "global_natural_006": {"verdict": "pass_alternate_source", "note": "Equivalent answer-bearing provisions were retrieved."},
    "global_natural_007": {"verdict": "clean_failure", "note": "Keep as a precise special-origin-rule retrieval miss."},
    "global_natural_008": {"verdict": "revised", "note": "Question now names the TIR Convention; rerun before scoring."},
    "global_natural_009": {"verdict": "partial_failure", "note": "Same agreement was found, but not the required Committee-on-Trade-in-Goods rule."},
    "global_natural_010": {"verdict": "pass_alternate_source", "note": "Equivalent verification triggers were retrieved."},
    "global_natural_011": {"verdict": "clean_failure", "note": "Right topic/document, but not the answer-bearing measurement clause."},
    "global_natural_012": {"verdict": "exclude", "note": "No demonstrated shared legal inquiry between the selected instruments."},
    "global_natural_013": {"verdict": "exclude", "note": "Temporal coherence between CN editions is not established."},
    "global_natural_014": {"verdict": "exclude", "note": "Temporal coherence between CN editions is not established."},
    "global_natural_015": {"verdict": "exclude", "note": "The two customs provisions do not establish shared applicability."},
    "global_natural_016": {"verdict": "exclude", "note": "The sources belong to different trade-agreement frameworks."},
    "global_natural_017": {"verdict": "exclude", "note": "The paired technical regimes are unrelated."},
    "global_natural_018": {"verdict": "revised", "note": "Question now fixes the 2021–2025 table version; later allocation changes are not a retrieval error."},
    "global_natural_019": {"verdict": "revised", "note": "Question now fixes the 2021–2025 table version."},
    "global_natural_020": {"verdict": "revised_gold", "note": "Gold now includes rows 0–2, which are needed to answer the comparison."},
}


def candidates() -> list[dict[str, Any]]:
    values = [dict(item) for item in (*_TEXT_CASES, *_TABLE_CASES)]
    if len(values) != 20:
        raise AssertionError("the approved formative candidate allocation must contain exactly 20 cases")
    for number, value in enumerate(values, start=1):
        value["case_id"] = f"global_natural_{number:03d}"
        adjudication = _ADJUDICATION[value["case_id"]]
        value["external_adjudication"] = {"source": "ChatGPT adjudication supplied by project owner", **adjudication}
        value["review_status"] = "excluded_pending_replacement" if adjudication["verdict"] == "exclude" else "reviewed_pending_finalization"
        value["cross_document_coherence"] = "confirm" if value["category"] == "cross_document_dependent" else "not_applicable"
    return values


def _source_pool_lookup(source_pool: Path) -> dict[tuple[str, str], str]:
    pool = json.loads(source_pool.read_text(encoding="utf-8"))
    return {
        (item["document_id"], item["chunk_id"]): item["excerpt"]
        for values in pool["strata"].values()
        for item in values
    }


def _expected_table(root: Path, document_id: str, table_id: str, row_id: int | tuple[int, ...]) -> dict[str, object]:
    source = json.loads((root / "tables" / "table_store" / f"{document_id}_{table_id}.json").read_text(encoding="utf-8"))
    rows = source.get("data") or []
    row_ids = (row_id,) if isinstance(row_id, int) else row_id
    if any(value >= len(rows) for value in row_ids):
        raise ValueError(f"Expected table row is unavailable: {document_id} {table_id} {row_ids}")
    return {"document_id": document_id, "table_id": table_id, "row_ids": list(row_ids), "headers": source.get("header"), "rows": [rows[value] for value in row_ids]}


def _bundle_preview(bundle: object, *, limit: int = 8) -> dict[str, object]:
    chunks: dict[tuple[str, str], dict[str, object]] = {}
    for item in getattr(bundle, "evidence_items", []):
        for source in item.source_chunks:
            chunks.setdefault((source.document_id, source.chunk_id), {
                "document_id": source.document_id, "chunk_id": source.chunk_id,
                "excerpt": " ".join(source.text.split())[:900], "origin": list(item.retrieval_origins),
            })
    for source in getattr(bundle, "retrieval_metadata", {}).get("direct_chunk_matches", []):
        if isinstance(source, dict):
            key = (str(source.get("document_id", "")), str(source.get("chunk_id", "")))
            chunks.setdefault(key, {"document_id": key[0], "chunk_id": key[1], "excerpt": str(source.get("text", ""))[:900], "origin": ["direct_chunk"]})
    tables = [
        {"document_id": item.document_id, "table_id": item.table_id, "row_ids": item.row_ids, "headers": item.headers, "rows": item.matched_rows}
        for item in getattr(bundle, "table_evidence", [])[:limit]
    ]
    return {"status": bundle.status, "chunks": list(chunks.values())[:limit], "tables": tables, "warnings": bundle.retrieval_metadata.get("warnings", [])}


async def prepare(args: argparse.Namespace) -> dict[str, object]:
    from sentence_transformers import SentenceTransformer

    artifacts = load_global_artifacts(args.artifact_root)
    indices = PersistedERIndices.load(args.community_dir / "er_index")
    embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    selector, orientation, descriptors = _load_community_guidance(
        args.community_dir / "er_index", indices,
        hierarchy_path=args.community_dir / "community_hierarchy.json",
        descriptor_path=args.community_dir / "community_descriptors.json",
    )
    mechanism = RetrievalMechanism(
        embedder,
        chunk_indices=[artifacts.chunk_index],
        table_indices=[artifacts.table_index] if artifacts.table_index is not None else [],
        structured_retriever=DirectRDFRetriever(
            artifacts.dataset, ERMatcher(indices, embedder), artifacts.resolve_chunk,
            interpreter=LeafQueryInterpreter(), community_selector=selector,
            max_quads_per_seed=GLOBAL_MAX_QUADS_PER_SEED,
        ),
        community_orientation_builder=orientation,
        community_descriptors=descriptors,
        # This packet is retrieval-only: do not invoke a model for optional
        # community orientation summaries.
        community_summarizer=None,
        document_metadata=artifacts.document_metadata,
    )
    excerpts = _source_pool_lookup(args.source_pool)
    packet_cases: list[dict[str, object]] = []
    selected = set(getattr(args, "case_id", []))
    for case in candidates():
        if selected and case["case_id"] not in selected:
            continue
        expected_chunks = [
            {"document_id": doc, "chunk_id": chunk, "excerpt": excerpts.get((doc, chunk), "SOURCE EXCERPT MISSING — do not approve")}
            for doc, chunk in case.get("sources", ())
        ]
        expected_table = _expected_table(args.artifact_root, *case["table"]) if "table" in case else None
        bundle = await mechanism.retrieve_evidence(RetrievalRequest(case["case_id"], case["question"]))
        packet_cases.append({
            **case,
            "expected_chunks": expected_chunks,
            **({"expected_table": expected_table} if expected_table is not None else {}),
            "retrieved": _bundle_preview(bundle),
            "human_review": {"source_validity": None, "retrieval_relevance": None, "cross_document_coherence": None, "notes": ""},
        })
    return {
        "packet_version": "1.0",
        "purpose": "Formative source-first global natural-question retrieval review; not a legal-QA benchmark.",
        "source_selection": "Independent deterministic chunk-text sampling; prior AI Act/GDPR global-smoke topic excluded.",
        "retrieval_mode": "Global Oxigraph/FAISS retrieval with deterministic LeafQueryInterpreter; no NIM call.",
        "case_count": len(packet_cases),
        "eligible_after_adjudication": sum(case["review_status"] != "excluded_pending_replacement" for case in packet_cases),
        "category_counts": dict(Counter(str(case["category"]) for case in packet_cases)),
        "cases": packet_cases,
    }


def _write_markdown(packet: dict[str, object], destination: Path) -> None:
    lines = ["# Global natural-question candidate packet", "", str(packet["purpose"]), "", "Each candidate is pending review. Cross-document cases must be confirmed as coherent before scoring.", ""]
    for case in packet["cases"]:
        lines.extend([f"## {case['case_id']} — {case['category']}", "", f"**Question:** {case['question']}", "", "### Expected source"])
        for source in case["expected_chunks"]:
            lines.extend([f"- `{source['document_id']}`, `{source['chunk_id']}`: {source['excerpt']}"])
        if "expected_table" in case:
            table = case["expected_table"]
            lines.extend(["", f"### Expected table rows\n\n- `{table['document_id']}`, `{table['table_id']}`, rows {table['row_ids']}: `{table['rows']}`"])
        retrieved = case["retrieved"]
        lines.extend(["", f"### Retrieved evidence — status `{retrieved['status']}`", ""])
        for source in retrieved["chunks"]:
            lines.append(f"- `{source['document_id']}`, `{source['chunk_id']}`: {source['excerpt']}")
        if not retrieved["chunks"]:
            lines.append("- No text chunk was returned.")
        for table in retrieved["tables"]:
            lines.append(f"- table `{table['document_id']}`, `{table['table_id']}`, rows {table['row_ids']}: `{table['rows']}`")
        adjudication = case["external_adjudication"]
        lines.extend(["", f"**Adjudication:** `{adjudication['verdict']}` — {adjudication['note']}", "", "**Review:** source validity / retrieval relevance / cross-document coherence / notes", ""])
    destination.write_text("\n".join(lines), encoding="utf-8")


def refresh_existing_packet(args: argparse.Namespace) -> dict[str, object]:
    """Apply adjudication and wording fixes without rerunning global retrieval.

    Changed questions deliberately receive a stale marker.  This makes the
    review packet immediately honest and avoids pretending that old retrieval
    results answer revised questions on a memory-constrained laptop.
    """
    packet = json.loads(args.output.read_text(encoding="utf-8"))
    previous = {case["case_id"]: case for case in packet["cases"]}
    excerpts = _source_pool_lookup(args.source_pool)
    refreshed: list[dict[str, object]] = []
    for template in candidates():
        case = dict(previous[template["case_id"]])
        case.update(template)
        case["expected_chunks"] = [
            {"document_id": doc, "chunk_id": chunk, "excerpt": excerpts.get((doc, chunk), "SOURCE EXCERPT MISSING — do not approve")}
            for doc, chunk in template.get("sources", ())
        ]
        if "table" in template:
            case["expected_table"] = _expected_table(args.artifact_root, *template["table"])
        verdict = template["external_adjudication"]["verdict"]
        if verdict in {"revised", "revised_gold"}:
            case["retrieved"] = {
                "status": "stale_pending_rerun",
                "chunks": [], "tables": [],
                "warnings": ["Question or expected evidence changed after adjudication; rerun this case before scoring."],
            }
        refreshed.append(case)
    packet["packet_version"] = "1.1"
    packet["adjudication_note"] = "Verdicts are external ChatGPT adjudication supplied by the project owner; they are recorded as formative review, not benchmark ground truth."
    packet["eligible_after_adjudication"] = sum(
        case["review_status"] != "excluded_pending_replacement" for case in refreshed
    )
    packet["cases"] = refreshed
    return packet


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, default=Path("jurisynth/global_artifacts"))
    parser.add_argument("--community-dir", type=Path, default=Path("jurisynth/global_artifacts/community"))
    parser.add_argument("--source-pool", type=Path, default=Path("jurisynth/evaluation_artifacts/global_source_first_pool.json"))
    parser.add_argument("--output", type=Path, default=Path("jurisynth/evaluation_artifacts/global_natural_candidate_packet.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("jurisynth/evaluation_artifacts/GLOBAL_NATURAL_CANDIDATE_PACKET.md"))
    parser.add_argument("--case-id", action="append", default=[], help="Refresh only this case id; may be repeated.")
    parser.add_argument("--merge-into-existing", action="store_true", help="Replace refreshed cases in an existing full packet.")
    parser.add_argument("--reuse-retrieval", action="store_true", help="Apply adjudication changes without executing retrieval; revised cases are marked stale.")
    args = parser.parse_args()
    selected = set(args.case_id)
    if selected:
        known = {case["case_id"] for case in candidates()}
        unknown = selected - known
        if unknown:
            parser.error(f"unknown case id(s): {', '.join(sorted(unknown))}")
    if args.reuse_retrieval:
        if args.case_id or args.merge_into_existing:
            parser.error("--reuse-retrieval cannot be combined with --case-id or --merge-into-existing")
        if not args.output.exists():
            parser.error("--reuse-retrieval requires an existing --output packet")
        packet = refresh_existing_packet(args)
    else:
        packet = asyncio.run(prepare(args))
    if args.merge_into_existing:
        if not args.output.exists():
            parser.error("--merge-into-existing requires an existing --output packet")
        existing = json.loads(args.output.read_text(encoding="utf-8"))
        updates = {case["case_id"]: case for case in packet["cases"]}
        existing_cases = existing.get("cases", [])
        existing["cases"] = [updates.get(case.get("case_id"), case) for case in existing_cases]
        existing["packet_version"] = "1.1"
        existing["eligible_after_adjudication"] = sum(
            case.get("review_status") != "excluded_pending_replacement" for case in existing["cases"]
        )
        packet = existing
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _write_markdown(packet, args.markdown_output)
    print(json.dumps({"output": str(args.output), "markdown": str(args.markdown_output), "case_count": packet["case_count"], "category_counts": packet["category_counts"]}, indent=2))


if __name__ == "__main__":
    main()
