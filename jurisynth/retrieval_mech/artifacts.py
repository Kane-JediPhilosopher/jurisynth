"""Load and query persisted preprocessing/KG retrieval artifacts without rebuilding them."""

from __future__ import annotations

import json
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import numpy as np

try:
    import faiss
except ModuleNotFoundError:  # Keep contracts/imports usable without the optional runtime.
    faiss = None

from jurisynth.contracts import ImageEvidence, SourceChunk, TableEvidence


class Embedder(Protocol):
    def encode(self, texts: list[str], *, normalize_embeddings: bool = True, **kwargs: object) -> object: ...


def _query_vector(embedder: Embedder, query: str) -> np.ndarray:
    vector = np.asarray(
        embedder.encode([query], normalize_embeddings=True), dtype=np.float32
    )
    if vector.ndim != 2 or vector.shape[0] != 1:
        raise ValueError("embedder must return one two-dimensional query vector")
    return vector


def _require_faiss() -> Any:
    if faiss is None:
        raise RuntimeError(
            "FAISS is required to load or search persisted retrieval indices. "
            "Run Jurisynth in its configured Conda environment."
        )
    return faiss


@dataclass(slots=True)
class ChunkIndex:
    index: Any
    metadata: dict[int, dict[str, str]]

    @classmethod
    def load(cls, index_path: Path, metadata_path: Path) -> "ChunkIndex":
        with metadata_path.open("rb") as file:
            raw_metadata = pickle.load(file)
        return cls(
            index=_require_faiss().read_index(str(index_path)),
            metadata={int(key): value for key, value in raw_metadata.items()},
        )

    def search(self, query: str, embedder: Embedder, top_k: int) -> list[SourceChunk]:
        scores, ids = self.index.search(_query_vector(embedder, query), min(top_k, self.index.ntotal))
        hits: list[SourceChunk] = []
        for score, vector_id in zip(scores[0], ids[0]):
            if vector_id < 0:
                continue
            item = self.metadata[int(vector_id)]
            hits.append(SourceChunk(
                chunk_id=item["chunk_id"], document_id=item["doc_id"],
                text=item["content"], similarity=float(score),
            ))
        return hits


@dataclass(slots=True)
class TableIndex:
    """Lazy row-index access; row FAISS files are only opened for top tables."""

    root: Path
    table_index: Any
    table_metadata: list[dict[str, str]]
    row_metadata: dict[str, list[dict[str, object]]]
    table_store: Path | None = None

    @classmethod
    def load(
        cls,
        batch_dir: Path,
        *,
        index_dir: Path | None = None,
        table_store: Path | None = None,
    ) -> "TableIndex":
        index_dir = index_dir or batch_dir / "table_index"
        with (index_dir / "table_metadata.json").open(encoding="utf-8") as file:
            table_metadata = json.load(file)
        with (index_dir / "row_metadata.json").open(encoding="utf-8") as file:
            row_metadata = json.load(file)
        return cls(
            batch_dir,
            _require_faiss().read_index(str(index_dir / "table.index")),
            table_metadata,
            row_metadata,
            table_store or batch_dir / "table_store",
        )

    def search(
        self,
        query: str,
        embedder: Embedder,
        table_top_k: int,
        row_top_k: int,
        *,
        document_ids: set[str] | None = None,
    ) -> list[TableEvidence]:
        query_vector = _query_vector(embedder, query)
        candidate_count = self.table_index.ntotal if document_ids is not None else min(table_top_k, self.table_index.ntotal)
        table_scores, table_ids = self.table_index.search(query_vector, candidate_count)
        hits: list[TableEvidence] = []
        selected_tables = 0
        for table_score, table_vector_id in zip(table_scores[0], table_ids[0]):
            if table_vector_id < 0:
                continue
            table = self.table_metadata[int(table_vector_id)]
            if document_ids is not None and table["doc_id"] not in document_ids:
                continue
            selected_tables += 1
            key = f"{table['doc_id']}__{table['table_id']}"
            row_index_path = self.root / "table_index" / "rows" / f"{key}.index"
            if not row_index_path.exists() or key not in self.row_metadata:
                continue
            row_index = _require_faiss().read_index(str(row_index_path))
            row_scores, row_ids = row_index.search(query_vector, min(row_top_k, row_index.ntotal))
            source = self._load_table(table["doc_id"], table["table_id"])
            for row_score, row_vector_id in zip(row_scores[0], row_ids[0]):
                if row_vector_id < 0:
                    continue
                row_id = int(self.row_metadata[key][int(row_vector_id)]["row_id"])
                rows = source.get("data") or []
                if row_id >= len(rows):
                    continue
                hits.append(TableEvidence(
                    table_id=table["table_id"], document_id=table["doc_id"],
                    headers=source.get("header"), matched_rows=[rows[row_id]], row_ids=[row_id],
                    table_score=float(table_score), row_score=float(row_score),
                    combined_score=float(table_score * row_score),
                ))
            if selected_tables >= table_top_k:
                break
        return sorted(hits, key=lambda item: item.combined_score or 0.0, reverse=True)

    def _load_table(self, document_id: str, table_id: str) -> dict[str, object]:
        path = (self.table_store or self.root / "table_store") / f"{document_id}_{table_id}.json"
        with path.open(encoding="utf-8") as file:
            return json.load(file)


@dataclass(slots=True)
class ImageIndex:
    """Per-batch FAISS index over non-authoritative visual descriptions."""

    index: Any
    metadata: list[dict[str, object]]

    @classmethod
    def load(cls, batch_dir: Path, *, index_dir: Path | None = None) -> "ImageIndex":
        index_dir = index_dir or batch_dir / "image_index"
        manifest = json.loads((index_dir / "metadata.json").read_text(encoding="utf-8"))
        metadata = manifest.get("metadata")
        if not isinstance(metadata, list):
            raise ValueError("Image index metadata must contain a list of records.")
        index = _require_faiss().read_index(str(index_dir / "image.index"))
        if index.ntotal != len(metadata):
            raise ValueError("Image index/metadata cardinality mismatch.")
        return cls(index, metadata)

    def search(self, query: str, embedder: Embedder, top_k: int) -> list[ImageEvidence]:
        scores, ids = self.index.search(_query_vector(embedder, query), min(top_k, self.index.ntotal))
        hits: list[ImageEvidence] = []
        for score, vector_id in zip(scores[0], ids[0]):
            if vector_id < 0:
                continue
            item = self.metadata[int(vector_id)]
            hits.append(ImageEvidence(
                image_id=str(item["image_id"]), document_id=str(item["document_id"]),
                relative_path=str(item["relative_path"]), mime_type=str(item["mime_type"]),
                description=str(item["description"]), legible_text=str(item.get("legible_text", "")),
                similarity=float(score), source_url=item.get("source_url") if isinstance(item.get("source_url"), str) else None,
                alt=item.get("alt") if isinstance(item.get("alt"), str) else None,
            ))
        return hits
