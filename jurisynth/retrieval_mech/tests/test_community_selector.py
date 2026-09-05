from jurisynth.retrieval_mech.community_selector import CommunitySelector
from jurisynth.retrieval_mech.community_hierarchy import CommunityHierarchy, CommunityNode
from jurisynth.retrieval_mech.er_matcher import ERMatch, ERMatchResult


def _match(concept_id, community_ids, similarity):
    return ERMatch(concept_id, concept_id, f"https://example.test/{concept_id}", concept_id, similarity, community_ids)


def test_selector_rewards_coverage_without_discarding_similarity():
    matches = ERMatchResult(
        entity_matches=(
            _match("c1", ("community_a",), 0.95),
            _match("c1", ("community_b",), 0.70),
            _match("c2", ("community_b",), 0.70),
        ),
        relation_matches=(),
    )

    selected = CommunitySelector(top_n=2).select(matches)

    assert [item.community_id for item in selected] == ["community_b", "community_a"]
    assert selected[0].supporting_concept_ids == ("c1", "c2")
    assert selected[0].concept_coverage == 1.0


def test_selector_returns_no_communities_when_matches_have_no_membership():
    matches = ERMatchResult((_match("c1", (), 0.9),), ())

    assert CommunitySelector().select(matches) == []


def test_selector_applies_bounded_novelty_only_after_relevance_gate():
    hierarchy = CommunityHierarchy(
        {
            "near": CommunityNode("near", 0, "parent"),
            "far": CommunityNode("far", 0, "root"),
            "parent": CommunityNode("parent", 1, "root", child_ids=("near",)),
            "root": CommunityNode("root", 2, child_ids=("parent", "far")),
        },
        "fixture",
    )
    matches = ERMatchResult(
        entity_matches=(
            _match("c1", ("near",), 0.95),
            _match("c2", ("near",), 0.90),
            _match("c1", ("far",), 0.76),
            _match("c2", ("far",), 0.75),
            _match("c1", ("noise",), 0.49),
        ),
        relation_matches=(),
    )

    selected = CommunitySelector(top_n=2, hierarchy=hierarchy).select(matches)

    assert [item.community_id for item in selected] == ["near", "far"]
    assert selected[0].dispersion_bonus == 0.0
    assert selected[1].dispersion_bonus == 0.75
    assert "noise" not in [item.community_id for item in selected]
