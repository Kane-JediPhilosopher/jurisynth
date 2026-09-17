"""Build global communities and E-R indexes on a high-memory machine.

The RDFLib/igraph implementation materialises the whole graph and is guarded
accordingly. Use this command on GCP, not the local 16-GB laptop.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import threading
import time
import sys
from pathlib import Path

from rdflib import Dataset
from sentence_transformers import SentenceTransformer

from jurisynth.retrieval_mech.community_hierarchy import CommunityHierarchy, write_hierarchy_artifact, write_orientation_descriptors
from jurisynth.retrieval_mech.er_index_builder import build_er_indices, save_er_indices


def _sha256_file(source: Path) -> str:
    digest = hashlib.sha256()
    with source.open("rb") as handle:
        for block in iter(lambda: handle.read(1_048_576), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_memory(minimum_available_gb: float) -> None:
    try:
        import psutil
    except ModuleNotFoundError:
        return
    available = psutil.virtual_memory().available / (1024 ** 3)
    if available < minimum_available_gb:
        raise RuntimeError(
            f"Global community construction needs at least {minimum_available_gb:.0f} GB available RAM "
            f"with the current RDFLib/igraph implementation; only {available:.1f} GB is available."
        )


def _log(message: str) -> None:
    print(
        f"[Community Build] {message}",
        flush=True,
    )


def _memory_status() -> str:
    try:
        import psutil

        memory = psutil.virtual_memory()
        return (
            f"RAM used={memory.used / (1024 ** 3):.1f} GiB "
            f"available={memory.available / (1024 ** 3):.1f} GiB "
            f"({memory.percent:.1f}% used)"
        )
    except Exception:
        return "RAM status unavailable"


def _run_with_heartbeat(
    label: str,
    function,
    *,
    interval: float = 60.0,
):
    start = time.monotonic()
    stop_event = threading.Event()

    def heartbeat() -> None:
        while not stop_event.wait(interval):
            elapsed = time.monotonic() - start
            _log(
                f"{label} still running | "
                f"elapsed={elapsed / 60:.1f} min | "
                f"{_memory_status()}"
            )

    _log(
        f"START {label} | {_memory_status()}"
    )

    thread = threading.Thread(
        target=heartbeat,
        daemon=True,
    )
    thread.start()

    try:
        result = function()
    finally:
        stop_event.set()
        thread.join(timeout=1)

    elapsed = time.monotonic() - start

    _log(
        f"DONE {label} | "
        f"elapsed={elapsed / 60:.1f} min | "
        f"{_memory_status()}"
    )

    return result


def build_global_community(
    graph_path: Path,
    destination: Path,
    *,
    model_id: str = "all-MiniLM-L6-v2",
    max_levels: int = 5,
    resolution: float = 1.0,
) -> dict[str, int | str]:

    _log("Global community build starting.")
    _log(f"Graph: {graph_path}")
    _log(f"Destination: {destination}")
    _log(_memory_status())

    source_dir = (
        Path(__file__).parent
        / "kg_construction_pipeline"
        / "src"
    )

    if str(source_dir) not in sys.path:
        sys.path.insert(0, str(source_dir))

    from community_graph_constructor import (
        build_graph_communities,
        serialize_communities,
    )

    dataset = Dataset()

    _run_with_heartbeat(
        "Parsing global N-Quads into RDFLib Dataset",
        lambda: dataset.parse(
            graph_path,
            format="nquads",
        ),
    )

    _log(
        f"Dataset loaded | "
        f"contexts={sum(1 for _ in dataset.graphs())} | "
        f"{_memory_status()}"
    )

    hierarchy, entity_graph = _run_with_heartbeat(
        "Building entity graph + Leiden hierarchy",
        lambda: build_graph_communities(
            dataset,
            max_levels=max_levels,
            resolution=resolution,
        ),
    )

    _log(
        f"Entity graph complete | "
        f"vertices={entity_graph.vcount():,} | "
        f"edges={entity_graph.ecount():,} | "
        f"levels={len(hierarchy)}"
    )

    destination.mkdir(
        parents=True,
        exist_ok=False,
    )

    fingerprint = _run_with_heartbeat(
        "Hashing source graph",
        lambda: _sha256_file(graph_path),
    )

    hierarchy_artifact = (
        CommunityHierarchy.from_leiden_hierarchy(
            hierarchy,
            graph_fingerprint=fingerprint,
        )
    )

    _log("Writing community hierarchy artifact.")

    write_hierarchy_artifact(
        destination / "community_hierarchy.json",
        hierarchy_artifact,
    )

    _run_with_heartbeat(
        "Serializing community RDF",
        lambda: serialize_communities(
            hierarchy
        ).serialize(
            destination / "community_graph.nq",
            format="nquads",
        ),
    )

    _log(
        f"Loading embedding model: {model_id}"
    )

    embedder = SentenceTransformer(
        model_id,
        local_files_only=True,
    )

    artifacts = _run_with_heartbeat(
        "Building global entity/relation indexes",
        lambda: build_er_indices(
            dataset,
            hierarchy,
            embedder,
        ),
    )

    if artifacts.entity_index is not None:
        dimension = int(
            artifacts.entity_index.d
        )
    elif artifacts.relation_index is not None:
        dimension = int(
            artifacts.relation_index.d
        )
    else:
        raise RuntimeError(
            "Neither entity nor relation index "
            "was produced."
        )

    _log(
        f"E-R records complete | "
        f"entities={len(artifacts.entity_records):,} | "
        f"relations={len(artifacts.relation_records):,}"
    )

    _log("Saving E-R indexes.")

    save_er_indices(
        artifacts,
        destination / "er_index",
        manifest={
            "artifact_version": "1.0",
            "source_graph": str(graph_path),
            "graph_fingerprint": fingerprint,
            "embedding_model": model_id,
            "embedding_dimension": dimension,
            "normalized": True,
            "community_levels": len(hierarchy),
        },
    )

    labels = {
        record.uri: record.label
        for record in artifacts.entity_records
    }

    _log("Writing community orientation descriptors.")

    write_orientation_descriptors(
        destination / "community_descriptors.json",
        hierarchy_artifact,
        labels,
    )

    metadata = {
        "source_graph": str(graph_path),
        "graph_fingerprint": fingerprint,
        "entity_graph_vertices":
            entity_graph.vcount(),
        "entity_graph_edges":
            entity_graph.ecount(),
        "community_levels": len(hierarchy),
        "entity_records":
            len(artifacts.entity_records),
        "relation_records":
            len(artifacts.relation_records),
        "embedding_model": model_id,
    }

    (
        destination
        / "build_metadata.json"
    ).write_text(
        json.dumps(
            metadata,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    _log("GLOBAL COMMUNITY BUILD COMPLETE.")

    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", type=Path, default=Path("jurisynth/global_artifacts/graph/jurisynth_graph.nq"))
    parser.add_argument("--destination", type=Path, default=Path("jurisynth/global_artifacts/community"))
    parser.add_argument("--model-id", default="all-MiniLM-L6-v2")
    parser.add_argument("--max-levels", type=int, default=5)
    parser.add_argument("--resolution", type=float, default=1.0)
    parser.add_argument("--minimum-available-gb", type=float, default=48.0)
    args = parser.parse_args()
    _require_memory(args.minimum_available_gb)
    print(json.dumps(build_global_community(
        args.graph, args.destination, model_id=args.model_id,
        max_levels=args.max_levels, resolution=args.resolution,
    ), indent=2))


if __name__ == "__main__":
    main()
