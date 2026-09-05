from jurisynth.inspect_pilot_coverage import _label_hits, _lexical_chunk_hits


def test_lexical_chunk_hits_return_bounded_context():
    chunks = [{"doc_id": "doc_1", "chunk_id": "chunk_1", "content": "A data controller processes personal data."}]

    hits = _lexical_chunk_hits("data controller", chunks, max_hits=1)

    assert hits[0]["document_id"] == "doc_1"
    assert "data controller" in hits[0]["text_excerpt"]


def test_label_hits_are_case_insensitive_and_bounded():
    records = [{"uri": "urn:one", "label": "Data Controller"}, {"uri": "urn:two", "label": "controller"}]

    hits = _label_hits("data controller", records, max_hits=1)

    assert hits == [{"uri": "urn:one", "label": "Data Controller"}]
