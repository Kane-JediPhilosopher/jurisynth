"""Prepare bounded-source AI review packets without APIs, indexes or predictions."""
from __future__ import annotations

import hashlib
import json
import random
import sqlite3
import sys
import zipfile
from collections import Counter
from pathlib import Path

from jurisynth.table_rdf_enricher import chunk_uri_candidates

ROOT = Path(__file__).parent / 'evaluation_artifacts'
SOURCE_PACKET = ROOT / 'global_natural_candidate_packet.json'
DESTINATION = ROOT / 'ai_assisted_review_v1'

# Paraphrases and hypotheses are proposals, not statements of current law.
# Each family derives from ONE supplied instrument, not an artificial legal join.
# Three hypotheses per class per family; all must be independently adjudicated.
NLI_FAMILIES = [
    ('assistance', 1, 'When requested assistance is withheld or denied, the decision and its reasons must be notified to the applicant authority without delay.',
     ['When requested assistance is withheld or denied, the applicant authority must receive the reasons.',
      'A denial of assistance triggers an obligation to notify the decision.',
      'The prescribed notification must occur without delay.'],
     ['No decision needs to be notified when the requested assistance is denied.',
      'The reasons for denying assistance need not be communicated to the applicant authority.',
      'The stated rule imposes no requirement to notify a refusal without delay.'],
     ['Every refusal must also be copied to all EU Member States.',
      'The applicant authority has a right to appeal the refusal to a court.',
      'The applicant authority must pay a fee for a refused request.']),
    ('interim_ip', 2, 'At an applicant\'s request, judicial authorities may issue an interlocutory injunction to prevent an imminent intellectual-property infringement, provisionally forbid continuation, or require guarantees for compensation. An injunction may also be issued against an intermediary whose services are used by a third party to infringe an intellectual-property right.',
     ['Preventing an imminent infringement is a permitted purpose of an interlocutory injunction.',
      'The described interim measures can make continuation subject to compensation guarantees.',
      'An intermediary whose services are used for infringement can be subject to an interlocutory injunction.'],
     ['Judicial authorities are prohibited from issuing an interlocutory injunction to prevent an imminent infringement.',
      'The stated measures exclude making continuation subject to compensation guarantees.',
      'An intermediary whose services are used for infringement can never be subject to the described injunction.'],
     ['Judicial authorities must grant every application for an interlocutory injunction.',
      'Court fees for an injunction application are EUR 100.',
      'An applicant automatically receives damages when requesting an injunction.']),
    ('vinegar', 4, 'For heading 2001, vegetables, fruit, nuts and other edible plant parts prepared or preserved by vinegar or acetic acid must contain at least 0.5% free volatile acid by weight, expressed as acetic acid.',
     ['The stated minimum free volatile acid content is 0.5% by weight.',
      'A relevant product containing only 0.4% free volatile acid by weight fails the stated acid-content requirement.',
      'The free volatile acid content is expressed as acetic acid.'],
     ['The stated acid-content rule sets a minimum of 0.05% by weight instead of 0.5%.',
      'A relevant product with 0.4% free volatile acid by weight satisfies the stated minimum acid-content requirement.',
      'The stated rule imposes no minimum free volatile acid content for the described heading-2001 products.'],
     ['Meeting the acid-content requirement is sufficient to satisfy every other classification condition.',
      'The tariff duty for the described products is 10%.',
      'This historical provision remains unchanged and applicable in September 2026.']),
    ('wood_flour', 5, 'For heading 4405, wood flour means wood powder of which not more than 8% by weight is retained by a sieve with an aperture of 0.63 mm.',
     ['The stated sieve aperture is 0.63 mm.',
      'Retaining exactly 8% by weight satisfies the stated maximum-retention condition.',
      'Wood powder with 9% by weight retained on the specified sieve does not meet this definition.'],
     ['The stated sieve aperture is 0.75 mm, not 0.63 mm.',
      'The definition requires at least 8% rather than not more than 8% retained by weight.',
      'Wood powder with 9% retained on the specified sieve meets this definition.'],
     ['The conventional tariff duty for all wood flour is 5%.',
      'Wood flour imported from Japan is prohibited.',
      'Passing the stated sieve condition exempts the importer from customs declarations.']),
    ('water_pipe', 6, 'For subheading 2403 11, water-pipe tobacco is tobacco intended for smoking in a water pipe and consisting of tobacco and glycerol, whether or not it contains aromatic oils and extracts, molasses or sugar, and whether or not it is fruit-flavoured. Tobacco-free products intended for water-pipe smoking are excluded.',
     ['The definition requires tobacco and glycerol.',
      'Fruit flavouring is optional under the stated definition.',
      'A tobacco-free water-pipe smoking product is excluded from the stated subheading.'],
     ['Fruit flavouring is mandatory under the stated definition.',
      'Tobacco-free water-pipe smoking products are expressly included in this subheading.',
      'The stated definition prohibits any product containing molasses or sugar.'],
     ['Every water-pipe tobacco product must contain at least 2% nicotine.',
      'Every distributor must obtain a special licence to sell this product.',
      'The rule prescribes a particular health warning on the packaging.']),
    ('blank_origin', 7, 'For a good or part made from a blank covered by the stated same-heading rule, origin is the country where every working edge, working surface and working part was configured to final shape and dimension, provided that the imported blank was incapable of functioning and was not advanced beyond initial stamping or the specified material-removal processing. If those criteria are not satisfied, origin is the origin of the blank of this Chapter.',
     ['Incapability of functioning in the imported condition is one required condition of the specified finishing-country rule.',
      'The stated rule concerns final configuration of every working edge, surface and part.',
      'If the paragraph-a criteria fail, the stated fallback is the country of origin of the blank.'],
     ['A fully functioning imported blank satisfies the specified incapability-of-functioning condition.',
      'Configuring only one working edge is sufficient even when other working edges, surfaces and parts remain unconfigured.',
      'The stated fallback when paragraph-a criteria fail is always the destination country, even if the blank originated elsewhere.'],
     ['The exporter automatically receives a refund of import duties.',
      'The finished good may enter the EU without any safety assessment.',
      'The rule specifies which customs office must receive the declaration.']),
    ('tir_entry', 8, 'The Convention enters into force six months after five eligible States have signed without reservation of ratification, acceptance or approval, or deposited their specified instruments. After that threshold, it enters into force for further Contracting Parties six months after deposit of their instruments.',
     ['The stated initial threshold is five eligible States completing the specified steps.',
      'The initial entry-into-force interval is six months after the threshold date.',
      'For further Contracting Parties, the stated interval is six months after their deposit.'],
     ['The initial rule requires only four eligible States, rather than five.',
      'The initial interval is three months rather than six months after the threshold date.',
      'A further Contracting Party is bound immediately on deposit, rather than after the stated six-month interval.'],
     ['The fifth eligible State completed the specified step on 1 May 2027.',
      'A particular named State has already deposited its instrument.',
      'Every later amendment takes effect on the same date as the original Convention.']),
    ('trade_committee', 9, 'The Committee on Trade in Goods shall meet at the request of a Party or the Trade Committee to consider any matter arising under the relevant Chapter and shall comprise representatives of the Parties.',
     ['A Party can request a meeting of the Committee on Trade in Goods.',
      'The Trade Committee can request such a meeting.',
      'The Committee on Trade in Goods comprises representatives of the Parties.'],
     ['Only the Trade Committee, and never a Party, can request such a meeting.',
      'The Trade Committee is expressly prohibited from requesting such a meeting.',
      'The Committee must comprise only representatives of third States, not representatives of the Parties.'],
     ['The meeting must take place within seven days of a request.',
      'Every meeting must be held in Brussels.',
      'The requesting Party must bear every cost of the meeting.']),
    ('origin_verification', 10, 'Subsequent verification of proofs of origin shall be carried out at random or whenever the importing country\'s customs authorities have reasonable doubts about document authenticity, product originating status or fulfilment of the other requirements of the Protocol.',
     ['Random subsequent verification is provided for by the stated rule.',
      'Reasonable doubts about document authenticity are a stated trigger for subsequent verification.',
      'Reasonable doubts about product originating status are a stated trigger for subsequent verification.'],
     ['Random subsequent verification is expressly forbidden under the stated rule.',
      'The stated rule excludes reasonable doubts about document authenticity as a verification trigger.',
      'The rule excludes doubts about fulfilment of other Protocol requirements as a verification trigger.'],
     ['All verification requests must be completed within five days.',
      'The importer always receives compensation when a proof is verified.',
      'The importer must pay a fixed fee for random verification.']),
    ('road_load', 11, 'During the stated road-load procedure, elapsed time, vehicle speed and relative air velocity, including wind speed and direction, shall be measured at 5 Hz. Ambient temperature shall be synchronised and sampled at a minimum of 1 Hz. Coastdown measurements require at least ten consecutive runs, five in each direction.',
     ['Vehicle speed must be measured at 5 Hz in the stated procedure.',
      'Ambient temperature sampled at 0.5 Hz fails the stated minimum sampling-frequency condition.',
      'The stated coastdown run count is at least ten, five in each direction.'],
     ['Vehicle speed measured only at 4 Hz meets the stated 5 Hz requirement.',
      'Ambient temperature sampled only at 0.5 Hz meets the stated minimum of 1 Hz.',
      'One coastdown run alone meets the stated minimum run-count requirement.'],
     ['The anemometer must be recalibrated every six months.',
      'Only equipment manufactured in the EU may be used.',
      'The procedure remains legally unchanged and applicable in September 2026.']),
]

