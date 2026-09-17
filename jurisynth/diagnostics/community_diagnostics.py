"""Read-only diagnostics for a persisted community hierarchy sidecar."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from jurisynth.retrieval_mech.lazy_community_metadata import SQLiteCommunityHierarchy


def diagnose(
    metadata_path: Path,
    *,
    bundle_path: Path | None = None,
    selector_top_n: int = 3,
    summary_min_communities: int = 6,
    summary_min_average_distance: float = 4.0,
) -> dict[str, object]:
    connection = sqlite3.connect(metadata_path)
    try:
        metadata = dict(connection.execute("SELECT key, value FROM metadata"))
        levels = [
            {"level": int(level), "nodes": int(nodes), "roots": int(roots)}
            for level, nodes, roots in connection.execute(
                "SELECT level, COUNT(*), SUM(CASE WHEN parent_id IS NULL THEN 1 ELSE 0 END) "
                "FROM hierarchy GROUP BY level ORDER BY level"
            )
        ]
        descriptor_row = connection.execute(
            "SELECT COUNT(*), MIN(member_count), AVG(member_count), MAX(member_count), "
            "MIN(child_count), AVG(child_count), MAX(child_count), "
            "SUM(CASE WHEN child_count = 0 THEN 1 ELSE 0 END) FROM descriptors"
        ).fetchone()
        orphan_count = int(connection.execute(
            "SELECT COUNT(*) FROM hierarchy child LEFT JOIN hierarchy parent "
            "ON child.parent_id = parent.community_id "
            "WHERE child.parent_id IS NOT NULL AND parent.community_id IS NULL"
        ).fetchone()[0])
    finally:
        connection.close()

    result: dict[str, object] = {
        "metadata_path": str(metadata_path),
        "graph_fingerprint": metadata.get("graph_fingerprint"),
        "descriptor_version": int(metadata.get("descriptor_version", "0")),
        "node_count": sum(item["nodes"] for item in levels),
        "levels": levels,
        "descriptor_stats": {
            "count": int(descriptor_row[0]),
            "member_count": {
                "minimum": int(descriptor_row[1]),
                "average": float(descriptor_row[2]),
                "maximum": int(descriptor_row[3]),
            },
            "child_count": {
                "minimum": int(descriptor_row[4]),
                "average": float(descriptor_row[5]),
                "maximum": int(descriptor_row[6]),
                "leaf_nodes": int(descriptor_row[7]),
            },
        },
        "orphan_parent_count": orphan_count,
        "configured_behavior": {
            "selector_top_n": selector_top_n,
            "maximum_orientation_communities": selector_top_n + 1,
            "summary_min_communities": summary_min_communities,
            "community_count_trigger_reachable": selector_top_n + 1 >= summary_min_communities,
            "summary_min_average_distance": summary_min_average_distance,
        },
    }
    if bundle_path is not None:
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        orientation = bundle.get("retrieval_metadata", {}).get("community_orientation")
        if isinstance(orientation, dict):
            selected = orientation.get("contributing_communities", [])
            average = float(orientation.get("average_tree_distance", 0.0))
            hierarchy = SQLiteCommunityHierarchy(metadata_path)
            try:
                result["observed_retrieval"] = {
                    "community_count": len(selected),
                    "communities": selected,
                    "all_present_in_hierarchy": all(item in hierarchy.nodes for item in selected),
                    "lca": orientation.get("lca"),
                    "average_tree_distance": average,
                    "max_tree_distance": int(orientation.get("max_tree_distance", 0)),
                    "summary_triggered": "lazy_community_summary" in bundle.get("retrieval_metadata", {}),
                    "community_count_trigger": len(selected) >= summary_min_communities,
                    "tree_dispersion_trigger": average >= summary_min_average_distance,
                }
            finally:
                hierarchy.close()
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = diagnose(args.metadata, bundle_path=args.bundle)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
