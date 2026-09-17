"""Reconstruct logged wall-clock leaf timing; preserve uncertainty about attribution."""
import ast
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path('jurisynth')
DEST = ROOT/'evaluation_artifacts/leaf_execution_handoff_v2'


def when(row):
    return datetime.fromisoformat(row['timestamp']).timestamp()


def analyze(path):
    rows = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
    plan = next(r for r in rows if r['event'] == 'plan_started')
    finished = next(r for r in rows if r['event'] == 'plan_completed')
    begin, end = when(plan), when(finished)
    leaves = {}
    for r in rows:
        if r['event'] == 'node_started':
            leaves[r['query_id']] = {'query_id': r['query_id'], 'dependencies': r['dependency_ids'], 'start': when(r)}
        elif r['event'] in {'retrieval_completed', 'leaf_generation_completed', 'node_completed'}:
            leaf = leaves[r['query_id']]
            if r['event'] == 'retrieval_completed':
                leaf.update(retrieval_end=when(r), retrieval_seconds=r['duration_ms']/1000,
                            evidence_count=len(r['evidence_ids']), retrieval_status=r['retrieval_status'])
            elif r['event'] == 'leaf_generation_completed':
                leaf['generation_seconds'] = r['duration_ms']/1000
            else:
                leaf.update(end=when(r), claims=len(r['claim_ids']))
    calls = {}
    previous_terminals = []
    for index, r in enumerate(rows):
        event = r['event']
        if event == 'nim_request_started':
            cid = r['call_id']
            if cid not in calls:
                schema = r.get('schema_name')
                owner, association = None, 'not correlated'
                trigger = 'node_started' if schema == 'retrieval_concepts' else 'retrieval_completed' if schema == 'evidence_grounded_leaf_answer' else None
                candidates = [key for key, leaf in leaves.items() if
                              (leaf['start'] <= when(r) < leaf['retrieval_end'] if schema == 'retrieval_concepts' else
                               leaf['retrieval_end'] <= when(r) < leaf['end'] if schema == 'evidence_grounded_leaf_answer' else False)]
                if len(candidates) == 1:
                    owner, association = candidates[0], 'only active leaf in this phase; temporal inference'
                elif trigger == 'retrieval_completed':
                    near = [p for p in rows[:index] if p['event'] == trigger and 0 <= when(r)-when(p) <= .1]
                    if len(near) == 1 and near[-1]['query_id'] in candidates:
                        owner, association = near[-1]['query_id'], 'inferred from immediate phase-boundary timestamp'
                    else:
                        near = [p for p in previous_terminals if calls[p['call_id']]['schema'] == schema and 0 <= when(r)-when(p) <= .1]
                        if len(near) == 1:
                            owner = calls[near[-1]['call_id']]['query_id']
                            association = 'inferred validation-call continuation from immediate preceding completion'
                calls[cid] = {'call_id': cid, 'schema': schema, 'query_id': owner, 'association': association,
                              'candidate_query_ids': candidates, 'start': when(r), 'max_tokens': r['max_tokens'], 'attempts': [], 'ends': []}
            calls[cid]['attempts'].append(r)
        elif event in {'nim_request_completed', 'nim_retry_scheduled', 'nim_request_cancelled', 'nim_request_failed', 'nim_retries_exhausted'}:
            calls[r['call_id']]['ends'].append(r)
            if event == 'nim_request_completed':
                previous_terminals.append(r)
    leaf_calls = [c for c in calls.values() if c['schema'] in {'retrieval_concepts', 'evidence_grounded_leaf_answer'} and begin <= c['start'] <= end]
    for leaf in leaves.values():
        owned = [c for c in leaf_calls if c['query_id'] == leaf['query_id']]
        interpretation = [c for c in owned if c['schema'] == 'retrieval_concepts']
        leaf['interpreter_observed_seconds'] = sum(max(when(r) for r in c['ends'])-c['start'] for c in interpretation)
        possible = [c for c in leaf_calls if c['schema'] == 'retrieval_concepts' and
                    (c['query_id'] == leaf['query_id'] or (c['query_id'] is None and leaf['query_id'] in c['candidate_query_ids']))]
        spans = sorted((max(c['start'], leaf['start']), min(max(when(r) for r in c['ends']), leaf['retrieval_end'])) for c in possible)
        merged = []
        for left, right in spans:
            if merged and left <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(right, merged[-1][1]))
            else:
                merged.append((left, right))
        leaf['possible_interpreter_interval_upper_seconds'] = sum(max(0, right-left) for left, right in merged)
        leaf['retrieval_remainder_lower_seconds'] = max(0, leaf['retrieval_seconds']-leaf['possible_interpreter_interval_upper_seconds'])
        leaf['retrieval_outside_interpreter_interval_seconds'] = leaf['retrieval_seconds']-leaf['interpreter_observed_seconds']
        generation = [c for c in owned if c['schema'] == 'evidence_grounded_leaf_answer']
        leaf['answer_attempts'] = sum(len(c['attempts']) for c in generation)
        leaf['answer_logical_calls'] = len(generation)
        leaf['answer_length_completions'] = sum(r.get('finish_reason') == 'length' for c in generation for r in c['ends'])
        leaf['logged_503_retries'] = sum(r.get('status_code') == 503 for c in owned for r in c['ends'])
        dependency_ready = max([leaves[k]['end'] for k in leaf['dependencies']] or [begin])
        leaf['start_after_required_dependencies_ready_seconds'] = leaf['start']-dependency_ready
        leaf['start_minutes_from_plan'] = (leaf['start']-begin)/60
        leaf['finish_minutes_from_plan'] = (leaf['end']-begin)/60
        leaf['total_seconds'] = leaf['end']-leaf['start']
    points = sorted({begin, end} | {l['start'] for l in leaves.values()} | {l['end'] for l in leaves.values()})
    intervals = []
    for left, right in zip(points, points[1:]):
        active = [k for k, l in leaves.items() if l['start'] <= left < l['end']]
        intervals.append({'start_min': (left-begin)/60, 'end_min': (right-begin)/60, 'active_leaves': active})
    return {'log': str(path), 'leaf_wall_seconds': end-begin, 'leaves': list(leaves.values()),
            'active_intervals': intervals, 'leaf_calls': leaf_calls,
            'uncorrelated_leaf_calls': [c['call_id'] for c in leaf_calls if c['query_id'] is None],
            'all_request_attempts': sum(r['event'] == 'nim_request_started' for r in rows),
            'all_retry_statuses': dict(Counter(str(r.get('status_code')) for r in rows if r['event'] == 'nim_retry_scheduled')),
            'expression': next(r['expression'] for r in rows if r['event'] == 'qcompiler_compiled')}


