from jurisynth.prepare_retrieval_ablation import select_development


def test_ablation_split_balances_outcomes_and_is_reproducible():
    results = []
    for index in range(60):
        results.append({'case_id': str(index), 'assertion_recalled': index < 20,
                        'subject_entity_recalled': 20 <= index < 40,
                        'object_entity_recalled': False, 'predicate_recalled': False})
    selected, strata = select_development(results)
    assert len(selected) == len(set(selected)) == 40
    assert [len(values) for values in strata.values()] == [14, 13, 13]
    assert select_development(results) == (selected, strata)
