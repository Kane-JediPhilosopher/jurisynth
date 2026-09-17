"""Summarize document-ID families and apparent years without mutating corpus metadata."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sqlite3


def family(doc_id: str) -> str:
    lower = doc_id.lower()
    if lower.startswith("jol_"):
        return "JOL"
    if lower.startswith("l_"):
        return "OJ_L"
    if lower.startswith("c_"):
        return "OJ_C"
    if re.match(r"m\d", lower):
        return "merger_m"
    if re.match(r"\d", lower):
        return "numeric_CELEX_like"
    return "other"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=Path("jurisynth/global_artifacts/chunk_index/chunk_metadata.sqlite"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    connection = sqlite3.connect(f"file:{args.database.as_posix()}?mode=ro", uri=True)
    document_chunks: Counter[str] = Counter()
    try:
        document_chunks.update(dict(connection.execute("SELECT doc_id, COUNT(*) FROM chunks GROUP BY doc_id")))
    finally:
        connection.close()
    family_documents: Counter[str] = Counter()
    family_chunks: Counter[str] = Counter()
    year_documents: Counter[str] = Counter()
    year_chunks: Counter[str] = Counter()
    no_year = 0
    for doc_id, chunks in document_chunks.items():
        group = family(doc_id)
        family_documents[group] += 1
        family_chunks[group] += chunks
        match = re.search(r"(?:19|20)\d{2}", doc_id)
        if match:
            year_documents[match.group()] += 1
            year_chunks[match.group()] += chunks
        else:
            no_year += 1
    payload = {
        "family_documents": dict(family_documents.most_common()),
        "family_chunks": dict(family_chunks.most_common()),
        "year_documents": dict(sorted(year_documents.items())),
        "year_chunks": dict(sorted(year_chunks.items())),
        "documents_without_apparent_year": no_year,
    }
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"family_documents": payload["family_documents"], "documents_without_apparent_year": no_year}, indent=2))


if __name__ == "__main__":
    main()
