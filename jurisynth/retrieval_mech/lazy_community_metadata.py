"""SQLite sidecars for global Community Graph guidance.

These are deliberately graph-orientation metadata only.  They never contain
source text or generated legal answers, and are queried only for communities
already surfaced by E-R matching.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from collections.abc import Iterator, Mapping
from pathlib import Path

from jurisynth.retrieval_mech.community_hierarchy import CommunityNode
from jurisynth.retrieval_mech.community_summary import CommunitySummaryInput


class _SQLiteNodes(Mapping[str, CommunityNode]):
    def __init__(self, owner: "SQLiteCommunityHierarchy") -> None:
        self.owner = owner

    def __getitem__(self, community_id: str) -> CommunityNode:
        row = self.owner._row(community_id)
        if row is None:
            raise KeyError(community_id)
        return CommunityNode(str(community_id), int(row[0]), str(row[1]) if row[1] is not None else None)

    def __iter__(self) -> Iterator[str]:
        with self.owner._lock:
            rows = self.owner._connection.execute("SELECT community_id FROM hierarchy ORDER BY community_id").fetchall()
        yield from (str(row[0]) for row in rows)

    def __len__(self) -> int:
        with self.owner._lock:
            return int(self.owner._connection.execute("SELECT COUNT(*) FROM hierarchy").fetchone()[0])

    def __contains__(self, community_id: object) -> bool:
        return isinstance(community_id, str) and self.owner._row(community_id) is not None


class SQLiteCommunityHierarchy:
    """A hierarchy API compatible with query-time selector/orientation needs."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._connection = sqlite3.connect(self.path, check_same_thread=False)
        self._lock = threading.Lock()
        with self._lock:
            row = self._connection.execute("SELECT value FROM metadata WHERE key = 'graph_fingerprint'").fetchone()
        if row is None:
            raise ValueError("Malformed community metadata sidecar.")
        self.graph_fingerprint = str(row[0])
        self.nodes: Mapping[str, CommunityNode] = _SQLiteNodes(self)

    def _row(self, community_id: str):
        with self._lock:
            return self._connection.execute(
                "SELECT level, parent_id FROM hierarchy WHERE community_id = ?", (community_id,),
            ).fetchone()

    def ancestors(self, community_id: str) -> tuple[str, ...]:
        result: list[str] = []
        current: str | None = community_id
        while current is not None:
            row = self._row(current)
            if row is None:
                return ()
            result.append(current)
            current = str(row[1]) if row[1] is not None else None
        return tuple(result)

    def lca(self, community_ids: list[str] | tuple[str, ...]) -> str | None:
        valid = [item for item in community_ids if item in self.nodes]
        if not valid:
            return None
        first = self.ancestors(valid[0])
        other_sets = [set(self.ancestors(item)) for item in valid[1:]]
        return next((item for item in first if all(item in values for values in other_sets)), None)

    def distance(self, left: str, right: str) -> int | None:
        left_ancestors, right_ancestors = self.ancestors(left), self.ancestors(right)
        lca = self.lca((left, right))
        if lca is None:
            return None
        return left_ancestors.index(lca) + right_ancestors.index(lca)

    def close(self) -> None:
        self._connection.close()


class SQLiteOrientationDescriptors(Mapping[str, CommunitySummaryInput]):
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._connection = sqlite3.connect(self.path, check_same_thread=False)
        self._lock = threading.Lock()
        with self._lock:
            values = dict(self._connection.execute("SELECT key, value FROM metadata").fetchall())
        if values.get("kind") != "deterministic_graph_orientation":
            raise ValueError("Unsupported community orientation metadata sidecar.")
        self._provenance = {
            "artifact_kind": values["kind"], "descriptor_version": int(values["descriptor_version"]),
            "graph_fingerprint": values.get("graph_fingerprint"), "authoritative": False,
        }

    def __getitem__(self, community_id: str) -> CommunitySummaryInput:
        with self._lock:
            row = self._connection.execute(
                "SELECT level, member_count, child_count, anchor_labels FROM descriptors WHERE community_id = ?", (community_id,),
            ).fetchone()
        if row is None:
            raise KeyError(community_id)
        anchors = json.loads(str(row[3]))
        detail = f"Community {community_id} (level {int(row[0])}; {int(row[1])} members; {int(row[2])} children)"
        if anchors:
            detail += "; anchors: " + ", ".join(anchors)
        return CommunitySummaryInput(community_id, detail + ".", int(row[0]), dict(self._provenance))

    def __iter__(self) -> Iterator[str]:
        with self._lock:
            rows = self._connection.execute("SELECT community_id FROM descriptors ORDER BY community_id").fetchall()
        yield from (str(row[0]) for row in rows)

    def __len__(self) -> int:
        with self._lock:
            return int(self._connection.execute("SELECT COUNT(*) FROM descriptors").fetchone()[0])

    def close(self) -> None:
        self._connection.close()


