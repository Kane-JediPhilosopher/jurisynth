"""Live Ultra format smoke without loading global indexes or scoring legal QA."""
import asyncio
import argparse
import json
import time
from dataclasses import asdict, replace
from pathlib import Path

from jurisynth.agentic_reasoner.llm import NIMConfig, OpenAICompatibleNIM
from jurisynth.agentic_reasoner.qcompiler_translator import QCompilerTranslator
from jurisynth.contracts import RetrievalRequest
from jurisynth.reasoning_log import ReasoningLog
from jurisynth.retrieval_mech.query_interpreter import NIMQueryInterpreter


async def run(args):
    output = args.output
    if output.exists():
        raise FileExistsError(f'Refusing to overwrite prior format smoke: {output}')
    started = time.perf_counter()
    config = replace(NIMConfig.from_environment(), request_timeout_seconds=args.request_timeout_seconds or None)
    model = OpenAICompatibleNIM(config, reasoning_log=ReasoningLog(
        Path('jurisynth/reasoning_logs')/f'{output.stem}.jsonl', 'structured_output_smoke'))
    payload = {'status': 'running', 'kind': 'structured-output component smoke; not legal QA', 'cases': []}
    def persist():
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    persist()
    async def exercise():
        for variant in (('organized', 'messy') if args.variant == 'both' else (args.variant,)):
            case_started = time.perf_counter()
            query = Path(f'jurisynth/evaluation_artifacts/complex_ai_medical_{variant}.txt').read_text(encoding='utf-8')
            compilation = await QCompilerTranslator(model).compile(query)
            concepts = await NIMQueryInterpreter(model).interpret(RetrievalRequest(
                f'{variant}_first_leaf', compilation.leaves[0].query, contextual_facts=(query,)))
            payload['cases'].append({'variant': variant, 'seconds': round(time.perf_counter()-case_started, 3),
                                     'expression': compilation.expression, 'ast': compilation.ast,
                                     'attempts': compilation.attempts, 'leaves': [asdict(leaf) for leaf in compilation.leaves],
                                     'entities': [asdict(item) for item in concepts[0]],
                                     'relations': [asdict(item) for item in concepts[1]]})
            persist()
    try:
        await asyncio.wait_for(exercise(), timeout=args.query_timeout_seconds or None)
        payload['status'] = 'success'
    except TimeoutError:
        payload.update(status='timed_out', error='Overall format-smoke deadline exceeded.')
    except Exception as exc:
        payload.update(status='failed', error=repr(exc))
    finally:
        await model.aclose()
        payload['elapsed_seconds'] = round(time.perf_counter()-started, 3)
        persist()
    print(json.dumps({'output': str(output), 'status': payload['status']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--variant', choices=('organized', 'messy', 'both'), default='both')
    parser.add_argument('--output', type=Path, default=Path('jurisynth/run_outputs/structured_output_smoke_v2.json'))
    parser.add_argument('--request-timeout-seconds', type=float, default=0, help='0 disables the HTTP timeout; the overall query deadline remains active.')
    parser.add_argument('--query-timeout-seconds', type=float, default=900)
    args = parser.parse_args()
    if args.request_timeout_seconds < 0 or args.query_timeout_seconds < 0:
        parser.error('Smoke deadlines must be nonnegative; 0 disables them.')
    asyncio.run(run(args))
