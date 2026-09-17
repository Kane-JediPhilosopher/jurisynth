"""Prepare a source-complete, AI-assisted curation follow-up without API calls."""
import json
from pathlib import Path


def main():
    root = Path('jurisynth/evaluation_artifacts/ai_assisted_review_v1/chat_adjudicated_v1')
    output = root/'CHAT_FOLLOWUP_SOURCE_COMPLETE.md'
    if output.exists():
        raise FileExistsError(output)
    cases = [json.loads(line) for line in (root/'reviewed_natural_cases.jsonl').read_text(encoding='utf-8').splitlines()]
    pairs = [json.loads(line) for line in (root/'reviewed_nli_pairs.jsonl').read_text(encoding='utf-8').splitlines()]
    sections = ['# Focused AI-assisted review follow-up\n\nNo expert validation is claimed. Do not score system QA accuracy: system answers have not been generated.\n\nFor each of the six pending questions below, return a natural user-facing question, readable instrument/title and date or allocation period, revised reference answer, and exact supporting chunks/table rows. Keep machine IDs in metadata, not question text. Avoid implying simultaneous legal applicability across unrelated instruments. If supplied context cannot establish the title or period, mark unresolved rather than inventing it.\n\nFor the two NLI families, supply a corrected source-faithful premise preserving modal verbs and scope, then confirm or revise the labels for all nine hypotheses against that exact new premise. These are synthetic, AI-adjudicated labels, not independent expert gold.\n']
    for case in cases:
        if case.get('question_revision_pending'):
            sections.append(f"## QA {case['case_id']}\n\n```json\n" + json.dumps(case, ensure_ascii=False, indent=2) + '\n```\n')
    families = sorted({pair['family_id'] for pair in pairs if pair.get('scope_correction_pending')})
    for family in families:
        selected = [pair for pair in pairs if pair['family_id'] == family]
        sections.append(f'## NLI family {family}\n\n```json\n' + json.dumps(selected, ensure_ascii=False, indent=2) + '\n```\n')
    output.write_text('\n'.join(sections), encoding='utf-8')
    print(json.dumps({'output': str(output), 'pending_questions': sum(bool(c.get('question_revision_pending')) for c in cases), 'pending_nli_families': len(families)}))


if __name__ == '__main__':
    main()
