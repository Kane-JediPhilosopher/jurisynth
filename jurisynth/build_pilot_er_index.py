"""Build a reproducible E-R index for one completed Jurisynth pilot batch."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

from rdflib import Dataset
from sentence_transformers import SentenceTransformer

from jurisynth.retrieval_mech.er_index_builder import build_er_indices, save_er_indices
from jurisynth.retrieval_mech.community_hierarchy import CommunityHierarchy, write_hierarchy_artifact


def build_pilot_er_index(processed_batch_dir: Path, destination: Path, *, model_id: str = "all-MiniLM-L6-v2") -> tuple[int, int]:
    """Build E-R FAISS artifacts from a batch graph and its Community Graph hierarchy."""
    source_dir = Path(__file__).parent / "kg_construction_pipeline" / "src"
    if str(source_dir) not in sys.path:
        sys.path.insert(0, str(source_dir))
    from community_graph_constructor import build_graph_communities

    graph_path = processed_batch_dir / "graph" / "jurisynth_graph.nq"
    dataset = Dataset()
    dataset.parse(graph_path, format="nquads")
    hierarchy, _entity_graph = build_graph_communities(dataset)
    embedder = SentenceTransformer(model_id, local_files_only=True)
    artifacts = build_er_indices(dataset, hierarchy, embedder)
    dimension = int(artifacts.entity_index.d if artifacts.entity_index is not None else artifacts.relation_index.d)
    save_er_indices(
        artifacts,
        destination,
        manifest={
            "artifact_version": "1.0",
            "source_graph": str(graph_path),
            "embedding_model": model_id,
            "embedding_dimension": dimension,
            "normalized": True,
            "community_levels": len(hierarchy),
        },
    )
    write_hierarchy_artifact(
        destination / "community_hierarchy.json",
        CommunityHierarchy.from_leiden_hierarchy(
            hierarchy,
            graph_fingerprint=_sha256_file(graph_path),
        ),
    )
    return len(artifacts.entity_records), len(artifacts.relation_records)


def _sha256_file(source: Path) -> str:
    digest = hashlib.sha256()
    with source.open("rb") as handle:
        for block in iter(lambda: handle.read(1_048_576), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("processed_batch_dir", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--model-id", default="all-MiniLM-L6-v2")
    args = parser.parse_args()
    entities, relations = build_pilot_er_index(args.processed_batch_dir, args.destination, model_id=args.model_id)
    print({"entity_records": entities, "relation_records": relations, "destination": str(args.destination)})


if __name__ == "__main__":
    main()
