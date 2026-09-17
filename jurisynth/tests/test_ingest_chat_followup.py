import json
from pathlib import Path
import pytest
from jurisynth.ingest_chat_followup import run

ROOT = Path('jurisynth/evaluation_artifacts/ai_assisted_review_v1/chat_adjudicated_v1')


def fixture_workspace(tmp_path, monkeypatch):
    source = ROOT/'followup_v2/CHAT_FOLLOWUP_COMPLETED.json'
    review = json.loads(source.read_text(encoding='utf-8'))
    target = tmp_path/ROOT
    target.mkdir(parents=True)
    for name in ('reviewed_nli_pairs.jsonl', 'reviewed_natural_cases.jsonl'):
        (target/name).write_bytes((ROOT/name).read_bytes())
    input_path = tmp_path/'review.json'
    input_path.write_text(json.dumps(review), encoding='utf-8')
    monkeypatch.chdir(tmp_path)
    return input_path, target, review


def test_import_preserves_originals_and_freezes_corrected_scope(tmp_path, monkeypatch):
    source, target, _ = fixture_workspace(tmp_path, monkeypatch)
    original = (target/'reviewed_nli_pairs.jsonl').read_bytes()
    run(source)
    assert (target/'reviewed_nli_pairs.jsonl').read_bytes() == original
    result = json.loads((target/'followup_v2/IMPORT_SUMMARY.json').read_text())
    assert result['corrected_premises'] == 18 and result['nli_pairs'] == 90
    with pytest.raises(FileExistsError):
        run(source)


@pytest.mark.parametrize('corruption', ['duplicate', 'hypothesis', 'table'])
def test_invalid_review_rejected_before_writes(tmp_path, monkeypatch, corruption):
    source, target, review = fixture_workspace(tmp_path, monkeypatch)
    if corruption == 'duplicate':
        review['qa_cases'].append(review['qa_cases'][0])
    elif corruption == 'hypothesis':
        review['nli_families'][0]['labels'][0][1] = 'changed hypothesis'
    else:
        next(c for c in review['qa_cases'] if c['support']['type'] == 'table_rows')['support']['rows'][0][0] = 'changed cell'
    source.write_text(json.dumps(review), encoding='utf-8')
    with pytest.raises(ValueError):
        run(source)
    assert not (target/'followup_v2').exists()
