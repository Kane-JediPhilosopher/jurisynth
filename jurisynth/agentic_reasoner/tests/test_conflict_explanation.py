import asyncio
import json

import pytest

from jurisynth.agentic_reasoner.conflict_explanation import BatchedConflictExplainer
from jurisynth.agentic_reasoner.contradiction import Contradiction
from jurisynth.agentic_reasoner.models import Claim, LeafAnswer
from jurisynth.contracts import Assertion, EvidenceBundle, EvidenceItem, SourceChunk


def fixture():
    answers = []
    for identifier, text in (("C1", "The operator must report."), ("C2", "The operator need not report.")):
        evidence = EvidenceItem("E1", Assertion("operator", "must_report", "incident"), [SourceChunk("chunk_1", "synthetic", text)])
        answers.append(LeafAnswer(identifier, "supported", text, [Claim(identifier, text, ["E1"])], EvidenceBundle(identifier, "success", [evidence])))
    conflict = Contradiction("X1", "C1", "C2", 0.99, "Original warning", ("operator", "incident"), "nli_cross_encoder")
    return answers, conflict


def test_explainer_retries_invalid_ids_and_preserves_scores_and_evidence():
    class Model:
        calls = 0
        async def complete(self, **kwargs):
            self.calls += 1
            assert kwargs["response_schema"]["name"] == "contradiction_explanations"
            payload = json.loads(kwargs["user"])
            assert payload["conflicts"][0]["claim_a"]["evidence"][0]["source_chunks"][0]["document_id"] == "synthetic"
            identifier = "invented" if self.calls == 1 else "X1"
            return json.dumps({"explanations": [{"contradiction_id": identifier, "explanation": "The claims disagree about the reporting obligation."}]})
    answers, conflict = fixture()
    model = Model()
    result = asyncio.run(BatchedConflictExplainer(model).explain([conflict], answers))
    assert model.calls == 2
    assert result[0].score == conflict.score
    assert result[0].claim_a_id == "C1"
    assert result[0].explanation != conflict.explanation


@pytest.mark.parametrize("records", [[], [{"contradiction_id": "X1", "explanation": "a"}] * 2])
def test_explainer_rejects_missing_and_duplicate_ids(records):
    with pytest.raises(ValueError):
        BatchedConflictExplainer._validate(json.dumps({"explanations": records}), {"X1"})
