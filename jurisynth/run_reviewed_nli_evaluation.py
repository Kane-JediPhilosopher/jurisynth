"""Offline CPU evaluation of frozen synthetic, AI-adjudicated legal NLI pairs."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import time

LABELS = ('contradiction', 'entailment', 'neutral')


def classification_metrics(gold, predictions):
    if not gold or len(gold) != len(predictions):
        raise ValueError('Nonempty aligned labels are required.')
    matrix = [[0]*3 for _ in LABELS]
    for actual, predicted in zip(gold, predictions):
        matrix[LABELS.index(actual)][LABELS.index(predicted)] += 1
    per_class = {}
    for i, label in enumerate(LABELS):
        tp = matrix[i][i]
        support = sum(matrix[i])
        predicted_count = sum(row[i] for row in matrix)
        precision = tp/predicted_count if predicted_count else 0.0
        recall = tp/support if support else 0.0
        per_class[label] = {'precision': precision, 'recall': recall,
                            'f1': 2*precision*recall/(precision+recall) if precision+recall else 0.0,
                            'support': support}
    return {'count': len(gold), 'accuracy': sum(matrix[i][i] for i in range(3))/len(gold),
            'macro_f1': sum(v['f1'] for v in per_class.values())/3,
            'per_class': per_class, 'confusion_matrix': matrix, 'matrix_label_order': LABELS}


def validate_dataset(rows):
    ids = [r['pair_id'] for r in rows]
    if not rows or len(ids) != len(set(ids)):
        raise ValueError('Empty or duplicate pairs.')
    groups = {}
    docs = {}
    for row in rows:
        if row['adjudicated_label'] not in LABELS or row['split'] not in {'development', 'locked_test'} or row.get('scope_correction_pending'):
            raise ValueError('Unreviewed labels or invalid split.')
        for key, registry in [('family_id', groups), ('source_document_id', docs)]:
            value = row[key]
            if value in registry and registry[value] != row['split']:
                raise ValueError('Family/document leakage across splits.')
            registry[value] = row['split']
    if set(groups.values()) != {'development', 'locked_test'}:
        raise ValueError('Both splits are required.')


def run(args):
    if args.output.exists():
        raise FileExistsError(args.output)
    raw = args.cases.read_bytes()
    rows = [json.loads(line) for line in raw.decode('utf-8').splitlines()]
    validate_dataset(rows)
    # Only cached local weights: no NIM calls or automatic downloads.
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    import numpy as np
    import torch
    from sentence_transformers import CrossEncoder
    torch.set_num_threads(2)
    started = time.perf_counter()
    model = CrossEncoder('cross-encoder/nli-deberta-v3-base', device='cpu', local_files_only=True)
    model.model.eval()
    pairs = [(r['premise'], r['hypothesis']) for r in rows]
    token_counts = [len(model.tokenizer(a, b, truncation=False)['input_ids']) for a, b in pairs]
    max_length = model.max_length or getattr(model.model.config, 'max_position_embeddings', 512)
    if max(token_counts) > max_length:
        raise ValueError('NLI pair would be truncated; revise the evaluation explicitly.')
    forward = np.asarray(model.predict(pairs, batch_size=4, show_progress_bar=False, activation_fn=torch.nn.Identity()))
    reverse = np.asarray(model.predict([(b, a) for a, b in pairs], batch_size=4, show_progress_bar=False, activation_fn=torch.nn.Identity()))
    if forward.shape != (len(rows), 3) or reverse.shape != forward.shape or not np.isfinite(forward).all() or not np.isfinite(reverse).all():
        raise ValueError('Expected finite three-class logits.')
    def probability(logits):
        values = np.exp(logits-logits.max(axis=1, keepdims=True))
        return values/values.sum(axis=1, keepdims=True)
    fp, rp = probability(forward), probability(reverse)
    records = [{**r, 'prediction': LABELS[int(forward[i].argmax())],
                'reverse_prediction_diagnostic_only': LABELS[int(reverse[i].argmax())],
                'forward_probabilities': dict(zip(LABELS, map(float, fp[i]))),
                'reverse_probabilities': dict(zip(LABELS, map(float, rp[i]))),
                'symmetric_contradiction_score_diagnostic': float((fp[i, 0]+rp[i, 0])/2),
                'input_tokens': token_counts[i]} for i, r in enumerate(rows)]
    results = {}
    for split in ('development', 'locked_test'):
        selected = [r for r in records if r['split'] == split]
        metrics = classification_metrics([r['adjudicated_label'] for r in selected], [r['prediction'] for r in selected])
        # No threshold selection; .95 is a diagnostic, not a new production default.
        from jurisynth.run_synthetic_nli_calibration import metrics as binary_metrics
        metrics['fixed_095_symmetric_diagnostic'] = binary_metrics(
            [r['adjudicated_label'] == 'contradiction' for r in selected],
            [r['symmetric_contradiction_score_diagnostic'] for r in selected], .95)
        metrics['aggregate_gate_only'] = metrics['macro_f1'] >= .70 and metrics['per_class']['contradiction']['precision'] >= .80
        results[split] = metrics
    result = {'status': 'completed', 'model': 'cross-encoder/nli-deberta-v3-base',
              'model_commit': getattr(model.model.config, '_commit_hash', None),
              'dataset_sha256': hashlib.sha256(raw).hexdigest(), 'dataset_kind': 'synthetic; AI-adjudicated, not expert validated',
              'seconds': round(time.perf_counter()-started, 3), 'device': 'cpu', 'threads': 2, 'batch_size': 4,
              'max_length': max_length, 'max_input_tokens': max(token_counts), 'truncated_pairs': 0,
              'class_order': LABELS, 'splits': results, 'threshold_tuning': False,
              'reverse_order_note': 'Reverse argmax is diagnostic only: forward entailment/neutral gold is not transferable. Symmetric contradiction uses mean of both directional probabilities; qualitative scope review still required.',
              'production_changes': False}
    args.output.mkdir(parents=True)
    (args.output/'RESULTS.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    (args.output/'predictions.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in records), encoding='utf-8')
    disagreements = [r for r in records if r['prediction'] != r['adjudicated_label']]
    text = '# AI-assisted NLI error review\n\nThis is synthetic AI-adjudicated data, not expert gold. Forward prediction errors below include source excerpts and scope notes. Assess whether the existing label remains justified; explicitly flag ambiguous negation/modality, actor, time or conditional scope. Do not tune thresholds or claim independent validation. Test results are now observed; any resulting dataset changes need a new version and must not be portrayed as untouched holdout validation. Reverse three-class outputs are diagnostic only.\n'
    for row in disagreements:
        text += '\n## '+row['pair_id']+'\n\n```json\n'+json.dumps(row, ensure_ascii=False, indent=2)+'\n```\n'
    (args.output/'CHAT_NLI_ERROR_REVIEW.md').write_text(text, encoding='utf-8')
    print(json.dumps({'status': 'completed', 'output': str(args.output), 'seconds': result['seconds'], 'disagreements': len(disagreements), 'splits': results}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', type=Path, default=Path('jurisynth/evaluation_artifacts/ai_assisted_review_v1/chat_adjudicated_v1/followup_v2/corrected_nli_pairs.jsonl'))
    parser.add_argument('--output', type=Path, default=Path('jurisynth/evaluation_artifacts/reviewed_nli_evaluation_v1'))
    run(parser.parse_args())
