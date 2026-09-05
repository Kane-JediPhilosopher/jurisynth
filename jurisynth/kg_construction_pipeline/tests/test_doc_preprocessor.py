import base64
import json
from pathlib import Path

import faiss
import numpy as np
import pytest
from lxml import html

import doc_preprocessor as dp


# =============================================================================
# Fixtures / test utilities
# =============================================================================


class FakeEmbeddingModel:
    """
    Deterministic embedding model suitable for testing the FAISS pipeline.

    Texts are mapped to small vectors based on recognizable keywords.
    """

    def encode(
        self,
        texts,
        batch_size=128,
        normalize_embeddings=True,
        show_progress_bar=False,
    ):
        vectors = []

        for text in texts:
            text = text.lower()

            if "france" in text:
                vector = np.array([1.0, 0.0, 0.0], dtype=np.float32)
            elif "germany" in text:
                vector = np.array([0.0, 1.0, 0.0], dtype=np.float32)
            elif "installation" in text or "value" in text:
                vector = np.array([0.0, 0.0, 1.0], dtype=np.float32)
            elif "country" in text:
                vector = np.array([1.0, 0.0, 0.0], dtype=np.float32)
            elif "population" in text:
                vector = np.array([0.0, 1.0, 0.0], dtype=np.float32)
            else:
                vector = np.array([1.0, 1.0, 1.0], dtype=np.float32)

            if normalize_embeddings:
                norm = np.linalg.norm(vector)
                vector = vector / norm

            vectors.append(vector)

        return np.asarray(vectors, dtype=np.float32)


class RecordingEmbeddingModel(FakeEmbeddingModel):
    """Captures encode calls to verify memory-bounded row indexing."""

    def __init__(self):
        self.calls = []

    def encode(self, texts, **kwargs):
        self.calls.append(list(texts))
        return super().encode(texts, **kwargs)


@pytest.fixture
def embed_model():
    return FakeEmbeddingModel()


@pytest.fixture
def simple_oj_table():
    return html.fromstring(
        """
        <table class="oj-table">
            <tr>
                <td><p class="oj-tbl-hdr">Country</p></td>
                <td><p class="oj-tbl-hdr">Population</p></td>
            </tr>
            <tr>
                <td>France</td>
                <td>68 million</td>
            </tr>
            <tr>
                <td>Germany</td>
                <td>84 million</td>
            </tr>
        </table>
        """
    )


# =============================================================================
# Core semantic-table extraction
# =============================================================================


def test_extract_oj_table_extracts_headers_and_data(simple_oj_table):
    result = dp.extract_oj_table(
        simple_oj_table,
        doc_id="doc1",
        table_id="table_1",
        context="Population statistics",
    )

    assert result["doc_id"] == "doc1"
    assert result["table_id"] == "table_1"
    assert result["context"] == "Population statistics"

    assert result["header"] == [
        "Country",
        "Population",
    ]

    assert result["data"] == [
        ["France", "68 million"],
        ["Germany", "84 million"],
    ]

    assert result["parent_table_id"] is None
    assert result["children"] == []


def test_extract_oj_table_supports_multilevel_headers():
    table = html.fromstring(
        """
        <table class="oj-table">
            <tr>
                <td rowspan="2">
                    <p class="oj-tbl-hdr">Country</p>
                </td>
                <td colspan="2">
                    <p class="oj-tbl-hdr">Area of applicability</p>
                </td>
            </tr>
            <tr>
                <td><p class="oj-tbl-hdr">Code</p></td>
                <td><p class="oj-tbl-hdr">Value</p></td>
            </tr>
            <tr>
                <td>France</td>
                <td>FR</td>
                <td>42</td>
            </tr>
        </table>
        """
    )

    result = dp.extract_oj_table(
        table,
        doc_id="doc1",
        table_id="table_1",
    )

    assert result["header"] == [
        "Country",
        "Area of applicability | Code",
        "Area of applicability | Value",
    ]

    assert result["data"] == [
        ["France", "FR", "42"],
    ]


def test_extract_oj_table_supports_th_fallback():
    table = html.fromstring(
        """
        <table class="oj-table">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>A</td>
                    <td>10</td>
                </tr>
            </tbody>
        </table>
        """
    )

    result = dp.extract_oj_table(
        table,
        doc_id="doc1",
        table_id="table_1",
    )

    assert result["header"] == ["Name", "Value"]
    assert result["data"] == [["A", "10"]]


