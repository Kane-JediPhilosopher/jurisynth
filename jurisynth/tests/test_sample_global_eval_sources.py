from __future__ import annotations

import sqlite3

from jurisynth.sample_global_eval_sources import sample_sources


def test_source_sampling_is_independent_and_excludes_prior_smoke_topics(tmp_path) -> None:
    database = tmp_path / "chunks.sqlite"
    connection = sqlite3.connect(database)
    connection.execute("CREATE TABLE chunks (vector_id INTEGER, doc_id TEXT, chunk_id TEXT, content TEXT)")
    connection.executemany(
        "INSERT INTO chunks VALUES (?, ?, ?, ?)",
        [
            (17, "one", "chunk_1", "The operator shall submit a report within 10 days."),
            (228, "two", "chunk_1", "For the purposes of this Regulation, port means a specified area."),
            (439, "three", "chunk_1", "The authority shall not disclose the record."),
            (650, "four", "chunk_1", "The Artificial Intelligence Act shall apply here."),
        ],
    )
    connection.commit()
    connection.close()
    sampled = sample_sources(database, per_stratum=4)
    all_documents = {item["document_id"] for values in sampled["strata"].values() for item in values}
    assert "four" not in all_documents
    assert {"one", "two", "three"}.issubset(all_documents)
