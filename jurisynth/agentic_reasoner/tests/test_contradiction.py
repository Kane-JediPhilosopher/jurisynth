import asyncio

import pytest

from jurisynth.agentic_reasoner.contradiction import (
    ContradictionCandidate,
    ContradictionDetector,
    ExplicitNegationScorer,
    NLIContradictionScorer,
    RetrievedAssertion,
)
from jurisynth.contracts import Assertion, EvidenceBundle, EvidenceItem, SourceChunk


def _bundle(query_id: str, *items: EvidenceItem) -> EvidenceBundle:
    return EvidenceBundle(query_id, "success", list(items))


def _item(evidence_id: str, subject: str, predicate: str, object_: str, document: str = "doc") -> EvidenceItem:
    return EvidenceItem(
        evidence_id, Assertion(subject, predicate, object_),
        [SourceChunk(f"chunk-{evidence_id}", document, f"source for {evidence_id}")],
    )


def _assertion(identifier: str, text: str) -> RetrievedAssertion:
    subject, predicate, object_ = text.split(" ", 2)
    return RetrievedAssertion(identifier, subject, predicate, object_, text, (identifier,), ("q1",), ())


def _candidate(index: int = 1) -> ContradictionCandidate:
    return ContradictionCandidate(
        _assertion(f"A{index}a", "controller may_process data"),
        _assertion(f"A{index}b", "controller may_not_process data"),
    )


def test_detector_consumes_evidence_assertions_and_does_not_require_claims():
    class FixedScorer:
        name = "nli_cross_encoder"
        model_name = "cross-encoder/nli-deberta-v3-base"
        last_metrics = {}

        def score(self, candidates):
            return [0.99] * len(candidates)

    bundles = [_bundle("q1", _item("E1", "controller", "may_process", "data")),
               _bundle("q2", _item("E2", "controller", "may_not_process", "data"))]
    detector = ContradictionDetector(FixedScorer())
    conflicts = asyncio.run(detector.detect(bundles))

    assert len(conflicts) == 1
    assert {conflicts[0].assertion_a_evidence_refs, conflicts[0].assertion_b_evidence_refs} == {("E1",), ("E2",)}
    assert detector.last_metrics["raw_retrieved_assertion_count"] == 2
    assert detector.last_metrics["unique_assertion_count"] == 2
    assert detector.last_metrics["pair_count"] == 1


def test_duplicate_assertion_across_leaves_is_deduplicated_and_merges_provenance():
    duplicate_a = _item("E1", "controller", "must_report", "incident", "doc-a")
    duplicate_b = _item("E2", "controller", "must_report", "incident", "doc-b")
    detector = ContradictionDetector(ExplicitNegationScorer())
    values = detector.collect_assertions([_bundle("q1", duplicate_a), _bundle("q2", duplicate_b)])

    assert len(values) == 1
    assert values[0].evidence_refs == ("E1", "E2")
    assert values[0].leaf_ids == ("q1", "q2")
    assert {source.document_id for source in values[0].provenance} == {"doc-a", "doc-b"}


def test_modifiers_keep_legally_distinct_assertions_separate():
    first = _item("E1", "controller", "must_report", "incident")
    second = _item("E2", "controller", "must_report", "incident")
    first.modifiers = [{"condition": "within 24 hours"}]
    second.modifiers = [{"condition": "within 72 hours"}]
    detector = ContradictionDetector(ExplicitNegationScorer())
    assert len(detector.collect_assertions([_bundle("q1", first, second)])) == 2


def test_all_unique_unordered_assertion_pairs_no_self_or_reversed_pairs():
    detector = ContradictionDetector(ExplicitNegationScorer())
    assertions = [_assertion(f"A{i}", f"s{i} p o") for i in range(3)]
    candidates = detector.candidates(assertions)
    assert len(candidates) == 3
    assert {(value.assertion_a.assertion_id, value.assertion_b.assertion_id) for value in candidates} == {
        ("A0", "A1"), ("A0", "A2"), ("A1", "A2"),
    }
    assert detector.candidates([]) == []
    assert detector.candidates(assertions[:1]) == []