REFERENCE_DRAFTS = {
    1: 'Notify the applicant authority of the refusal/withholding decision and the reasons, without delay; do not infer an appeal right or a fixed numeric deadline.',
    2: 'An interlocutory injunction may prevent imminent infringement, provisionally forbid continuation or require compensation guarantees. Preserve the applicant-request condition and any national-law qualifications; permission is not automatic grant.',
    3: 'The report checklist covers test substance, test species and test conditions. Complete the draft against the full supplied checklist; do not invent missing endpoint/report requirements.',
    4: 'At least 0.5% free volatile acid by weight, expressed as acetic acid, is the stated requirement for the described heading-2001 products. This threshold alone does not prove every classification condition.',
    5: 'Not more than 8% by weight retained by a sieve with a 0.63 mm aperture is the stated wood-flour definition for heading 4405.',
    6: 'Tobacco intended for water-pipe smoking and consisting of tobacco and glycerol, with listed additives/flavouring optional; tobacco-free products are excluded from subheading 2403 11.',
    7: 'Apply the finishing-country rule only if all paragraph-a conditions are met; otherwise use origin of the blank under paragraph b. Preserve the same-heading, functioning and processing conditions.',
    8: 'Six months after five eligible States complete the specified steps; further Contracting Parties are covered six months after their deposit. Do not infer actual deposit dates.',
    9: 'A Party or the Trade Committee may request the meeting, to consider matters arising under the relevant Chapter; preserve the agreement-specific scope.',
    10: 'At random or on reasonable doubts concerning authenticity, originating status or other Protocol requirements; do not silently make every agreement identical.',
    11: 'Elapsed time, vehicle speed and relative air velocity (wind speed/direction) at 5 Hz; synchronised ambient temperature at least 1 Hz. Preserve the procedure-specific scope.',
    18: 'The supplied Audi Brussels row records 3,076 for each year 2021–2025, totalling 15,380. A later revision for the same period may differ: identify document/version, not just years.',
    19: 'The supplied Lakeland Killeshandra row records 4,334 for each year 2021–2025, totalling 21,670. Confirm document/version and any later allocation revisions.',
    20: 'Rows 0–2 distinguish Metier*Fleet segment (Cell): A/A1/A2/A3; Metier: B/B1/B2/B3; Fleet segment: C/C1/C2/C3 across the displayed geographic levels. Do not invent the substantive meaning of the symbols.',
}


