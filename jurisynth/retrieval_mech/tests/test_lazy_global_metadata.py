import json

from jurisynth.retrieval_mech.community_hierarchy import CommunityOrientationBuilder
from jurisynth.retrieval_mech.lazy_community_metadata import (
    SQLiteCommunityHierarchy,
    SQLiteOrientationDescriptors,
    build_sqlite_community_metadata,
)
from jurisynth.retrieval_mech.lazy_er_metadata import SQLiteResourceRecords, build_sqlite_er_metadata


def test_lazy_er_metadata_preserves_vector_and_exact_label_lookup(tmp_path):
    source = tmp_path / "metadata.json"
    destination = tmp_path / "er_metadata.sqlite"
    source.write_text(json.dumps({
        "entities": [{"uri": "e1", "label": "Data_Controller", "community_ids": ["c1"]}],
        "relations": [{"uri": "r1", "label": "has duty", "community_ids": []}],
    }, indent=2), encoding="utf-8")
    assert build_sqlite_er_metadata(source, destination)["entity_records"] == 1
    records = SQLiteResourceRecords(destination, "entity")
    assert records[0].label == "Data_Controller"
    assert records.exact_matches({"data controller": "data controller"})[0][1].uri == "e1"


def test_lazy_community_metadata_supports_selector_orientation_api(tmp_path):
    hierarchy_source = tmp_path / "hierarchy.json"
    descriptor_source = tmp_path / "descriptors.json"
    destination = tmp_path / "community_metadata.sqlite"
    hierarchy_source.write_text(json.dumps({"schema_version": 1, "graph_fingerprint": "fixture", "nodes": [
        {"community_id": "c0", "level": 0, "parent_id": "c1", "child_ids": [], "member_ids": ["e1"]},
        {"community_id": "c1", "level": 1, "parent_id": None, "child_ids": ["c0"], "member_ids": []},
    ]}, indent=2), encoding="utf-8")
    descriptor_source.write_text(json.dumps({"schema_version": 1, "descriptor_version": 1, "kind": "deterministic_graph_orientation", "nodes": [
        {"community_id": "c0", "level": 0, "member_count": 1, "child_count": 0, "anchor_labels": ["controller"]},
        {"community_id": "c1", "level": 1, "member_count": 1, "child_count": 1, "anchor_labels": []},
    ]}, indent=2), encoding="utf-8")
    assert build_sqlite_community_metadata(hierarchy_source, descriptor_source, destination)["hierarchy_nodes"] == 2
    hierarchy = SQLiteCommunityHierarchy(destination)
    descriptors = SQLiteOrientationDescriptors(destination)
    assert hierarchy.lca(["c0", "c1"]) == "c1"
    orientation = CommunityOrientationBuilder(hierarchy, {}, descriptors).build(["c0"])
    assert orientation is not None and "controller" in orientation.text
