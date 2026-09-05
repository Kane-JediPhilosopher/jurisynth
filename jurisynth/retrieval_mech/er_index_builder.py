"""Build persisted entity/relation FAISS indices from a completed community KG."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    import faiss
    import numpy as np
except ModuleNotFoundError:
    faiss = None
    np = None

from rdflib import RDFS, URIRef


@dataclass(frozen=True, slots=True)
class ResourceRecord:
    uri: str
    label: str
    community_ids: tuple[str, ...] = ()


@dataclass(slots=True)
class ERIndexArtifacts:
    entity_index: Any
    relation_index: Any
    entity_records: list[ResourceRecord]
    relation_records: list[ResourceRecord]


def _require_faiss() -> None:
    if faiss is None or np is None:
        raise RuntimeError("E-R index building requires faiss-cpu and numpy in the Python 3.12 environment.")


def _fallback_label(uri: URIRef) -> str:
    text = str(uri).rstrip("/#")
    return text.rsplit("/", maxsplit=1)[-1].rsplit("#", maxsplit=1)[-1].replace("_", " ")


def _resource_label(dataset, uri: URIRef) -> str:
    for _, _, label, _ in dataset.quads((uri, RDFS.label, None, None)):
        return str(label)
    return _fallback_label(uri)


def _community_memberships(hierarchy: dict[int, dict[int, dict[str, object]]]) -> dict[URIRef, set[str]]:
    """Map level-0 entity members to their direct community IDs."""
    memberships: dict[URIRef, set[str]] = {}
    for data in hierarchy.get(0, {}).values():
        community_id = str(data["uri"])
        for member in data["members"]:
            if isinstance(member, URIRef):
                memberships.setdefault(member, set()).add(community_id)
    return memberships


def build_resource_records(dataset, hierarchy, *, chunk_namespace: str = "http://jurisynth/source/chunk/") -> tuple[list[ResourceRecord], list[ResourceRecord]]:
    """Create stable metadata records without constructing any vector index yet."""
    memberships = _community_memberships(hierarchy)
    entities: set[URIRef] = set()
    relations: set[URIRef] = set()
    relation_memberships: dict[URIRef, set[str]] = {}

    for graph in dataset.graphs():
        if not str(graph.identifier).startswith(chunk_namespace):
            continue
        for subject, predicate, obj in graph:
            if not isinstance(subject, URIRef) or not isinstance(obj, URIRef):
                continue
            entities.update((subject, obj))
            relations.add(predicate)
            relation_memberships.setdefault(predicate, set()).update(memberships.get(subject, set()))
            relation_memberships[predicate].update(memberships.get(obj, set()))

    def records(resources: Iterable[URIRef], resource_memberships: dict[URIRef, set[str]]):
        return [
            ResourceRecord(str(uri), _resource_label(dataset, uri), tuple(sorted(resource_memberships.get(uri, set()))))
            for uri in sorted(resources, key=str)
        ]

    return records(entities, memberships), records(relations, relation_memberships)


def _build_index(records: list[ResourceRecord], embedder, batch_size: int) -> Any:
    _require_faiss()
    if not records:
        return None
    vectors = np.asarray(
        embedder.encode([record.label for record in records], batch_size=batch_size, normalize_embeddings=True),
        dtype=np.float32,
    )
    if vectors.ndim != 2 or len(vectors) != len(records):
        raise ValueError("Embedding model returned vectors inconsistent with resource metadata.")
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    return index


def build_er_indices(dataset, hierarchy, embedder, *, batch_size: int = 128) -> ERIndexArtifacts:
    """Build separate normalized entity and relation/property indexes."""
    entity_records, relation_records = build_resource_records(dataset, hierarchy)
    return ERIndexArtifacts(
        entity_index=_build_index(entity_records, embedder, batch_size),
        relation_index=_build_index(relation_records, embedder, batch_size),
        entity_records=entity_records,
        relation_records=relation_records,
    )


def save_er_indices(artifacts: ERIndexArtifacts, output_dir: Path, *, manifest: dict[str, object]) -> None:
    """Persist indexes, records, and a caller-owned reproducibility manifest."""
    _require_faiss()
    output_dir.mkdir(parents=True, exist_ok=True)
    if artifacts.entity_index is not None:
        faiss.write_index(artifacts.entity_index, str(output_dir / "entity.index"))
    if artifacts.relation_index is not None:
        faiss.write_index(artifacts.relation_index, str(output_dir / "relation.index"))
    payload = {
        "entities": [asdict(record) for record in artifacts.entity_records],
        "relations": [asdict(record) for record in artifacts.relation_records],
    }
    (output_dir / "metadata.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
