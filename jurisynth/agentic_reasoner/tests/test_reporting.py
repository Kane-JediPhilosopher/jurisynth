import asyncio

import pytest

from jurisynth.agentic_reasoner.models import Claim, LeafAnswer
from jurisynth.agentic_reasoner.reporting import FinalReport, FinalReportSynthesizer, ReportSection, progressive_disclosure_payload
from jurisynth.contracts import Assertion, EvidenceBundle, EvidenceItem, SourceChunk


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


def test_synthesizer_parses_nested_sections_with_valid_claim_references():
    model = FakeModel('{"overview":"Summary","sections":[{"section_id":"s1","title":"Parent","answer_text":"Parent answer","claim_refs":[],"child_sections":[{"section_id":"s2","title":"Child","answer_text":"A duty exists.","claim_refs":["C1"]}]}],"contradiction_refs":[]}')
    report = asyncio.run(FinalReportSynthesizer(model).synthesize("question", [_answer()]))
    assert report.sections[0].child_sections[0].claim_refs == ["C1"]
