import os

from jurisynth.agentic_reasoner.contradiction import NLIContradictionScorer
from jurisynth.main import _configured_contradiction_detector


def test_nli_is_the_default_contradiction_scorer(monkeypatch):
    monkeypatch.delenv("JURISYNTH_CONTRADICTION_SCORER", raising=False)
    detector = _configured_contradiction_detector()
    assert isinstance(detector.scorer, NLIContradictionScorer)
    assert detector.scorer.device == "cpu"


def test_explicit_negation_is_diagnostic_only_opt_in(monkeypatch):
    monkeypatch.setenv("JURISYNTH_CONTRADICTION_SCORER", "explicit_negation")
    detector = _configured_contradiction_detector()
    assert detector.scorer.name == "explicit_negation_heuristic"
