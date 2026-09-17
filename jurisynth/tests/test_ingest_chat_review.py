import pytest
from jurisynth.ingest_chat_review import quote_match, validate_ids


def test_ordered_quotes_are_not_claimed_as_contiguous_verbatim_text():
    assert quote_match('First rule. Second rule.', 'First rule. 2. Second rule.') == 'ordered_source_fragments'
    assert quote_match('First rule. ... Last rule.', 'First rule. Middle rule. Last rule.') == 'ordered_source_fragments'
    assert quote_match('Invented rule.', 'Actual rule.') == 'not_verified'


def test_duplicate_or_missing_review_ids_are_rejected():
    with pytest.raises(ValueError):
        validate_ids([{'pair_id': 'a'}, {'pair_id': 'a'}], {'a', 'b'}, 'pair_id')
