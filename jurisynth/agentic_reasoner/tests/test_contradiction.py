import asyncio

from jurisynth.agentic_reasoner.contradiction import (
    ContradictionCandidate,
    ContradictionDetector,
    ExplicitNegationScorer,
    NLIContradictionScorer,
)
from jurisynth.agentic_reasoner.models import Claim, LeafAnswer
from jurisynth.contracts import Assertion, EvidenceBundle, EvidenceItem


def _answer(query_id: str, claim_id: str, text: str, assertion: Assertion) -> LeafAnswer:
    evidence = EvidenceItem("E1", assertion, [])
    return LeafAnswer(query_id, "supported", text, [Claim(claim_id, text, ["E1"])], EvidenceBundle(query_id, "success", [evidence]))


def test_detector_flags_only_explicit_opposing_claims_about_the_same_evidence_resources():
    assertion = Assertion("controller", "may_process", "personal data")
    answers = [
        _answer("q1", "C1", "A controller may process personal data.", assertion),
        _answer("q2", "C2", "A controller may not process personal data.", assertion),
    ]

    conflicts = asyncio.run(ContradictionDetector(ExplicitNegationScorer()).detect(answers))

    assert len(conflicts) == 1
    assert conflicts[0].contradiction_id == "X001"
    assert {conflicts[0].claim_a_id, conflicts[0].claim_b_id} == {"C1", "C2"}
    assert conflicts[0].score == 0.95


def test_detector_does_not_flag_unrelated_or_same_polarity_claims():
    answers = [
        _answer("q1", "C1", "A controller may process personal data.", Assertion("controller", "may_process", "personal data")),
        _answer("q2", "C2", "A processor may process personal data.", Assertion("processor", "may_process", "personal data")),
    ]

    assert asyncio.run(ContradictionDetector(ExplicitNegationScorer()).detect(answers)) == []


def test_nli_scorer_uses_the_contradiction_probability_from_three_logits():
    class FakeCrossEncoder:
        def predict(self, pairs):
            assert pairs == [("A claim.", "Another claim.")]
            return [[2.0, 0.0, 0.0]]

    scorer = NLIContradictionScorer(_model=FakeCrossEncoder())
    scores = scorer.score([
        ContradictionCandidate("C1", "A claim.", (), "C2", "Another claim.", (), ("s", "p"))
    ])

    assert 0.78 < scores[0] < 0.79
