import json
from types import SimpleNamespace

from jurisynth.run_bounded_global_smokes import interrupt_stale_run, terminate_owned_tree


def test_no_deadline_reuses_gate_and_runs_globals_serially(tmp_path, monkeypatch):
    import jurisynth.run_bounded_global_smokes as module
    from pathlib import Path
    monkeypatch.chdir(tmp_path)
    gate = tmp_path/'passed.json'
    gate.write_text('{"status":"success","cases":[{"variant":"messy"}]}', encoding='utf-8')
    waits, commands = [], []
    monkeypatch.setattr(module.psutil, 'virtual_memory', lambda: SimpleNamespace(available=10*1024**3))
    def launch(arguments, **kwargs):
        commands.append(arguments)
        Path(arguments[arguments.index('--output')+1]).write_text('{"status":"success"}', encoding='utf-8')
        return SimpleNamespace(pid=123, returncode=0, wait=lambda timeout: waits.append(timeout))
    monkeypatch.setattr(module.subprocess, 'Popen', launch)
    module.run(10, query_timeout_seconds=0, passed_format_output=gate)
    assert len(commands) == 2 and waits == [None, None]
    assert all(c[c.index('--query-timeout-seconds')+1] == '0' for c in commands)
    summary = json.loads(Path('jurisynth/run_outputs/bounded_global_smokes_v10.json').read_text())
    assert summary['query_timeout_seconds'] is None and summary['process_watchdog_seconds'] is None
    assert [r['variant'] for r in summary['runs']] == ['messy', 'organized']


def test_failed_component_cannot_be_reused(tmp_path, monkeypatch):
    import jurisynth.run_bounded_global_smokes as module
    import pytest
    monkeypatch.chdir(tmp_path)
    gate = tmp_path/'failed.json'
    gate.write_text('{"status":"failed"}', encoding='utf-8')
    with pytest.raises(ValueError, match='successful messy'):
        module.run(10, query_timeout_seconds=0, passed_format_output=gate)


def test_smoke_disables_only_transport_deadline(tmp_path, monkeypatch):
    import jurisynth.run_bounded_global_smokes as module
    from pathlib import Path
    monkeypatch.chdir(tmp_path)
    commands = []
    def launch(arguments, **kwargs):
        commands.append(arguments)
        output = Path(arguments[arguments.index('--output')+1])
        output.write_text('{"status":"failed"}', encoding='utf-8')
        return SimpleNamespace(pid=123, returncode=0, wait=lambda timeout: 0)
    monkeypatch.setattr(module.subprocess, 'Popen', launch)
    module.run(9)
    command = commands[0]
    assert command[command.index('--request-timeout-seconds')+1] == '0'
    assert command[command.index('--query-timeout-seconds')+1] == '900'
    summary = json.loads(Path('jurisynth/run_outputs/bounded_global_smokes_v9.json').read_text())
    assert summary['request_timeout_seconds'] is None
    assert summary['process_watchdog_seconds'] == 930


def test_exited_child_running_output_is_interrupted(tmp_path):
    from jurisynth.run_bounded_global_smokes import finalized_result
    path = tmp_path/'result.json'
    path.write_text('{"status":"running"}', encoding='utf-8')
    assert finalized_result(path, 1)['status'] == 'interrupted'


def test_malformed_child_output_is_failure(tmp_path):
    from jurisynth.run_bounded_global_smokes import finalized_result
    path = tmp_path/'result.json'
    path.write_text('broken', encoding='utf-8')
    assert finalized_result(path, 1)['status'] == 'failed_before_valid_output'


def test_preflight_refusal_does_not_create_running_summary(tmp_path, monkeypatch):
    from jurisynth.run_bounded_global_smokes import run
    import pytest
    monkeypatch.chdir(tmp_path)
    root = tmp_path/'jurisynth/run_outputs'
    root.mkdir(parents=True)
    (root/'structured_output_smoke_v2.json').write_text('{}', encoding='utf-8')
    with pytest.raises(FileExistsError):
        run(7)
    assert not (root/'bounded_global_smokes_v7.json').exists()


def test_stale_running_is_not_treated_as_continuous_runtime(tmp_path):
    output = tmp_path/'run.json'
    output.write_text(json.dumps({'status': 'running', 'started_at': 'earlier'}), encoding='utf-8')
    interrupt_stale_run(output)
    result = json.loads(output.read_text(encoding='utf-8'))
    assert result['status'] == 'interrupted'
    assert result['elapsed_seconds'] is None and result['runtime_not_recoverable']


def test_watchdog_terminates_only_owned_parent_and_descendants(monkeypatch):
    import jurisynth.run_bounded_global_smokes as module
    killed = []
    child = SimpleNamespace(terminate=lambda: killed.append('child'), kill=lambda: None)
    parent = SimpleNamespace(children=lambda recursive: [child], terminate=lambda: killed.append('parent'))
    monkeypatch.setattr(module.psutil, 'Process', lambda pid: parent)
    monkeypatch.setattr(module.psutil, 'wait_procs', lambda targets, timeout: (targets, []))
    terminate_owned_tree(SimpleNamespace(pid=123))
    assert killed == ['child', 'parent']
