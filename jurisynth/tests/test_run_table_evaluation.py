from jurisynth.run_table_evaluation import _parser


def test_table_evaluation_cli_defaults_to_small_reviewable_scope():
    args = _parser().parse_args([])
    assert args.limit == 20
    assert args.query_style == "natural"
