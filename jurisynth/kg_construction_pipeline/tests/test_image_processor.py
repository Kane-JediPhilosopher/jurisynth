"""Unit tests for the opt-in image-description/index stage; no NIM calls."""

import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import patch

import faiss
import numpy as np


PIPELINE_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PIPELINE_SRC) not in sys.path:
    sys.path.insert(0, str(PIPELINE_SRC))

from image_processor import ImageAsset, _parse_description, describe_assets, load_image_assets, write_image_index
from vision_llm_utils import VisionNIMConfig, create_vision_client


class FakeDescriber:
    async def describe(self, asset):
        return {"description": f"diagram for {asset.document_id}", "image_type": "diagram", "legible_text": "Annex I"}


class FakeEmbedder:
    def encode(self, texts, **_kwargs):
        return np.asarray([[float(len(text)), 1.0] for text in texts], dtype=np.float32)


def test_vision_client_accepts_explicit_nano_configuration_without_reusing_ultra_model():
    config = VisionNIMConfig("test-key", "https://example.test/v1", "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning")
    with patch("vision_llm_utils.openai.AsyncOpenAI") as client:
        result = create_vision_client(config)

    client.assert_called_once_with(
        base_url="https://example.test/v1", api_key="test-key", max_retries=0
    )
    assert result is client.return_value


def test_load_image_assets_uses_manifest_provenance_and_skips_invalid_entries(tmp_path):
    store = tmp_path / "image_store"
    store.mkdir()
    (store / "doc_1_image_001.jpeg").write_bytes(b"image")
    (store / "doc_1.json").write_text(json.dumps([
        {"status": "success", "filename": "doc_1_image_001.jpeg", "mime_type": "image/jpeg", "sha256": "abc", "source_url": "https://example.test/a"},
        {"status": "failed", "filename": "nope.jpeg", "mime_type": "image/jpeg"},
        {"status": "success", "filename": "missing.svg", "mime_type": "image/svg+xml"},
    ]), encoding="utf-8")

    assets = load_image_assets(store)

    assert len(assets) == 1
    assert assets[0].image_id == "doc_1:image:001"
    assert assets[0].sha256 == "abc"


def test_description_parser_enforces_bounded_retrieval_text():
    raw = json.dumps({
        "description": " ".join(f"description{i}" for i in range(120)),
        "image_type": "scan",
        "legible_text": " ".join(f"text{i}" for i in range(90)),
    })

    parsed = _parse_description(raw)

    assert len(parsed["description"].split()) == 110
    assert len(parsed["legible_text"].split()) == 80


def test_description_records_preserve_relative_provenance(tmp_path):
    batch = tmp_path / "batch_0009"
    image = batch / "image_store" / "doc_1_image_001.jpeg"
    image.parent.mkdir(parents=True)
    image.write_bytes(b"image")
    asset = ImageAsset("doc_1:image:001", "doc_1", image.name, image, "image/jpeg", "abc", None, "Image")

    records = asyncio.run(describe_assets([asset], FakeDescriber(), batch_dir=batch))

    assert records[0].status == "success"
    assert records[0].relative_path == "image_store/doc_1_image_001.jpeg"
    assert records[0].description == "diagram for doc_1"


def test_write_image_index_persists_description_records_and_faiss_lookup(tmp_path):
    batch = tmp_path / "batch_0009"
    image = batch / "image_store" / "doc_1_image_001.jpeg"
    image.parent.mkdir(parents=True)
    image.write_bytes(b"image")
    asset = ImageAsset("doc_1:image:001", "doc_1", image.name, image, "image/jpeg", "abc", None, None)
    records = asyncio.run(describe_assets([asset], FakeDescriber(), batch_dir=batch))

    result = write_image_index(records, batch / "image_index", FakeEmbedder(), embedding_model_id="fake-v1")
    manifest = json.loads((batch / "image_index" / "metadata.json").read_text(encoding="utf-8"))
    index = faiss.read_index(str(batch / "image_index" / "image.index"))

    assert result == {"records": 1, "indexed": 1, "errors": 0}
    assert manifest["embedding_model"] == "fake-v1"
    assert manifest["metadata"][0]["image_id"] == "doc_1:image:001"
    assert index.ntotal == 1
