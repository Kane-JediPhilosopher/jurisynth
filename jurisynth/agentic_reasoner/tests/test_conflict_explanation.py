import asyncio
import json

import pytest

from jurisynth.agentic_reasoner.conflict_explanation import BatchedConflictExplainer
from jurisynth.agentic_reasoner.contradiction import AssertionSource, Contradiction
from jurisynth.agentic_reasoner.models import Claim, LeafAnswer
from jurisynth.contracts import Assertion, EvidenceBundle, EvidenceItem, SourceChunk


def fixture():
    answers = []
    for identifier, text in (("C1", "The operator must report."), ("C2", "The operator need not report.")):
        evidence = EvidenceItem("E1", Assertion("operator", "must_report", "incident"), [SourceChunk("chunk_1", "synthetic", text)])
        answers.append(LeafAnswer(identifier, "supported", text, [Claim(identifier, text, ["E1"])], EvidenceBundle(identifier, "success", [evidence])))
    conflict = Contradiction(
        "X1", "A1", "A2", 0.99, "Original warning", "nli_cross_encoder",
        "cross-encoder/nli-deberta-v3-base",
        "operator must_report incident", ("E1",), ("C1",),
        (AssertionSource("E1", "C1", "synthetic", "chunk_1", "The operator must report."),),
        "operator need_not_report incident", ("E1",), ("C2",),
        (AssertionSource("E1", "C2", "synthetic", "chunk_1", "The operator need not report."),),
    )
    return answers, conflict


def test_explainer_retries_invalid_ids_and_preserves_scores_and_evidence():
    class Model:
        calls = 0
        async def complete(self, **kwargs):
            self.calls += 1
            assert kwargs["response_schema"]["name"] == "contradiction_explanations"
            payload = json.loads(kwargs["user"])
            assert payload["conflicts"][0]["assertion_a"]["provenance"][0]["document_id"] == "synthetic"
            identifier = "invented" if self.calls == 1 else "X1"
            return json.dumps({"explanations": [{"contradiction_id": identifier, "explanation": "The claims disagree about the reporting obligation."}]})
    answers, conflict = fixture()
    model = Model()
    result = asyncio.run(BatchedConflictExplainer(model).explain([conflict], answers))
    assert model.calls == 2
    assert result[0].score == conflict.score
    assert result[0].assertion_a_id == "A1"
    assert result[0].explanation != conflict.explanation


@pytest.mark.parametrize("records", [[], [{"contradiction_id": "X1", "explanation": "a"}] * 2])
def test_explainer_rejects_missing_and_duplicate_ids(records):
    with pytest.raises(ValueError):
        BatchedConflictExplainer._validate(json.dumps({"explanations": records}), {"X1"})
