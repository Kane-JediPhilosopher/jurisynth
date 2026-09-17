"""Read-only lexical and distribution audit of Jurisynth metadata sidecars."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
import time


def ro(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)


def rows(connection: sqlite3.Connection, query: str, parameters=()) -> list[dict]:
    cursor = connection.execute(query, parameters)
    names = [item[0] for item in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("jurisynth/global_artifacts"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")

    result: dict[str, object] = {"root": str(args.root)}
    er = ro(args.root / "community/er_index/er_metadata.sqlite")
    started = time.perf_counter()
    try:
        result["resource_lexical_stats"] = rows(er, """
            SELECT kind,
                   COUNT(*) AS records,
                   COUNT(DISTINCT uri) AS distinct_uris,
                   COUNT(DISTINCT normalized_label) AS distinct_normalized_labels,
                   ROUND(AVG(LENGTH(label)), 3) AS mean_characters,
                   MAX(LENGTH(label)) AS max_characters,
                   SUM(LENGTH(TRIM(label)) = 0) AS blank_labels,
                   SUM(LENGTH(label) > 80) AS labels_over_80_chars,
                   SUM(LENGTH(label) > 150) AS labels_over_150_chars,
                   SUM(LENGTH(label) > 500) AS labels_over_500_chars,
                   SUM(LENGTH(label) > 1000) AS labels_over_1000_chars,
                   SUM((LENGTH(label) - LENGTH(REPLACE(label, ' ', '')) + 1) > 12) AS labels_over_12_words,
                   SUM((LENGTH(label) - LENGTH(REPLACE(label, ' ', '')) + 1) > 25) AS labels_over_25_words,
                   SUM(LOWER(label) LIKE 'the %') AS starts_with_the,
                   SUM(LOWER(label) LIKE 'this %' OR LOWER(label) LIKE 'that %'
                       OR LOWER(label) LIKE 'it %' OR LOWER(label) LIKE 'they %') AS starts_demonstrative_or_pronoun,
                   SUM(label GLOB '*[0-9]*') AS contains_digit
            FROM resources GROUP BY kind ORDER BY kind
        """)
        result["generic_relation_labels"] = rows(er, """
            SELECT label, uri FROM resources
            WHERE kind = 'relation' AND normalized_label IN
              ('is','are','has','have','means','includes','include','applies','provides','requires','shall_be')
            ORDER BY normalized_label, uri LIMIT 100
        """)
        result["long_relation_examples"] = rows(er, """
            SELECT label, uri, LENGTH(label) AS characters FROM resources
            WHERE kind = 'relation' AND LENGTH(label) > 80
            ORDER BY LENGTH(label) DESC LIMIT 30
        """)
        result["long_entity_examples"] = rows(er, """
            SELECT label, uri, LENGTH(label) AS characters FROM resources
            WHERE kind = 'entity' AND LENGTH(label) > 150
            ORDER BY LENGTH(label) DESC LIMIT 30
        """)
        result["high_frequency_normalized_labels"] = rows(er, """
            SELECT kind, normalized_label, COUNT(*) AS records,
                   COUNT(DISTINCT uri) AS distinct_uris
            FROM resources
            GROUP BY kind, normalized_label HAVING COUNT(*) > 1
            ORDER BY records DESC LIMIT 50
        """)
    finally:
        er.close()
    result["resource_query_seconds"] = round(time.perf_counter() - started, 6)

    community = ro(args.root / "community/community_metadata.sqlite")
    started = time.perf_counter()
    try:
        result["community_levels"] = rows(community, """
            SELECT level, COUNT(*) AS communities,
                   SUM(member_count) AS summed_members,
                   ROUND(AVG(member_count), 3) AS mean_members,
                   MIN(member_count) AS min_members,
                   MAX(member_count) AS max_members,
                   ROUND(AVG(child_count), 3) AS mean_children,
                   MAX(child_count) AS max_children
            FROM descriptors GROUP BY level ORDER BY level
        """)
        result["community_size_buckets"] = rows(community, """
            SELECT level,
                   SUM(member_count = 1) AS singleton,
                   SUM(member_count BETWEEN 2 AND 5) AS size_2_to_5,
                   SUM(member_count BETWEEN 6 AND 20) AS size_6_to_20,
                   SUM(member_count BETWEEN 21 AND 100) AS size_21_to_100,
                   SUM(member_count BETWEEN 101 AND 1000) AS size_101_to_1000,
                   SUM(member_count > 1000) AS over_1000
            FROM descriptors GROUP BY level ORDER BY level
        """)
        result["largest_communities"] = rows(community, """
            SELECT community_id, level, member_count, child_count, anchor_labels
            FROM descriptors ORDER BY member_count DESC LIMIT 30
        """)
        result["community_metadata"] = rows(community, "SELECT key, value FROM metadata ORDER BY key")
        result["orphan_nonroot_communities"] = rows(community, """
            SELECT level, COUNT(*) AS communities FROM hierarchy
            WHERE level > 0 AND parent_id IS NULL GROUP BY level ORDER BY level
        """)
    finally:
        community.close()
    result["community_query_seconds"] = round(time.perf_counter() - started, 6)

    chunks = ro(args.root / "chunk_index/chunk_metadata.sqlite")
    started = time.perf_counter()
    try:
        result["chunk_stats"] = rows(chunks, """
            SELECT COUNT(*) AS chunks, COUNT(DISTINCT doc_id) AS documents,
                   ROUND(AVG(LENGTH(content)), 3) AS mean_characters,
                   MAX(LENGTH(content)) AS max_characters,
                   SUM(LENGTH(TRIM(content)) = 0) AS empty_chunks,
                   SUM(LENGTH(content) > 10000) AS chunks_over_10000_chars,
                   SUM(LENGTH(content) > 50000) AS chunks_over_50000_chars
            FROM chunks
        """)
        result["documents_with_most_chunks"] = rows(chunks, """
            SELECT doc_id, COUNT(*) AS chunks, SUM(LENGTH(content)) AS characters
            FROM chunks GROUP BY doc_id ORDER BY chunks DESC LIMIT 30
        """)
    finally:
        chunks.close()
    result["chunk_query_seconds"] = round(time.perf_counter() - started, 6)

    manifest = json.loads((args.root / "manifest.json").read_text(encoding="utf-8"))
    batches = manifest["batches"]
    result["manifest_coverage"] = {
        "batches": len(batches),
        "graph_batches": sum(item.get("graph_nquads") is not None for item in batches),
        "chunk_index_batches": sum(item.get("chunk_index") is not None for item in batches),
        "table_index_batches": sum(item.get("table_index") is not None for item in batches),
        "image_index_batches": sum(item.get("image_index") is not None for item in batches),
    }
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "sections": sorted(result)}, indent=2))


if __name__ == "__main__":
    main()
