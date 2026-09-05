import asyncio

from jurisynth.agentic_reasoner.models import Claim, LeafAnswer
from jurisynth.agentic_reasoner.qcompiler_translator import QCompilerTranslator
from jurisynth.agentic_reasoner.reasoner import AgenticReasoner
from jurisynth.agentic_reasoner.workflow import AgenticWorkflow, TaskAnalysis
from jurisynth.contracts import EvidenceBundle


class Analyzer:
    def __init__(self, route): self.route = route
    async def analyze(self, query): return TaskAnalysis(self.route, ("EU law",), {"jurisdiction": "EU"})


class Model:
    async def complete(self, **kwargs):
        return "find the Directive * what does {Directive} require"


class Retriever:
    async def retrieve_evidence(self, request): return EvidenceBundle(request.query_id, "empty")


async def generate(node, dependencies, evidence):
    return LeafAnswer(node.query_id, "insufficient_evidence", "No support.", [Claim(None, "No support.", [], "insufficient_evidence")], evidence)


def test_direct_route_creates_one_leaf_with_analysis_context():
    result = asyncio.run(AgenticWorkflow(Analyzer("direct"), AgenticReasoner(Retriever(), generate)).run("single question"))
    assert len(result.leaves) == 1
    assert result.leaves[0].constraints["jurisdiction"] == "EU"


def test_complex_route_uses_qcompiler_dependency_plan():
    result = asyncio.run(AgenticWorkflow(Analyzer("complex"), AgenticReasoner(Retriever(), generate), QCompilerTranslator(Model())).run("complex question"))
    assert [(leaf.query_id, leaf.dependency_ids) for leaf in result.leaves] == [("q001", ()), ("q002", ("q001",))]


def test_multiline_direct_question_reaches_the_leaf_unchanged():
    query = """For a citizens' initiative:\n- identify the relevant personal-data obligation;\n- state the source-supported consequence of non-compliance."""

    result = asyncio.run(AgenticWorkflow(Analyzer("direct"), AgenticReasoner(Retriever(), generate)).run(query))

    assert result.leaves[0].query == query


def test_multiline_complex_question_reaches_qcompiler_translation():
    query = """First, identify Regulation (EU) 2016/679.\n\nThen explain what it regulates.\nFinally, list one source-supported obligation."""

    result = asyncio.run(AgenticWorkflow(Analyzer("complex"), AgenticReasoner(Retriever(), generate), QCompilerTranslator(Model())).run(query))

    assert len(result.leaves) == 2
    assert result.leaves[1].dependency_ids == ("q001",)


def test_multiline_complex_consumer_query_preserves_facts_and_executes_parallel_and_dependent_leaves():
    query = """Hi, I bought a laptop from a retailer in Berlin.
The screen was defective from the beginning, and the retailer says it is not responsible.

Please identify the relevant consumer-sale remedies, assess whether that denial may be compatible with those remedies,
and list practical next steps for the buyer."""

    class ConsumerAnalyzer:
        async def analyze(self, received_query):
            assert received_query == query
            return TaskAnalysis(
                "complex",
                ("A laptop was bought from a retailer in Berlin.", "The screen was defective from the beginning.", "The retailer denied responsibility."),
                {"jurisdiction": "Germany", "topic": "consumer sale"},
            )

    class ConsumerModel:
        async def complete(self, **kwargs):
            return (
                "identify consumer-sale remedies for a defective laptop in Germany * "
                "assess the retailer denial using {identify consumer-sale remedies for a defective laptop in Germany} + "
                "identify practical next steps for a buyer of defective goods in Germany"
            )

    class CapturingRetriever:
        def __init__(self):
            self.requests = []

        async def retrieve_evidence(self, request):
            self.requests.append(request)
            return EvidenceBundle(request.query_id, "weak")

    async def answer(node, dependencies, evidence):
        text = "Available remedies include repair or replacement." if node.query_id == "q001" else f"Answer for {node.query_id}."
        return LeafAnswer(
            node.query_id,
            "insufficient_evidence",
            text,
            [Claim(None, text, [], "insufficient_evidence")],
            evidence,
        )

    retriever = CapturingRetriever()
    result = asyncio.run(
        AgenticWorkflow(
            ConsumerAnalyzer(),
            AgenticReasoner(retriever, answer),
            QCompilerTranslator(ConsumerModel()),
        ).run(query)
    )

    assert [(leaf.query_id, leaf.dependency_ids) for leaf in result.leaves] == [
        ("q001", ()),
        ("q002", ("q001",)),
        ("q003", ()),
    ]
    requests = {request.query_id: request for request in retriever.requests}
    assert set(requests) == {"q001", "q002", "q003"}
    assert requests["q001"].constraints == {"jurisdiction": "Germany", "topic": "consumer sale"}
    assert requests["q003"].contextual_facts[-1] == "The retailer denied responsibility."
    assert requests["q002"].dependency_claims[0]["claim_id"] == "q001:C1"
    assert requests["q002"].leaf_query == "assess the retailer denial using Available remedies include repair or replacement."