def source_record(connection, item):
    result = dict(item)
    rows = None
    for candidate in chunk_uri_candidates(item['document_id'], item['chunk_id']):
        rows = connection.execute('SELECT content FROM chunks WHERE graph_uri=? AND doc_id=? AND chunk_id=? ORDER BY vector_id DESC LIMIT 1',
                                  (str(candidate), item['document_id'], item['chunk_id'])).fetchone()
        if rows:
            break
    result['full_text'] = rows[0] if rows else item.get('excerpt', '')
    result['source_resolution'] = 'document_chunk_sqlite' if rows else 'packet_excerpt_only'
    result['text_is_complete'] = bool(rows)
    return result


def build_nli(cases):
    by_number = {int(case['case_id'].rsplit('_', 1)[1]): case for case in cases}
    families = [family[0] for family in NLI_FAMILIES]
    shuffled = sorted(families)
    random.Random(312).shuffle(shuffled)
    development_families = set(shuffled[:6])
    records = []
    for family, number, premise, entailed, contradicted, neutral in NLI_FAMILIES:
        source = by_number[number]['expected_chunks'][0]
        for label, hypotheses in [('entailment', entailed), ('contradiction', contradicted), ('neutral', neutral)]:
            for index, hypothesis in enumerate(hypotheses, 1):
                records.append({'pair_id': f'{family}_{label}_{index}', 'family_id': family,
                    'source_document_id': source['document_id'], 'source_chunk_id': source['chunk_id'],
                    'premise': premise, 'hypothesis': hypothesis,
                    'premise_kind': 'Codex paraphrase; source grounding requires review',
                    'hypothesis_kind': 'synthetic diagnostic proposition; not a claim of actual law',
                    'scope_assumption': 'Interpret under the same stated rule and conditions; infer neither current applicability nor unstated duties.',
                    'proposed_label': label, 'label_origin': 'Codex synthetic proposal',
                    'adjudicated_label': None, 'review_status': 'pending_AI_adjudication',
                    'split': 'development' if family in development_families else 'locked_test',
                    'source_excerpt': source['full_text'],
                    'difficulty_tag': ('modality_conditions_scope' if label != 'neutral' else 'unstated_actor_time_or_extra_duty'),
                    'rationale': 'Check against the entire premise and source, not lexical overlap.',
                    'reviewer_notes': ''})
    return records


