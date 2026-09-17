"""Prepare a loss-of-intent/dependency review from the preserved component AST."""
import json
from pathlib import Path


def main():
    root = Path('jurisynth')
    output = root/'evaluation_artifacts/CHAT_AST_FIDELITY_REVIEW_v1.md'
    if output.exists():
        raise FileExistsError(output)
    smoke = json.loads((root/'run_outputs/structured_output_smoke_v4.json').read_text(encoding='utf-8'))
    case = next(c for c in smoke['cases'] if c['variant'] == 'messy')
    query = (root/'evaluation_artifacts/complex_ai_medical_messy.txt').read_text(encoding='utf-8')
    text = '# AST intent-fidelity review\n\nThis is a successful compilation/first-leaf interpretation component smoke, not proof of complete query coverage or end-to-end legal QA. Review whether the AST preserves every distinct original request, scenario facts, uncertainty and conditional scope. Specifically check GDPR data reuse, cross-regime compliance, subgroup performance and incident-response questions. For each dependency, distinguish a real need for an upstream answer from a related topic. Do not force dependencies merely to make the tree look complex. Return omissions, unsupported additions, questionable edges, and a proposed faithful decomposition. Changes to prompts/planning require owner approval. No legal answer is requested.\n\n## Original user question\n\n'+query+'\n\n## Preserved compilation\n\n```json\n'+json.dumps({k: case[k] for k in ('expression', 'ast', 'leaves', 'attempts')}, ensure_ascii=False, indent=2)+'\n```\n'
    output.write_text(text, encoding='utf-8')
    print(json.dumps({'output': str(output), 'leaf_count': len(case['leaves'])}))


if __name__ == '__main__':
    main()