def test_detector_has_no_whole_kg_or_retriever_dependency():
    detector = ContradictionDetector(ExplicitNegationScorer())
    assert not hasattr(detector, "graph")
    assert not hasattr(detector, "retriever")
    assert len(detector.collect_assertions([_bundle("q1", _item("E1", "s", "p", "o"))])) == 1


def test_zero_or_one_retrieved_assertion_skips_nli():
    class NeverCalled:
        name = "nli_cross_encoder"
        called = False

        def score(self, candidates):
            self.called = True
            return []

    scorer = NeverCalled()
    detector = ContradictionDetector(scorer)
    assert asyncio.run(detector.detect([])) == []
    assert asyncio.run(detector.detect([_bundle("q1", _item("E1", "s", "p", "o"))])) == []
    assert scorer.called is False


def test_nli_scorer_uses_contradiction_probability_and_label_mapping():
    class FakeCrossEncoder:
        def predict(self, pairs):
            return [[6.0, 0.0, 0.0], [0.0, 6.0, 0.0], [0.0, 0.0, 6.0]][:len(pairs)]

    scorer = NLIContradictionScorer(_model=FakeCrossEncoder(), batch_size=3)
    scores = scorer.score([_candidate(1), _candidate(2), _candidate(3)])
    assert scores[0] > 0.95
    assert scores[1] < 0.01
    assert scores[2] < 0.01
    assert scorer.LABELS == ("contradiction", "entailment", "neutral")


@pytest.mark.parametrize(
    ("logits", "flagged"),
    [([6.0, 0.0, 0.0], True), ([0.0, 6.0, 0.0], False), ([0.0, 0.0, 6.0], False)],
)
def test_detector_flags_contradiction_but_not_entailment_or_neutral(logits, flagged):
    class FakeCrossEncoder:
        def predict(self, pairs): return [logits for _ in pairs]

    detector = ContradictionDetector(NLIContradictionScorer(_model=FakeCrossEncoder()))
    bundles = [_bundle("q1", _item("E1", "controller", "may_process", "data")),
               _bundle("q2", _item("E2", "controller", "may_not_process", "data"))]
    assert bool(asyncio.run(detector.detect(bundles))) is flagged


def test_nli_defaults_remain_cpu_batch_32_and_512_tokens():
    scorer = NLIContradictionScorer()
    assert scorer.device == "cpu"
    assert scorer.batch_size == 32
    assert scorer.max_length == 512
    assert scorer.local_files_only is True


def test_nli_loads_once_and_scores_in_bounded_batches():
    loaded = []

    class FakeCrossEncoder:
        def __init__(self): self.calls = []
        def predict(self, pairs):
            self.calls.append(pairs)
            return [[2.0, 0.0, 0.0] for _ in pairs]

    fake = FakeCrossEncoder()

    def loader(model_name, *, device, max_length, local_files_only):
        loaded.append((model_name, device, max_length, local_files_only))
        return fake

    scorer = NLIContradictionScorer(batch_size=2, model_loader=loader)
    assert len(scorer.score([_candidate(i) for i in range(5)])) == 5
    assert len(scorer.score([_candidate(9)])) == 1
    assert scorer.load_count == 1
    assert loaded == [("cross-encoder/nli-deberta-v3-base", "cpu", 512, True)]
    assert [len(batch) for batch in fake.calls] == [2, 2, 1, 1]


def test_nli_failure_is_explicit_and_never_falls_back_to_heuristic():
    def failing_loader(*args, **kwargs):
        raise RuntimeError("local NLI model unavailable")

    with pytest.raises(RuntimeError, match="local NLI model unavailable"):
        NLIContradictionScorer(model_loader=failing_loader).score([_candidate()])


def test_explicit_negation_remains_diagnostic_only_identity():
    assert ExplicitNegationScorer().name == "explicit_negation_heuristic"