def test_extract_oj_table_handles_colspan_in_data_rows():
    table = html.fromstring(
        """
        <table class="oj-table">
            <tr>
                <td><p class="oj-tbl-hdr">Type</p></td>
                <td><p class="oj-tbl-hdr">Description</p></td>
                <td><p class="oj-tbl-hdr">Status</p></td>
            </tr>
            <tr>
                <td>A</td>
                <td colspan="2">Combined information</td>
            </tr>
        </table>
        """
    )

    result = dp.extract_oj_table(
        table,
        doc_id="doc1",
        table_id="table_1",
    )

    assert result["data"] == [
        ["A", "Combined information", "Combined information"],
    ]


def test_headerless_oj_table_is_preserved_as_headerless():
    table = html.fromstring(
        """
        <table class="oj-table">
            <tr>
                <td>A</td>
                <td>B</td>
            </tr>
        </table>
        """
    )

    result = dp.extract_oj_table(
        table,
        doc_id="doc1",
        table_id="table_1",
    )

    assert result["header"] is None
    assert result["data"] == [["A", "B"]]


# =============================================================================
# Document-level preprocessing
# =============================================================================


def test_preprocess_extracts_oj_table_and_removes_it_from_document():
    document = html.fromstring(
        """
        <html>
            <body>
                <p>Before table</p>

                <table class="oj-table">
                    <tr>
                        <td><p class="oj-tbl-hdr">Country</p></td>
                        <td><p class="oj-tbl-hdr">Value</p></td>
                    </tr>
                    <tr>
                        <td>France</td>
                        <td>42</td>
                    </tr>
                </table>

                <p>After table</p>
            </body>
        </html>
        """
    )

    tables = dp.preprocess_docs(
        document,
        doc_id="doc1",
    )

    assert len(tables) == 1
    assert tables[0]["table_id"] == "table_1"
    assert tables[0]["data"] == [["France", "42"]]

    remaining_tables = document.xpath("//table")
    assert remaining_tables == []

    text = " ".join(document.itertext())
    assert "Before table" in text
    assert "After table" in text


def test_non_oj_table_is_linearized_and_not_extracted():
    document = html.fromstring(
        """
        <html>
            <body>
                <p>Introduction</p>

                <table>
                    <tr>
                        <td>First column</td>
                        <td>Second column</td>
                    </tr>
                    <tr>
                        <td>Third column</td>
                        <td>Fourth column</td>
                    </tr>
                </table>

                <p>Conclusion</p>
            </body>
        </html>
        """
    )

    tables = dp.preprocess_docs(
        document,
        doc_id="doc1",
    )

    assert tables == []
    assert document.xpath("//table") == []

    text = " ".join(document.itertext())

    assert "First column" in text
    assert "Second column" in text
    assert "Third column" in text
    assert "Fourth column" in text
    assert "Introduction" in text
    assert "Conclusion" in text


def test_nested_oj_tables_are_extracted_independently_and_linked():
    document = html.fromstring(
        """
        <html>
            <body>
                <table class="oj-table">
                    <tr>
                        <td>
                            <p class="oj-tbl-hdr">Outer</p>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            Parent content

                            <table class="oj-table">
                                <tr>
                                    <td><p class="oj-tbl-hdr">Inner</p></td>
                                </tr>
                                <tr>
                                    <td>Nested value</td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        """
    )

    tables = dp.preprocess_docs(
        document,
        doc_id="doc1",
    )

    assert len(tables) == 2

    outer, inner = tables

    assert outer["table_id"] == "table_1"
    assert outer["parent_table_id"] is None

    assert inner["table_id"] == "table_2"
    assert inner["parent_table_id"] == "table_1"
    assert inner["parent_row"] == 1
    assert inner["parent_cell"] == 0

    assert inner["header"] == ["Inner"]
    assert inner["data"] == [["Nested value"]]

    assert document.xpath("//table") == []


def test_non_oj_table_containing_oj_table_preserves_oj_extraction():
    document = html.fromstring(
        """
        <html>
            <body>
                <table>
                    <tr>
                        <td>Layout content</td>
                    </tr>
                    <tr>
                        <td>
                            <table class="oj-table">
                                <tr>
                                    <td><p class="oj-tbl-hdr">Code</p></td>
                                </tr>
                                <tr>
                                    <td>ABC</td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        """
    )

    tables = dp.preprocess_docs(
        document,
        doc_id="doc1",
    )

    assert len(tables) == 1
    assert tables[0]["header"] == ["Code"]
    assert tables[0]["data"] == [["ABC"]]

    assert document.xpath("//table") == []

    text = " ".join(document.itertext())
    assert "Layout content" in text


