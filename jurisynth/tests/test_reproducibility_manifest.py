import json

from jurisynth.reproducibility_manifest import write_manifest


def test_manifest_hashes_artifacts_and_never_needs_secrets(tmp_path):
    artifact = tmp_path / "artifact.json"
    artifact.write_text("pilot", encoding="utf-8")
    destination = tmp_path / "manifest.json"
    write_manifest(destination, artifacts={"pilot": artifact}, commands=["python -m jurisynth.run_pilot_evaluation"], models={"embedder": "all-MiniLM-L6-v2"}, config={"top_k": 5})
    payload = json.loads(destination.read_text(encoding="utf-8"))
    assert payload["artifacts"]["pilot"]["sha256"]
    assert "api_key" not in json.dumps(payload).lower()
