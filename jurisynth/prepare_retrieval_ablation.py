"""Freeze a 40-case diagnostic development subset; never manufacture gold."""
import json
import random
from pathlib import Path


def select_development(results, seed=312):
    groups = {'exact_hit': [], 'component_miss': [], 'semantic_miss': []}
    for item in results:
        group = 'exact_hit' if item['assertion_recalled'] else (
            'component_miss' if any(item[field] for field in ('subject_entity_recalled', 'object_entity_recalled', 'predicate_recalled'))
            else 'semantic_miss')
        groups[group].append(item['case_id'])
    rng = random.Random(seed)
    selected, strata = [], {}
    for group, count in zip(groups, (14, 13, 13)):
        identifiers = sorted(groups[group])
        rng.shuffle(identifiers)
        if len(identifiers) < count:
            raise ValueError(f'Only {len(identifiers)} cases in {group}; need {count}.')
        strata[group] = identifiers[:count]
        selected.extend(identifiers[:count])
    return selected, strata


def main():
    root = Path('jurisynth/evaluation_artifacts')
    prefix = 'global_batch_stratified_subject-predicate_200_v2'
    results = [json.loads(line) for line in (root / f'{prefix}_results.jsonl').read_text(encoding='utf-8').splitlines()]
    cases = [json.loads(line) for line in (root / f'{prefix}_cases.jsonl').read_text(encoding='utf-8').splitlines()]
    identifiers, strata = select_development(results)
    destination = root / 'retrieval_ablation'
    destination.mkdir(exist_ok=True)
    plan = {'seed': 312, 'development_n': 40, 'held_out_n': 160,
            'gold_status': 'unvalidated KG-derived controlled probes; not legal-QA gold',
            'strata': strata, 'held_out_ids': sorted(set(item['case_id'] for item in cases) - set(identifiers))}
    target = destination / 'development_cases.jsonl'
    if target.exists():
        raise FileExistsError(f'Refusing to replace frozen development split: {target}')
    selected = {item['case_id']: item for item in cases}
    target.write_text(''.join(json.dumps(selected[identifier]) + '\n' for identifier in identifiers), encoding='utf-8')
    (destination / 'split_manifest.json').write_text(json.dumps(plan, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'development_n': 40, 'held_out_n': 160, 'destination': str(destination)}))


if __name__ == '__main__':
    main()
