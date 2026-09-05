from jurisynth.agentic_reasoner.reporting import FinalReport, ReportSection
from jurisynth.lexglue_adapter import adapt_report


def test_adapter_flattens_nested_report_in_deterministic_order():
    report = FinalReport(
        "Overview",
        [ReportSection("s1", "Parent", "Parent answer", ["C1"], [ReportSection("s2", "Child", "Child answer", ["C2"])])],
        ["X1"],
    )
    adapted = adapt_report(report)
    assert adapted.answer_text == "Overview\n\nParent answer\n\nChild answer"
    assert adapted.claim_ids == ("C1", "C2")
    assert adapted.contradiction_ids == ("X1",)


def test_adapter_returns_cautious_empty_answer_without_a_report():
    assert adapt_report(None).claim_ids == ()
