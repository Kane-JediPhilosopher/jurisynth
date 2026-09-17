"""Offline contract tests for lazy visual expansion; no NIM calls."""

import asyncio
from pathlib import Path

from jurisynth.contracts import ImageEvidence
from jurisynth.retrieval_mech import image_expander
from jurisynth.retrieval_mech.image_expander import ImageExpander
from vision_llm_utils import VisionNIMConfig


class _Completions:
    def __init__(self):
        self.calls = 0

    async def create(self, **_kwargs):
        self.calls += 1
        message = type("Message", (), {"content": '{"expanded_description":"A labelled form with two fields.","visual_findings":["Two visible labels"],"relevance":0.75}'})
        return type("Response", (), {"choices": [type("Choice", (), {"message": message})]})


class FakeClient:
    def __init__(self):
        self.chat = type("Chat", (), {"completions": _Completions()})()

    async def close(self):
        pass


def test_expander_preserves_canonical_similarity_and_caches_query_result(tmp_path):
    root = Path(tmp_path)
    path = root / "image_store" / "form.png"
    path.parent.mkdir()
    path.write_bytes(b"not-a-real-png")
    client = FakeClient()
    expander = ImageExpander(root, client=client, config=VisionNIMConfig("test", "https://example.test/v1", "test-model"))
    image = ImageEvidence("doc:image:001", "doc", "image_store/form.png", "image/png", "A form", "", similarity=0.42)

    first = asyncio.run(expander.expand([image], "What fields does this form show?"))[0]
    second = asyncio.run(expander.expand([image], "What fields does this form show?"))[0]

    assert first.similarity == 0.42
    assert first.expanded_description == "A labelled form with two fields."
    assert first.expansion_relevance == 0.75
    assert client.chat.completions.calls == 1


def test_expander_ignores_path_outside_approved_root(tmp_path):
    root = Path(tmp_path) / "batch"
    root.mkdir()
    expander = ImageExpander(root, client=FakeClient(), config=VisionNIMConfig("test", "https://example.test/v1", "test-model"))
    image = ImageEvidence("x", "doc", "../outside.png", "image/png", "Description", "")

    assert asyncio.run(expander.expand([image], "Explain this diagram.")) == [image]


def test_expander_retries_retryable_provider_failure_indefinitely_until_success(tmp_path, monkeypatch):
    root = Path(tmp_path)
    path = root / "image_store" / "form.png"
    path.parent.mkdir()
    path.write_bytes(b"image")
    client = FakeClient()
    original_create = client.chat.completions.create
    calls = 0

    async def create(**kwargs):
        nonlocal calls
        calls += 1
        if calls == 1:
            raise RuntimeError("503 Service Unavailable")
        return await original_create(**kwargs)

    client.chat.completions.create = create
    monkeypatch.setattr(image_expander, "_retry_delay", lambda _exc, _attempt: 0)
    expander = ImageExpander(root, client=client, config=VisionNIMConfig("test", "https://example.test/v1", "test-model"), requests_per_second=1000)
    image = ImageEvidence("doc:image:001", "doc", "image_store/form.png", "image/png", "A form", "")

    result = asyncio.run(expander.expand([image], "What fields are visible?"))[0]

    assert result.expanded_description == "A labelled form with two fields."
    assert calls == 2
