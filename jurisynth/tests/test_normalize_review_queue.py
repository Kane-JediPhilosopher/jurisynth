import json

from jurisynth.normalize_review_queue import normalise_queue


def test_normalise_queue_repairs_only_missing_human_review_brace(tmp_path):
    source = tmp_path / "source.jsonl"
    destination = tmp_path / "normalised.jsonl"
    source.write_text(
        '{"case":{"id":"one"},"human_review":{"status":"yes"},"result":{"ok":true}}\n'
        '{"case":{"id":"two"},"human_review":{"status":"no", "result":{"ok":false}}\n',
        encoding="utf-8",
    )

    assert normalise_queue(source, destination) == 1
    records = [json.loads(line) for line in destination.read_text(encoding="utf-8").splitlines()]
    assert records[0]["human_review"]["status"] == "yes"
    assert records[1]["result"]["ok"] is False
