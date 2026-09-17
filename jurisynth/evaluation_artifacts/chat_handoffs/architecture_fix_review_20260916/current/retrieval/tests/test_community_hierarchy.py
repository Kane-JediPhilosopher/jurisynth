import json

from jurisynth.retrieval_mech.community_hierarchy import (
    CommunityHierarchy,
    CommunityNode,
    CommunityOrientationBuilder,
    load_hierarchy_artifact,
    load_orientation_descriptors,
    write_orientation_descriptors,
    write_hierarchy_artifact,
)


def _hierarchy():
    return CommunityHierarchy(
        nodes={
            "l0_a": CommunityNode("l0_a", 0, "l1_left", member_ids=("entity_a", "entity_b")),
            "l0_b": CommunityNode("l0_b", 0, "l1_left", member_ids=("entity_c",)),
            "l0_c": CommunityNode("l0_c", 0, "l1_right", member_ids=("entity_d",)),
            "l1_left": CommunityNode("l1_left", 1, "l2_root", child_ids=("l0_a", "l0_b")),
            "l1_right": CommunityNode("l1_right", 1, "l2_root", child_ids=("l0_c",)),
            "l2_root": CommunityNode("l2_root", 2, child_ids=("l1_left", "l1_right")),
        },
        graph_fingerprint="fixture-v1",
    )


def test_hierarchy_round_trips_and_calculates_lca_and_distance(tmp_path):
    source = tmp_path / "hierarchy.json"
    hierarchy = _hierarchy()
    write_hierarchy_artifact(source, hierarchy)

    loaded = load_hierarchy_artifact(source)

    assert loaded == hierarchy
    assert loaded.lca(["l0_a", "l0_b"]) == "l1_left"
    assert loaded.lca(["l0_a", "l0_c"]) == "l2_root"
    assert loaded.distance("l0_a", "l0_c") == 4


def test_orientation_is_deterministic_and_contains_no_evidence_text():
    orientation = CommunityOrientationBuilder(
        _hierarchy(),
        {"entity_a": "data controller", "entity_b": "personal data", "entity_c": "supervisory authority"},
    ).build(["l0_a", "l0_b"])

    assert orientation is not None
    assert "Community orientation only" in orientation.text
    assert "Shared hierarchy region: l1_left" in orientation.text
    assert orientation.provenance["authoritative"] is False
    assert orientation.provenance["branch_count"] == 2
    assert "source_chunks" not in orientation.text


def test_orientation_descriptors_are_deterministic_and_non_authoritative(tmp_path):
    destination = tmp_path / "descriptors.json"
    write_orientation_descriptors(destination, _hierarchy(), {"entity_a": "data controller"})

    payload = json.loads(destination.read_text(encoding="utf-8"))
    leaf = next(item for item in payload["nodes"] if item["community_id"] == "l0_a")
    assert payload["kind"] == "deterministic_graph_orientation"
    assert leaf["anchor_labels"] == ["data controller", "entity b"]
    assert leaf["authoritative"] is False

    loaded = load_orientation_descriptors(destination)
    assert loaded["l0_a"].level == 0
    assert "data controller" in loaded["l0_a"].summary
    assert loaded["l0_a"].provenance["authoritative"] is False
