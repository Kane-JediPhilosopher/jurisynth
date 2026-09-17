"""Create an independent, source-first pool for global natural-question drafting.

This deliberately samples legal-provision language from the chunk sidecar. It
does not consume prior smoke queries, RDF triples, LLM output, or retrieval
scores. The pool is a drafting aid only; a reviewer must still approve every
question and expected source before it becomes an evaluation case.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


_STRATA = {
    "obligations_prohibitions": ("%shall%", "%shall not%"),
    "definitions_scope": ("% means %", "%for the purposes%"),
    "procedures_deadlines": ("%within %", "%shall submit%", "%shall notify%"),
}


def sample_sources(database: Path, *, per_stratum: int = 24, modulus: int = 211, residue: int = 17) -> dict[str, object]:
    connection = sqlite3.connect(database)
    try:
        output: dict[str, list[dict[str, str]]] = {}
        for stratum, patterns in _STRATA.items():
            selected: list[dict[str, str]] = []
            seen_documents: set[str] = set()
            for pattern in patterns:
                rows = connection.execute(
                    """
                    SELECT doc_id, chunk_id, content
                    FROM chunks
                    WHERE lower(content) LIKE ?
                      AND vector_id % ? = ?
                    ORDER BY vector_id
                    LIMIT ?
                    """,
                    (pattern, modulus, residue, per_stratum * 8),
                )
                for document_id, chunk_id, content in rows:
                    if document_id in seen_documents or _excluded_topic(content):
                        continue
                    selected.append({
                        "document_id": str(document_id),
                        "chunk_id": str(chunk_id),
                        "excerpt": _excerpt(str(content)),
                    })
                    seen_documents.add(str(document_id))
                    if len(selected) == per_stratum:
                        break
                if len(selected) == per_stratum:
                    break
            output[stratum] = selected
        return {
            "method": "deterministic source-text sampling; independent of prior global smoke queries and retrieval scores",
            "parameters": {"per_stratum": per_stratum, "modulus": modulus, "residue": residue},
            "strata": output,
        }
    finally:
        connection.close()


def _excluded_topic(content: str) -> bool:
    value = content.casefold()
    return "artificial intelligence act" in value or "general data protection regulation" in value


def _excerpt(content: str, limit: int = 1_100) -> str:
    return " ".join(content.split())[:limit]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=Path("jurisynth/global_artifacts/chunk_index/chunk_metadata.sqlite"))
    parser.add_argument("--per-stratum", type=int, default=24)
    parser.add_argument("--output", type=Path, default=Path("jurisynth/evaluation_artifacts/global_source_first_pool.json"))
    args = parser.parse_args()
    payload = sample_sources(args.database, per_stratum=args.per_stratum)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: len(value) for key, value in payload["strata"].items()}, indent=2))


if __name__ == "__main__":
    main()
