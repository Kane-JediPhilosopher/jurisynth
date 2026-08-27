import pytest

from pathlib import Path
import asyncio
import json

import main


# ---------------------------------------------------------------------
# get_batch_paths()
# ---------------------------------------------------------------------

def test_get_batch_paths_constructs_expected_paths(tmp_path, monkeypatch):
    input_root = tmp_path / "eu_legislation"
    intermediate_root = tmp_path / "intermediate"
    output_root = tmp_path / "output"

    batch_dir = input_root / "batch_01"
    batch_dir.mkdir(parents=True)

    monkeypatch.setattr(main, "INTERMEDIATE_DIR", intermediate_root)
    monkeypatch.setattr(main, "OUTPUT_DIR", output_root)

    paths = main.get_batch_paths(batch_dir)

    assert paths["input_dir"] == batch_dir

    assert paths["batch_intermediate_dir"] == (
        intermediate_root / "batch_01"
    )

    assert paths["converted_dir"] == (
        intermediate_root / "batch_01" / "converted"
    )

    assert paths["batch_output_dir"] == (
        output_root / "batch_01"
    )

    assert paths["chunk_index_dir"] == (
        output_root / "batch_01" / "chunk_index"
    )

    assert paths["chunk_index_path"] == (
        output_root
        / "batch_01"
        / "chunk_index"
        / "chunk_index.faiss"
    )

    assert paths["chunk_metadata_path"] == (
        output_root
        / "batch_01"
        / "chunk_index"
        / "chunk_metadata.pkl"
    )

    assert paths["graph_output_dir"] == (
        output_root / "batch_01" / "graph"
    )

    assert paths["graph_output_file"] == (
        output_root
        / "batch_01"
        / "graph"
        / "jurisynth_graph.nq"
    )

    assert paths["success_marker"] == (
        output_root / "batch_01" / ".success"
    )


# ---------------------------------------------------------------------
# discover_batches()
# ---------------------------------------------------------------------

def test_discover_batches_returns_directories_in_sorted_order(
    tmp_path,
    monkeypatch,
):
    input_dir = tmp_path / "eu_legislation"
    input_dir.mkdir()

    (input_dir / "batch_03").mkdir()
    (input_dir / "batch_01").mkdir()
    (input_dir / "batch_02").mkdir()

    (input_dir / "not_a_batch.txt").write_text("ignore")

    monkeypatch.setattr(main, "INPUT_DIR", input_dir)

    batches = main.discover_batches()

    assert batches == [
        input_dir / "batch_01",
        input_dir / "batch_02",
        input_dir / "batch_03",
    ]


# ---------------------------------------------------------------------
# is_batch_complete()
# ---------------------------------------------------------------------

def test_is_batch_complete_returns_false_without_marker(tmp_path):
    paths = {
        "success_marker": tmp_path / ".success"
    }

    assert main.is_batch_complete(paths) is False


def test_is_batch_complete_returns_true_with_marker(tmp_path):
    marker = tmp_path / ".success"
    marker.touch()

    paths = {
        "success_marker": marker
    }

    assert main.is_batch_complete(paths) is True


