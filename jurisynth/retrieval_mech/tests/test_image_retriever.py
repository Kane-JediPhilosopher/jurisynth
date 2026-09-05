"""Offline image-index adapter and visual-intent routing tests."""

import json

import faiss
import numpy as np
import pytest

from jurisynth.contracts import RetrievalRequest
from jurisynth.retrieval_mech.artifacts import ImageIndex
from jurisynth.retrieval_mech.mechanism import RetrievalMechanism


class FakeEmbedder:
    def encode(self, texts, **_kwargs):
        return np.asarray([[1.0, 0.0] for _text in texts], dtype=np.float32)


def _image_index(tmp_path):
    root = tmp_path / "batch_0009" / "image_index"
    root.mkdir(parents=True)
    index = faiss.IndexFlatIP(2)
    index.add(np.asarray([[1.0, 0.0]], dtype=np.float32))
    faiss.write_index(index, str(root / "image.index"))
    (root / "metadata.json").write_text(json.dumps({"metadata": [{
        "image_id": "doc:image:001", "document_id": "doc", "relative_path": "image_store/a.jpeg",
        "mime_type": "image/jpeg", "description": "A fishing chart", "legible_text": "gear",
        "source_url": "https://example.test/a", "alt": "Image",
    }]}), encoding="utf-8")
    return ImageIndex.load(root.parent)


@pytest.mark.asyncio
async def test_image_retrieval_is_off_for_ordinary_legal_questions(tmp_path):
    mechanism = RetrievalMechanism(FakeEmbedder(), image_indices=[_image_index(tmp_path)])
    bundle = await mechanism.retrieve_evidence(RetrievalRequest("q1", "What duties apply to the authority?"))
    assert bundle.image_evidence == []


@pytest.mark.asyncio
async def test_image_retrieval_is_auxiliary_for_visual_intent(tmp_path):
    mechanism = RetrievalMechanism(FakeEmbedder(), image_indices=[_image_index(tmp_path)])
    bundle = await mechanism.retrieve_evidence(RetrievalRequest("q1", "What does the fishing diagram show?"))
    assert [item.image_id for item in bundle.image_evidence] == ["doc:image:001"]
    assert bundle.status == "empty"
    assert bundle.retrieval_metadata["image_matches"][0]["document_id"] == "doc"
