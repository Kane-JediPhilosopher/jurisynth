"""Freeze reviewed follow-up data without overwriting the original adjudication."""
import hashlib
import json
from pathlib import Path

from jurisynth.ingest_chat_review import quote_match, validate_ids


def run(source=Path('C:/Users/Roxas/OneDrive/Desktop/CHAT_FOLLOWUP_COMPLETED.json')):
    root = Path('jurisynth/evaluation_artifacts/ai_assisted_review_v1/chat_adjudicated_v1')
    destination = root/'followup_v2'
    if destination.exists():
        raise FileExistsError(destination)
    raw = source.read_bytes()
    review = json.loads(raw.decode('utf-8-sig'))
    pairs = [json.loads(line) for line in (root/'reviewed_nli_pairs.jsonl').read_text(encoding='utf-8').splitlines()]
    cases = [json.loads(line) for line in (root/'reviewed_natural_cases.jsonl').read_text(encoding='utf-8').splitlines()]
    validate_ids(review['qa_cases'], [c['case_id'] for c in cases if c['question_revision_pending']], 'case_id')
    families = review['nli_families']
    validate_ids(families, {p['family_id'] for p in pairs if p['scope_correction_pending']}, 'family_id')
    by_id = {p['pair_id']: p for p in pairs}
    for family in families:
        expected = {p['pair_id'] for p in pairs if p['family_id'] == family['family_id']}
        labels = family['labels']
        ids = [label[0] for label in labels]
        if len(ids) != len(set(ids)) or set(ids) != expected:
            raise ValueError('NLI label inventory mismatch.')
        for pair_id, hypothesis, label, status in labels:
            pair = by_id[pair_id]
            if hypothesis != pair['hypothesis'] or label not in {'entailment', 'contradiction', 'neutral'}:
                raise ValueError('NLI hypothesis/label mismatch.')
            if family['source'] != {'document_id': pair['source_document_id'], 'chunk_id': pair['source_chunk_id']}:
                raise ValueError('NLI source mismatch.')
            match = quote_match(family['exact_supporting_quote'], pair['source_excerpt'])
            if match in {'missing', 'not_verified'}:
                raise ValueError('NLI supporting text not verified.')
            pair.update(original_premise=pair['premise'], premise=family['corrected_premise'],
                        adjudicated_label=label, scope_correction_pending=False,
                        followup_status=status, family_scope_note=family['family_note'],
                        followup_quote_match=match)
    by_case = {c['case_id']: c for c in cases}
    for revised in review['qa_cases']:
        case = by_case[revised['case_id']]
        support = revised['support']
        if support['type'] == 'chunk':
            matches = [s for s in case['expected_chunks'] if (s['document_id'], s['chunk_id']) == (support['document_id'], support['chunk_id'])]
            if not matches or quote_match(support['exact_supporting_quote'], matches[0]['full_text']) in {'missing', 'not_verified'}:
                raise ValueError('QA supporting text not verified.')
        else:
            expected = [{k: s[k] for k in ('document_id', 'table_id', 'row_ids', 'headers', 'rows')} for s in case['expected_tables']]
            if {k: support[k] for k in ('document_id', 'table_id', 'row_ids', 'headers', 'rows')} not in expected:
                raise ValueError('QA table support mismatch.')
        case.update(original_question=case['question'], question=revised['question'],
                    reference_answer=revised['reference_answer'], followup_review=revised,
                    question_revision_pending=False, score_eligible=False,
                    benchmark_scope='contextual pilot; standalone global applicability not established')
    destination.mkdir()
    (destination/'CHAT_FOLLOWUP_COMPLETED.json').write_bytes(raw)
    for name, records in [('corrected_nli_pairs.jsonl', pairs), ('contextual_natural_cases.jsonl', cases)]:
        (destination/name).write_text(''.join(json.dumps(row, ensure_ascii=False)+'\n' for row in records), encoding='utf-8')
    summary = {'nli_pairs': len(pairs), 'corrected_premises': sum('original_premise' in p for p in pairs),
               'qa_cases': len(cases), 'revised_questions': len(review['qa_cases']),
               'expert_validated': False, 'system_QA_accuracy_scored': False,
               'review_sha256': hashlib.sha256(raw).hexdigest(),
               'nli_dataset_sha256': hashlib.sha256((destination/'corrected_nli_pairs.jsonl').read_bytes()).hexdigest()}
    (destination/'IMPORT_SUMMARY.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(summary))


if __name__ == '__main__':
    run()
