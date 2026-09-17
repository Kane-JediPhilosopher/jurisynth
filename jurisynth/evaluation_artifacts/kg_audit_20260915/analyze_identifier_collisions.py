"""Reproduce serializer identifiers and measure provenance-key collisions read-only."""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import sqlite3


def normalize_identifier(text: object) -> str:
    value = str(text).strip().lower()
    value = re.sub(r"\.[^.]+$", "", value)
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=Path("jurisynth/global_artifacts/chunk_index/chunk_metadata.sqlite"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")

    connection = sqlite3.connect(f"file:{args.database.as_posix()}?mode=ro", uri=True)
    document_groups: dict[str, set[str]] = defaultdict(set)
    graph_groups: dict[str, set[tuple[str, str]]] = defaultdict(set)
    try:
        for graph_uri, doc_id, chunk_id in connection.execute(
            "SELECT graph_uri, doc_id, chunk_id FROM chunks"
        ):
            document_groups[normalize_identifier(doc_id)].add(doc_id)
            graph_groups[graph_uri].add((doc_id, chunk_id))
    finally:
        connection.close()

    document_collisions = [
        {"normalized_id": key, "source_ids": sorted(values), "source_id_count": len(values)}
        for key, values in document_groups.items() if len(values) > 1
    ]
    document_collisions.sort(key=lambda item: (-item["source_id_count"], item["normalized_id"]))
    graph_collisions = [
        {"graph_uri": key, "source_pairs": sorted(values), "source_pair_count": len(values)}
        for key, values in graph_groups.items() if len(values) > 1
    ]
    graph_collisions.sort(key=lambda item: (-item["source_pair_count"], item["graph_uri"]))

    payload = {
        "source_document_ids": sum(len(values) for values in document_groups.values()),
        "normalized_document_ids": len(document_groups),
        "colliding_document_keys": len(document_collisions),
        "source_documents_in_collision_groups": sum(item["source_id_count"] for item in document_collisions),
        "largest_document_collision_size": max((item["source_id_count"] for item in document_collisions), default=1),
        "document_collision_examples": document_collisions[:30],
        "source_chunk_pairs": sum(len(values) for values in graph_groups.values()),
        "distinct_graph_uris": len(graph_groups),
        "colliding_graph_uris": len(graph_collisions),
        "source_chunks_in_collision_groups": sum(item["source_pair_count"] for item in graph_collisions),
        "largest_graph_collision_size": max((item["source_pair_count"] for item in graph_collisions), default=1),
        "graph_collision_examples": graph_collisions[:30],
    }
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in payload.items() if not key.endswith("examples")}, indent=2))


if __name__ == "__main__":
    main()
