"""Package retry locations, raw retrieval events, ASTs and current uncapped client."""
from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import zipfile

from jurisynth.prepare_leaf_execution_handoff import analyze
from jurisynth.vendor.qcompiler_parser import Parser

ROOT = Path('jurisynth')
DEST = ROOT/'evaluation_artifacts/leaf_execution_handoff_v3'


def parsed_tree(node):
    return {'type': node.type, 'query': node.value,
            'children': [parsed_tree(child) for child in node.children or []]}


def main():
    if DEST.exists():
        raise FileExistsError(DEST)
    payloads = {}
    text = '# Jurisynth leaf execution / retry / AST follow-up\n\n## Changes since the observed runs\n\nAt the owner’s request the current Reasoner NIM wrapper and retrieval ImageExpander no longer transmit max_tokens or max_completion_tokens. Legacy adapter budget arguments remain accepted for compatibility but are ignored by the shared NIM wrapper; they are not applied output caps. Provider default limits still exist: omitted does not mean infinite output. Prompts, schemas, retry rules, temperature=0 and top_p=.000001 remain unchanged. KG construction’s separate llm_utils and Image Processor configs are not changed. No API rerun was performed for this patch. The v10 logs describe the old explicit caps; do not assume their metadata describes the patched code.\n\n## Questions for Chat\n\nDiagnose the large uninstrumented retrieval intervals, shared semaphore/FAISS/embedding contention, sequential image expansion and dependency barriers. Distinguish confirmed causes from hypotheses. Propose scoped instrumentation and experiments before changes. Inspect provider-default output limits as a remaining uncertainty, not a guarantee against truncation. Keep the source KG pipeline prompt frozen. NLI/retrieval relevance is not evaluated by a success-status event.\n\n## Evidence limitations\n\nFull leaf answers, final report responses, internal per-search spans, Omni expansion calls and complete evidence bundles were not checkpointed on report failure. The available retrieval events contain total duration, status, evidence IDs and table IDs, not evidence text/scores/individual stage durations. Complete API retry events and raw logs are packaged. NIM logs lack query IDs: per-leaf API correlation is inferred, ambiguous calls stay unassigned with candidate leaves. Times overlap; do not sum them as run duration. Most interpretation intervals cannot be uniquely assigned to concurrent leaves.\n'
    DEST.mkdir(parents=True)
    for variant, name in [('messy', 'global_smoke_252757.jsonl'), ('organized', 'global_smoke_257808.jsonl')]:
        path = ROOT/'reasoning_logs'/name
        rows = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
        report = analyze(path)
        calls = {r['call_id']: r for r in rows if r['event'] == 'nim_request_started'}
        correlations = {c['call_id']: c for c in report['leaf_calls']}
        retries = []
        for r in rows:
            if r['event'] == 'nim_retry_scheduled':
                associated = correlations.get(r['call_id'], {})
                retries.append({**r, 'stage': calls[r['call_id']]['schema_name'],
                                'query_id_if_correlated': associated.get('query_id'),
                                'candidate_query_ids': associated.get('candidate_query_ids', []),
                                'leaf_association': associated.get('association', 'outside leaf execution')})
        retry_counts = Counter(r['stage'] for r in retries)
        tree = parsed_tree(Parser().parse_complex_query(report['expression']))
        plan = next(r['leaves'] for r in rows if r['event'] == 'leaf_plan_ready')
        retrieval = [r for r in rows if r['event'] == 'retrieval_completed']
        payloads[variant] = {'timing': report, 'retry_events': retries, 'retry_counts': dict(retry_counts),
                             'parsed_ast': tree, 'semantic_execution_plan': plan, 'retrieval_events': retrieval}
        (DEST/f'{variant}_retrieval_events.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in retrieval), encoding='utf-8')
        (DEST/f'{variant}_retry_events.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in retries), encoding='utf-8')
        edges = [(d, p['query_id']) for p in plan for d in p['dependency_ids']]
        dag = 'flowchart LR\n'+'\n'.join(f'  {p["query_id"]}["{p["query_id"]}"]' for p in plan)+'\n'+'\n'.join(f'  {a} --> {b}' for a, b in edges)+'\n'
        (DEST/f'{variant}_execution_DAG.mmd').write_text(dag, encoding='utf-8')
        (DEST/f'{variant}_parsed_AST.json').write_text(json.dumps(tree, indent=2)+'\n', encoding='utf-8')
        ast_mermaid = ['flowchart TD']
        atomic = []
        def visit(node):
            identifier = f'n{len(ast_mermaid)}'
            if node['type'] == 'AtomicQuery':
                atomic.append(node['query'])
                label = f'q{len(atomic):03}'
            else:
                label = node['type']
            ast_mermaid.append(f'  {identifier}["{label}"]')
            for child in node['children']:
                other = visit(child)
                ast_mermaid.append(f'  {identifier} --> {other}')
            return identifier
        visit(tree)
        (DEST/f'{variant}_AST.mmd').write_text('\n'.join(ast_mermaid)+'\n', encoding='utf-8')
        text += f'\n## {variant}: retry locations\n\n'+ '\n'.join(f'- {stage}: {count} HTTP 503 retries.' for stage, count in retry_counts.items())+'\n'
        text += '\nAll logged Ultra retry statuses: '+str(dict(Counter(r.get('status_code') for r in retries)))+'. Separate vision-client retries are not in these logs.\n'
        text += '\n### AST versus actual execution plan\n\nThe parser AST records expression structure. The semantic planner then changes required leaf dependencies; these are separate artifacts. q-numbers below follow atomic expression traversal. Exact leaf text is included in parsed_AST.json.\n\n```mermaid\n'+'\n'.join(ast_mermaid)+'\n```\n\nExecution DAG after semantic planning:\n\n```mermaid\n'+dag+'```\n'
        for i, query in enumerate(atomic, 1):
            text += f'\n- q{i:03}: {query}\n'
        text += '\n### Per-leaf retrieval and generation minutes\n'
        for leaf in report['leaves']:
            text += f'\n- {leaf["query_id"]}: retrieval {leaf["retrieval_seconds"]/60:.2f}; answer generation {leaf["generation_seconds"]/60:.2f}; uninstrumented retrieval remainder at least {leaf["retrieval_remainder_lower_seconds"]/60:.2f} (conservative temporal bound, not CPU time).\n'
        text += '\n### Exact retry events\n\n```json\n'+json.dumps(retries, indent=2)+'\n```\n'
        text += '\n### Available retrieval events\n\n```json\n'+json.dumps(retrieval, indent=2)+'\n```\n'
    files = ['agentic_reasoner/llm.py','agentic_reasoner/reporting.py','agentic_reasoner/schemas.py',
             'agentic_reasoner/reasoner.py','agentic_reasoner/scheduler.py','agentic_reasoner/workflow.py',
             'agentic_reasoner/dependency_planner.py','agentic_reasoner/qcompiler_translator.py','agentic_reasoner/intake.py',
             'retrieval_mech/query_interpreter.py','retrieval_mech/mechanism.py','retrieval_mech/config.py',
             'retrieval_mech/rdf_retriever.py','retrieval_mech/image_expander.py','retrieval_mech/community_summary.py',
             'retrieval_mech/er_shards.py','retrieval_mech/lazy_er_metadata.py','retrieval_mech/artifacts.py',
             'retrieval_mech/er_matcher.py','retrieval_mech/lazy_chunk_metadata.py','vendor/qcompiler_parser.py',
             'main.py','run_global_smoke.py','run_bounded_global_smokes.py','reasoning_log.py',
             'kg_construction_pipeline/src/llm_utils.py','kg_construction_pipeline/src/vision_llm_utils.py',
             'kg_construction_pipeline/src/assertion_extractor.py','kg_construction_pipeline/src/ent_rel_resolver.py',
             'reasoning_logs/global_smoke_252757.jsonl','reasoning_logs/global_smoke_257808.jsonl',
             'run_outputs/global_complex_ai_medical_messy_bounded_v10.json',
             'run_outputs/global_complex_ai_medical_organized_bounded_v10.json','run_outputs/bounded_global_smokes_v10.json',
             'evaluation_artifacts/complex_ai_medical_messy.txt','evaluation_artifacts/complex_ai_medical_organized.txt']
    text += '\n## Relevant files included\n\n'+ '\n'.join('- jurisynth/'+file for file in files)+'\n'
    (DEST/'CHAT_LEAF_EXECUTION_FOLLOWUP.md').write_text(text, encoding='utf-8')
    (DEST/'RECONSTRUCTION.json').write_text(json.dumps(payloads, indent=2)+'\n', encoding='utf-8')
    manifest = {}
    archive_path = DEST/'CHAT_LEAF_EXECUTION_FOLLOWUP.zip'
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for file in files:
            content = (ROOT/file).read_bytes()
            if b'nvapi-' in content:
                raise ValueError('Potential credentials detected; refusing to package.')
            archive.writestr('jurisynth/'+file, content)
            manifest[file] = hashlib.sha256(content).hexdigest()
        for path in DEST.iterdir():
            if path != archive_path:
                archive.write(path, path.name)
        archive.writestr('SOURCE_HASHES.json', json.dumps(manifest, indent=2))
    print(json.dumps({'archive': str(archive_path), 'retry_counts': {v: p['retry_counts'] for v, p in payloads.items()}, 'included_source_files': len(files)}))


if __name__ == '__main__':
    main()