# =============================================================================
# Table descriptions / retrieval representations
# =============================================================================


def test_build_table_description_respects_information_priority():
    table = {
        "title": "Population by country",
        "header": ["Country", "Population"],
        "data": [
            ["France", "68 million"],
            ["Germany", "84 million"],
            ["Italy", "59 million"],
        ],
        "context": "European demographic statistics",
    }

    description = dp.build_table_description(table)

    assert description.startswith("Population by country")
    assert "Country | Population" in description
    assert "France | 68 million" in description
    assert "Germany | 84 million" in description
    assert "Italy | 59 million" in description
    assert "European demographic statistics" in description


def test_build_row_retrieval_text_prefixes_cells_with_headers():
    row = ["France", "68 million"]

    result = dp.build_row_retrieval_text(
        row,
        ["Country", "Population"],
    )

    assert result == (
        "Country: France | Population: 68 million"
    )


def test_build_row_retrieval_units_preserves_row_ids_and_table_identity():
    tables = [
        {
            "doc_id": "doc1",
            "table_id": "table_1",
            "header": ["Country", "Population"],
            "data": [
                ["France", "68 million"],
                ["Germany", "84 million"],
            ],
        }
    ]

    units = dp.build_row_retrieval_units(tables)

    assert ("doc1", "table_1") in units

    payload = units[("doc1", "table_1")]

    assert payload["rows"] == [
        "Country: France | Population: 68 million",
        "Country: Germany | Population: 84 million",
    ]

    assert payload["metadata"] == [
        {
            "doc_id": "doc1",
            "table_id": "table_1",
            "row_id": 0,
            "type": "row",
        },
        {
            "doc_id": "doc1",
            "table_id": "table_1",
            "row_id": 1,
            "type": "row",
        },
    ]


# =============================================================================
# Persistence
# =============================================================================


def test_store_table_persists_structured_source_of_truth(tmp_path):
    table = {
        "doc_id": "doc1",
        "table_id": "table_1",
        "parent_table_id": None,
        "description": "ignored description",
        "context": "Population statistics",
        "header": ["Country", "Population"],
        "data": [
            ["France", "68 million"],
        ],
        "children": [],
    }

    path = dp.store_table(
        table,
        tmp_path,
    )

    assert path.exists()
    assert path.name == "doc1_table_1.json"

    stored = json.loads(
        path.read_text(encoding="utf-8")
    )

    assert stored == {
        "doc_id": "doc1",
        "table_id": "table_1",
        "context": "Population statistics",
        "description": "ignored description",
        "header": ["Country", "Population"],
        "data": [["France", "68 million"]],
    }


# =============================================================================
# Image processing
# =============================================================================


def test_extract_images_persists_embedded_image_and_removes_img(tmp_path):
    image_bytes = b"fake-image-data"
    encoded = base64.b64encode(image_bytes).decode()

    root = html.fromstring(
        f"""
        <html>
            <body>
                <p>Before</p>
                <img
                    src="data:image/png;base64,{encoded}"
                    alt="Test image"
                />
                <p>After</p>
            </body>
        </html>
        """
    )

    metadata = dp.extract_images(
        root,
        tmp_path,
        "doc1",
    )

    assert len(metadata) == 1

    item = metadata[0]

    assert item["status"] == "success"
    assert item["source_type"] == "embedded"
    assert item["alt"] == "Test image"
    assert item["mime_type"] == "image/png"

    image_path = tmp_path / item["filename"]

    assert image_path.exists()
    assert image_path.read_bytes() == image_bytes

    assert root.xpath("//img") == []


def test_extract_images_removes_failed_images_and_records_failure(tmp_path):
    root = html.fromstring(
        """
        <html>
            <body>
                <img src="unsupported-source" alt="Broken" />
            </body>
        </html>
        """
    )

    metadata = dp.extract_images(
        root,
        tmp_path,
        "doc1",
    )

    assert len(metadata) == 1
    assert metadata[0]["status"] == "failed"
    assert "error" in metadata[0]
    assert metadata[0]["alt"] == "Broken"

    assert root.xpath("//img") == []


