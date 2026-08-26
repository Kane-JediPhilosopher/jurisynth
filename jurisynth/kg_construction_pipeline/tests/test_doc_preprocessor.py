from pathlib import Path

import faiss
import json
import pytest
from sentence_transformers import SentenceTransformer

from doc_preprocessor import run_batch, process_batches


# =============================================================================
# Configuration
# =============================================================================

# -------------------------------------------------------------------------
# Fixture paths
# -------------------------------------------------------------------------

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "doc_preprocessor"

NORMAL_DOC = FIXTURES_DIR / "normal.html"
SPARSE_DOC = FIXTURES_DIR / "sparse.html"
CANDIDATE_DOC = FIXTURES_DIR / "candidate.html"
HEADER_VARIANTS_DOC = FIXTURES_DIR / "header_variants.html"
HIERARCHICAL_COLUMNS_DOC = FIXTURES_DIR / "hierarchical_columns.html"
FRAGMENTED_DOC = FIXTURES_DIR / "fragmented.html"
NESTED_DOC = FIXTURES_DIR / "nested.html"
TABLE_HEAVY_DOC = FIXTURES_DIR / "table_heavy.html"
MALFORMED_DOC = FIXTURES_DIR / "malformed.html"


# -------------------------------------------------------------------------
# Embedding model
# -------------------------------------------------------------------------
# Keep this fixture session-scoped so the model is loaded only once.

@pytest.fixture(scope="session")
def embed_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


# -------------------------------------------------------------------------
# Temporary batch builder
# -------------------------------------------------------------------------

def make_batch(tmp_path, name, *documents):
    """
    Create a temporary batch directory containing the supplied fixture files.
    """
    batch_dir = tmp_path / name
    batch_dir.mkdir()

    for document in documents:
        destination = batch_dir / document.name
        destination.write_bytes(document.read_bytes())

    return batch_dir


# -------------------------------------------------------------------------
# Output helpers
# -------------------------------------------------------------------------

def batch_output_dir(results_dir, batch_name):
    return results_dir / batch_name


def assert_batch_output_structure(results_dir, batch_name):
    """
    Verify the public filesystem structure produced for a successful batch.
    """
    batch_dir = batch_output_dir(results_dir, batch_name)

    assert batch_dir.is_dir()

    assert (batch_dir / "table_store").is_dir()
    assert (batch_dir / "processed_docs").is_dir()
    assert (batch_dir / "index").is_dir()


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


# =============================================================================
# T01 — Basic successful processing
# =============================================================================

def test_basic_successful_processing(tmp_path, embed_model):
    """
    A normal document should be processed successfully and produce
    the expected persistent artifacts.
    """
    batch_dir = make_batch(
        tmp_path,
        "batch_0001",
        NORMAL_DOC,
    )

    results_dir = tmp_path / "results"

    reports = process_batches(
        [batch_dir],
        results_dir,
        embed_model,
        max_workers=1,
        batch_size=16,
    )

    assert reports

    assert_batch_output_structure(
        results_dir,
        "batch_0001",
    )

    output_dir = batch_output_dir(
        results_dir,
        "batch_0001",
    )

    assert any(
        (output_dir / "processed_docs").glob("*.html")
    )

    assert any(
        (output_dir / "table_store").glob("*.json")
    )

    assert (output_dir / "index" / "table.index").exists()
    assert (output_dir / "index" / "table_metadata.json").exists()
    assert (output_dir / "index" / "row_metadata.json").exists()


# =============================================================================
# T02 — Sparse / formatting tables rejected
# =============================================================================

def test_sparse_tables_are_not_persisted_as_semantic_tables(
    tmp_path,
    embed_model,
):
    """
    Sparse/formatting tables should not appear in semantic-table persistence.
    """
    batch_dir = make_batch(
        tmp_path,
        "batch_0001",
        SPARSE_DOC,
    )

    results_dir = tmp_path / "results"

    process_batches(
        [batch_dir],
        results_dir,
        embed_model,
        max_workers=1,
        batch_size=16,
    )

    table_store = (
        results_dir
        / "batch_0001"
        / "table_store"
    )

    # TODO:
    # Replace this with the exact expected assertion once the table-store
    # naming/layout is finalized.
    persisted_tables = list(table_store.glob("*.json"))

    # A sparse-only fixture should produce no semantic table persistence.
    assert persisted_tables == []


# =============================================================================
# T03 — Candidate-table handling
# =============================================================================

