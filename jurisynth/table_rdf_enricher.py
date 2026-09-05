"""Minimal RDF provenance links for persisted Jurisynth table artifacts.

Table contents deliberately remain in the persisted JSON artifact.  This module
only creates a stable table resource and connects it to its source document and,
when supplied, source chunk.  It does not model rows, cells, headers, or any
table-specific ontology properties.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from rdflib import Dataset, Namespace, RDF, URIRef


JS_SOURCE = Namespace("http://jurisynth/source/")
DOCUMENT = Namespace("http://jurisynth/source/document/")
CHUNK = Namespace("http://jurisynth/source/chunk/")
TABLE = Namespace("http://jurisynth/source/table/")


def normalize_identifier(value: object) -> str:
    """Return the Graph Serializer-compatible URI fragment for an identifier."""
    text = re.sub(r"\.[^.]+$", "", str(value).strip().lower())
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def document_uri(doc_id: object) -> URIRef:
    return DOCUMENT[normalize_identifier(doc_id)]


def chunk_uri(doc_id: object, chunk_id: object) -> URIRef:
    return CHUNK[f"{normalize_identifier(doc_id)}_{normalize_identifier(chunk_id)}"]


def table_uri(doc_id: object, table_id: object) -> URIRef:
    """Return a stable table URI scoped by the original document identifier."""
    return TABLE[f"{normalize_identifier(doc_id)}_{normalize_identifier(table_id)}"]


def _validate_table_record(record: Mapping[str, Any]) -> tuple[str, str, str | None]:
    doc_id = record.get("doc_id")
    table_id = record.get("table_id")
    source_chunk_id = record.get("source_chunk_id")
    if doc_id is None or not str(doc_id).strip():
        raise ValueError("Table record requires a non-empty 'doc_id'.")
    if table_id is None or not str(table_id).strip():
        raise ValueError("Table record requires a non-empty 'table_id'.")
    if source_chunk_id is not None and not str(source_chunk_id).strip():
        raise ValueError("'source_chunk_id' must be non-empty when supplied.")
    return str(doc_id), str(table_id), None if source_chunk_id is None else str(source_chunk_id)


def enrich_dataset_with_tables(
    dataset: Dataset,
    table_records: Iterable[Mapping[str, Any]],
) -> Dataset:
    """Add minimal table provenance quads to an existing RDF dataset.

    Each table is represented in its document named graph. Repeated records are
    idempotent because RDF graphs are sets. A source-chunk link is emitted only
    when the persisted record gives an explicit, reliable chunk identifier.
    """
    dataset.bind("source", JS_SOURCE)
    dataset.bind("table", TABLE)

    for record in table_records:
        doc_id, table_id, source_chunk_id = _validate_table_record(record)
        document = document_uri(doc_id)
        table = table_uri(doc_id, table_id)
        graph = dataset.graph(document)

        graph.add((table, RDF.type, JS_SOURCE.Table))
        graph.add((document, JS_SOURCE.has_table, table))
        graph.add((table, JS_SOURCE.source_document, document))

        if source_chunk_id is not None:
            graph.add((table, JS_SOURCE.source_chunk, chunk_uri(doc_id, source_chunk_id)))

    return dataset


def load_table_records(table_store: str | Path) -> list[dict[str, Any]]:
    """Load documented persisted-table JSON files in deterministic path order."""
    table_store_path = Path(table_store)
    records: list[dict[str, Any]] = []
    for table_path in sorted(table_store_path.glob("*.json")):
        with table_path.open(encoding="utf-8") as handle:
            record = json.load(handle)
        if not isinstance(record, dict):
            raise ValueError(f"Table artifact is not a JSON object: {table_path}")
        records.append(record)
    return records


def enrich_dataset_from_table_store(dataset: Dataset, table_store: str | Path) -> Dataset:
    """Load table artifacts from *table_store* and enrich *dataset* in place."""
    return enrich_dataset_with_tables(dataset, load_table_records(table_store))