# ---------------------------------------------------------------------
# run_batch_pipeline()
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_run_batch_pipeline_calls_pipeline_stages_in_order(
    tmp_path,
    monkeypatch,
):
    batch_dir = tmp_path / "batch_01"
    batch_dir.mkdir()

    paths = {
        "converted_dir": tmp_path / "converted",
        "chunk_index_dir": tmp_path / "chunk_index",
        "chunk_index_path": tmp_path / "chunk_index.faiss",
        "chunk_metadata_path": tmp_path / "chunk_metadata.pkl",
        "graph_output_dir": tmp_path / "graph",
        "graph_output_file": tmp_path / "graph" / "graph.nq",
        "diagnostics_dir": tmp_path / "diagnostics",
        "extraction_errors_path": tmp_path / "diagnostics" / "extraction_errors.json",
        "resolution_metadata_path": tmp_path / "diagnostics" / "resolution_metadata.json",
        "validation_errors_path": tmp_path / "diagnostics" / "validation_errors.json",
        "validation_stats_path": tmp_path / "diagnostics" / "validation_stats.json",
    }

    calls = []

    def fake_convert_documents(input_dir, output_dir):
        calls.append(("convert", input_dir, output_dir))

    def fake_chunk_documents(converted_dir):
        calls.append(("chunk", converted_dir))

        return [
            {
                "doc_id": "d1",
                "chunk_id": "chunk_1",
                "content": type(
                    "Chunk",
                    (),
                    {"text": "Test chunk."},
                )(),
            }
        ]

    def fake_build_chunk_vector_store(
        raw_chunks,
        embedding_model,
    ):
        calls.append(("build_index", raw_chunks, embedding_model))
        return "INDEX", "LOOKUP"

    def fake_save_chunk_vector_store(
        index,
        lookup,
        index_path,
        metadata_path,
    ):
        calls.append(
            (
                "save_index",
                index,
                lookup,
                index_path,
                metadata_path,
            )
        )

    def fake_process_chunks(raw_chunks):
        calls.append(("process", raw_chunks))
        return ["processed"]

    async def fake_extract_assertions(
        client,
        processed_chunks,
    ):
        calls.append(
            (
                "extract",
                client,
                processed_chunks,
            )
        )
        return ["assertion"], []

    def fake_normalize_assertions(assertions):
        calls.append(("normalize", assertions))
        return ["normalized"]

    def fake_match_assertions(
        assertions,
        classes,
        object_properties,
        datatype_properties,
        resource_metadata,
        emb_model,
    ):
        calls.append(("match", assertions))
        return ["scored"]

    async def fake_resolve_assertions(
        client,
        scored_assertions,
        emb_model,
    ):
        calls.append(("resolve", scored_assertions))
        return ["resolved"], {}

    def fake_validate(
        assertions,
        resource_metadata,
    ):
        calls.append(("validate", assertions))
        return ["validated"], [], {}

    def fake_serialize_graph(
        assertions,
        schema_namespaces,
        output_file,
    ):
        calls.append(("serialize", assertions, output_file))

    monkeypatch.setattr(
        main,
        "convert_documents",
        fake_convert_documents,
    )
    monkeypatch.setattr(
        main,
        "chunk_documents",
        fake_chunk_documents,
    )
    monkeypatch.setattr(
        main,
        "build_chunk_vector_store",
        fake_build_chunk_vector_store,
    )
    monkeypatch.setattr(
        main,
        "save_chunk_vector_store",
        fake_save_chunk_vector_store,
    )
    monkeypatch.setattr(
        main,
        "process_chunks",
        fake_process_chunks,
    )
    monkeypatch.setattr(
        main,
        "extract_assertions",
        fake_extract_assertions,
    )
    monkeypatch.setattr(
        main,
        "normalize_assertions",
        fake_normalize_assertions,
    )
    monkeypatch.setattr(
        main,
        "match_assertions",
        fake_match_assertions,
    )
    monkeypatch.setattr(
        main,
        "resolve_assertions",
        fake_resolve_assertions,
    )
    monkeypatch.setattr(
        main,
        "run_assertion_validation",
        fake_validate,
    )
    monkeypatch.setattr(
        main,
        "serialize_graph",
        fake_serialize_graph,
    )

    schema = {
        "classes": {},
        "object_properties": {},
        "datatype_properties": {},
        "resource_metadata": {},
        "namespaces": set(),
    }

    emb_model = object()
    client = object()

    await main.run_batch_pipeline(
        batch_dir=batch_dir,
        batch_paths=paths,
        schema=schema,
        emb_model=emb_model,
        client=client,
    )

    assert [call[0] for call in calls] == [
        "convert",
        "chunk",
        "build_index",
        "save_index",
        "process",
        "extract",
        "normalize",
        "match",
        "resolve",
        "validate",
        "serialize",
    ]


# ---------------------------------------------------------------------
# main() — no batches
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_main_rejects_empty_batch_directory(
    tmp_path,
    monkeypatch,
):
    monkeypatch.setattr(main, "INPUT_DIR", tmp_path)

    monkeypatch.setattr(
        main,
        "SentenceTransformer",
        lambda *_args, **_kwargs: object(),
    )

    monkeypatch.setattr(
        main,
        "create_client",
        lambda: object(),
    )

    monkeypatch.setattr(
        main,
        "load_schema",
        lambda *_args: {},
    )

    with pytest.raises(RuntimeError, match="No batch directories"):
        await main.main()


