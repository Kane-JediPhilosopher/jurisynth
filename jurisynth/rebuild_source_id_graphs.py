"""Rebuild source-identity-safe RDF from saved resolution checkpoints.

This does not call an LLM or alter existing per-batch/global artifacts.  The
destination must be a new, versioned directory.  Run from the project_space
root with ``python -m jurisynth.rebuild_source_id_graphs``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pickle
import shutil
import sys
from pathlib import Path
from uuid import uuid4

from jurisynth.kg_construction_pipeline.src.source_uri import scoped_fragment


def _source_modules():
    source_dir = Path(__file__).resolve().parent / "kg_construction_pipeline" / "src"
    if str(source_dir) not in sys.path:
        sys.path.insert(0, str(source_dir))
    from assertion_validator import run_assertion_validation
    from graph_serializer import serialize_graph
    from schema_loader import load_schema
    return run_assertion_validation, serialize_graph, load_schema


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _batches(processed_root: Path) -> list[Path]:
    batches = sorted(path for path in processed_root.glob("batch_*") if path.is_dir() and (path / ".success").is_file())
    if not batches:
        raise FileNotFoundError(f"No completed batches in {processed_root}")
    return batches


def _selected_batches(processed_root: Path, names: list[str]) -> list[Path]:
    batches = _batches(processed_root)
    if not names:
        return batches
    by_name = {path.name: path for path in batches}
    missing = sorted(set(names) - by_name.keys())
    if missing:
        raise FileNotFoundError(f"Unknown completed batches: {', '.join(missing)}")
    return [by_name[name] for name in sorted(set(names))]


def _checkpoint(batch: Path) -> Path:
    return batch / "checkpoints" / "resolved_assertions.pkl"


def check_inputs(processed_root: Path) -> dict[str, int]:
    """Check checkpoint completeness and injective source URI mapping."""
    document_to_uri: dict[str, str] = {}
    uri_to_document: dict[str, str] = {}
    chunk_to_uri: dict[tuple[str, str], str] = {}
    uri_to_chunk: dict[str, tuple[str, str]] = {}
    batch_count = 0
    chunk_records = 0
    for batch in _batches(processed_root):
        checkpoint = _checkpoint(batch)
        metadata_path = batch / "chunk_index" / "chunk_metadata.pkl"
        if not checkpoint.is_file() or not metadata_path.is_file():
            raise FileNotFoundError(f"Incomplete checkpoint/chunk metadata for {batch.name}")
        with metadata_path.open("rb") as handle:
            metadata = pickle.load(handle)
        if not isinstance(metadata, dict):
            raise ValueError(f"Malformed chunk metadata for {batch.name}")
        for item in metadata.values():
            doc_id, chunk_id = str(item["doc_id"]), str(item["chunk_id"])
            doc_uri = scoped_fragment(doc_id)
            chunk_uri = scoped_fragment(doc_id, chunk_id)
            previous_doc = uri_to_document.setdefault(doc_uri, doc_id)
            previous_chunk = uri_to_chunk.setdefault(chunk_uri, (doc_id, chunk_id))
            if previous_doc != doc_id or previous_chunk != (doc_id, chunk_id):
                raise RuntimeError(f"Source URI collision in {batch.name}: {doc_id!r}, {chunk_id!r}")
            document_to_uri[doc_id] = doc_uri
            chunk_to_uri[(doc_id, chunk_id)] = chunk_uri
            chunk_records += 1
        batch_count += 1
    return {
        "batches": batch_count,
        "source_document_ids": len(document_to_uri),
        "source_chunk_pairs": len(chunk_to_uri),
        "chunk_records": chunk_records,
        "document_uri_collisions": 0,
        "chunk_uri_collisions": 0,
    }


def build_batches(processed_root: Path, schema_dir: Path, destination: Path, names: list[str], *, resume: bool) -> dict[str, int]:
    """Revalidate saved resolved assertions and serialize into new batch files."""
    if not schema_dir.is_dir():
        raise FileNotFoundError(schema_dir)
    if destination.resolve() == processed_root.resolve():
        raise ValueError("The rebuild destination cannot be the existing pipeline output root")
    validator, serializer, load_schema = _source_modules()
    schema = load_schema(schema_dir)
    built = skipped = 0
    for batch in _selected_batches(processed_root, names):
        checkpoint = _checkpoint(batch)
        if not checkpoint.is_file():
            raise FileNotFoundError(checkpoint)
        batch_out = destination / "batches" / batch.name / "graph"
        graph_out = batch_out / "jurisynth_graph.nq"
        summary_out = batch_out / "rebuild_metadata.json"
        if graph_out.exists() or summary_out.exists():
            if not resume or not graph_out.is_file() or not summary_out.is_file():
                raise FileExistsError(f"Incomplete or existing rebuilt batch: {batch_out}")
            summary = json.loads(summary_out.read_text(encoding="utf-8"))
            if summary.get("resolved_sha256") != _sha256(checkpoint) or summary.get("graph_sha256") != _sha256(graph_out):
                raise ValueError(f"Rebuilt batch changed since its summary was written: {batch.name}")
            print(json.dumps({"batch": batch.name, "status": "verified_and_skipped"}), flush=True)
            skipped += 1
            continue
        with checkpoint.open("rb") as handle:
            resolved_assertions = pickle.load(handle)
        validated, errors, statistics = validator(resolved_assertions, schema["resource_metadata"])
        old_stats_path = batch / "diagnostics" / "validation_stats.json"
        if old_stats_path.is_file():
            old_stats = json.loads(old_stats_path.read_text(encoding="utf-8"))
            if statistics != old_stats:
                raise ValueError(f"Validation statistics changed for {batch.name}; refusing silent graph drift")
        batch_out.mkdir(parents=True, exist_ok=True)
        pending = batch_out / f"jurisynth_graph.{uuid4().hex}.pending.nq"
        try:
            dataset = serializer(validated, schema_namespaces=schema["namespaces"], output_file=str(pending))
            del dataset
            if not pending.is_file() or pending.stat().st_size == 0:
                raise RuntimeError(f"Empty rebuilt RDF file for {batch.name}")
            summary = {
                "batch": batch.name,
                "resolved_records": len(resolved_assertions),
                "validated_records": len(validated),
                "invalid_records": len(errors),
                "validation_statistics": statistics,
                "resolved_sha256": _sha256(checkpoint),
                "graph_sha256": _sha256(pending),
                "graph_bytes": pending.stat().st_size,
                "source_uri_version": 2,
            }
            pending.replace(graph_out)
            summary_pending = batch_out / f"rebuild_metadata.{uuid4().hex}.pending.json"
            summary_pending.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
            summary_pending.replace(summary_out)
        finally:
            pending.unlink(missing_ok=True)
        print(json.dumps({"batch": batch.name, "status": "built", "graph_bytes": summary["graph_bytes"]}), flush=True)
        built += 1
    return {"selected": len(_selected_batches(processed_root, names)), "built": built, "skipped": skipped}


def merge_graphs(processed_root: Path, destination: Path) -> dict[str, int | str]:
    """Stream rebuilt per-batch N-Quads into a new global file."""
    if destination.resolve() == processed_root.resolve():
        raise ValueError("The rebuild destination cannot be the existing pipeline output root")
    graph_out = destination / "graph" / "jurisynth_graph.nq"
    if graph_out.exists():
        raise FileExistsError(f"Refusing to overwrite {graph_out}")
    batches = _batches(processed_root)
    for batch in batches:
        source = destination / "batches" / batch.name / "graph" / "jurisynth_graph.nq"
        summary = source.with_name("rebuild_metadata.json")
        if not source.is_file() or not summary.is_file():
            raise FileNotFoundError(f"Missing rebuilt RDF/summary for {batch.name}")
        metadata = json.loads(summary.read_text(encoding="utf-8"))
        if metadata.get("resolved_sha256") != _sha256(_checkpoint(batch)) or metadata.get("graph_sha256") != _sha256(source):
            raise ValueError(f"Checkpoint or rebuilt RDF changed before merge: {batch.name}")
    graph_out.parent.mkdir(parents=True, exist_ok=True)
    pending = graph_out.with_name(f"jurisynth_graph.{uuid4().hex}.pending.nq")
    try:
        with pending.open("xb") as output:
            for batch in batches:
                source = destination / "batches" / batch.name / "graph" / "jurisynth_graph.nq"
                with source.open("rb") as handle:
                    shutil.copyfileobj(handle, output, length=1024 * 1024)
                output.write(b"\n")
        pending.replace(graph_out)
    finally:
        pending.unlink(missing_ok=True)
    return {"batches": len(batches), "graph": str(graph_out), "graph_bytes": graph_out.stat().st_size, "sha256": _sha256(graph_out)}


def _verify_loaded_store(store) -> dict[str, int]:
    """Check RDF identity and one-valued Assertion/Modifier component shape."""
    query = """
        SELECT (COUNT(?doc) AS ?document_uris)
               (SUM(?labels) AS ?source_labels)
               (SUM(IF(?labels > 1, 1, 0)) AS ?shared_document_uris)
        WHERE {
          {
            SELECT ?doc (COUNT(DISTINCT ?label) AS ?labels)
            WHERE {
              GRAPH ?g { ?doc <http://www.w3.org/2000/01/rdf-schema#label> ?label }
              FILTER(STRSTARTS(STR(?doc), "http://jurisynth/source/document/"))
            }
            GROUP BY ?doc
          }
        }
    """
    solutions = store.query(query)
    variables = [str(getattr(variable, "value", variable)) for variable in solutions.variables]
    rows = list(solutions)
    if len(rows) != 1:
        raise RuntimeError(f"Expected one store aggregate row, received {len(rows)}")
    counts = {name: int(str(getattr(value, "value", value))) for name, value in zip(variables, rows[0])}
    if counts["shared_document_uris"] != 0:
        raise RuntimeError(f"Rebuilt RDF still has shared document URIs: {counts['shared_document_uris']}")
    component_query = """
        SELECT ?property (COUNT(*) AS ?values) (COUNT(DISTINCT ?resource) AS ?resources)
        WHERE {
          VALUES ?property {
            <http://jurisynth/source/subject>
            <http://jurisynth/source/predicate>
            <http://jurisynth/source/object>
            <http://jurisynth/source/source_chunk>
            <http://jurisynth/source/value>
          }
          GRAPH <http://jurisynth/source/assertion/> { ?resource ?property ?value }
        }
        GROUP BY ?property
    """
    component_solutions = store.query(component_query)
    component_variables = [str(getattr(variable, "value", variable)) for variable in component_solutions.variables]
    for row in component_solutions:
        entry = {name: str(getattr(value, "value", value)) for name, value in zip(component_variables, row)}
        if int(entry["values"]) != int(entry["resources"]):
            raise RuntimeError(
                f"Rebuilt RDF has a multi-valued {entry['property']} component: "
                f"{entry['values']} values on {entry['resources']} resources"
            )
        counts[entry["property"].rsplit("/", 1)[-1] + "_resources"] = int(entry["resources"])
    return counts


def verify_store(store_path: Path) -> dict[str, int]:
    """Open a versioned Oxigraph store read-only and check source identity."""
    from pyoxigraph import Store

    return _verify_loaded_store(Store.read_only(str(store_path)))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check", "build", "merge", "verify"))
    parser.add_argument("--processed-root", type=Path, default=Path("jurisynth/kg_construction_pipeline/output"))
    parser.add_argument("--schema-dir", type=Path, default=Path("jurisynth/schema"))
    parser.add_argument("--destination", type=Path, default=Path("jurisynth/global_artifacts_source_uri_v2"))
    parser.add_argument("--batch", action="append", default=[], help="Build only this completed batch; repeat as needed")
    parser.add_argument("--resume", action="store_true", help="Skip rebuilt batches only after hash verification")
    args = parser.parse_args()
    if args.action == "check":
        result = check_inputs(args.processed_root)
    elif args.action == "build":
        result = build_batches(args.processed_root, args.schema_dir, args.destination, args.batch, resume=args.resume)
    elif args.action == "merge":
        result = merge_graphs(args.processed_root, args.destination)
    else:
        result = verify_store(args.destination / "oxigraph")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
