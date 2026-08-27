from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from hybrid_chunker import chunk_documents


# =====================================================================
# Helpers
# =====================================================================

def _make_fake_chunk(text):
    return SimpleNamespace(text=text)


def _make_fake_document():
    return object()


# =====================================================================
# Chunking
# =====================================================================

def test_chunk_documents_returns_chunks(tmp_path):
    document_path = tmp_path / "simple.md"
    document_path.write_text(
        "# Simple Document\n\nTest content.",
        encoding="utf-8",
    )

    fake_chunks = [
        _make_fake_chunk("First chunk"),
        _make_fake_chunk("Second chunk"),
    ]

    fake_chunker = MagicMock()
    fake_chunker.chunk.return_value = iter(fake_chunks)

    fake_converter = MagicMock()
    fake_converter.convert.return_value.document = (
        _make_fake_document()
    )

    with patch(
        "hybrid_chunker.AutoTokenizer.from_pretrained"
    ) as mock_tokenizer, patch(
        "hybrid_chunker.HuggingFaceTokenizer"
    ) as mock_hf_tokenizer, patch(
        "hybrid_chunker.HybridChunker",
        return_value=fake_chunker,
    ), patch(
        "hybrid_chunker.DocumentConverter",
        return_value=fake_converter,
    ):

        result = chunk_documents(tmp_path)

    assert len(result) == 2
    assert result[0]["content"] == fake_chunks[0]
    assert result[1]["content"] == fake_chunks[1]


# =====================================================================
# Document IDs
# =====================================================================

def test_chunk_documents_assigns_document_id(tmp_path):
    document_path = tmp_path / "simple.md"
    document_path.write_text(
        "# Simple Document",
        encoding="utf-8",
    )

    fake_chunker = MagicMock()
    fake_chunker.chunk.return_value = iter(
        [_make_fake_chunk("Test chunk")]
    )

    fake_converter = MagicMock()
    fake_converter.convert.return_value.document = (
        _make_fake_document()
    )

    with patch(
        "hybrid_chunker.AutoTokenizer.from_pretrained"
    ), patch(
        "hybrid_chunker.HuggingFaceTokenizer"
    ), patch(
        "hybrid_chunker.HybridChunker",
        return_value=fake_chunker,
    ), patch(
        "hybrid_chunker.DocumentConverter",
        return_value=fake_converter,
    ):

        result = chunk_documents(tmp_path)

    assert result[0]["doc_id"] == "simple"


# =====================================================================
# Chunk IDs
# =====================================================================

def test_chunk_documents_generates_sequential_chunk_ids(
    tmp_path,
):
    document_path = tmp_path / "simple.md"
    document_path.write_text(
        "# Simple Document",
        encoding="utf-8",
    )

    fake_chunker = MagicMock()
    fake_chunker.chunk.return_value = iter(
        [
            _make_fake_chunk("Chunk one"),
            _make_fake_chunk("Chunk two"),
            _make_fake_chunk("Chunk three"),
        ]
    )

    fake_converter = MagicMock()
    fake_converter.convert.return_value.document = (
        _make_fake_document()
    )

    with patch(
        "hybrid_chunker.AutoTokenizer.from_pretrained"
    ), patch(
        "hybrid_chunker.HuggingFaceTokenizer"
    ), patch(
        "hybrid_chunker.HybridChunker",
        return_value=fake_chunker,
    ), patch(
        "hybrid_chunker.DocumentConverter",
        return_value=fake_converter,
    ):

        result = chunk_documents(tmp_path)

    assert [
        chunk["chunk_id"]
        for chunk in result
    ] == [
        "chunk_1",
        "chunk_2",
        "chunk_3",
    ]


# =====================================================================
# Parallel processing
# =====================================================================

def test_chunk_documents_processes_multiple_documents(
    tmp_path,
):
    first = tmp_path / "first.md"
    second = tmp_path / "second.md"

    first.write_text("# First", encoding="utf-8")
    second.write_text("# Second", encoding="utf-8")

    fake_chunker = MagicMock()
    fake_chunker.chunk.side_effect = [
        iter([_make_fake_chunk("First content")]),
        iter([_make_fake_chunk("Second content")]),
    ]

    fake_converter = MagicMock()
    fake_converter.convert.return_value.document = (
        _make_fake_document()
    )

    with patch(
        "hybrid_chunker.AutoTokenizer.from_pretrained"
    ), patch(
        "hybrid_chunker.HuggingFaceTokenizer"
    ), patch(
        "hybrid_chunker.HybridChunker",
        return_value=fake_chunker,
    ), patch(
        "hybrid_chunker.DocumentConverter",
        return_value=fake_converter,
    ):

        result = chunk_documents(tmp_path)

    assert len(result) == 2

    assert result[0]["doc_id"] == "first"
    assert result[1]["doc_id"] == "second"


# =====================================================================
# Handling subdirectories
# =====================================================================

def test_chunk_documents_ignores_subdirectories(tmp_path):
    document_path = tmp_path / "simple.md"
    document_path.write_text(
        "# Simple Document",
        encoding="utf-8",
    )

    ignored_dir = tmp_path / "ignored"
    ignored_dir.mkdir()

    fake_chunker = MagicMock()
    fake_chunker.chunk.return_value = iter(
        [_make_fake_chunk("Test chunk")]
    )

    fake_converter = MagicMock()
    fake_converter.convert.return_value.document = (
        _make_fake_document()
    )

    with patch(
        "hybrid_chunker.AutoTokenizer.from_pretrained"
    ), patch(
        "hybrid_chunker.HuggingFaceTokenizer"
    ), patch(
        "hybrid_chunker.HybridChunker",
        return_value=fake_chunker,
    ), patch(
        "hybrid_chunker.DocumentConverter",
        return_value=fake_converter,
    ):

        result = chunk_documents(tmp_path)

    assert len(result) == 1
    assert result[0]["doc_id"] == "simple"

    fake_converter.convert.assert_called_once()


# =====================================================================
# Chunker configuration
# =====================================================================

def test_chunk_documents_uses_configured_tokenizer_and_chunker(
    tmp_path,
):
    document_path = tmp_path / "simple.md"
    document_path.write_text(
        "# Simple Document",
        encoding="utf-8",
    )

    fake_tokenizer = object()
    fake_hf_tokenizer = object()

    fake_chunker = MagicMock()
    fake_chunker.chunk.return_value = iter([])

    fake_converter = MagicMock()
    fake_converter.convert.return_value.document = (
        _make_fake_document()
    )

    with patch(
        "hybrid_chunker.AutoTokenizer.from_pretrained",
        return_value=fake_tokenizer,
    ) as mock_auto_tokenizer, patch(
        "hybrid_chunker.HuggingFaceTokenizer",
        return_value=fake_hf_tokenizer,
    ) as mock_hf, patch(
        "hybrid_chunker.HybridChunker",
        return_value=fake_chunker,
    ) as mock_hybrid, patch(
        "hybrid_chunker.DocumentConverter",
        return_value=fake_converter,
    ):

        chunk_documents(tmp_path)

    mock_auto_tokenizer.assert_called_once_with(
        "nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16"
    )

    mock_hf.assert_called_once_with(
        tokenizer=fake_tokenizer,
        max_tokens=1024,
    )

    mock_hybrid.assert_called_once_with(
        tokenizer=fake_hf_tokenizer,
        merge_peers=True,
    )


# =====================================================================
# Helpers
# =====================================================================