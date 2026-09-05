"""Inspect whether a pilot question is lexically represented in Jurisynth artifacts.

This is a corpus-coverage diagnostic, not a legal-answering component.  It
helps distinguish an unsupported question from a retrieval failure before
interpreting evaluation outcomes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from jurisynth.retrieval_mech.artifacts import ChunkIndex


def inspect_coverage(
    terms: Iterable[str],
    *,
    processed_batch: str | Path,
    er_index: str | Path,
    max_hits: int = 5,
) -> dict[str, object]:
    """Report lexical support in source chunks and persisted E-R labels."""
    cleaned_terms = [term.strip() for term in terms if term.strip()]
    if not cleaned_terms:
        raise ValueError("Provide at least one non-empty term.")
    if max_hits < 1:
        raise ValueError("max_hits must be positive.")

    processed = Path(processed_batch)
    chunks = ChunkIndex.load(
        processed / "chunk_index" / "chunk_index.faiss",
        processed / "chunk_index" / "chunk_metadata.pkl",
    )
    records = _load_er_records(Path(er_index) / "metadata.json")
    return {
        "processed_batch": str(processed),
        "chunk_count": len(chunks.metadata),
        "document_count": len({item["doc_id"] for item in chunks.metadata.values()}),
        "terms": [
            {
                "term": term,
                "chunk_hits": _lexical_chunk_hits(term, chunks.metadata.values(), max_hits=max_hits),
                "entity_label_hits": _label_hits(term, records["entities"], max_hits=max_hits),
                "relation_label_hits": _label_hits(term, records["relations"], max_hits=max_hits),
            }
            for term in cleaned_terms
        ],
        "interpretation": "No lexical hit means this pilot cannot establish coverage for that term; it does not prove the law is absent from the full corpus.",
    }


def _load_er_records(path: Path) -> dict[str, list[dict[str, object]]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {
        "entities": list(payload.get("entities", [])),
        "relations": list(payload.get("relations", [])),
    }


def _lexical_chunk_hits(term: str, chunks: Iterable[dict[str, str]], *, max_hits: int) -> list[dict[str, str]]:
    needle = term.casefold()
    hits: list[dict[str, str]] = []
    for item in chunks:
        text = item.get("content", "")
        position = text.casefold().find(needle)
        if position < 0:
            continue
        start = max(0, position - 180)
        end = min(len(text), position + len(term) + 320)
        hits.append({
            "document_id": item["doc_id"],
            "chunk_id": item["chunk_id"],
            "text_excerpt": text[start:end],
        })
        if len(hits) >= max_hits:
            break
    return hits


def _label_hits(term: str, records: Iterable[dict[str, object]], *, max_hits: int) -> list[dict[str, str]]:
    needle = term.casefold()
    hits: list[dict[str, str]] = []
    for record in records:
        label = str(record.get("label", ""))
        if needle not in label.casefold():
            continue
        hits.append({"uri": str(record.get("uri", "")), "label": label})
        if len(hits) >= max_hits:
            break
    return hits


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect lexical coverage in the batch_0009 Jurisynth pilot.")
    parser.add_argument("terms", nargs="+", help="Terms or phrases to check before evaluating a question.")
    parser.add_argument("--processed-batch", type=Path, default=Path("jurisynth/kg_construction_pipeline/output/batch_0009"))
    parser.add_argument("--er-index", type=Path, default=Path("jurisynth/pilot_artifacts/batch_0009/er_index"))
    parser.add_argument("--max-hits", type=int, default=5)
    parser.add_argument("--output", type=Path, help="Optional UTF-8 JSON destination.")
    return parser


def main() -> None:
    args = _parser().parse_args()
    result = inspect_coverage(args.terms, processed_batch=args.processed_batch, er_index=args.er_index, max_hits=args.max_hits)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(json.dumps({"output": str(args.output)}, indent=2))
    else:
        print(rendered)


if __name__ == "__main__":
    main()
