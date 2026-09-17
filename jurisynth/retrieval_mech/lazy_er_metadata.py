"""SQLite-backed E-R metadata for corpus-scale FAISS matching.

The FAISS vectors remain memory-mapped by FAISS; this module keeps the much
larger URI/label/community metadata out of the Python heap until a candidate
actually needs to be rendered.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import sys
from collections.abc import Iterator, Mapping
from pathlib import Path

from jurisynth.retrieval_mech.resource_records import ResourceRecord


def normalize_label(value: str) -> str:
    return " ".join(value.replace("_", " ").casefold().split())


class SQLiteResourceRecords(Mapping[int, ResourceRecord]):
    """FAISS-vector-ID keyed resource records resolved only when selected."""

    def __init__(self, path: str | Path, kind: str) -> None:
        self.path, self.kind = Path(path), kind
        self._connection = sqlite3.connect(self.path, check_same_thread=False)
        self._lock = threading.Lock()

    def __getitem__(self, vector_id: int) -> ResourceRecord:
        with self._lock:
            row = self._connection.execute(
                "SELECT uri, label, community_ids FROM resources WHERE kind = ? AND vector_id = ?",
                (self.kind, int(vector_id)),
            ).fetchone()
        if row is None:
            raise KeyError(vector_id)
        return ResourceRecord(str(row[0]), str(row[1]), tuple(json.loads(str(row[2]))))

    def __iter__(self) -> Iterator[int]:
        with self._lock:
            rows = self._connection.execute(
                "SELECT vector_id FROM resources WHERE kind = ? ORDER BY vector_id", (self.kind,),
            ).fetchall()
        yield from (int(row[0]) for row in rows)

    def __len__(self) -> int:
        with self._lock:
            return int(self._connection.execute(
                "SELECT COUNT(*) FROM resources WHERE kind = ?", (self.kind,),
            ).fetchone()[0])

    def exact_matches(self, normalized_terms: Mapping[str, str]) -> list[tuple[str, ResourceRecord]]:
        if not normalized_terms:
            return []
        placeholders = ", ".join("?" for _ in normalized_terms)
        with self._lock:
            rows = self._connection.execute(
                f"SELECT normalized_label, uri, label, community_ids FROM resources "
                f"WHERE kind = ? AND normalized_label IN ({placeholders}) ORDER BY uri",
                (self.kind, *normalized_terms),
            ).fetchall()
        return [
            (str(row[0]), ResourceRecord(str(row[1]), str(row[2]), tuple(json.loads(str(row[3])))))
            for row in rows
        ]

    def close(self) -> None:
        self._connection.close()


def build_sqlite_er_metadata(source: str | Path, destination: str | Path) -> dict[str, int]:
    """Convert one persisted E-R metadata JSON artifact into a lazy sidecar."""
    source, destination = Path(source), Path(destination)
    if not source.is_file():
        raise FileNotFoundError(source)
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing E-R metadata store: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(destination)
    try:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute(
            "CREATE TABLE resources (kind TEXT NOT NULL, vector_id INTEGER NOT NULL, uri TEXT NOT NULL, "
            "label TEXT NOT NULL, normalized_label TEXT NOT NULL, community_ids TEXT NOT NULL, "
            "PRIMARY KEY(kind, vector_id))"
        )
        counts: dict[str, int] = {}
        for kind, field in (("entity", "entities"), ("relation", "relations")):
            rows: list[tuple[str, int, str, str, str, str]] = []
            count = 0
            for vector_id, record in enumerate(_iter_array_records(source, field)):
                if not isinstance(record, dict) or not isinstance(record.get("uri"), str) or not isinstance(record.get("label"), str):
                    raise ValueError(f"Malformed {field} record {vector_id}.")
                communities = record.get("community_ids", [])
                if not isinstance(communities, (list, tuple)) or not all(isinstance(value, str) for value in communities):
                    raise ValueError(f"Malformed community IDs in {field} record {vector_id}.")
                rows.append((kind, vector_id, record["uri"], record["label"], normalize_label(record["label"]), json.dumps(list(communities))))
                if len(rows) >= 10_000:
                    connection.executemany(
                        "INSERT INTO resources(kind, vector_id, uri, label, normalized_label, community_ids) VALUES (?, ?, ?, ?, ?, ?)", rows,
                    )
                    count += len(rows)
                    if count % 50_000 == 0:
                        print(f"[E-R sidecar] {kind}: {count:,} records", file=sys.stderr, flush=True)
                    rows.clear()
            if rows:
                connection.executemany(
                    "INSERT INTO resources(kind, vector_id, uri, label, normalized_label, community_ids) VALUES (?, ?, ?, ?, ?, ?)", rows,
                )
                count += len(rows)
            counts[f"{kind}_records"] = count
        connection.execute("CREATE INDEX resources_exact_label_idx ON resources(kind, normalized_label, uri)")
        connection.commit()
        connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        connection.execute("PRAGMA journal_mode=DELETE")
        counts["destination_bytes"] = destination.stat().st_size
        return counts
    finally:
        connection.close()


def _iter_array_records(source: Path, field: str):
    """Incrementally decode one named JSON array without loading the document."""
    # The builder writes pretty JSON. Restrict lookup to a top-level key so an
    # ordinary resource label such as "relations" cannot be mistaken for the
    # relation-record array.
    marker = f'\n  "{field}"'
    decoder = json.JSONDecoder()
    with source.open("r", encoding="utf-8") as handle:
        buffer = ""
        started = False
        while True:
            if not started:
                marker_index = buffer.find(marker)
                if marker_index >= 0:
                    bracket_index = buffer.find("[", marker_index + len(marker))
                    if bracket_index >= 0:
                        buffer = buffer[bracket_index + 1:]
                        started = True
                    else:
                        more = handle.read(1 << 16)
                        if not more:
                            raise ValueError(f"Could not find array for {field!r}.")
                        buffer += more
                        continue
                else:
                    more = handle.read(1 << 16)
                    if not more:
                        raise ValueError(f"Could not find field {field!r}.")
                    buffer += more
                    # Keep enough overlap to recognize a marker split across
                    # a read boundary, but do not retain the whole document.
                    if len(buffer) > (1 << 16) + len(marker) + 32:
                        buffer = buffer[-((1 << 16) + len(marker) + 32):]
                    continue
            buffer = buffer.lstrip()
            if buffer.startswith(","):
                buffer = buffer[1:]
                continue
            if buffer.startswith("]"):
                return
            try:
                record, end = decoder.raw_decode(buffer)
            except json.JSONDecodeError:
                more = handle.read(1 << 16)
                if not more:
                    raise ValueError(f"Malformed or truncated JSON array for {field!r}.")
                buffer += more
                continue
            if not isinstance(record, dict):
                raise ValueError(f"Malformed {field!r} record.")
            yield record
            buffer = buffer[end:]
