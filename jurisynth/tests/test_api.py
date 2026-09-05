import asyncio

from fastapi.testclient import TestClient

from jurisynth.api import create_app, dossier_from_workflow


def test_health_and_unconfigured_query_boundary():
    client = TestClient(create_app())
    assert client.get("/api/v1/health").json() == {"status": "ok", "live_query_enabled": False}
    response = client.post("/api/v1/query", json={"query": "What obligations apply?"})
    assert response.status_code == 503
    assert "not configured" in response.json()["detail"]


def test_query_runner_returns_progressive_disclosure_payload():
    class Result:
        presentation = {"overview": "A grounded answer.", "sections": [{"section_id": "s1"}], "contradiction_refs": []}
        report = None

    async def runner(query):
        assert query == "What obligations apply?"
        return Result()

    client = TestClient(create_app(runner=runner))
    payload = client.post("/api/v1/query", json={"query": "What obligations apply?"}).json()
    assert payload["overview"] == "A grounded answer."
    assert payload["sections"] == [{"section_id": "s1"}]
    assert payload["status"] == "complete"


def test_dossier_adapter_handles_missing_presentation():
    class Report:
        overview = "Fallback overview"

    class Result:
        presentation = None
        report = Report()

    assert dossier_from_workflow(Result(), "q")["overview"] == "Fallback overview"