# ---------------------------------------------------------------------
# main() — skips completed batches
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_main_skips_completed_batches(
    tmp_path,
    monkeypatch,
):
    input_dir = tmp_path / "eu_legislation"
    input_dir.mkdir()

    batch_01 = input_dir / "batch_01"
    batch_01.mkdir()

    output_dir = tmp_path / "output"
    batch_output = output_dir / "batch_01"
    batch_output.mkdir(parents=True)

    success_marker = batch_output / ".success"
    success_marker.touch()

    monkeypatch.setattr(main, "INPUT_DIR", input_dir)
    monkeypatch.setattr(main, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(
        main,
        "INTERMEDIATE_DIR",
        tmp_path / "intermediate",
    )

    monkeypatch.setattr(
        main,
        "SentenceTransformer",
        lambda *_args, **_kwargs: object(),
    )

    monkeypatch.setattr(
        main,
        "create_client",
        lambda: object(),
    )

    monkeypatch.setattr(
        main,
        "load_schema",
        lambda *_args: {},
    )

    async def fail_if_called(*args, **kwargs):
        pytest.fail(
            "run_batch_pipeline should not be called "
            "for a completed batch."
        )

    monkeypatch.setattr(
        main,
        "run_batch_pipeline",
        fail_if_called,
    )

    await main.main()


# ---------------------------------------------------------------------
# main() — failed batch does not stop later batches
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_main_continues_after_batch_failure(
    tmp_path,
    monkeypatch,
):
    input_dir = tmp_path / "eu_legislation"
    input_dir.mkdir()

    batch_01 = input_dir / "batch_01"
    batch_02 = input_dir / "batch_02"

    batch_01.mkdir()
    batch_02.mkdir()

    output_dir = tmp_path / "output"
    intermediate_dir = tmp_path / "intermediate"

    monkeypatch.setattr(main, "INPUT_DIR", input_dir)
    monkeypatch.setattr(main, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(
        main,
        "INTERMEDIATE_DIR",
        intermediate_dir,
    )

    monkeypatch.setattr(
        main,
        "SentenceTransformer",
        lambda *_args, **_kwargs: object(),
    )

    monkeypatch.setattr(
        main,
        "create_client",
        lambda: object(),
    )

    monkeypatch.setattr(
        main,
        "load_schema",
        lambda *_args: {},
    )

    processed = []

    async def fake_run_batch_pipeline(
        batch_dir,
        batch_paths,
        schema,
        emb_model,
        client,
    ):
        processed.append(batch_dir.name)

        if batch_dir.name == "batch_01":
            raise RuntimeError("synthetic failure")

        batch_paths["success_marker"].parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    monkeypatch.setattr(
        main,
        "run_batch_pipeline",
        fake_run_batch_pipeline,
    )

    await main.main()

    assert processed == [
        "batch_01",
        "batch_02",
    ]

    assert not (
        output_dir / "batch_01" / ".success"
    ).exists()

    assert (
        output_dir / "batch_02" / ".success"
    ).exists()


# ---------------------------------------------------------------------
# main() — successful batch receives success marker
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_main_marks_successful_batch_complete(
    tmp_path,
    monkeypatch,
):
    input_dir = tmp_path / "eu_legislation"
    input_dir.mkdir()

    batch_dir = input_dir / "batch_01"
    batch_dir.mkdir()

    output_dir = tmp_path / "output"
    intermediate_dir = tmp_path / "intermediate"

    monkeypatch.setattr(main, "INPUT_DIR", input_dir)
    monkeypatch.setattr(main, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(
        main,
        "INTERMEDIATE_DIR",
        intermediate_dir,
    )

    monkeypatch.setattr(
        main,
        "SentenceTransformer",
        lambda *_args, **_kwargs: object(),
    )

    monkeypatch.setattr(
        main,
        "create_client",
        lambda: object(),
    )

    monkeypatch.setattr(
        main,
        "load_schema",
        lambda *_args: {},
    )

    async def fake_run_batch_pipeline(
        batch_dir,
        batch_paths,
        schema,
        emb_model,
        client,
    ):
        batch_paths["success_marker"].parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    monkeypatch.setattr(
        main,
        "run_batch_pipeline",
        fake_run_batch_pipeline,
    )

    await main.main()

    assert (
        output_dir / "batch_01" / ".success"
    ).exists()

# ---------------------------------------------------------------------
# Interruption handling
# ---------------------------------------------------------------------

@pytest.mark.asyncio
async def test_main_propagates_cancellation(
    tmp_path,
    monkeypatch,
):
    input_dir = tmp_path / "eu_legislation"
    input_dir.mkdir()

    batch_dir = input_dir / "batch_01"
    batch_dir.mkdir()

    output_dir = tmp_path / "output"

    monkeypatch.setattr(main, "INPUT_DIR", input_dir)
    monkeypatch.setattr(main, "OUTPUT_DIR", output_dir)

    monkeypatch.setattr(
        main,
        "SentenceTransformer",
        lambda *_args, **_kwargs: object(),
    )

    monkeypatch.setattr(
        main,
        "create_client",
        lambda: object(),
    )

    monkeypatch.setattr(
        main,
        "load_schema",
        lambda *_args: {},
    )

    async def fake_run_batch_pipeline(
        batch_dir,
        batch_paths,
        schema,
        emb_model,
        client,
    ):
        raise asyncio.CancelledError

    monkeypatch.setattr(
        main,
        "run_batch_pipeline",
        fake_run_batch_pipeline,
    )

    with pytest.raises(asyncio.CancelledError):
        await main.main()


@pytest.mark.asyncio
async def test_interrupted_batch_is_not_marked_successful(
    tmp_path,
    monkeypatch,
):
    input_dir = tmp_path / "eu_legislation"
    input_dir.mkdir()

    batch_dir = input_dir / "batch_01"
    batch_dir.mkdir()

    output_dir = tmp_path / "output"

    monkeypatch.setattr(main, "INPUT_DIR", input_dir)
    monkeypatch.setattr(main, "OUTPUT_DIR", output_dir)

    monkeypatch.setattr(
        main,
        "SentenceTransformer",
        lambda *_args, **_kwargs: object(),
    )

    monkeypatch.setattr(
        main,
        "create_client",
        lambda: object(),
    )

    monkeypatch.setattr(
        main,
        "load_schema",
        lambda *_args: {},
    )

    async def fake_run_batch_pipeline(
        batch_dir,
        batch_paths,
        schema,
        emb_model,
        client,
    ):
        raise asyncio.CancelledError

    monkeypatch.setattr(
        main,
        "run_batch_pipeline",
        fake_run_batch_pipeline,
    )

    with pytest.raises(asyncio.CancelledError):
        await main.main()

    assert not (
        output_dir / "batch_01" / ".success"
    ).exists()


# ---------------------------------------------------------------------
# Persisting diagnostics
# ---------------------------------------------------------------------

def test_save_json(tmp_path):
    output_path = tmp_path / "diagnostics.json"

    data = {
        "errors": ["example"],
        "count": 1,
    }

    main.save_json(data, output_path)

    assert output_path.exists()

    with output_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        loaded = json.load(file)

    assert loaded == data


@pytest.mark.asyncio
async def test_batch_pipeline_creates_diagnostics_directory(
    tmp_path,
    monkeypatch,
):
    batch_dir = tmp_path / "batch_01"
    batch_dir.mkdir()

    output_dir = tmp_path / "output"
    intermediate_dir = tmp_path / "intermediate"

    monkeypatch.setattr(
        main,
        "OUTPUT_DIR",
        output_dir,
    )

    monkeypatch.setattr(
        main,
        "INTERMEDIATE_DIR",
        intermediate_dir,
    )

    batch_paths = main.get_batch_paths(batch_dir)

    assert batch_paths["diagnostics_dir"] == (
        output_dir / "batch_01" / "diagnostics"
    )