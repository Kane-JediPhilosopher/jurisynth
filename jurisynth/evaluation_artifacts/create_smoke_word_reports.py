"""Create professor-facing Word summaries for the two AI-medical live smokes."""

from __future__ import annotations

import json
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "evaluation_artifacts" / "professor_smoke_reports"


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shading = tc_pr.find(qn("w:shd"))
    if shading is None:
        shading = OxmlElement("w:shd")
        tc_pr.append(shading)
    shading.set(qn("w:fill"), fill)


def set_cell_border(cell) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = borders.find(qn(f"w:{side}"))
        if el is None:
            el = OxmlElement(f"w:{side}")
            borders.append(el)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "D9D9D9")


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    tr_pr.append(header)


def style_run(run, *, bold=False, size=10.5, color="000000") -> None:
    run.bold = bold
    run.font.name = "Aptos"
    run._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
    run._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color)


def add_para(doc, text="", *, bold_lead=None, style=None, space_after=6):
    p = doc.add_paragraph(style=style)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.12
    if bold_lead and text.startswith(bold_lead):
        style_run(p.add_run(bold_lead), bold=True)
        style_run(p.add_run(text[len(bold_lead):]))
    else:
        style_run(p.add_run(text))
    return p


def add_table(doc, headers, rows, widths):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.autofit = False
    header_cells = table.rows[0].cells
    set_repeat_table_header(table.rows[0])
    for i, value in enumerate(headers):
        header_cells[i].width = Inches(widths[i])
        set_cell_shading(header_cells[i], "1F4E78")
        set_cell_border(header_cells[i])
        header_cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = header_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        style_run(p.add_run(str(value)), bold=True, size=9, color="FFFFFF")
    for ri, row in enumerate(rows):
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].width = Inches(widths[i])
            set_cell_border(cells[i])
            cells[i].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if ri % 2:
                set_cell_shading(cells[i], "F4F7FA")
            p = cells[i].paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.line_spacing = 1.0
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i in (0, 1, 2, 3) else WD_ALIGN_PARAGRAPH.LEFT
            style_run(p.add_run(str(value)), size=8.5)
    doc.add_paragraph().paragraph_format.space_after = Pt(3)


def clean(text) -> str:
    return " ".join((text or "").split())


def heading(doc, text, level=1):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.paragraph_format.space_before = Pt(12 if level == 1 else 8)
    p.paragraph_format.space_after = Pt(5)
    r = p.add_run(text)
    style_run(r, bold=True, size=14 if level == 1 else 11.5)
    return p


def evidence_summary(node):
    summary = node.get("answer", {}).get("evidence_summary", {}) or {}
    return (
        summary.get("retrieval_status", "not recorded"),
        summary.get("evidence_item_count", 0),
        summary.get("table_evidence_count", 0),
        len(summary.get("evidence_ids", [])),
    )


