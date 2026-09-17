"""SQLite sidecars that keep global chunk metadata off the Python heap."""

from __future__ import annotations

import pickle
import sqlite3
import threading
from collections.abc import Mapping
from pathlib import Path
from typing import Iterator

from jurisynth.contracts import SourceChunk
from jurisynth.table_rdf_enricher import chunk_uri


class SQLiteChunkMetadata(Mapping[int, dict[str, str]]):
    """Read vector metadata on demand for FAISS result IDs."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._connection = sqlite3.connect(self.path, check_same_thread=False)
        self._lock = threading.Lock()

    def __getitem__(self, vector_id: int) -> dict[str, str]:
        with self._lock:
            row = self._connection.execute(
                "SELECT chunk_id, doc_id, content FROM chunks WHERE vector_id = ?", (int(vector_id),),
            ).fetchone()
        if row is None:
            raise KeyError(vector_id)
        return {"chunk_id": str(row[0]), "doc_id": str(row[1]), "content": str(row[2])}

    def __iter__(self) -> Iterator[int]:
        with self._lock:
            rows = self._connection.execute("SELECT vector_id FROM chunks ORDER BY vector_id").fetchall()
        yield from (int(row[0]) for row in rows)

    def __len__(self) -> int:
        with self._lock:
            return int(self._connection.execute("SELECT COUNT(*) FROM chunks").fetchone()[0])

    def resolve_graph(self, graph_id: str) -> SourceChunk | None:
        with self._lock:
            row = self._connection.execute(
                "SELECT chunk_id, doc_id, content FROM chunks WHERE graph_uri = ? ORDER BY vector_id DESC LIMIT 1", (graph_id,),
            ).fetchone()
        if row is None:
            return None
        return SourceChunk(chunk_id=str(row[0]), document_id=str(row[1]), text=str(row[2]))

    def has_ambiguous_provenance(self, graph_id: str) -> bool:
        """Whether a normalized graph ID identifies multiple source pairs."""
        with self._lock:
            rows = self._connection.execute(
                "SELECT doc_id, chunk_id FROM chunks WHERE graph_uri = ? GROUP BY doc_id, chunk_id LIMIT 2", (graph_id,),
            ).fetchall()
        return len(rows) > 1

    def records_for_documents(
        self, document_ids: set[str]
    ) -> list[tuple[int, dict[str, str]]]:
        """Return only persisted vectors belonging to explicitly selected documents."""
        if not document_ids:
            return []
        placeholders = ",".join("?" for _ in document_ids)
        with self._lock:
            rows = self._connection.execute(
                "SELECT vector_id, chunk_id, doc_id, content FROM chunks "
                f"WHERE doc_id IN ({placeholders}) ORDER BY vector_id",
                tuple(sorted(document_ids)),
            ).fetchall()
        return [
            (
                int(row[0]),
                {"chunk_id": str(row[1]), "doc_id": str(row[2]), "content": str(row[3])},
            )
            for row in rows
        ]

    def close(self) -> None:
        self._connection.close()


def build_sqlite_chunk_metadata(source: str | Path, destination: str | Path) -> dict[str, int]:
    """Convert an existing aggregate pickle once; global querying becomes lazy."""
    source, destination = Path(source), Path(destination)
    if not source.is_file():
        raise FileNotFoundError(source)
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing chunk metadata store: {destination}")
    with source.open("rb") as file:
        metadata = pickle.load(file)
    if not isinstance(metadata, dict):
        raise ValueError("Chunk metadata pickle must contain a dictionary.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(destination)
    try:
        connection.execute("PRAGMA journal_mode=WAL")
        # Graph URI normalization predates this sidecar and is not injective for
        # every corpus identifier.  Keep every source record, then resolve the
        # highest vector ID to match the previous dict-comprehension behaviour
        # (last record wins) while reporting ambiguity to callers.
        connection.execute("CREATE TABLE chunks (vector_id INTEGER PRIMARY KEY, graph_uri TEXT NOT NULL, chunk_id TEXT NOT NULL, doc_id TEXT NOT NULL, content TEXT NOT NULL)")
        rows: list[tuple[int, str, str, str, str]] = []
        for key, item in metadata.items():
            if not isinstance(item, dict) or not all(isinstance(item.get(field), str) for field in ("chunk_id", "doc_id", "content")):
                raise ValueError(f"Malformed metadata record for vector {key!r}")
            chunk_id, doc_id, content = item["chunk_id"], item["doc_id"], item["content"]
            rows.append((int(key), str(chunk_uri(doc_id, chunk_id)), chunk_id, doc_id, content))
        connection.executemany(
            "INSERT INTO chunks(vector_id, graph_uri, chunk_id, doc_id, content) VALUES (?, ?, ?, ?, ?)", rows,
        )
        connection.execute("CREATE INDEX chunks_graph_uri_idx ON chunks(graph_uri, vector_id DESC)")
        connection.commit()
        # Leave one portable sidecar behind rather than a large companion WAL
        # file after this one-shot build finishes.
        connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        connection.execute("PRAGMA journal_mode=DELETE")
        duplicate_graphs = int(connection.execute(
            "SELECT COUNT(*) FROM (SELECT graph_uri FROM chunks GROUP BY graph_uri HAVING COUNT(*) > 1)"
        ).fetchone()[0])
        return {
            "records": len(rows), "ambiguous_graph_uri_count": duplicate_graphs,
            "destination_bytes": destination.stat().st_size,
        }
    finally:
        connection.close()
