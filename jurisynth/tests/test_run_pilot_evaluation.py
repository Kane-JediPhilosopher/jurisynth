from jurisynth.run_pilot_evaluation import _parser


def test_pilot_evaluation_cli_has_bounded_default_scope():
    args = _parser().parse_args([])

    assert args.limit == 50
    assert str(args.er_index).endswith("jurisynth\\pilot_artifacts\\batch_0009\\er_index")