def test_persist_image_metadata_writes_json(tmp_path):
    metadata = [
        {
            "status": "success",
            "source_type": "embedded",
            "filename": "doc1_image_001.png",
        }
    ]

    output_path = tmp_path / "images" / "doc1.json"

    dp.persist_image_metadata(
        metadata,
        output_path,
    )

    assert json.loads(
        output_path.read_text(encoding="utf-8")
    ) == metadata


# =============================================================================
# Hierarchical FAISS indexing
# =============================================================================


def test_build_table_index_creates_table_and_row_indices(embed_model):
    tables = [
        {
            "doc_id": "doc1",
            "table_id": "table_1",
            "context": "Country statistics",
            "header": ["Country", "Population"],
            "data": [
                ["France", "68 million"],
                ["Germany", "84 million"],
            ],
        },
        {
            "doc_id": "doc1",
            "table_id": "table_2",
            "context": "Installation information",
            "header": ["Installation", "Value"],
            "data": [
                ["A", "100"],
            ],
        },
    ]

    index = dp.build_table_index(
        tables,
        embed_model,
        batch_size=2,
    )

    assert index["table_index"] is not None
    assert index["table_index"].ntotal == 2
    assert len(index["table_metadata"]) == 2

    assert set(index["row_indices"]) == {
        ("doc1", "table_1"),
        ("doc1", "table_2"),
    }

    assert index["row_indices"][
        ("doc1", "table_1")
    ].ntotal == 2

    assert index["row_indices"][
        ("doc1", "table_2")
    ].ntotal == 1

    assert len(
        index["row_metadata"][("doc1", "table_1")]
    ) == 2


def test_build_table_index_embeds_rows_per_table():
    model = RecordingEmbeddingModel()
    tables = [
        {
            "doc_id": "doc1",
            "table_id": "one",
            "context": "Country statistics",
            "header": ["Country"],
            "data": [["France"], ["Germany"]],
        },
        {
            "doc_id": "doc1",
            "table_id": "two",
            "context": "Installation information",
            "header": ["Value"],
            "data": [["A"], ["100"]],
        },
    ]

    result = dp.build_table_index(tables, model, batch_size=2)

    assert [len(call) for call in model.calls] == [2, 2, 2]
    assert sum(index.ntotal for index in result["row_indices"].values()) == 4


def test_build_table_index_empty_tables_returns_empty_structure(
    embed_model,
):
    result = dp.build_table_index(
        [],
        embed_model,
    )

    assert result["table_index"] is None
    assert result["table_metadata"] == []
    assert result["row_indices"] == {}
    assert result["row_metadata"] == {}


def test_build_table_index_skips_tables_without_retrieval_text(
    embed_model,
):
    tables = [
        {
            "doc_id": "doc1",
            "table_id": "empty",
            "context": None,
            "header": None,
            "data": [["value"]],
        },
        {
            "doc_id": "doc1",
            "table_id": "valid",
            "context": "Country statistics",
            "header": ["Country"],
            "data": [["France"]],
        },
    ]

    result = dp.build_table_index(
        tables,
        embed_model,
    )

    assert result["table_index"].ntotal == 1
    assert result["table_metadata"] == [
        {
            "doc_id": "doc1",
            "table_id": "valid",
            "type": "table",
            "description": None,
        }
    ]

    assert ("doc1", "valid") in result["row_indices"]
    assert ("doc1", "empty") not in result["row_indices"]


# =============================================================================
# Hierarchical retrieval
# =============================================================================


def test_search_table_rows_performs_table_then_row_retrieval(
    embed_model,
):
    tables = [
        {
            "doc_id": "doc1",
            "table_id": "table_1",
            "context": "Country statistics",
            "header": ["Country", "Population"],
            "data": [
                ["France", "68 million"],
                ["Germany", "84 million"],
            ],
        },
        {
            "doc_id": "doc1",
            "table_id": "table_2",
            "context": "Installation information",
            "header": ["Installation", "Value"],
            "data": [
                ["A", "100"],
            ],
        },
    ]

    retrieval_index = dp.build_table_index(
        tables,
        embed_model,
    )

    results = dp.search_table_rows(
        "France population",
        embed_model,
        retrieval_index,
        table_top_k=1,
        row_top_k=2,
    )

    assert results
    assert results[0]["doc_id"] == "doc1"
    assert results[0]["table_id"] == "table_1"
    assert results[0]["row_id"] == 0

    assert "table_score" in results[0]
    assert "row_score" in results[0]
    assert "combined_score" in results[0]

    assert results[0]["combined_score"] == pytest.approx(
        results[0]["table_score"]
        * results[0]["row_score"]
    )