def build_sqlite_community_metadata(hierarchy_source: str | Path, descriptor_source: str | Path, destination: str | Path) -> dict[str, int]:
    """Convert bulky hierarchy/descriptors JSON into one lazy global sidecar."""
    hierarchy_source, descriptor_source, destination = Path(hierarchy_source), Path(descriptor_source), Path(destination)
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing community metadata store: {destination}")
    fingerprint = _read_string_field(hierarchy_source, "graph_fingerprint")
    kind = _read_string_field(descriptor_source, "kind")
    descriptor_version = _read_int_field(descriptor_source, "descriptor_version")
    if kind != "deterministic_graph_orientation":
        raise ValueError("Malformed community descriptor artifact.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(destination)
    try:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        connection.execute("CREATE TABLE hierarchy (community_id TEXT PRIMARY KEY, level INTEGER NOT NULL, parent_id TEXT)")
        connection.execute("CREATE TABLE descriptors (community_id TEXT PRIMARY KEY, level INTEGER NOT NULL, member_count INTEGER NOT NULL, child_count INTEGER NOT NULL, anchor_labels TEXT NOT NULL)")
        hierarchy_rows: list[tuple[str, int, str | None]] = []
        for raw in _iter_array_records(hierarchy_source, "nodes"):
            if not isinstance(raw, dict) or not isinstance(raw.get("community_id"), str) or not isinstance(raw.get("level"), int):
                raise ValueError("Malformed community hierarchy node.")
            hierarchy_rows.append((raw["community_id"], raw["level"], raw.get("parent_id")))
            if len(hierarchy_rows) >= 10_000:
                connection.executemany("INSERT INTO hierarchy(community_id, level, parent_id) VALUES (?, ?, ?)", hierarchy_rows)
                hierarchy_rows.clear()
        hierarchy_count = len(hierarchy_rows)
        if hierarchy_rows:
            connection.executemany("INSERT INTO hierarchy(community_id, level, parent_id) VALUES (?, ?, ?)", hierarchy_rows)
        descriptor_rows: list[tuple[str, int, int, int, str]] = []
        descriptor_count = 0
        for raw in _iter_array_records(descriptor_source, "nodes"):
            if not isinstance(raw, dict) or not isinstance(raw.get("community_id"), str):
                raise ValueError("Malformed community descriptor node.")
            if not all(isinstance(raw.get(field), int) for field in ("level", "member_count", "child_count")):
                raise ValueError("Malformed community descriptor counts.")
            anchors = raw.get("anchor_labels")
            if not isinstance(anchors, list) or not all(isinstance(value, str) for value in anchors):
                raise ValueError("Malformed community descriptor anchors.")
            descriptor_rows.append((raw["community_id"], raw["level"], raw["member_count"], raw["child_count"], json.dumps(anchors)))
            if len(descriptor_rows) >= 10_000:
                connection.executemany("INSERT INTO descriptors(community_id, level, member_count, child_count, anchor_labels) VALUES (?, ?, ?, ?, ?)", descriptor_rows)
                descriptor_count += len(descriptor_rows)
                descriptor_rows.clear()
        if descriptor_rows:
            connection.executemany("INSERT INTO descriptors(community_id, level, member_count, child_count, anchor_labels) VALUES (?, ?, ?, ?, ?)", descriptor_rows)
            descriptor_count += len(descriptor_rows)
        connection.executemany("INSERT INTO metadata(key, value) VALUES (?, ?)", [
            ("graph_fingerprint", fingerprint), ("kind", kind),
            ("descriptor_version", str(descriptor_version)),
        ])
        connection.execute("CREATE INDEX hierarchy_parent_idx ON hierarchy(parent_id)")
        connection.commit()
        connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        connection.execute("PRAGMA journal_mode=DELETE")
        hierarchy_count += int(connection.execute("SELECT COUNT(*) FROM hierarchy").fetchone()[0]) - hierarchy_count
        return {"hierarchy_nodes": hierarchy_count, "descriptor_nodes": descriptor_count, "destination_bytes": destination.stat().st_size}
    finally:
        connection.close()


def _read_string_field(source: Path, field: str) -> str:
    value = _read_scalar_field(source, field)
    if not isinstance(value, str):
        raise ValueError(f"Malformed {field!r} field.")
    return value


def _read_int_field(source: Path, field: str) -> int:
    value = _read_scalar_field(source, field)
    if not isinstance(value, int):
        raise ValueError(f"Malformed {field!r} field.")
    return value


def _read_scalar_field(source: Path, field: str):
    marker, decoder = f'\n  "{field}"', json.JSONDecoder()
    with source.open("r", encoding="utf-8") as handle:
        buffer = ""
        while True:
            index = buffer.find(marker)
            if index >= 0:
                colon = buffer.find(":", index + len(marker))
                if colon >= 0:
                    try:
                        return decoder.raw_decode(buffer[colon + 1:].lstrip())[0]
                    except json.JSONDecodeError:
                        pass
            more = handle.read(1 << 20)
            if not more:
                raise ValueError(f"Could not find {field!r}.")
            buffer += more
            if len(buffer) > (1 << 20) + len(marker) + 64:
                buffer = buffer[-((1 << 20) + len(marker) + 64):]


def _iter_array_records(source: Path, field: str):
    marker, decoder = f'\n  "{field}"', json.JSONDecoder()
    with source.open("r", encoding="utf-8") as handle:
        buffer, started = "", False
        while True:
            if not started:
                index = buffer.find(marker)
                if index >= 0:
                    bracket = buffer.find("[", index + len(marker))
                    if bracket >= 0:
                        buffer, started = buffer[bracket + 1:], True
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
