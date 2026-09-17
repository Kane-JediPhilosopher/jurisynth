"""Build an untuned development-only review packet from existing ablation runs."""
import json
from pathlib import Path
import re
import sqlite3


def normalize(value):
    text = re.sub(r'\.[^.]+$', '', str(value).strip().lower())
    return re.sub(r'_+', '_', re.sub(r'[^a-z0-9]+', '_', text)).strip('_')


def main():
    root = Path('jurisynth/evaluation_artifacts/retrieval_ablation')
    output = root/'CHAT_RETRIEVAL_DIAGNOSTICS.md'
    if output.exists():
        raise FileExistsError(output)
    def rows(name):
        return [json.loads(line) for line in (root/name).read_text(encoding='utf-8').splitlines()]
    reviews = {r['case']['case_id']: r for r in rows('retrieval_ablation_A_review_set.jsonl')}
    cases = {r['case_id']: r for r in rows('development_cases.jsonl')}
    results = {variant: {r['case_id']: r for r in rows(f'retrieval_ablation_{variant}_results.jsonl')} for variant in 'ABC'}
    pools = {variant: {r['case_id']: r for r in rows(f'retrieval_ablation_{variant}_ranked_pool.jsonl')} for variant in 'ABC'}
    changed = [key for key in cases if results['A'][key]['assertion_recalled'] != results['C'][key]['assertion_recalled']]
    misses = [key for key in cases if not results['A'][key]['assertion_recalled'] and key not in changed]
    selected = changed + misses[:max(0, 6-len(changed))]
    summaries = {variant: json.loads((root/f'retrieval_ablation_{variant}_summary.json').read_text()) for variant in 'ABC'}
    text = '# Development retrieval calibration review\n\nThese are controlled, source-derived assertion probes, not natural legal-QA questions. Gold assertions are extracted KG data and remain unvalidated. The 40-case development set is untuned; the separate 160-case test set is not included. Selection prioritizes A/C hit changes then existing misses, so this six-case packet is intentionally nonrepresentative. Do not equate exact-source misses with semantic failure or query runtime with provider latency. A=expansion off/cap50, B=on/cap50, C=off/cap100; production behavior is unchanged. Timing is sequential and affected by caching/order: do not infer causal speedups.\n\nFor each case: assess whether the expected chunk actually supports the gold assertion, identify answer-bearing alternate sources, distinguish entity/predicate matching, candidate-scope and ranking failures, and propose bounded development experiments. Do not prescribe perfect-1.0 similarity filtering or silent legal applicability assumptions. Candidate excerpts are truncated views, not full documents. The preview includes top 12 and any exact-gold rank plus adjacent ranks; scores used the entire recorded pool. No live AST/NIM interpretation was used for these probes. Proposed changes require owner approval.\n\n## Full 40-case summaries\n\n```json\n'+json.dumps(summaries, indent=2)+'\n```\n'
    database = Path('jurisynth/global_artifacts/chunk_index/chunk_metadata.sqlite').resolve()
    with sqlite3.connect(f'file:{database.as_posix()}?mode=ro', uri=True) as connection:
        for key in selected:
            case = cases[key]
            expected_sources = []
            for chunk in case['expected_chunk_ids']:
                doc = case['expected_document_id']
                graph = f'http://jurisynth/source/chunk/{normalize(doc)}_{normalize(chunk)}'
                found = connection.execute('SELECT content FROM chunks WHERE graph_uri=? AND doc_id=? AND chunk_id=? ORDER BY vector_id DESC LIMIT 1', (graph, doc, chunk)).fetchone()
                expected_sources.append({'document_id': doc, 'chunk_id': chunk, 'full_text': found[0] if found else None,
                                         'source_resolution': 'exact_document_chunk' if found else 'unresolved'})
            comparisons = {}
            for variant in 'ABC':
                result, pool = results[variant][key], pools[variant][key]
                rank = result.get('expected_assertion_rank')
                chosen = [r for r in pool['assertions'] if r['rank'] <= 12 or (rank is not None and abs(r['rank']-rank) <= 1)]
                comparisons[variant] = {'metrics': {k: v for k, v in result.items() if k != 'retrieved_evidence'},
                                        'full_scoring_pool_count': pool['scoring_pool_count'], 'ranked_preview': chosen,
                                        'direct_chunk_matches': pool['direct_chunk_matches']}
            payload = {'case': case, 'expected_sources': expected_sources, 'comparisons': comparisons}
            text += '\n## '+key+'\n\n```json\n'+json.dumps(payload, ensure_ascii=False, indent=2)+'\n```\n'
    output.write_text(text, encoding='utf-8')
    print(json.dumps({'output': str(output), 'cases': len(selected), 'changed_hit_cases': len(changed)}))


if __name__ == '__main__':
    main()
