import asyncio

import pytest

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
    assert conflicts[0].claim_a_evidence_refs == ("E1",)
    assert conflicts[0].claim_b_evidence_refs == ("E1",)


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


def _candidates(count: int) -> list[ContradictionCandidate]:
    return [ContradictionCandidate(f"C{index}a", "A claim.", (), f"C{index}b", "Another claim.", (), ()) for index in range(count)]


def test_nli_loads_once_and_scores_in_bounded_batches_on_cpu():
    loaded = []

    class FakeCrossEncoder:
        def __init__(self):
            self.calls = []

        def predict(self, pairs):
            self.calls.append(pairs)
            return [[2.0, 0.0, 0.0] for _ in pairs]

    fake = FakeCrossEncoder()

    def loader(model_name, *, device, max_length, local_files_only):
        loaded.append((model_name, device, max_length, local_files_only))
        return fake

    scorer = NLIContradictionScorer(batch_size=2, model_loader=loader)
    assert len(scorer.score(_candidates(5))) == 5
    assert len(scorer.score(_candidates(1))) == 1
    assert scorer.load_count == 1
    assert loaded == [("cross-encoder/nli-deberta-v3-base", "cpu", 512, True)]
    assert [len(batch) for batch in fake.calls] == [2, 2, 1, 1]


def test_nli_label_mapping_flags_contradiction_not_entailment_or_neutral():
    class FakeCrossEncoder:
        def predict(self, pairs):
            return [[6.0, 0.0, 0.0], [0.0, 6.0, 0.0], [0.0, 0.0, 6.0]][:len(pairs)]

    scorer = NLIContradictionScorer(_model=FakeCrossEncoder(), batch_size=3)
    scores = scorer.score(_candidates(3))
    assert scores[0] > 0.95
    assert scores[1] < 0.01
    assert scores[2] < 0.01
    assert scorer.LABELS == ("contradiction", "entailment", "neutral")


def test_detector_uses_all_unique_unordered_pairs_and_skips_zero_or_one_claim():
    answers = [
        _answer("q1", "C1", "Claim one.", Assertion("s1", "p", "o")),
        _answer("q2", "C2", "Claim two.", Assertion("s2", "p", "o")),
        _answer("q3", "C3", "Claim three.", Assertion("s3", "p", "o")),
    ]
    detector = ContradictionDetector(ExplicitNegationScorer())
    candidates = detector.candidates(answers)
    assert len(candidates) == 3
    assert {(item.claim_a_id, item.claim_b_id) for item in candidates} == {("C1", "C2"), ("C1", "C3"), ("C2", "C3")}
    assert detector.candidates([]) == []
    assert detector.candidates(answers[:1]) == []


def test_nli_failure_is_explicit_and_never_falls_back_to_heuristic():
    def failing_loader(*args, **kwargs):
        raise RuntimeError("local NLI model unavailable")

    scorer = NLIContradictionScorer(model_loader=failing_loader)
    with pytest.raises(RuntimeError, match="local NLI model unavailable"):
        scorer.score(_candidates(1))

