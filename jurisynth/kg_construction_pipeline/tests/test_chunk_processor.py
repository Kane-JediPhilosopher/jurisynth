from types import SimpleNamespace
from unittest.mock import patch

import pytest

from chunk_processor import process_chunks


# =====================================================================
# Test doubles
# =====================================================================

class FakeToken:
    def __init__(self, pos):
        self.pos_ = pos


class FakeSentence:
    def __init__(self, text, pos_tags):
        self.text = text
        self.tokens = [
            FakeToken(pos)
            for pos in pos_tags
        ]

    def __iter__(self):
        return iter(self.tokens)


class FakeDoc:
    def __init__(self, sentences):
        self.sents = sentences


class FakeNLP:
    def __init__(self, docs):
        self.docs = docs
        self.pipe_calls = []

    def pipe(self, texts, batch_size=64, n_process=2):
        texts = list(texts)

        self.pipe_calls.append(
            {
                "texts": texts,
                "batch_size": batch_size,
                "n_process": n_process,
            }
        )

        return iter(self.docs)


# =====================================================================
# Sentences with verbs
# =====================================================================

def test_process_chunks_keeps_sentences_with_verbs():
    raw_chunks = [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk_1",
            "content": SimpleNamespace(
                text="The undertaking operates."
            ),
        }
    ]

    nlp = FakeNLP(
        [
            FakeDoc(
                [
                    FakeSentence(
                        "The undertaking operates.",
                        ["DET", "NOUN", "VERB"],
                    )
                ]
            )
        ]
    )

    result = process_chunks(
        raw_chunks,
        nlp=nlp,
    )

    assert result == [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk_1",
            "content": "The undertaking operates.",
        }
    ]


# =====================================================================
# Sentences with auxiliary verbs
# =====================================================================

def test_process_chunks_keeps_sentences_with_auxiliaries():
    raw_chunks = [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk_1",
            "content": SimpleNamespace(
                text="The undertaking shall comply."
            ),
        }
    ]

    nlp = FakeNLP(
        [
            FakeDoc(
                [
                    FakeSentence(
                        "The undertaking shall comply.",
                        ["DET", "NOUN", "AUX", "VERB"],
                    )
                ]
            )
        ]
    )

    result = process_chunks(
        raw_chunks,
        nlp=nlp,
    )

    assert len(result) == 1
    assert result[0]["content"] == (
        "The undertaking shall comply."
    )


# =====================================================================
# Verbless sentences
# =====================================================================

def test_process_chunks_filters_verbless_sentences():
    raw_chunks = [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk_1",
            "content": SimpleNamespace(
                text="Article 12. The undertaking complies."
            ),
        }
    ]

    nlp = FakeNLP(
        [
            FakeDoc(
                [
                    FakeSentence(
                        "Article 12.",
                        ["NOUN", "NUM"],
                    ),
                    FakeSentence(
                        "The undertaking complies.",
                        ["DET", "NOUN", "VERB"],
                    ),
                ]
            )
        ]
    )

    result = process_chunks(
        raw_chunks,
        nlp=nlp,
    )

    assert result[0]["content"] == (
        "The undertaking complies."
    )


# =====================================================================
# Empty/whitespace-only sentences
# =====================================================================

def test_process_chunks_ignores_empty_sentences():
    raw_chunks = [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk_1",
            "content": SimpleNamespace(
                text="   The undertaking complies.   "
            ),
        }
    ]

    nlp = FakeNLP(
        [
            FakeDoc(
                [
                    FakeSentence(
                        "   ",
                        [],
                    ),
                    FakeSentence(
                        "   The undertaking complies.   ",
                        ["DET", "NOUN", "VERB"],
                    ),
                ]
            )
        ]
    )

    result = process_chunks(
        raw_chunks,
        nlp=nlp,
    )

    assert result[0]["content"] == (
        "The undertaking complies."
    )


# =====================================================================
# Whitespace between sentences
# =====================================================================

def test_process_chunks_normalizes_whitespace():
    raw_chunks = [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk_1",
            "content": SimpleNamespace(
                text="First sentence. Second sentence."
            ),
        }
    ]

    nlp = FakeNLP(
        [
            FakeDoc(
                [
                    FakeSentence(
                        "First   sentence.",
                        ["VERB"],
                    ),
                    FakeSentence(
                        "Second\nsentence.",
                        ["VERB"],
                    ),
                ]
            )
        ]
    )

    result = process_chunks(
        raw_chunks,
        nlp=nlp,
    )

    assert result[0]["content"] == (
        "First sentence. Second sentence."
    )


# =====================================================================
# Chunks with no valid sentences
# =====================================================================

def test_process_chunks_drops_chunks_with_no_valid_sentences():
    raw_chunks = [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk_1",
            "content": SimpleNamespace(
                text="Article 12. Section 3."
            ),
        }
    ]

    nlp = FakeNLP(
        [
            FakeDoc(
                [
                    FakeSentence(
                        "Article 12.",
                        ["NOUN", "NUM"],
                    ),
                    FakeSentence(
                        "Section 3.",
                        ["NOUN", "NUM"],
                    ),
                ]
            )
        ]
    )

    result = process_chunks(
        raw_chunks,
        nlp=nlp,
    )

    assert result == []


# =====================================================================
# Document/chunk ID handling
# =====================================================================

def test_process_chunks_preserves_chunk_metadata():
    raw_chunks = [
        {
            "doc_id": "legal_doc_42",
            "chunk_id": "chunk_7",
            "content": SimpleNamespace(
                text="The court decides."
            ),
        }
    ]

    nlp = FakeNLP(
        [
            FakeDoc(
                [
                    FakeSentence(
                        "The court decides.",
                        ["DET", "NOUN", "VERB"],
                    )
                ]
            )
        ]
    )

    result = process_chunks(
        raw_chunks,
        nlp=nlp,
    )

    assert result[0]["doc_id"] == "legal_doc_42"
    assert result[0]["chunk_id"] == "chunk_7"


# =====================================================================
# Batching configuration
# =====================================================================

def test_process_chunks_passes_batch_configuration():
    raw_chunks = [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk_1",
            "content": SimpleNamespace(
                text="The undertaking complies."
            ),
        }
    ]

    nlp = FakeNLP(
        [
            FakeDoc(
                [
                    FakeSentence(
                        "The undertaking complies.",
                        ["DET", "NOUN", "VERB"],
                    )
                ]
            )
        ]
    )

    process_chunks(
        raw_chunks,
        nlp=nlp,
        batch_size=16,
        n_process=1,
    )

    assert nlp.pipe_calls == [
        {
            "texts": [
                "The undertaking complies."
            ],
            "batch_size": 16,
            "n_process": 1,
        }
    ]


# =====================================================================
# SpaCy fallback
# =====================================================================

def test_process_chunks_loads_default_model_when_nlp_is_not_supplied():
    raw_chunks = [
        {
            "doc_id": "doc1",
            "chunk_id": "chunk_1",
            "content": SimpleNamespace(
                text="The undertaking complies."
            ),
        }
    ]

    fake_nlp = FakeNLP(
        [
            FakeDoc(
                [
                    FakeSentence(
                        "The undertaking complies.",
                        ["DET", "NOUN", "VERB"],
                    )
                ]
            )
        ]
    )

    with patch(
        "chunk_processor.spacy.load",
        return_value=fake_nlp,
    ) as mock_load:

        result = process_chunks(raw_chunks)

    mock_load.assert_called_once_with(
        "en_core_web_lg"
    )

    assert len(result) == 1