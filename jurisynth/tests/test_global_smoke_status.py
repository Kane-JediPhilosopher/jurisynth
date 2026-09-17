from jurisynth.run_global_smoke import _execution_summary


def test_leaf_completion_does_not_hide_upstream_retrieval_errors():
    summary = _execution_summary({'node_results': {'q1': {'status': 'complete', 'answer': {
        'claims': [], 'evidence_summary': {'retrieval_status': 'error'}}}}})
    assert summary == {'leaf_count': 1, 'failed_leaf_count': 0, 'retrieval_error_count': 1, 'claim_count': 0}