def test_candidate_table_handling(tmp_path, embed_model):
    """
    Candidate tables should follow the established extraction rules.
    """
    batch_dir = make_batch(
        tmp_path,
        "batch_0001",
        CANDIDATE_DOC,
    )

    results_dir = tmp_path / "results"

    reports = process_batches(
        [batch_dir],
        results_dir,
        embed_model,
        max_workers=1,
        batch_size=16,
    )

    assert len(reports) == 1
    assert reports[0]["documents"] == 1

    document_result = reports[0]["results"][0]
    tables = document_result["tables"]

    assert len(tables) == 1

    table = tables[0]

    assert table["header"] == [
        "Member State",
        "Population",
        "Year",
    ]

    assert table["data"] == [
        ["Alpha", "1000000", "2020"],
        ["Beta", "2000000", "2021"],
    ]


# =============================================================================
# T04 — Header handling
# =============================================================================

def test_header_handling(tmp_path, embed_model):
    """
    Explicit and inferred headers should be represented correctly,
    while a headerless table should have no header.
    """
    batch_dir = make_batch(
        tmp_path,
        "batch_0001",
        HEADER_VARIANTS_DOC,
    )

    results_dir = tmp_path / "results"

    reports = process_batches(
        [batch_dir],
        results_dir,
        embed_model,
        max_workers=1,
        batch_size=16,
    )

    assert len(reports) == 1
    assert reports[0]["documents"] == 1

    document_result = reports[0]["results"][0]
    tables = document_result["tables"]

    assert len(tables) == 3

    headers = [
        table["header"]
        for table in tables
    ]

    assert ["Country", "Population"] in headers
    assert ["Year", "Amount"] in headers

    # The exact representation of a headerless table is determined
    # by the extraction module's table schema.
    assert any(
        header is None or header == []
        for header in headers
    )


# =============================================================================
# T05 — Parent-child column concatenation
# =============================================================================

def test_parent_child_column_concatenation(
    tmp_path,
    embed_model,
):
    """
    Hierarchical parent/child columns should be concatenated according
    to the established extraction rule.
    """
    batch_dir = make_batch(
        tmp_path,
        "batch_0001",
        HIERARCHICAL_COLUMNS_DOC,
    )

    results_dir = tmp_path / "results"

    reports = process_batches(
        [batch_dir],
        results_dir,
        embed_model,
        max_workers=1,
        batch_size=16,
    )

    assert len(reports) == 1
    assert reports[0]["documents"] == 1

    document_result = reports[0]["results"][0]
    tables = document_result["tables"]

    assert len(tables) == 1

    table = tables[0]

    assert table["header"] == [
        "Country",
        "Population | Total",
        "Population | Urban",
    ]

    assert table["data"] == [
        ["Alpha", "1000", "700"],
        ["Beta", "2000", "1500"],
    ]


# =============================================================================
# T06 — Fragment merging
# =============================================================================

def test_fragment_merging(tmp_path, embed_model):
    """
    Related table fragments should be merged without losing or duplicating
    rows.
    """
    batch_dir = make_batch(
        tmp_path,
        "batch_0001",
        FRAGMENTED_DOC,
    )

    results_dir = tmp_path / "results"

    reports = process_batches(
        [batch_dir],
        results_dir,
        embed_model,
        max_workers=1,
        batch_size=16,
    )

    assert len(reports) == 1
    assert reports[0]["documents"] == 1

    document_result = reports[0]["results"][0]
    tables = document_result["tables"]

    assert len(tables) == 1

    table = tables[0]

    assert table["header"] == [
        "Item",
        "Value",
    ]

    assert table["data"] == [
        ["Alpha", "10"],
        ["Beta", "20"],
        ["Gamma", "30"],
        ["Delta", "40"],
    ]

# =============================================================================
# T07 — Nested tables
# =============================================================================

def test_nested_table_document(
    tmp_path,
    embed_model,
):
    """
    Nested-table documents should process successfully without corrupting
    the extracted semantic tables or processed HTML.
    """
    batch_dir = make_batch(
        tmp_path,
        "batch_0001",
        NESTED_DOC,
    )

    results_dir = tmp_path / "results"

    reports = process_batches(
        [batch_dir],
        results_dir,
        embed_model,
        max_workers=1,
        batch_size=16,
    )

    assert reports

    assert_batch_output_structure(
        results_dir,
        "batch_0001",
    )


# =============================================================================
# T08 — Table-heavy document
# =============================================================================

