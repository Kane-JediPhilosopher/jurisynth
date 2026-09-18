"""Read-only corpus check for the blind legal-case evaluation."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def main() -> None:
    database = Path("jurisynth/global_artifacts_source_uri_v2/document_metadata.sqlite")
    connection = sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True)
    tables = connection.execute(
        "SELECT name, sql FROM sqlite_master WHERE type = 'table' ORDER BY name"
    ).fetchall()
    for name, sql in tables:
        print(f"TABLE {name}\n{sql}\n")

    terms = (
        "%privacy and electronic communications%",
        "%general data protection regulation%",
        "%protection of individuals with regard to the processing of personal data%",
        "%2009 136%",
        "%95 46%",
    )
    for term in terms:
        rows = connection.execute(
            """
            SELECT document_id, celex, eli, title, aliases_json, canonical_keys_json
            FROM documents
            WHERE lower(coalesce(title, '')) LIKE ?
               OR lower(aliases_json) LIKE ?
               OR lower(canonical_keys_json) LIKE ?
            ORDER BY document_id
            """,
            (term, term, term),
        ).fetchall()
        print(f"MATCH {term}: {len(rows)}")
        for row in rows[:20]:
            print(row)

    chunk_database = Path(
        "jurisynth/global_artifacts_source_uri_v2/chunk_index/chunk_metadata.sqlite"
    )
    chunk_connection = sqlite3.connect(
        f"file:{chunk_database.as_posix()}?mode=ro", uri=True
    )
    chunk_tables = chunk_connection.execute(
        "SELECT name, sql FROM sqlite_master WHERE type = 'table' ORDER BY name"
    ).fetchall()
    for name, sql in chunk_tables:
        print(f"CHUNK TABLE {name}\n{sql}\n")

    amendment_ids = [
        row[0]
        for row in connection.execute(
            "SELECT document_id FROM documents WHERE aliases_json LIKE '%2009 136%' ORDER BY document_id"
        ).fetchall()
    ]
    for document_id in ("32002L0058en", "L_2016119EN.01000101", *amendment_ids):
        count = chunk_connection.execute(
            "SELECT count(*) FROM chunks WHERE doc_id = ?", (document_id,)
        ).fetchone()[0]
        print(f"CHUNKS {document_id}: {count}")
        samples = chunk_connection.execute(
            """
            SELECT chunk_id, substr(content, 1, 700)
            FROM chunks
            WHERE doc_id = ?
              AND (lower(content) LIKE '%article 5%' OR lower(content) LIKE '%pre-ticked%' OR lower(content) LIKE '%consent%')
            ORDER BY vector_id
            LIMIT 4
            """,
            (document_id,),
        ).fetchall()
        for chunk_id, content in samples:
            print(f"SAMPLE {document_id} {chunk_id}: {content!r}")
        targeted = chunk_connection.execute(
            """
            SELECT chunk_id, graph_uri, substr(content, 1, 1400)
            FROM chunks
            WHERE doc_id = ?
              AND (
                lower(content) LIKE '%storing of information%'
                OR lower(content) LIKE '%pre-ticked boxes%'
                OR lower(content) LIKE '%clear affirmative action%'
                OR lower(content) LIKE '%terminal equipment%'
              )
            ORDER BY vector_id
            LIMIT 8
            """,
            (document_id,),
        ).fetchall()
        for chunk_id, graph_uri, content in targeted:
            print(f"TARGET {document_id} {chunk_id} {graph_uri}: {content!r}")


if __name__ == "__main__":
    main()