def render_nli(records):
    lines = ['# AI-assisted legal-text NLI adjudication', '',
             'Proposed labels and model scores are withheld from this review copy.',
             'Label premise→hypothesis as entailment, contradiction or neutral, or reject/uncertain.',
             'First verify the premise against its supplied source. Hypotheses are synthetic, not real legal rules.',
             'Then label the exact premise→hypothesis text, not extra facts elsewhere in the source. If scope is missing, propose a correction instead of silently adding it.',
             'Do not import unstated law; permission does not entail obligation, and missing information is not negation.',
             'Return pair_id, premise_supported, label, confidence, rationale, exact supporting quote, and any scope correction.',
             'Do not tune thresholds. AI adjudication is not expert-certified ground truth.', '']
    sources = {}
    for record in records:
        source_key = (record['source_document_id'], record['source_chunk_id'])
        sources[source_key] = record['source_excerpt']
        lines.extend([f"## {record['pair_id']}", '', f"Premise: {record['premise']}", '',
                      f"Hypothesis: {record['hypothesis']}", '', f"Scope: {record['scope_assumption']}", '',
                      f"Source context below: {record['source_document_id']} / {record['source_chunk_id']}", ''])
    lines.extend(['# Source contexts (deduplicated)', ''])
    for (document_id, chunk_id), excerpt in sources.items():
        lines.extend([f'## {document_id} / {chunk_id}', '', '```text', excerpt, '```', ''])
    return '\n'.join(lines)


