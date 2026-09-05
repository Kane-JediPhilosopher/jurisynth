"""Deterministic Community Graph artifacts and orientation context.

The hierarchy is retrieval guidance only.  It deliberately contains no source
chunks, tables, or assertion text, so its descriptions cannot be mistaken for
legal evidence.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


SCHEMA_VERSION = 1
DESCRIPTOR_VERSION = 1


@dataclass(frozen=True, slots=True)
class CommunityNode:
    community_id: str
    level: int
    parent_id: str | None = None
    child_ids: tuple[str, ...] = ()
    member_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CommunityHierarchy:
    """A small query-time representation of the persisted community tree."""

    nodes: Mapping[str, CommunityNode]
    graph_fingerprint: str

    def __post_init__(self) -> None:
        for community_id, node in self.nodes.items():
            if community_id != node.community_id:
                raise ValueError("Community node key must equal its community_id")
            if node.parent_id is not None and node.parent_id not in self.nodes:
                raise ValueError(f"Unknown parent community: {node.parent_id}")
            if any(child not in self.nodes for child in node.child_ids):
                raise ValueError(f"Unknown child community in {community_id}")

    @classmethod
    def from_leiden_hierarchy(
        cls,
        hierarchy: Mapping[int, Mapping[int, Mapping[str, object]]],
        *,
        graph_fingerprint: str,
    ) -> "CommunityHierarchy":
        nodes: dict[str, CommunityNode] = {}
        for level, communities in hierarchy.items():
            for record in communities.values():
                community_id = str(record["uri"])
                nodes[community_id] = CommunityNode(
                    community_id=community_id,
                    level=int(level),
                    parent_id=str(record["parent"]) if record.get("parent") is not None else None,
                    child_ids=tuple(sorted(map(str, record.get("children", [])))),
                    member_ids=tuple(sorted(map(str, record.get("members", [])))),
                )
        return cls(nodes=nodes, graph_fingerprint=graph_fingerprint)

    def ancestors(self, community_id: str) -> tuple[str, ...]:
        if community_id not in self.nodes:
            return ()
        result: list[str] = []
        current: str | None = community_id
        while current is not None:
            result.append(current)
            current = self.nodes[current].parent_id
        return tuple(result)

    def lca(self, community_ids: list[str] | tuple[str, ...]) -> str | None:
        valid = [item for item in community_ids if item in self.nodes]
        if not valid:
            return None
        first_ancestors = self.ancestors(valid[0])
        other_ancestor_sets = [set(self.ancestors(item)) for item in valid[1:]]
        return next((item for item in first_ancestors if all(item in values for values in other_ancestor_sets)), None)

    def distance(self, left: str, right: str) -> int | None:
        if left not in self.nodes or right not in self.nodes:
            return None
        lca = self.lca((left, right))
        if lca is None:
            return None
        return self.ancestors(left).index(lca) + self.ancestors(right).index(lca)


def write_hierarchy_artifact(destination: Path, hierarchy: CommunityHierarchy) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "graph_fingerprint": hierarchy.graph_fingerprint,
        "nodes": [
            {
                "community_id": item.community_id,
                "level": item.level,
                "parent_id": item.parent_id,
                "child_ids": list(item.child_ids),
                "member_ids": list(item.member_ids),
            }
            for item in sorted(hierarchy.nodes.values(), key=lambda item: item.community_id)
        ],
    }
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_hierarchy_artifact(source: Path) -> CommunityHierarchy:
    payload = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported community hierarchy artifact.")
    if not isinstance(payload.get("graph_fingerprint"), str) or not isinstance(payload.get("nodes"), list):
        raise ValueError("Malformed community hierarchy artifact.")
    nodes: dict[str, CommunityNode] = {}
    for raw in payload["nodes"]:
        if not isinstance(raw, dict) or not isinstance(raw.get("community_id"), str) or not isinstance(raw.get("level"), int):
            raise ValueError("Malformed community hierarchy node.")
        node = CommunityNode(
            community_id=raw["community_id"],
            level=raw["level"],
            parent_id=raw.get("parent_id"),
            child_ids=tuple(raw.get("child_ids", [])),
            member_ids=tuple(raw.get("member_ids", [])),
        )
        if node.community_id in nodes:
            raise ValueError(f"Duplicate community hierarchy ID: {node.community_id}")
        nodes[node.community_id] = node
    return CommunityHierarchy(nodes=nodes, graph_fingerprint=payload["graph_fingerprint"])


@dataclass(frozen=True, slots=True)
class CommunityOrientation:
    """One non-authoritative, deterministic orientation payload per request."""

    text: str
    provenance: dict[str, object]


@dataclass(frozen=True, slots=True)
class CommunityOrientationBuilder:
    hierarchy: CommunityHierarchy
    labels: Mapping[str, str]
    max_anchor_labels: int = 6
    max_characters: int = 1_500

    def build(self, community_ids: list[str] | tuple[str, ...]) -> CommunityOrientation | None:
        selected = tuple(dict.fromkeys(item for item in community_ids if item in self.hierarchy.nodes))
        if not selected:
            return None
        lca = self.hierarchy.lca(selected)
        distances = [
            distance for index, left in enumerate(selected)
            for right in selected[index + 1 :]
            if (distance := self.hierarchy.distance(left, right)) is not None
        ]
        lines = [
            "Community orientation only — not legal evidence.",
            f"Selected communities: {', '.join(selected)}.",
        ]
        if lca is not None:
            lines.append(f"Shared hierarchy region: {lca}.")
        for community_id in selected:
            node = self.hierarchy.nodes[community_id]
            anchors = [self.labels.get(member, member.rsplit("/", 1)[-1].replace("_", " ")) for member in node.member_ids[: self.max_anchor_labels]]
            detail = f"{community_id} (level {node.level}; {len(node.member_ids)} members"
            if node.child_ids:
                detail += f"; {len(node.child_ids)} child communities"
            detail += ")"
            if anchors:
                detail += f": anchors include {', '.join(anchors)}"
            lines.append(detail + ".")
        text = "\n".join(lines)[: self.max_characters]
        return CommunityOrientation(
            text=text,
            provenance={
                "graph_fingerprint": self.hierarchy.graph_fingerprint,
                "descriptor_version": DESCRIPTOR_VERSION,
                "contributing_communities": list(selected),
                "lca": lca,
                "branch_count": len(selected),
                "average_tree_distance": sum(distances) / len(distances) if distances else 0.0,
                "max_tree_distance": max(distances, default=0),
                "authoritative": False,
            },
        )
