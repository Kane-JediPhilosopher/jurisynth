import asyncio
import json

from fastapi.testclient import TestClient

from jurisynth.api import LocalImageResolver, create_app, dossier_from_workflow


def test_health_and_unconfigured_query_boundary():
    client = TestClient(create_app())
    assert client.get("/api/v1/health").json() == {"status": "ok", "live_query_enabled": False}
    response = client.post("/api/v1/query", json={"query": "What obligations apply?"})
    assert response.status_code == 503
    assert "not configured" in response.json()["detail"]


def test_query_runner_returns_progressive_disclosure_payload():
    class Result:
        presentation = {"overview": "A grounded answer.", "sections": [{"section_id": "s1"}], "contradiction_refs": [], "auxiliary_images": [{"image_id": "i1", "auxiliary_only": True}]}
        report = None

    async def runner(query):
        assert query == "What obligations apply?"
        return Result()

    client = TestClient(create_app(runner=runner))
    payload = client.post("/api/v1/query", json={"query": "What obligations apply?"}).json()
    assert payload["overview"] == "A grounded answer."
    assert payload["sections"] == [{"section_id": "s1"}]
    assert payload["status"] == "complete"
    assert payload["auxiliary_images"] == [{"image_id": "i1", "auxiliary_only": True}]


def test_dossier_adapter_handles_missing_presentation():
    class Report:
        overview = "Fallback overview"

    class Result:
        presentation = None
        report = Report()

    assert dossier_from_workflow(Result(), "q")["overview"] == "Fallback overview"


def test_image_route_serves_only_manifest_indexed_file_under_approved_root(tmp_path):
    root = tmp_path / "batch"
    image = root / "image_store" / "one.png"
    image.parent.mkdir(parents=True)
    image.write_bytes(b"png bytes")
    index = root / "image_index"
    index.mkdir()
    (index / "metadata.json").write_text(json.dumps({"metadata": [
        {"image_id": "doc:image:001", "relative_path": "image_store/one.png", "mime_type": "image/png"},
        {"image_id": "escape", "relative_path": "../outside.png", "mime_type": "image/png"},
    ]}), encoding="utf-8")
    client = TestClient(create_app(image_resolver=LocalImageResolver([(root, index)])))
    response = client.get("/api/v1/images/doc:image:001")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content == b"png bytes"
    assert client.get("/api/v1/images/escape").status_code == 404
    assert client.get("/api/v1/images/../image_store/one.png").status_code == 404
