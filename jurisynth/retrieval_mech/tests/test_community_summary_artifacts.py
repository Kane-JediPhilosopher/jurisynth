from jurisynth.retrieval_mech.community_summary import CommunitySummaryInput
from jurisynth.retrieval_mech.community_summary_artifacts import load_summary_artifacts, write_summary_artifacts


def test_persisted_community_summaries_round_trip_without_evidence_chunks(tmp_path):
    destination = tmp_path / "community_summaries.json"
    write_summary_artifacts(destination, [CommunitySummaryInput("c1", "orientation", 1, 0, {"member_count": 3})], source_graph="kg.nq")
    loaded = load_summary_artifacts(destination)
    assert loaded["c1"].summary == "orientation"
    assert loaded["c1"].provenance["member_count"] == 3
