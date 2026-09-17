import pytest
from jurisynth.run_reviewed_nli_evaluation import classification_metrics, validate_dataset


def test_perfect_three_class_metrics():
    labels = ['contradiction', 'entailment', 'neutral']
    result = classification_metrics(labels, labels)
    assert result['macro_f1'] == 1
    assert result['confusion_matrix'] == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]


def test_zero_predicted_class_has_zero_precision():
    result = classification_metrics(['contradiction', 'entailment', 'neutral'], ['neutral']*3)
    assert result['per_class']['contradiction']['precision'] == 0


def test_family_leakage_is_rejected():
    rows = [dict(pair_id=str(i), family_id='shared', source_document_id=str(i), split=split,
                 adjudicated_label='neutral', scope_correction_pending=False) for i, split in enumerate(('development', 'locked_test'))]
    with pytest.raises(ValueError, match='leakage'):
        validate_dataset(rows)
