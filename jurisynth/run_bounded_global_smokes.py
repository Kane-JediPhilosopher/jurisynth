"""Run two global smokes serially with an independent process-tree watchdog."""
from __future__ import annotations

import json
import argparse
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import psutil


def interrupt_stale_run(path: Path):
    if not path.exists():
        return
    payload = json.loads(path.read_text(encoding='utf-8'))
    if payload.get('status') == 'running':
        payload.update(status='interrupted', interrupted_at=datetime.now(timezone.utc).isoformat(),
                       interruption_reason='No matching smoke/queue process remained when checked; prior running status was stale.',
                       elapsed_seconds=None, runtime_not_recoverable=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def terminate_owned_tree(process):
    try:
        parent = psutil.Process(process.pid)
        descendants = parent.children(recursive=True)
        for child in reversed(descendants):
            try:
                child.terminate()
            except psutil.NoSuchProcess:
                pass
        parent.terminate()
        _, alive = psutil.wait_procs(descendants+[parent], timeout=5)
        for child in alive:
            try:
                child.kill()
            except psutil.NoSuchProcess:
                pass
    except psutil.NoSuchProcess:
        pass


def _run(version=7, query_timeout_seconds=900, passed_format_output=None):
    root = Path('jurisynth/run_outputs')
    root.mkdir(parents=True, exist_ok=True)
    summary_path = root/f'bounded_global_smokes_v{version}.json'
    if summary_path.exists():
        raise FileExistsError(f'Refusing to overwrite watchdog summary: {summary_path}')
    summary = {'status': 'running', 'started_at': datetime.now(timezone.utc).isoformat(),
               'request_timeout_seconds': None, 'query_timeout_seconds': query_timeout_seconds or None,
               'process_watchdog_seconds': query_timeout_seconds+30 if query_timeout_seconds else None, 'runs': []}
    def persist():
        summary_path.write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    # Retest the last stalled API path first, without loading global artifacts.
    format_output = root/f'structured_output_smoke_v{version-5}.json'
    if passed_format_output is None and format_output.exists():
        raise FileExistsError(f'Refusing to overwrite prior format smoke: {format_output}')
    persist()
    if passed_format_output is not None:
        format_result = json.loads(Path(passed_format_output).read_text(encoding='utf-8'))
        if format_result.get('status') != 'success' or not any(c.get('variant') == 'messy' for c in format_result.get('cases', [])):
            raise ValueError('Reused format gate must contain a successful messy component case.')
        summary['reused_format_output'] = str(passed_format_output)
    else:
        format_result = run_format_gate(format_output, query_timeout_seconds, summary, persist)
    summary['format_smoke_status'] = format_result['status']
    summary.pop('active_process_id', None)
    summary.pop('active_variant', None)
    persist()
    if format_result['status'] != 'success':
        summary.update(status='stopped_format_smoke_failed')
        persist()
        return
    for variant in ('messy', 'organized'):
        if psutil.virtual_memory().available/1024**3 < 5.5:
            summary.pop('active_variant', None)
            summary.update(status='paused_insufficient_memory', pending_variant=variant)
            persist()
            return
        output = root/f'global_complex_ai_medical_{variant}_bounded_v{version}.json'
        if output.exists():
            raise FileExistsError(f'Refusing to overwrite prior bounded smoke: {output}')
        started = time.perf_counter()
        arguments = [sys.executable, '-m', 'jurisynth.run_global_smoke', '--query-file',
            f'jurisynth/evaluation_artifacts/complex_ai_medical_{variant}.txt',
            '--minimum-available-gb', '5.5', '--request-timeout-seconds', '0',
            '--query-timeout-seconds', str(query_timeout_seconds), '--output', str(output)]
        with (root/f'global_complex_{variant}_v{version}.out.log').open('w', encoding='utf-8') as stdout, \
             (root/f'global_complex_{variant}_v{version}.err.log').open('w', encoding='utf-8') as stderr:
            process = subprocess.Popen(arguments, stdout=stdout, stderr=stderr)
            summary['active_variant'] = variant
            summary['active_process_id'] = process.pid
            persist()
            try:
                process.wait(timeout=summary['process_watchdog_seconds'])
            except subprocess.TimeoutExpired:
                terminate_owned_tree(process)
                payload = {'status': 'timed_out', 'scope': 'global', 'call_status': 'timed_out',
                    'elapsed_seconds': round(time.perf_counter()-started, 3),
                    'error': 'Independent watchdog terminated owned smoke process tree.',
                    'process_watchdog_seconds': summary['process_watchdog_seconds']}
                output.write_text(json.dumps(payload, indent=2)+'\n', encoding='utf-8')
        payload = finalized_result(output, process.returncode)
        summary['runs'].append({'variant': variant, 'status': payload.get('status'),
                               'seconds': round(time.perf_counter()-started, 3), 'output': str(output)})
        summary.pop('active_process_id', None)
        summary.pop('active_variant', None)
        persist()
    summary.update(status='finished', finished_at=datetime.now(timezone.utc).isoformat())
    persist()


def run_format_gate(format_output, query_timeout_seconds, summary, persist):
    with format_output.with_suffix('.out.log').open('w', encoding='utf-8') as stdout, \
         format_output.with_suffix('.err.log').open('w', encoding='utf-8') as stderr:
        process = subprocess.Popen([sys.executable, '-m', 'jurisynth.run_structured_output_smoke',
            '--variant', 'messy', '--output', str(format_output), '--request-timeout-seconds', '0',
            '--query-timeout-seconds', str(query_timeout_seconds)], stdout=stdout, stderr=stderr)
        summary.update(active_variant='lightweight_messy_format', active_process_id=process.pid)
        persist()
        try:
            process.wait(timeout=summary['process_watchdog_seconds'])
        except subprocess.TimeoutExpired:
            terminate_owned_tree(process)
            format_output.write_text(json.dumps({'status': 'timed_out', 'error': 'Independent format-smoke watchdog fired.'})+'\n', encoding='utf-8')
    return finalized_result(format_output, process.returncode)


def finalized_result(path, exit_code):
    """An exited child cannot legitimately keep a running result."""
    try:
        payload = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(payload, dict):
            raise ValueError('Smoke result must be an object.')
    except (OSError, ValueError):
        payload = {'status': 'failed_before_valid_output'}
    if payload.get('status') == 'running':
        payload.update(status='interrupted', interruption_reason='Child exited without finalizing its result.')
    if exit_code not in (0, None) and payload.get('status') == 'success':
        payload['status'] = 'failed_process_exit'
    payload['process_exit_code'] = exit_code
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return payload


def run(version=7, query_timeout_seconds=900, passed_format_output=None):
    if query_timeout_seconds < 0:
        raise ValueError('Query timeout must be nonnegative.')
    path = Path(f'jurisynth/run_outputs/bounded_global_smokes_v{version}.json')
    # Never modify an existing run during an overwrite refusal.
    if path.exists():
        raise FileExistsError(f'Refusing to overwrite watchdog summary: {path}')
    try:
        return _run(version, query_timeout_seconds, passed_format_output)
    except BaseException as exc:
        if path.exists():
            summary = json.loads(path.read_text(encoding='utf-8'))
            pid = summary.pop('active_process_id', None)
            if pid is not None:
                terminate_owned_tree(type('OwnedProcess', (), {'pid': pid})())
            summary.update(status='interrupted' if isinstance(exc, KeyboardInterrupt) else 'failed_runner',
                           error_type=type(exc).__name__, finished_at=datetime.now(timezone.utc).isoformat())
            path.write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', type=int, default=7)
    parser.add_argument('--query-timeout-seconds', type=float, default=900, help='0 disables both query deadline and process watchdog.')
    parser.add_argument('--passed-format-output', type=Path, help='Reuse a preserved successful messy component result.')
    args = parser.parse_args()
    if args.version < 7:
        parser.error('Bounded retry versions start at 7.')
    run(args.version, args.query_timeout_seconds, args.passed_format_output)