def test_search_table_rows_returns_empty_for_empty_index(
    embed_model,
):
    retrieval_index = {
        "table_index": None,
        "table_metadata": [],
        "row_indices": {},
        "row_metadata": {},
    }

    assert dp.search_table_rows(
        "anything",
        embed_model,
        retrieval_index,
    ) == []


def test_search_table_rows_respects_top_k(embed_model):
    tables = [
        {
            "doc_id": "doc1",
            "table_id": "table_1",
            "context": "Country statistics",
            "header": ["Country"],
            "data": [
                ["France"],
                ["Germany"],
                ["Italy"],
            ],
        }
    ]

    retrieval_index = dp.build_table_index(
        tables,
        embed_model,
    )

    results = dp.search_table_rows(
        "France",
        embed_model,
        retrieval_index,
        table_top_k=1,
        row_top_k=1,
    )

    assert len(results) == 1


# =============================================================================
# Exact structured retrieval
# =============================================================================


def test_load_table_json_and_get_retrieved_row(tmp_path):
    table_store = tmp_path / "table_store"
    table_store.mkdir()

    table = {
        "doc_id": "doc1",
        "table_id": "table_1",
        "context": "Population",
        "header": ["Country", "Population"],
        "data": [
            ["France", "68 million"],
            ["Germany", "84 million"],
        ],
    }

    path = (
        table_store
        / "doc1_table_1.json"
    )

    path.write_text(
        json.dumps(table),
        encoding="utf-8",
    )

    result = {
        "doc_id": "doc1",
        "table_id": "table_1",
        "row_id": 1,
    }

    loaded = dp.load_table_json(
        result,
        table_store,
    )

    assert loaded == table

    retrieved = dp.get_retrieved_row(
        result,
        table_store,
    )

    assert retrieved == {
        "table": table,
        "row_id": 1,
        "row": ["Germany", "84 million"],
    }