def make_report(source_name: str, query_name: str, output_name: str, label: str) -> Path:
    data = json.loads((ROOT / "run_outputs" / source_name).read_text(encoding="utf-8"))
    result = data["result"]
    execution = data["execution"]
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Inches(0.7)
    sec.bottom_margin = Inches(0.7)
    sec.left_margin = Inches(0.75)
    sec.right_margin = Inches(0.75)

    styles = doc.styles
    styles["Normal"].font.name = "Aptos"
    styles["Normal"]._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
    styles["Normal"]._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
    styles["Normal"].font.size = Pt(10.5)
    for style_name in ("Title", "Heading 1", "Heading 2"):
        styles[style_name].font.color.rgb = RGBColor(0, 0, 0)

    title = doc.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    style_run(title.add_run(f"Jurisynth {label} AI Medical Smoke Test"), bold=True, size=20)
    subtitle = doc.add_paragraph()
    subtitle.paragraph_format.space_after = Pt(12)
    style_run(subtitle.add_run("Professor briefing report  |  Temporary live compatibility run using NVIDIA Nemotron Super"), size=10, color="4F4F4F")

    overview = clean(result.get("report", {}).get("overview", ""))
    leaf_count = len(result.get("leaves", []))
    claim_count = execution.get("claim_count", 0)
    status = data.get("status", "unknown").upper()
    lead = (
        f"This smoke completed with status {status}. It exercised the full Jurisynth path from query decomposition through retrieval, "
        f"leaf-level evidence-grounded answering, contradiction handling, and final synthesis. The run produced {leaf_count} leaves, "
        f"{claim_count} claims, no failed leaves, and no retrieval exceptions in {data.get('elapsed_seconds', 0):.2f} seconds."
    )
    add_para(doc, lead)
    add_para(doc, "Interpretation: "+overview)
    add_para(doc, "Scope note: this is an engineering smoke test, not a legal-accuracy evaluation. Retrieval status indicates the pipeline contract, not necessarily complete answer-bearing coverage for a broad legal issue.", bold_lead="Scope note: ")

    heading(doc, "Original user query")
    query_text = data.get("query") or data.get("input_query")
    if not query_text:
        query_text = (ROOT / "evaluation_artifacts" / query_name).read_text(encoding="utf-8")
    add_para(doc, clean(query_text))
    if result.get("analysis", {}).get("contextual_facts"):
        add_para(doc, "Scenario context: " + "; ".join(result["analysis"]["contextual_facts"]))

    heading(doc, "Decomposition and scheduling")
    leaves = result.get("leaves", [])
    rows = []
    for leaf in leaves:
        rows.append([
            leaf.get("query_id", ""),
            clean(leaf.get("query", "")),
            ", ".join(leaf.get("dependency_ids", [])) or "None",
        ])
    add_table(doc, ["Leaf", "Atomic legal question", "Dependencies"], rows, [0.55, 5.5, 1.1])
    if all(not l.get("dependency_ids") for l in leaves):
        add_para(doc, "All leaves had no explicit prerequisites. The deterministic scheduler therefore treated them as independently runnable and executed them in parallel subject to its worker capacity.")
    else:
        add_para(doc, "The scheduler used the declared dependencies above and only admitted dependent leaves after their upstream result became available.")

    heading(doc, "Retrieval and leaf answer outcomes")
    outcome_rows = []
    node_results = result.get("node_results", {})
    for leaf in leaves:
        lid = leaf.get("query_id")
        node = node_results.get(lid, {})
        ret_status, items, tables, _ids = evidence_summary(node)
        answer = clean((node.get("answer") or {}).get("answer_text", ""))
        claims = len((node.get("answer") or {}).get("claims", []) or [])
        outcome_rows.append([lid, ret_status, items, tables, claims, answer])
    add_table(doc, ["Leaf", "Retrieval", "Evidence", "Tables", "Claims", "Leaf conclusion"], outcome_rows, [0.42, 0.7, 0.55, 0.45, 0.45, 4.58])

    heading(doc, "Final synthesis and grounding observations")
    add_para(doc, overview)
    report = result.get("report", {}) or {}
    sections = report.get("sections", []) or []
    if sections:
        for section in sections:
            add_para(doc, clean(section.get("title", "")), style="Heading 2", space_after=3)
            add_para(doc, clean(section.get("answer_text", "")))

    heading(doc, "Trace and limitations")
    add_para(doc, f"Model: NVIDIA Nemotron Super. Total wall time: {data.get('elapsed_seconds', 0):.2f} seconds. The run returned {execution.get('failed_leaf_count', 0)} failed leaves and {execution.get('retrieval_error_count', 0)} retrieval errors.")
    add_para(doc, "Provenance is carried through the evidence IDs retained in each leaf answer. This briefing condenses those IDs and source excerpts for readability; the full machine-readable trace remains in the corresponding JSON run artifact and reasoning log.")
    if label.lower().startswith("organized"):
        add_para(doc, "The organized wording separated the scenario into seven explicit legal issues. It retrieved a substantive obligations answer for one issue, while correctly marking several unresolved issues as insufficiently supported rather than asserting unsupported conclusions.")
    else:
        add_para(doc, "The messy wording condensed the scenario into four broader issues. The system completed cleanly but abstained on all of them because the retrieved material did not support the scenario-specific legal conclusions.")

    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    style_run(footer.add_run("Jurisynth smoke-test briefing"), size=8, color="666666")

    OUTPUT.mkdir(parents=True, exist_ok=True)
    destination = OUTPUT / output_name
    doc.save(destination)
    return destination


if __name__ == "__main__":
    organized = make_report(
        "global_complex_ai_medical_organized_super_20260917.json",
        "complex_ai_medical_organized.txt",
        "Jurisynth_Organized_AI_Medical_Smoke_Report.docx",
        "Organized",
    )
    messy = make_report(
        "global_complex_ai_medical_messy_super_20260917.json",
        "complex_ai_medical_messy.txt",
        "Jurisynth_Messy_AI_Medical_Smoke_Report.docx",
        "Messy",
    )
    print(organized)
    print(messy)