def test_contradiction_detector_failure_does_not_block_report_generation():
    class FailingDetector:
        async def detect(self, answers):
            raise RuntimeError("scorer unavailable")

    class Synthesizer:
        async def synthesize(self, query, answers, *, contradictions, structural_guidance):
            assert contradictions == []
            return "report"

    result = asyncio.run(
        AgenticWorkflow(
            Analyzer("direct"),
            AgenticReasoner(Retriever(), generate),
            synthesizer=Synthesizer(),
            contradiction_detector=FailingDetector(),
        ).run("single question")
    )

    assert result.report == "report"
    assert result.contradictions == ()


def test_complex_consumer_scenario_preserves_context_and_waits_for_dependency_claims():
    scenario = (
        "Hi, I'm John Kent. I bought a laptop in Berlin with a defective screen. "
        "The seller denied responsibility. What warranty rights and next steps may apply?"
    )

    class ConsumerAnalyzer:
        async def analyze(self, query):
            assert query == scenario
            return TaskAnalysis(
                "complex",
                ("John Kent bought a laptop in Berlin.", "The screen was defective.", "The seller denied responsibility."),
                {"jurisdiction": "Germany", "topic": "consumer sale"},
            )

    class ConsumerModel:
        async def complete(self, **kwargs):
            return (
                "identify EU consumer-sale remedies for defective goods in Germany * "
                "what steps may John take under {EU consumer-sale remedies for defective goods in Germany}"
            )

    class CapturingRetriever:
        def __init__(self):
            self.requests = []

        async def retrieve_evidence(self, request):
            self.requests.append(request)
            return EvidenceBundle(request.query_id, "weak")

    async def answer(node, dependencies, evidence):
        return LeafAnswer(
            node.query_id,
            "insufficient_evidence",
            "Pilot answer.",
            [Claim(None, f"Claim for {node.query_id}.", [], "insufficient_evidence")],
            evidence,
        )

    retriever = CapturingRetriever()
    result = asyncio.run(
        AgenticWorkflow(
            ConsumerAnalyzer(),
            AgenticReasoner(retriever, answer),
            QCompilerTranslator(ConsumerModel()),
        ).run(scenario)
    )

    assert [(leaf.query_id, leaf.dependency_ids) for leaf in result.leaves] == [("q001", ()), ("q002", ("q001",))]
    assert retriever.requests[0].constraints["jurisdiction"] == "Germany"
    assert retriever.requests[1].dependency_claims[0]["claim_id"] == "q001:C1"
    assert retriever.requests[1].leaf_query == "what steps may John take under Pilot answer."
    assert retriever.requests[1].dependency_substitutions == [{
        "placeholder": "{EU consumer-sale remedies for defective goods in Germany}",
        "replacement": "Pilot answer.",
    }]


def test_stream_emits_planning_and_synthesis_events_without_changing_run_api():
    workflow = AgenticWorkflow(Analyzer("direct"), AgenticReasoner(Retriever(), generate))

    async def collect():
        return [event async for event in workflow.stream("single question")]

    events = asyncio.run(collect())
    assert any(event["event"] == "TASK_ANALYZED" for event in events)
    assert events[-1] == {"event": "SYNTHESIS_READY", "report_generated": False}


def test_clarification_stops_before_analysis_or_retrieval():
    class Intake:
        async def decide(self, query, history):
            from jurisynth.agentic_reasoner.intake import IntakeDecision
            return IntakeDecision("clarify", ("A product was bought.",), {}, "Which country was the purchase made in?")

    result = asyncio.run(AgenticWorkflow(Analyzer("direct"), AgenticReasoner(Retriever(), generate), intake=Intake()).run("What are my rights?"))
    assert result.leaves == ()
    assert result.clarification_question == "Which country was the purchase made in?"
