import asyncio

import pytest

from jurisynth.agentic_reasoner.models import Claim, LeafAnswer
from jurisynth.agentic_reasoner.contradiction import Contradiction
from jurisynth.agentic_reasoner.reporting import FinalReport, FinalReportSynthesizer, ReportSection, progressive_disclosure_payload
from jurisynth.contracts import Assertion, EvidenceBundle, EvidenceItem, ImageEvidence, SourceChunk


class FakeModel:
    def __init__(self, response):
        self.response = response

    async def complete(self, **kwargs):
        return self.response


class CapturingModel(FakeModel):
    def __init__(self, response):
        super().__init__(response)
        self.user = None
    async def complete(self, **kwargs):
        self.user = kwargs["user"]
        return await super().complete(**kwargs)


def _answer():
    return LeafAnswer("q1", "supported", "A duty exists.", [Claim("C1", "A duty exists.", ["E1"])], EvidenceBundle("q1", "success"))


def test_synthesizer_preserves_only_known_claim_references():
    model = FakeModel('{"overview":"Summary","sections":[{"section_id":"s1","title":"Duty","answer_text":"A duty exists.","claim_refs":["C1"]}],"contradiction_refs":[]}')
    report = asyncio.run(FinalReportSynthesizer(model).synthesize("question", [_answer()]))
    assert report.sections[0].claim_refs == ["C1"]


def test_synthesizer_receives_ast_guidance_without_turning_it_into_claims():
    model = CapturingModel('{"overview":"Summary","sections":[],"contradiction_refs":[]}')
    asyncio.run(FinalReportSynthesizer(model).synthesize("question", [_answer()], structural_guidance=[{"query_id":"q1","dependency_ids":[]}]))
    assert '"structural_guidance": [{"query_id": "q1", "dependency_ids": []}]' in model.user


def test_synthesizer_rejects_invented_claim_references():
    model = FakeModel('{"overview":"Summary","sections":[{"section_id":"s1","title":"Duty","answer_text":"A duty exists.","claim_refs":["made-up"]}],"contradiction_refs":[]}')
    with pytest.raises(ValueError, match="unknown Claim"):
        asyncio.run(FinalReportSynthesizer(model).synthesize("question", [_answer()]))


def test_synthesizer_rejects_invented_contradiction_references():
    class Conflict:
        contradiction_id = "X1"
        claim_a_id = "C1"
        claim_b_id = "C1"
        score = 0.95
        explanation = "Potential conflict."

    model = FakeModel('{"overview":"Summary","sections":[],"contradiction_refs":["made-up"]}')

    with pytest.raises(ValueError, match="unknown contradiction"):
        asyncio.run(FinalReportSynthesizer(model).synthesize("question", [_answer()], contradictions=[Conflict()]))


def test_progressive_payload_keeps_evidence_nested_under_its_claim():
    answer = LeafAnswer(
        "q1", "supported", "A duty exists.", [Claim("C1", "A duty exists.", ["E1"])],
        EvidenceBundle("q1", "success", [
            EvidenceItem("E1", Assertion("s", "p", "o"), [SourceChunk("chunk-1", "doc-1", "source excerpt")])
        ]),
    )
    payload = progressive_disclosure_payload(
        FinalReport("Summary", [ReportSection("s1", "Duty", "A duty exists.", ["C1"])], []),
        [answer],
    )
    assert payload["sections"][0]["claims"][0]["evidence"][0]["sources"][0]["excerpt"] == "source excerpt"


def test_progressive_payload_exposes_images_as_auxiliary_metadata_only():
    answer = LeafAnswer("q1", "supported", "A duty exists.", [], EvidenceBundle(
        "q1", "success", image_evidence=[ImageEvidence(
            "image-1", "doc-1", "private/path.png", "image/png", "A form", "",
            expanded_description="The form contains two labelled fields.",
        )],
    ))
    payload = progressive_disclosure_payload(FinalReport("Summary", [], []), [answer])
    image = payload["auxiliary_images"][0]
    assert image["auxiliary_only"] is True
    assert image["expanded_description"] == "The form contains two labelled fields."
    assert "relative_path" not in image


def test_synthesizer_parses_nested_sections_with_valid_claim_references():
    model = FakeModel('{"overview":"Summary","sections":[{"section_id":"s1","title":"Parent","answer_text":"Parent answer","claim_refs":[],"child_sections":[{"section_id":"s2","title":"Child","answer_text":"A duty exists.","claim_refs":["C1"]}]}],"contradiction_refs":[]}')
    report = asyncio.run(FinalReportSynthesizer(model).synthesize("question", [_answer()]))
    assert report.sections[0].child_sections[0].claim_refs == ["C1"]


def _two_claim_answers():
    assertion = Assertion("controller", "may_process", "data")
    first = LeafAnswer("q1", "supported", "May process.", [Claim("C1", "A controller may process data.", ["E1"])], EvidenceBundle("q1", "success", [EvidenceItem("E1", assertion, [SourceChunk("chunk-a", "doc-a", "first source")])]))
    second = LeafAnswer("q2", "supported", "May not process.", [Claim("C2", "A controller may not process data.", ["E2"])], EvidenceBundle("q2", "success", [EvidenceItem("E2", assertion, [SourceChunk("chunk-b", "doc-b", "second source")])]))
    return [first, second]


def _flag(a="C1", b="C2", identifier="X1", scorer="nli_cross_encoder"):
    return Contradiction(identifier, a, b, 0.95, "Potential conflict.", ("controller", "may_process"), scorer, "cross-encoder/nli-deberta-v3-base")


def test_synthesizer_attaches_traceable_potential_contradictions_even_when_model_omits_refs():
    report = asyncio.run(FinalReportSynthesizer(FakeModel('{"overview":"Summary","sections":[],"contradiction_refs":[]}')).synthesize("question", _two_claim_answers(), contradictions=[_flag()]))
    assert len(report.potential_contradictions) == 1
    flag = report.potential_contradictions[0]
    assert (flag.claim_a_id, flag.claim_b_id) == ("C1", "C2")
    assert flag.claim_a_evidence_refs == ["E1"]
    assert flag.scorer_model == "cross-encoder/nli-deberta-v3-base"
    payload = progressive_disclosure_payload(report, _two_claim_answers())
    assert payload["potential_contradictions_heading"] == "Potential Contradictions Identified"
    assert payload["potential_contradictions"][0]["claim_a"]["evidence"][0]["sources"][0]["document_id"] == "doc-a"


def test_potential_contradictions_deduplicate_reversed_pairs_and_omit_when_absent():
    answers = _two_claim_answers()
    report = asyncio.run(FinalReportSynthesizer(FakeModel('{"overview":"Summary","sections":[],"contradiction_refs":[]}')).synthesize("question", answers, contradictions=[_flag(), _flag("C2", "C1", "X2")]))
    assert len(report.potential_contradictions) == 1
    empty = asyncio.run(FinalReportSynthesizer(FakeModel('{"overview":"Summary","sections":[],"contradiction_refs":[]}')).synthesize("question", answers))
    assert empty.potential_contradictions == []
    assert progressive_disclosure_payload(empty, answers)["potential_contradictions_heading"] is None


def test_explicit_diagnostic_flags_never_appear_in_a_user_facing_report():
    report = asyncio.run(FinalReportSynthesizer(FakeModel('{"overview":"Summary","sections":[],"contradiction_refs":[]}')).synthesize("question", _two_claim_answers(), contradictions=[_flag(scorer="explicit_negation_heuristic")]))
    assert report.potential_contradictions == []