def main():
    if DEST.exists():
        raise FileExistsError(DEST)
    analyses = {variant: analyze(ROOT/'reasoning_logs'/name) for variant, name in
                [('messy', 'global_smoke_252757.jsonl'), ('organized', 'global_smoke_257808.jsonl')]}
    text = '# Jurisynth global smoke leaf-execution investigation\n\n## Request to Chat\n\nAnalyze local and provider-related latency separately. Identify confirmed causes versus hypotheses, challenge the dependency plan, assess shared semaphore/worker/index contention and auxiliary image calls, and propose the smallest instrumentation experiment before implementation. Do not silently change prompts, token budgets, retrieval policy or retry behavior. This packet contains code/logs and synthetic scenario text, never credentials.\n\n## Confirmed context\n\nBoth Ultra global runs completed ASTs and all leaves but failed final-report JSON parsing. Messy: six success-status retrievals and 17 claims; organized: seven and 29. These statuses do NOT establish answer relevance/legal accuracy. HTTP/query/watchdog timeouts were explicitly disabled. Overall run time was 5001.016s / 5781.875s; parent queue durations also include child startup/teardown. No query is running from this queue now.\n\n## Attribution limitations\n\n- Timings are wall-clock, not CPU or GPU time. Concurrent leaf durations must not be summed as total runtime.\n- NIM logs lack query IDs. Per-leaf API correlation below is timestamp-inferred and explicitly marked, not an SDK trace ID. Inspect raw logs; any uncorrelated calls are disclosed.\n- An API attempt interval includes transport, provider work and possible delayed local event-loop resumption. It is not pure NVIDIA inference time.\n- Retrieval includes chunk/table/image FAISS, structured matching/SPARQL/path/community work, shared operation-semaphore queues, and possible image explanation or lazy community synthesis. Only the shared Ultra client is in the reasoning log; ImageExpander uses a separate vision client, processes images sequentially, and does not log its requests here. No absence-of-call conclusion is justified from the Ultra log alone.\n- Retrieval outside the observed interpreter interval is uninstrumented elapsed time, NOT proven local CPU/index time. It includes semaphore waits before interpretation and other concurrent/auxiliary stages. Negative remainders would indicate correlation problems, not a speedup.\n- The scheduler uses a max-four semaphore and waits for the entire ready group before reconsidering dependency readiness. Extra delay after required dependencies finish may reflect that barrier or slot contention; it is not automatically provider delay.\n- Final response text and completed leaf bodies were not checkpointed on synthesis failure. Claim IDs and metadata are available, not full answers.\n\n## Completion configuration and final failure\n\nBaseline Assertion Extractor and E-R Resolver share llm_utils.get_completion: configurable default max_tokens=6000, temperature=0, top_p=.000001, reasoning_effort=none, non-streaming, strict JSON schema, SDK retries disabled. Reasoner uses the same deterministic sampling intent but separate output budgets: 400 intake/analysis/dependency planning, 2048 AST/interpretation, 800 leaf answer, 1400 final report. The exact final prompt/schema are included in reporting.py/schemas.py. Both final responses hit length at 1400 tokens: messy 6187 characters after133.502s; organized5427 characters after a503 retry (74.616s failed attempt,93.882s completion). Truncated text was not saved. Output limits explain the final failure and some leaf repair calls, not all observed latency.\n'
    for variant, report in analyses.items():
        text += f'\n## {variant}: per-leaf breakdown\n\nLeaf-execution wall time: {report["leaf_wall_seconds"]/60:.2f} minutes.\n'
        for leaf in report['leaves']:
            text += (f'\n- {leaf["query_id"]}; required dependencies {leaf["dependencies"] or "none"}; starts +{leaf["start_minutes_from_plan"]:.2f} min, finishes +{leaf["finish_minutes_from_plan"]:.2f} min. '
                     f'Retrieval {leaf["retrieval_seconds"]/60:.2f} min; attributable interpreter interval {leaf["interpreter_observed_seconds"]/60:.2f} min, possible upper bound {leaf["possible_interpreter_interval_upper_seconds"]/60:.2f} min; uninstrumented retrieval remainder therefore at least {leaf["retrieval_remainder_lower_seconds"]/60:.2f} min (temporal bounds, not CPU attribution). '
                     f'Answer generation {leaf["generation_seconds"]/60:.2f} min; at least {leaf["answer_attempts"]} correlated answer attempts across {leaf["answer_logical_calls"]} calls, {leaf["answer_length_completions"]} correlated length completions; {leaf["logged_503_retries"]} correlated503 retries (ambiguous calls remain unassigned; zero does not mean no call). '
                     f'Start delay after required prerequisites ready {leaf["start_after_required_dependencies_ready_seconds"]/60:.2f} min.\n')
        text += '\n### Execution overlap\n'
        for interval in report['active_intervals']:
            text += f'\n- +{interval["start_min"]:.2f} to +{interval["end_min"]:.2f} min: {", ".join(interval["active_leaves"]) or "no active leaves"}.\n'
        text += '\n### Generated expression\n\n```text\n'+report['expression']+'\n```\n'
        text += '\nUncorrelated leaf call IDs: '+str(report['uncorrelated_leaf_calls'])+'\n'
    text += '\n## Questions requiring a second opinion\n\n1. What explains the large retrieval remainder, especially in organized leaves, given interpreter latency alone is much smaller? Which steps need independent start/end timing?\n2. Could the global ImageExpander perform several serial Omni calls per leaf and consume this remainder? How can that be measured without assuming it occurred?\n3. Are generated hard dependencies justified, and how much is delayed by the ready-group barrier? Distinguish correct dependency waits from unnecessary waits.\n4. Do 800-token leaf completions trigger validation repairs? Quantify from the captured metadata without inventing response contents.\n5. Which shared embeddings, FAISS shard locks, internal operation limits, cold mmap/page faults or Python worker contention need profiling? Compare controlled sequential versus concurrent retrieval, keeping source queries fixed.\n6. Recommend a configurable completion budget and length-aware validation/persistence policy aligned with the baseline, but do not implement or silently change it.\n7. Provide an ordered plan: instrumentation first, reproducible isolated component timings second, then owner-approved targeted changes. Avoid blaming NVIDIA alone or recommending architectural replacement before evidence.\n'
    text += '\n## Correlation caution\n\nInterpretation calls may start after shared-operation queues, while several leaves are active; their query IDs cannot be recovered reliably from timestamps alone. This v2 packet leaves those calls unassigned and supplies candidate query IDs plus conservative temporal bounds. The JSON field interpreter_observed_seconds means attributable intervals only; retrieval_outside_interpreter_interval_seconds is the upper end of the possible remainder, not an exact measurement. Use retrieval_remainder_lower_seconds for the conservative lower bound. Per-leaf retry/answer counts are correlated minima; consult the complete raw call list for ambiguous calls. V1 was an intermediate reconstruction and is superseded by this packet.\n'
    for report in analyses.values():
        for leaf in report['leaves']:
            if abs(leaf['total_seconds']-leaf['retrieval_seconds']-leaf['generation_seconds']) > .2:
                raise ValueError('Leaf wall-time reconciliation failed.')
            if leaf['retrieval_remainder_lower_seconds'] < 0:
                raise ValueError('Invalid timing bound.')
    DEST.mkdir(parents=True)
    (DEST/'CHAT_LEAF_EXECUTION_HANDOFF.md').write_text(text, encoding='utf-8')
    (DEST/'TIMING_RECONSTRUCTION.json').write_text(json.dumps(analyses, indent=2)+'\n', encoding='utf-8')
    files = ['agentic_reasoner/llm.py', 'agentic_reasoner/reporting.py', 'agentic_reasoner/schemas.py',
             'agentic_reasoner/reasoner.py', 'agentic_reasoner/scheduler.py', 'agentic_reasoner/workflow.py',
             'agentic_reasoner/dependency_planner.py', 'agentic_reasoner/qcompiler_translator.py',
             'retrieval_mech/query_interpreter.py', 'retrieval_mech/mechanism.py', 'retrieval_mech/config.py',
             'retrieval_mech/rdf_retriever.py', 'retrieval_mech/image_expander.py', 'retrieval_mech/community_summary.py',
             'retrieval_mech/er_shards.py', 'retrieval_mech/lazy_er_metadata.py', 'main.py', 'run_global_smoke.py',
             'run_bounded_global_smokes.py', 'reasoning_log.py', 'kg_construction_pipeline/src/llm_utils.py',
             'kg_construction_pipeline/src/vision_llm_utils.py', 'reasoning_logs/global_smoke_252757.jsonl',
             'reasoning_logs/global_smoke_257808.jsonl', 'run_outputs/global_complex_ai_medical_messy_bounded_v10.json',
             'run_outputs/global_complex_ai_medical_organized_bounded_v10.json', 'run_outputs/bounded_global_smokes_v10.json',
             'evaluation_artifacts/complex_ai_medical_messy.txt', 'evaluation_artifacts/complex_ai_medical_organized.txt']
    manifest = {}
    archive_path = DEST/'CHAT_LEAF_EXECUTION_HANDOFF.zip'
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for file in files:
            path = ROOT/file
            content = path.read_bytes()
            if b'nvapi-' in content:
                raise ValueError('Potential credential detected: refusing to package.')
            archive.writestr('jurisynth/'+file, content)
            manifest[file] = hashlib.sha256(content).hexdigest()
        for file in ('CHAT_LEAF_EXECUTION_HANDOFF.md', 'TIMING_RECONSTRUCTION.json'):
            archive.write(DEST/file, file)
        archive.writestr('SOURCE_HASHES.json', json.dumps(manifest, indent=2))
    print(json.dumps({'archive': str(archive_path), 'leaves': {v: [{k: r[k] for k in ('query_id', 'dependencies', 'start_minutes_from_plan', 'finish_minutes_from_plan', 'retrieval_seconds', 'interpreter_observed_seconds', 'retrieval_outside_interpreter_interval_seconds', 'generation_seconds', 'answer_attempts', 'answer_length_completions')} for r in report['leaves']] for v, report in analyses.items()}}))


if __name__ == '__main__':
    main()