def test_table_heavy_document(
    tmp_path,
    embed_model,
):
    """
    A corpus-derived table-heavy document should complete successfully and
    produce internally consistent retrieval artifacts.
    """
    batch_dir = make_batch(
        tmp_path,
        "batch_0001",
        TABLE_HEAVY_DOC,
    )

    results_dir = tmp_path / "results"

    reports = process_batches(
        [batch_dir],
        results_dir,
        embed_model,
        max_workers=1,
        batch_size=32,
    )

    assert reports

    assert_batch_output_structure(
        results_dir,
        "batch_0001",
    )

    output_dir = batch_output_dir(
        results_dir,
        "batch_0001",
    )

    table_index = faiss.read_index(
        str(output_dir / "index" / "table.index")
    )

    table_metadata = load_json(
        output_dir / "index" / "table_metadata.json"
    )

    assert table_index.ntotal == len(table_metadata)


# =============================================================================
# T09 — Persistence consistency
# =============================================================================

def test_persistence_consistency(
    tmp_path,
    embed_model,
):
    """
    Persisted JSON, processed HTML, and FAISS indices should all be
    loadable and mutually consistent.
    """
    batch_dir = make_batch(
        tmp_path,
        "batch_0001",
        NORMAL_DOC,
    )

    results_dir = tmp_path / "results"

    process_batches(
        [batch_dir],
        results_dir,
        embed_model,
        max_workers=1,
        batch_size=16,
    )

    output_dir = batch_output_dir(
        results_dir,
        "batch_0001",
    )

    processed_docs = (
        output_dir / "processed_docs"
    )

    table_store = (
        output_dir / "table_store"
    )

    index_dir = (
        output_dir / "index"
    )

    # Processed HTML must be readable.
    html_files = list(
        processed_docs.glob("*.html")
    )

    assert html_files

    for path in html_files:
        assert path.read_text(
            encoding="utf-8"
        )

    # Table JSON must be valid.
    for path in table_store.glob("*.json"):
        load_json(path)

    # Table FAISS index must load.
    table_index = faiss.read_index(
        str(index_dir / "table.index")
    )

    table_metadata = load_json(
        index_dir / "table_metadata.json"
    )

    assert (
        table_index.ntotal
        == len(table_metadata)
    )

    # Row metadata must be valid JSON.
    row_metadata = load_json(
        index_dir / "row_metadata.json"
    )

    assert isinstance(row_metadata, dict)

    # Row indices must agree with their metadata.
    row_index_dir = index_dir / "rows"

    for key, metadata in row_metadata.items():
        index_path = (
            row_index_dir
            / f"{key}.index"
        )

        assert index_path.exists()

        row_index = faiss.read_index(
            str(index_path)
        )

        assert row_index.ntotal == len(metadata)


# =============================================================================
# T10 — Batch isolation
# =============================================================================

def test_batch_isolation(
    tmp_path,
    embed_model,
):
    """
    Each batch should receive independent output directories with no
    cross-batch contamination.
    """
    batch_1 = make_batch(
        tmp_path,
        "batch_0001",
        NORMAL_DOC,
    )

    batch_2 = make_batch(
        tmp_path,
        "batch_0002",
        HEADER_VARIANTS_DOC,
    )

    results_dir = tmp_path / "results"

    process_batches(
        [batch_1, batch_2],
        results_dir,
        embed_model,
        max_workers=1,
        batch_size=16,
    )

    assert_batch_output_structure(
        results_dir,
        "batch_0001",
    )

    assert_batch_output_structure(
        results_dir,
        "batch_0002",
    )

    batch_1_dir = batch_output_dir(
        results_dir,
        "batch_0001",
    )

    batch_2_dir = batch_output_dir(
        results_dir,
        "batch_0002",
    )

    # Each batch should contain its own processed document.
    assert (
        batch_1_dir / "processed_docs" / f"{NORMAL_DOC.stem}.html"
    ).exists()

    assert (
        batch_2_dir / "processed_docs" / f"{HEADER_VARIANTS_DOC.stem}.html"
    ).exists()

    # Neither batch should contain the other's processed document.
    assert not (
        batch_1_dir
        / "processed_docs"
        / f"{HEADER_VARIANTS_DOC.stem}.html"
    ).exists()

    assert not (
        batch_2_dir
        / "processed_docs"
        / f"{NORMAL_DOC.stem}.html"
    ).exists()


# =============================================================================
# T11 — Failed document isolation
# =============================================================================

