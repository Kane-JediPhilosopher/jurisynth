"""Deterministically sample common-predicate assertions from the read-only store."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3

from pyoxigraph import NamedNode, Store


PREDICATES = [
    "http://jurisynth/data/is",
    "http://jurisynth/data/are",
    "http://jurisynth/data/means",
    "http://jurisynth/data/shall_be",
    "http://jurisynth/data/shall_ensure",
    "http://jurisynth/data/has_duty_rate",
    "http://jurisynth/data/does_not_cover",
    "http://publications.europa.eu/ontology/cdm#includes",
]
CHUNK_PREFIX = "http://jurisynth/source/chunk/"


def text(term: object) -> str:
    return str(getattr(term, "value", term))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("jurisynth/global_artifacts"))
    parser.add_argument("--per-predicate", type=int, default=5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")

    store = Store.read_only(str(args.root / "oxigraph"))
    samples: list[dict] = []
    for predicate in PREDICATES:
        accepted = 0
        for quad in store.quads_for_pattern(None, NamedNode(predicate), None, None):
            graph = text(quad.graph_name)
            if not graph.startswith(CHUNK_PREFIX):
                continue
            samples.append({
                "subject": text(quad.subject),
                "predicate": predicate,
                "object": text(quad.object),
                "graph_uri": graph,
            })
            accepted += 1
            if accepted >= args.per_predicate:
                break

    graph_uris = sorted({sample["graph_uri"] for sample in samples})
    connection = sqlite3.connect(
        f"file:{(args.root / 'chunk_index/chunk_metadata.sqlite').as_posix()}?mode=ro", uri=True
    )
    try:
        content_by_graph: dict[str, dict] = {}
        # One sidecar scan is cheaper than a separate unindexed lookup per sample.
        window = 200
        for start in range(0, len(graph_uris), window):
            group = graph_uris[start:start + window]
            placeholders = ",".join("?" for _ in group)
            query = f"SELECT graph_uri, doc_id, chunk_id, content FROM chunks WHERE graph_uri IN ({placeholders})"
            for graph_uri, doc_id, chunk_id, content in connection.execute(query, group):
                content_by_graph[graph_uri] = {
                    "doc_id": doc_id,
                    "chunk_id": chunk_id,
                    "chunk_excerpt": content[:1200],
                }
    finally:
        connection.close()

    for sample in samples:
        sample.update(content_by_graph.get(sample["graph_uri"], {}))
    args.output.write_text(json.dumps({"samples": samples}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "samples": len(samples)}, indent=2))


if __name__ == "__main__":
    main()
