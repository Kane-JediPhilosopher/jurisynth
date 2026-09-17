"""Validate and import AI adjudication as data, preserving original artifacts."""
import hashlib
import json
import re
import unicodedata
import zipfile
from collections import Counter
from pathlib import Path

ROOT = Path('jurisynth/evaluation_artifacts/ai_assisted_review_v1')


def normalized(text):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', text)).strip()


def quote_match(quote, source):
    quote, source = normalized(quote), normalized(source)
    if not quote:
        return 'missing'
    if quote in source:
        return 'contiguous_normalized'
    fragments = re.split(r'\s*(?:\.\.\.|…)\s*|(?<=[.!?])\s+(?=[A-Z])', quote)
    position = 0
    for fragment in fragments:
        fragment = fragment.strip()
        if not fragment:
            continue
        found = source.find(fragment, position)
        if found < 0:
            return 'not_verified'
        position = found + len(fragment)
    return 'ordered_source_fragments'


def validate_ids(rows, expected, field):
    identifiers = [row[field] for row in rows]
    if len(identifiers) != len(set(identifiers)) or set(identifiers) != set(expected):
        raise ValueError(f'Duplicate, missing or unexpected {field} values.')


def run():
    archive_path = ROOT/'JURISYNTH_CHAT_REVIEW_RESULTS.zip'
    destination = ROOT/'chat_adjudicated_v1'
    if destination.exists():
        raise FileExistsError(f'Refusing to overwrite imported review: {destination}')
    proposals = [json.loads(line) for line in (ROOT/'nli_proposals_PRIVATE.jsonl').read_text(encoding='utf-8').splitlines()]
    originals = {row['pair_id']: row for row in proposals}
    natural = json.loads((ROOT/'natural_qa_candidates.json').read_text(encoding='utf-8'))
    original_cases = {row['case_id']: row for row in natural['cases']}
    allowed = {'CHAT_NLI_ADJUDICATION.csv', 'CHAT_NLI_ADJUDICATION.md', 'CHAT_NLI_ADJUDICATION.jsonl',
               'CHAT_NATURAL_QA_REVIEW.md', 'CHAT_NATURAL_QA_REVIEW.jsonl', 'CHAT_REVIEW_SUMMARY.md'}
    with zipfile.ZipFile(archive_path) as archive:
        entries = archive.infolist()
        if len(entries) != len(allowed) or {entry.filename for entry in entries} != allowed or sum(entry.file_size for entry in entries) > 3_000_000:
            raise ValueError('Archive inventory or size does not match expected review files.')
        contents = {entry.filename: archive.read(entry) for entry in entries}
    nli = [json.loads(line) for line in contents['CHAT_NLI_ADJUDICATION.jsonl'].decode('utf-8-sig').splitlines()]
    qa = [json.loads(line) for line in contents['CHAT_NATURAL_QA_REVIEW.jsonl'].decode('utf-8-sig').splitlines()]
    validate_ids(nli, originals, 'pair_id')
    validate_ids(qa, original_cases, 'case_id')
    merged_pairs, merged_cases = [], []
    for adjudication in nli:
        original = originals[adjudication['pair_id']]
        if adjudication['label'] not in {'entailment', 'contradiction', 'neutral'}:
            raise ValueError('Unsupported NLI label.')
        expected_key = f"{original['source_document_id']} / {original['source_chunk_id']}"
        if adjudication['source_key'] != expected_key:
            raise ValueError(f"NLI source mismatch: {original['pair_id']}")
        match = quote_match(adjudication['exact_supporting_quote'], original['source_excerpt'])
        merged = {**original, 'adjudicated_label': adjudication['label'], 'label_origin': 'ChatGPT AI-assisted adjudication',
                  'review_status': 'AI_adjudicated', 'review': adjudication, 'quote_match': match,
                  'scope_correction_pending': bool(adjudication.get('scope_correction')),
                  'expert_validated': False, 'confidence_is_calibrated_probability': False}
        merged_pairs.append(merged)
    for adjudication in qa:
        original = original_cases[adjudication['case_id']]
        if adjudication['decision'] not in {'valid', 'revise', 'reject', 'uncertain'} or adjudication['retrieval_label'] not in {'sufficient', 'partial', 'insufficient', 'irrelevant'}:
            raise ValueError('Unsupported natural-QA label.')
        matches = [quote_match(adjudication['supporting_quote'], source['full_text']) for source in original['expected_chunks']]
        merged_cases.append({**original, 'review': adjudication, 'reference_status': 'AI_adjudicated',
            'reference_answer': adjudication['verified_reference_answer'], 'label_origin': 'ChatGPT AI-assisted adjudication',
            'quote_matches': matches if matches else ['structured_table_requires_row_check'],
            'question_revision_pending': adjudication['decision'] == 'revise',
            'score_eligible': False, 'expert_validated': False,
            'system_QA_outcome': None})
    destination.mkdir()
    for filename, content in contents.items():
        (destination/filename).write_bytes(content)
    def jsonl(filename, records):
        (destination/filename).write_text(''.join(json.dumps(record, ensure_ascii=False)+'\n' for record in records), encoding='utf-8')
    jsonl('reviewed_nli_pairs.jsonl', merged_pairs)
    jsonl('reviewed_natural_cases.jsonl', merged_cases)
    summary = {'label_origin': 'AI-assisted; not expert legal validation', 'nli_n': len(merged_pairs),
        'nli_class_counts': dict(Counter(row['adjudicated_label'] for row in merged_pairs)),
        'nli_quote_matches': dict(Counter(row['quote_match'] for row in merged_pairs)),
        'nli_scope_correction_n': sum(row['scope_correction_pending'] for row in merged_pairs),
        'natural_n': len(merged_cases), 'natural_decisions': dict(Counter(row['review']['decision'] for row in merged_cases)),
        'natural_retrieval_labels': dict(Counter(row['review']['retrieval_label'] for row in merged_cases)),
        'system_QA_accuracy_computed': False,
        'archive_sha256': hashlib.sha256(archive_path.read_bytes()).hexdigest(),
        'proposal_sha256': hashlib.sha256((ROOT/'nli_proposals_PRIVATE.jsonl').read_bytes()).hexdigest(),
        'no_thresholds_changed': True}
    (destination/'IMPORT_SUMMARY.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    run()