def test_failed_document_does_not_abort_batch(
    tmp_path,
    monkeypatch,
):
    """
    A document-level extraction failure should be recorded as failed while
    other documents in the same batch continue processing.
    """

    batch_dir = make_batch(
        tmp_path,
        "batch_0001",
        NORMAL_DOC,
        MALFORMED_DOC,
    )

    table_store = tmp_path / "table_store"
    processed_dir = tmp_path / "processed_docs"

    class FakeFuture:
        def __init__(self, result=None, exception=None):
            self._result = result
            self._exception = exception

        def result(self):
            if self._exception is not None:
                raise self._exception
            return self._result

    class FakeExecutor:
        def __init__(self, max_workers=None):
            self.max_workers = max_workers

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def submit(
            self,
            function,
            path,
            doc_id,
            table_store,
            processed_dir,
        ):
            if doc_id == MALFORMED_DOC.stem:
                return FakeFuture(
                    exception=ValueError(
                        "synthetic extraction failure"
                    )
                )

            return FakeFuture(
                result={
                    "doc_id": doc_id,
                    "processed_path": str(
                        Path(processed_dir)
                        / f"{doc_id}.html"
                    ),
                    "tables": [],
                    "diagnostics": {},
                }
            )

    def fake_as_completed(futures):
        return list(futures)

    monkeypatch.setitem(
        run_batch.__globals__,
        "ProcessPoolExecutor",
        FakeExecutor,
    )
    monkeypatch.setitem(
        run_batch.__globals__,
        "as_completed",
        fake_as_completed,
    )

    results = list(
        run_batch(
            sorted(batch_dir.glob("*.html")),
            max_workers=1,
            table_store=str(table_store),
            processed_dir=str(processed_dir),
        )
    )

    assert len(results) == 2

    successful = [
        result
        for result in results
        if result.get("status") == "success"
    ]

    failed = [
        result
        for result in results
        if result.get("status") == "failed"
    ]

    assert len(successful) == 1
    assert len(failed) == 1

    assert successful[0]["doc_id"] == NORMAL_DOC.stem

    assert failed[0]["doc_id"] == MALFORMED_DOC.stem
    assert failed[0]["error"] == "synthetic extraction failure"


# =============================================================================
# T12 — Missing requested batch
# =============================================================================

def test_missing_batch_is_recorded_as_failed(tmp_path):
    """
    A nonexistent requested batch should be recorded as failed rather than
    aborting processing.
    """

    missing_batch = tmp_path / "batch_9999"
    results_dir = tmp_path / "results"

    reports = process_batches(
        [missing_batch],
        results_dir,
        None,
        max_workers=1,
        batch_size=16,
    )

    assert len(reports) == 1

    report = reports[0]

    assert report["batch"] == "batch_9999"
    assert report["status"] == "failed"
    assert "does not exist" in report["error"]

    # No partial output should remain for the failed batch.
    assert not (
        results_dir / "batch_9999"
    ).exists()


# =============================================================================
# T13 — Empty batch
# =============================================================================

def test_empty_batch_is_handled(
    tmp_path,
    embed_model,
):
    """
    An empty batch should be recorded without causing pipeline failure.
    """
    batch_dir = tmp_path / "batch_0001"
    batch_dir.mkdir()

    results_dir = tmp_path / "results"

    reports = process_batches(
        [batch_dir],
        results_dir,
        embed_model,
        max_workers=1,
        batch_size=16,
    )

    assert reports == [
        {
            "batch": "batch_0001",
            "documents": 0,
            "results": [],
        }
    ]

    assert_batch_output_structure(
        results_dir,
        "batch_0001",
    )


# =============================================================================
# T14 — Existing output refresh
# =============================================================================

def test_existing_output_is_refreshed(
    tmp_path,
    embed_model,
):
    """
    Re-running a batch should replace its previous output rather than
    leaving stale artifacts behind.
    """
    batch_dir = make_batch(
        tmp_path,
        "batch_0001",
        NORMAL_DOC,
    )

    results_dir = tmp_path / "results"

    process_batches(
        [batch_dir],
        results_dir,
        embed_model,
        max_workers=1,
        batch_size=16,
    )

    output_dir = batch_output_dir(
        results_dir,
        "batch_0001",
    )

    stale_files = [
        output_dir / "table_store" / "stale.json",
        output_dir / "processed_docs" / "stale.html",
        output_dir / "index" / "stale.index",
    ]

    for path in stale_files:
        path.write_text(
            "stale",
            encoding="utf-8",
        )
        assert path.exists()

    # Re-run the same batch.
    process_batches(
        [batch_dir],
        results_dir,
        embed_model,
        max_workers=1,
        batch_size=16,
    )

    for path in stale_files:
        assert not path.exists()

    assert_batch_output_structure(
        results_dir,
        "batch_0001",
    )