def render_qa(cases):
    lines = ['# AI-assisted natural-QA reference and retrieval review', '',
        'Phase A: validate questions, draft reference answers and answer-bearing retrieval.',
        'No system answers exist for these stored retrieval cases. Do NOT assign system PASS/PARTIAL/FAIL or QA accuracy yet.',
        'Do not accept source applicability, alternate-source equivalence or temporal coherence merely because wording matches.',
        'Return case_id; valid/revise/reject/uncertain; final question; verified reference answer with source quotes;',
        'expected source keys; sufficient/partial/insufficient/irrelevant retrieval; helpful retrieved source keys;',
        'scope/date/version caveats; confidence; and review notes. Use uncertain when sources are inadequate.',
        'Draft references are Codex proposals, not adjudicated gold. Review them independently.', '']
    for case in cases:
        lines.extend([f"## {case['case_id']}", '', case['question'], '',
                      f"Draft reference: {case['proposed_reference_answer']}", '',
                      f"Retrieval execution status: {case['retrieval_call_status']} (NOT relevance)", ''])
        for label, sources in [('Expected', case['expected_chunks']), ('Retrieved', case['retrieved_chunks'])]:
            for source in sources:
                lines.extend([f"### {label}: {source['document_id']} / {source['chunk_id']}", '',
                              f"Resolution: {source['source_resolution']}", '', '```text', source['full_text'], '```', ''])
        for label, tables in [('Expected table', case['expected_tables']), ('Retrieved table', case['retrieved_tables'])]:
            for table in tables:
                lines.extend([f"### {label}: {table['document_id']} / {table['table_id']}", '',
                              '```json', json.dumps(table, ensure_ascii=False, indent=2), '```', ''])
    return '\n'.join(lines)


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def finalize_existing():
    """Shuffle blinded presentation and bundle public files, preserving reviewed edits."""
    manifest_path = DESTINATION/'manifest_PRIVATE.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for filename, expected_hash in manifest['files_sha256'].items():
        if hashlib.sha256((DESTINATION/filename).read_bytes()).hexdigest() != expected_hash:
            raise RuntimeError(f'Packet file changed since generation; refusing regeneration: {filename}')
    path = DESTINATION/'nli_proposals_PRIVATE.jsonl'
    records = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
    random.Random(987612).shuffle(records)
    for index, record in enumerate(records, 1):
        record['pair_id'] = f'legal_nli_{index:03d}'
    path.write_text(''.join(json.dumps(record, ensure_ascii=False)+'\n' for record in records), encoding='utf-8')
    for index, offset in enumerate((0, 30, 60), 1):
        (DESTINATION/f'NLI_BATCH_{index}.md').write_text(render_nli(records[offset:offset+30]), encoding='utf-8')
    manifest['presentation_order_seed'] = 987612
    manifest['files_sha256'] = {file.name: hashlib.sha256(file.read_bytes()).hexdigest()
                               for file in sorted(DESTINATION.iterdir()) if file.name != manifest_path.name}
    write_json(manifest_path, manifest)
    public = [DESTINATION/'README.md'] + [DESTINATION/f'{prefix}_BATCH_{index}.md'
              for prefix in ('NATURAL_QA', 'NLI') for index in (1, 2, 3)]
    destination = DESTINATION/'AI_REVIEW_PACKETS.zip'
    with zipfile.ZipFile(destination, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for file in public:
            archive.write(file, arcname=file.name)
    print(json.dumps({'public_bundle': str(destination), 'private_files_included': False}))


def main():
    if DESTINATION.exists():
        raise FileExistsError(f'Refusing to overwrite versioned review packet: {DESTINATION}')
    original = json.loads(SOURCE_PACKET.read_text(encoding='utf-8'))
    connection = sqlite3.connect(f"file:{(Path(__file__).parent/'global_artifacts/chunk_index/chunk_metadata.sqlite').resolve().as_posix()}?mode=ro", uri=True)
    cases, excluded = [], []
    try:
        for old in original['cases']:
            if old['review_status'] == 'excluded_pending_replacement':
                excluded.append({'case_id': old['case_id'], 'question': old['question'],
                                 'reason': 'Previously rejected cross-instrument/temporal coherence; not in scoring denominator.'})
                continue
            number = int(old['case_id'].rsplit('_', 1)[1])
            expected_tables = [old['expected_table']] if old.get('expected_table') else []
            cases.append({'case_id': old['case_id'], 'category': old['category'],
                'question': old['question'], 'proposed_reference_answer': REFERENCE_DRAFTS[number],
                'reference_status': 'pending_AI_adjudication', 'system_answer': None,
                'score_eligible': False, 'expected_chunks': [source_record(connection, item) for item in old['expected_chunks']],
                'expected_tables': expected_tables,
                'retrieved_chunks': [source_record(connection, item) for item in old['retrieved']['chunks']],
                'retrieved_tables': old['retrieved']['tables'], 'retrieval_call_status': old['retrieved']['status'],
                'review': {'candidate_validity': None, 'reference_answer': None, 'answer_bearing_retrieval': None,
                           'scope_date_version_notes': '', 'confidence': None, 'label_origin': None}})
    finally:
        connection.close()
    records = build_nli(cases)
    DESTINATION.mkdir()
    write_json(DESTINATION/'natural_qa_candidates.json', {'stage': 'reference/retrieval review, not system QA scoring', 'cases': cases, 'excluded': excluded})
    for batch_number, batch in enumerate([cases[:5], cases[5:10], cases[10:]], 1):
        (DESTINATION/f'NATURAL_QA_BATCH_{batch_number}.md').write_text(render_qa(batch), encoding='utf-8')
    (DESTINATION/'nli_proposals_PRIVATE.jsonl').write_text(''.join(json.dumps(record, ensure_ascii=False)+'\n' for record in records), encoding='utf-8')
    for batch_number, batch in enumerate([records[:30], records[30:60], records[60:]], 1):
        # Label names in IDs must not anchor the reviewer.
        for offset, record in enumerate(batch, (batch_number-1)*30+1):
            record['pair_id'] = f'legal_nli_{offset:03d}'
        (DESTINATION/f'NLI_BATCH_{batch_number}.md').write_text(render_nli(batch), encoding='utf-8')
    # Persist opaque IDs in the machine-readable proposals too.
    (DESTINATION/'nli_proposals_PRIVATE.jsonl').write_text(''.join(json.dumps(record, ensure_ascii=False)+'\n' for record in records), encoding='utf-8')
    manifest = {'packet_version': '1', 'label_origin': 'AI-generated candidates; pending separate Chat adjudication',
        'natural_candidate_n': len(cases), 'natural_excluded_n': len(excluded),
        'nli_n': len(records), 'nli_proposed_class_counts': dict(Counter(record['proposed_label'] for record in records)),
        'nli_split_counts': dict(Counter(record['split'] for record in records)),
        'split_rule': 'seed 312, six of ten source families development, four locked-test; family/document disjoint',
        'split_status': 'preassigned before predictions; finalize reviewed labels before evaluation',
        'not_representative_benchmark': True,
        'source_packet_sha256': hashlib.sha256(SOURCE_PACKET.read_bytes()).hexdigest(),
        'files_sha256': {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(DESTINATION.iterdir())}}
    write_json(DESTINATION/'manifest_PRIVATE.json', manifest)
    readme = '''# Send these packets to Chat

Start with NATURAL_QA_BATCH_1.md, then batches 2 and 3. These 14 candidates
include expected AND retrieved complete chunk text and relevant table rows.
Six incoherent joins remain excluded; this set is formative, not representative.
Ask Chat to validate/correct the proposed references and review retrieval.
There are no system answers here yet: legal-QA outcome scoring is a later phase.

For NLI, send NLI_BATCH_1.md, then batches 2 and 3 (90 synthetic pairs, opaque
IDs, no proposed labels or predictions). Request the output fields at the top
of each packet. Do not send the PRIVATE proposal/manifest files during first
adjudication: they disclose proposed labels and splits. Allow uncertain/reject.
Do not force balanced final labels or tune on the locked test subset.

Save Chat's responses with the IDs and source-based rationales, and supply
them to Codex. Disagreement requires explicit adjudication/versioning; a vote
between AI models is not independent legal validation. All final labels must
be attributed to AI-assisted review, not expert review. No NIM calls or model
predictions were used to prepare these packets. No thresholds were changed.

The NLI corpus uses paraphrased source rules and synthetic hypotheses. It is
a legal-text component diagnostic, not a test that resolves real legal conflicts.
Full chunk text is supplied for scope checks; passage context may still depend
on another instrument or document version. Reject unsupported paraphrases.
'''
    (DESTINATION/'README.md').write_text(readme, encoding='utf-8')
    print(json.dumps({'destination': str(DESTINATION), 'natural_candidates': len(cases), 'nli_pairs': len(records)}))


if __name__ == '__main__':
    finalize_existing() if sys.argv[1:] == ['--finalize'] else main()
