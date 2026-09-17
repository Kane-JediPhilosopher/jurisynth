from collections import Counter

from jurisynth.build_ai_review_packets import NLI_FAMILIES, build_nli, render_nli


def test_nli_proposals_balanced_and_document_disjoint_before_predictions():
    cases = [{'case_id': f'global_natural_{number:03d}', 'expected_chunks': [
        {'document_id': f'doc_{number}', 'chunk_id': 'chunk_1', 'full_text': 'SOURCE CONTEXT'}]}
             for _, number, *_ in NLI_FAMILIES]
    records = build_nli(cases)
    assert len(records) == 90
    assert Counter(record['proposed_label'] for record in records) == {
        'entailment': 30, 'contradiction': 30, 'neutral': 30}
    assert not ({record['source_document_id'] for record in records if record['split'] == 'development'} &
                {record['source_document_id'] for record in records if record['split'] == 'locked_test'})
    assert all(record['adjudicated_label'] is None for record in records)


def test_blinded_render_has_no_proposal_fields_or_duplicate_context():
    records = [{'pair_id': 'legal_nli_001', 'premise': 'A rule.', 'hypothesis': 'A claim.',
                'scope_assumption': 'Same scope.', 'source_document_id': 'doc', 'source_chunk_id': 'chunk',
                'source_excerpt': 'SOURCE CONTEXT', 'proposed_label': 'neutral'}]
    rendered = render_nli(records * 2)
    assert 'proposed_label' not in rendered
    assert rendered.count('SOURCE CONTEXT') == 1