def test_get_retrieved_row_rejects_invalid_row_id(tmp_path):
    table_store = tmp_path / "table_store"
    table_store.mkdir()

    (table_store / "doc1_table_1.json").write_text(
        json.dumps(
            {
                "doc_id": "doc1",
                "table_id": "table_1",
                "data": [["A"]],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(IndexError):
        dp.get_retrieved_row(
            {
                "doc_id": "doc1",
                "table_id": "table_1",
                "row_id": 99,
            },
            table_store,
        )


# =============================================================================
# End-to-end single-document extraction
# =============================================================================


def test_extract_only_runs_complete_document_pipeline(tmp_path):
    input_path = tmp_path / "doc1.html"

    input_path.write_text(
        """
        <html>
            <body>
                <p>Document text.</p>

                <table class="oj-table">
                    <tr>
                        <td><p class="oj-tbl-hdr">Country</p></td>
                        <td><p class="oj-tbl-hdr">Value</p></td>
                    </tr>
                    <tr>
                        <td>France</td>
                        <td>42</td>
                    </tr>
                </table>

                <table>
                    <tr>
                        <td>Layout text</td>
                        <td>More layout text</td>
                    </tr>
                </table>

                <img
                    src="data:image/png;base64,ZmFrZQ=="
                    alt="Example"
                />
            </body>
        </html>
        """,
        encoding="utf-8",
    )

    table_store = tmp_path / "tables"
    image_store = tmp_path / "images"
    processed_dir = tmp_path / "processed"

    result = dp.extract_only(
        input_path,
        "doc1",
        table_store=table_store,
        image_store=image_store,
        processed_dir=processed_dir,
    )

    assert result["doc_id"] == "doc1"
    assert result["status"] if "status" in result else True

    assert result["diagnostics"] == {
        "semantic_tables": 1,
        "semantic_rows": 1,
        "headerless_semantic_tables": 0,
        "nested_semantic_tables": 0,
    }

    assert len(result["tables"]) == 1

    assert (
        table_store / "doc1_table_1.json"
    ).exists()

    assert (
        image_store / "doc1.json"
    ).exists()

    processed_path = Path(
        result["processed_path"]
    )

    assert processed_path.exists()

    processed_html = processed_path.read_text(
        encoding="utf-8"
    )

    assert "<table" not in processed_html
    assert "<img" not in processed_html
    assert "Document text." in processed_html
    assert "Layout text" in processed_html


# =============================================================================
# Batch execution
# =============================================================================


def test_run_batch_returns_successful_document_results(tmp_path):
    html_path = tmp_path / "doc1.html"

    html_path.write_text(
        """
        <html>
            <body>
                <table class="oj-table">
                    <tr>
                        <td><p class="oj-tbl-hdr">Country</p></td>
                    </tr>
                    <tr>
                        <td>France</td>
                    </tr>
                </table>
            </body>
        </html>
        """,
        encoding="utf-8",
    )

    results = list(
        dp.run_batch(
            [html_path],
            max_workers=1,
            table_store=str(tmp_path / "tables"),
            image_store=str(tmp_path / "images"),
            processed_dir=str(tmp_path / "processed"),
        )
    )

    assert len(results) == 1
    assert results[0]["status"] == "success"
    assert results[0]["doc_id"] == "doc1"
    assert len(results[0]["tables"]) == 1


def test_run_batch_isolates_document_failure(tmp_path):
    valid = tmp_path / "valid.html"
    valid.write_text(
        "<html><body><p>Valid</p></body></html>",
        encoding="utf-8",
    )

    missing = tmp_path / "missing.html"

    results = list(
        dp.run_batch(
            [valid, missing],
            max_workers=1,
            table_store=str(tmp_path / "tables"),
            image_store=str(tmp_path / "images"),
            processed_dir=str(tmp_path / "processed"),
        )
    )

    by_doc = {
        result["doc_id"]: result
        for result in results
    }

    assert by_doc["valid"]["status"] == "success"

    assert by_doc["missing"]["status"] == "failed"
    assert "error" in by_doc["missing"]


# =============================================================================
# End-to-end batch processing
# =============================================================================


def test_process_batches_creates_complete_batch_artifacts(
    tmp_path,
    embed_model,
):
    batch_dir = tmp_path / "batch_1"
    batch_dir.mkdir()

    (batch_dir / "doc1.html").write_text(
        """
        <html>
            <body>
                <table class="oj-table">
                    <tr>
                        <td><p class="oj-tbl-hdr">Country</p></td>
                        <td><p class="oj-tbl-hdr">Population</p></td>
                    </tr>
                    <tr>
                        <td>France</td>
                        <td>68 million</td>
                    </tr>
                </table>
            </body>
        </html>
        """,
        encoding="utf-8",
    )

    results_dir = tmp_path / "results"

    reports = dp.process_batches(
        [batch_dir],
        results_dir,
        embed_model,
        max_workers=1,
        batch_size=2,
    )

    assert len(reports) == 1

    report = reports[0]

    assert report["batch"] == "batch_1"
    assert report["status"] == "success"
    assert report["documents"] == 1

    batch_result = results_dir / "batch_1"

    assert (
        batch_result
        / "table_store"
        / "doc1_table_1.json"
    ).exists()

    assert (
        batch_result
        / "processed_docs"
        / "doc1.html"
    ).exists()

    assert (
        batch_result
        / "image_store"
        / "doc1.json"
    ).exists()

    index_dir = batch_result / "table_index"

    assert (
        index_dir / "table.index"
    ).exists()

    assert (
        index_dir / "table_metadata.json"
    ).exists()

    assert (
        index_dir / "row_metadata.json"
    ).exists()

    row_indices = list(
        (index_dir / "rows").glob("*.index")
    )

    assert len(row_indices) == 1

    table_index = faiss.read_index(
        str(index_dir / "table.index")
    )

    assert table_index.ntotal == 1


def test_process_batches_handles_missing_batch_directory(
    tmp_path,
    embed_model,
):
    missing_batch = tmp_path / "does_not_exist"

    reports = dp.process_batches(
        [missing_batch],
        tmp_path / "results",
        embed_model,
        max_workers=1,
    )

    assert len(reports) == 1
    assert reports[0]["status"] == "failed"
    assert "does not exist" in reports[0]["error"]


def test_build_table_description_supports_headerless_table():
    table = {
        "title": None,
        "header": None,
        "data": [
            ["France", "68 million"],
            ["Germany", "84 million"],
        ],
        "context": "Population statistics",
    }

    description = dp.build_table_description(table)

    assert "France | 68 million" in description
    assert "Germany | 84 million" in description
    assert "Population statistics" in description
