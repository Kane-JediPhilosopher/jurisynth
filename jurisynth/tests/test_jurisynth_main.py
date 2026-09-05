from dataclasses import dataclass

from jurisynth.agentic_reasoner.models import Claim, LeafAnswer, NodeResult, NodeStatus
from jurisynth.agentic_reasoner.workflow import TaskAnalysis
from jurisynth.contracts import Assertion, EvidenceBundle, EvidenceItem, SourceChunk
from jurisynth.main import _compact_result, _load_community_guidance, _parser
from jurisynth.retrieval_mech.er_matcher import PersistedERIndices
from jurisynth.retrieval_mech.er_index_builder import ResourceRecord
from jurisynth.retrieval_mech.community_hierarchy import CommunityHierarchy, CommunityNode, write_hierarchy_artifact


def test_pilot_cli_has_safe_batch_0009_defaults():
    args = _parser().parse_args(["What obligations apply?"])

    assert args.query == "What obligations apply?"
    assert str(args.processed_batch).endswith("jurisynth\\kg_construction_pipeline\\output\\batch_0009")
    assert str(args.raw_batch).endswith("eu_legislation\\batch_0009")
    assert str(args.er_index).endswith("jurisynth\\pilot_artifacts\\batch_0009\\er_index")


def test_compact_result_excludes_full_source_text():
    @dataclass
    class Result:
        analysis: object
        leaves: tuple = ()
        node_results: dict | None = None
        report: object | None = None

    answer = LeafAnswer(
        "q1",
        "supported",
        "Answer.",
        [Claim("C1", "Claim.", ["E1"])],
        EvidenceBundle("q1", "success", [EvidenceItem("E1", Assertion("s", "p", "o"), [SourceChunk("c1", "d1", "very long source text")])]),
    )
    result = Result(TaskAnalysis("direct", (), {}), node_results={"q1": NodeResult(NodeStatus.COMPLETE, answer)})

    compact = _compact_result(result)

    assert compact["node_results"]["q1"]["answer"]["evidence_summary"]["evidence_ids"] == ["E1"]
    assert "very long source text" not in str(compact)


def test_full_output_is_only_serialized_after_the_workflow_result_is_returned():
    # `_run` returns a workflow result so both compact and full renderers receive
    # the same object shape; this prevents a dict/object integration mismatch.
    import inspect
    from jurisynth.main import _run

    assert "asdict(" not in inspect.getsource(_run)


def test_optional_community_guidance_loads_without_becoming_a_hard_requirement(tmp_path):
    indices = PersistedERIndices(None, None, [ResourceRecord("e1", "data controller")], [])
    selector, orientation = _load_community_guidance(tmp_path, indices)
    assert selector.hierarchy is None
    assert orientation is None

    write_hierarchy_artifact(
        tmp_path / "community_hierarchy.json",
        CommunityHierarchy({"c1": CommunityNode("c1", 0, member_ids=("e1",))}, "fixture"),
    )
    selector, orientation = _load_community_guidance(tmp_path, indices)

    assert selector.hierarchy is not None
    assert orientation is not None
