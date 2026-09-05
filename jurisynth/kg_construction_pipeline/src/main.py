print("Importing modules...\n")

from pathlib import Path
from sentence_transformers import SentenceTransformer
import asyncio
import json
import os
import pickle

from llm_utils import create_client
print("Imported all required utilities.\n")

from schema_loader import load_schema
print(f"Loaded Schema Loader module | PID={os.getpid()}")

from doc_converter import convert_documents
print(f"Loaded Document Converter module | PID={os.getpid()}")

from hybrid_chunker import chunk_documents
print(f"Loaded Hybrid Chunker module | PID={os.getpid()}")

from chunk_index_builder import build_chunk_vector_store, save_chunk_vector_store
print(f"Loaded Chunk Index Builder module | PID={os.getpid()}")

from chunk_processor import process_chunks
print(f"Loaded Chunk Procesor module | PID={os.getpid()}")

from assertion_extractor import extract_assertions
print(f"Loaded Assertion Extractor module | PID={os.getpid()}")

from assertion_normalizer import normalize_assertions
print(f"Loaded Assertion Normalizer module | PID={os.getpid()}")

from semantic_matcher import match_assertions
print(f"Loaded Semantic Matcher module | PID={os.getpid()}")

from ent_rel_resolver import resolve_assertions
print(f"Loaded E-R Resolver module | PID={os.getpid()}")

from assertion_validator import run_assertion_validation
print(f"Loaded Assertion Validator module | PID={os.getpid()}")

from graph_serializer import serialize_graph
print(f"Loaded Graph Serializer module | PID={os.getpid()}")
print()


# Global paths
BASE_DIR = Path(__file__).resolve().parent.parent

SCHEMA_DIR = BASE_DIR.parent / "schema"
INPUT_DIR = BASE_DIR.parent.parent / "eu_legislation"

DATA_DIR = BASE_DIR / "data"
INTERMEDIATE_DIR = BASE_DIR / "intermediate"
OUTPUT_DIR = BASE_DIR / "output"


def get_batch_paths(batch_dir: Path) -> dict[str, Path]:
    """Construct all paths associated with a single processing batch."""

    batch_name = batch_dir.name

    batch_intermediate_dir = INTERMEDIATE_DIR / batch_name
    batch_output_dir = OUTPUT_DIR / batch_name

    checkpoints_dir = batch_output_dir / "checkpoints"
    diagnostics_dir = batch_output_dir / "diagnostics"
    converted_dir = batch_intermediate_dir / "converted"

    chunk_index_dir = batch_output_dir / "chunk_index"
    graph_output_dir = batch_output_dir / "graph"

    return {
        # Preprocessed input
        "batch_source_dir": batch_dir,
        "input_dir": batch_dir / "processed_docs",

        # Preprocessor artifacts
        "table_store_dir": batch_dir / "table_store",
        "table_index_dir": batch_dir / "table_index",
        "image_store_dir": batch_dir / "image_store",

        # Intermediate data
        "batch_intermediate_dir": batch_intermediate_dir,
        "converted_dir": converted_dir,

        # Persistent outputs
        "batch_output_dir": batch_output_dir,

        "checkpoints_dir": checkpoints_dir,
        "extracted_checkpoint": checkpoints_dir / "extracted_assertions.pkl",
        "normalized_checkpoint": checkpoints_dir / "normalized_assertions.pkl",
        "scored_checkpoint": checkpoints_dir / "scored_assertions.pkl",
        "resolved_checkpoint": checkpoints_dir / "resolved_assertions.pkl",

        "chunk_index_dir": chunk_index_dir,
        "chunk_index_path": chunk_index_dir / "chunk_index.faiss",
        "chunk_metadata_path": chunk_index_dir / "chunk_metadata.pkl",

        "graph_output_dir": graph_output_dir,
        "graph_output_file": graph_output_dir / "jurisynth_graph.nq",

        # Diagnostics
        "diagnostics_dir": diagnostics_dir,
        "extraction_errors_path":
            diagnostics_dir / "extraction_errors.json",
        "resolution_metadata_path":
            diagnostics_dir / "resolution_metadata.json",
        "validation_errors_path":
            diagnostics_dir / "validation_errors.json",
        "validation_stats_path":
            diagnostics_dir / "validation_stats.json",

        # Resumability
        "success_marker": batch_output_dir / ".success",
    }


def discover_batches() -> list[Path]:
    """Return batch directories in deterministic order."""

    return sorted(
        path
        for path in INPUT_DIR.iterdir()
        if (
            path.is_dir()
            and path.name.startswith("batch_")
        )
    )


def is_batch_complete(batch_paths: dict[str, Path]) -> bool:
    """Return whether a batch has been successfully completed."""

    return batch_paths["success_marker"].exists()


def save_pickle_atomic(
    data,
    output_path: Path,
) -> None:
    """
    Persist a pickle checkpoint atomically.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temp_path = output_path.with_suffix(
        output_path.suffix + ".tmp"
    )

    with temp_path.open("wb") as file:

        pickle.dump(
            data,
            file,
            protocol=pickle.HIGHEST_PROTOCOL,
        )

        file.flush()
        os.fsync(file.fileno())

    os.replace(
        temp_path,
        output_path,
    )


def load_pickle(
    input_path: Path,
):
    with input_path.open("rb") as file:
        return pickle.load(file)


def save_json(data, output_path: Path) -> None:
    """Persist diagnostic data as JSON."""

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
            default=str,
        )


async def run_batch_pipeline(
    batch_dir: Path,
    batch_paths: dict[str, Path],
    schema: dict,
    emb_model: SentenceTransformer,
    client,
):
    """Run the complete Jurisynth pipeline for one batch."""

    batch_name = batch_dir.name

    # -----------------------------------------------------------------
    # Create batch-specific directories.
    # -----------------------------------------------------------------

    for directory in (
        batch_paths["converted_dir"],
        batch_paths["chunk_index_dir"],
        batch_paths["graph_output_dir"],
        batch_paths["diagnostics_dir"],
        batch_paths["checkpoints_dir"],
    ):
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    print()
    print("=" * 80)
    print(f"PROCESSING {batch_name}")
    print("=" * 80)

    # -----------------------------------------------------------------
    # Determine resume point from latest available checkpoint.
    # -----------------------------------------------------------------

    if batch_paths["resolved_checkpoint"].exists():
        resume_stage = 10

    elif batch_paths["scored_checkpoint"].exists():
        resume_stage = 9

    elif batch_paths["normalized_checkpoint"].exists():
        resume_stage = 8

    elif batch_paths["extracted_checkpoint"].exists():
        resume_stage = 7

    else:
        resume_stage = 2

    print(
        f"[Resume] Starting from stage {resume_stage}/11.",
        flush=True,
    )

    # -----------------------------------------------------------------
    # 1. Document preprocessing.
    # -----------------------------------------------------------------

    print("\n[1/11] Document preprocessing is handled externally.")

    if resume_stage <= 6:

        # -----------------------------------------------------------------
        # 2. Convert documents.
        # -----------------------------------------------------------------

        print("\n[2/11] Converting HTML documents to Markdown...")

        convert_documents(
            input_dir=batch_paths["input_dir"],
            output_dir=batch_paths["converted_dir"],
        )

        print("[2/11] Document conversion complete.")

        # -----------------------------------------------------------------
        # 3. Chunk documents.
        # -----------------------------------------------------------------

        print("\n[3/11] Chunking documents...")

        raw_chunks = chunk_documents(
            batch_paths["converted_dir"]
        )

        print(
            f"[3/11] Chunking complete: "
            f"{len(raw_chunks)} raw chunks."
        )

        # -----------------------------------------------------------------
        # 4. Build chunk vector store.
        # -----------------------------------------------------------------

        print("\n[4/11] Building chunk vector store...")

        chunk_index, chunk_lookup = build_chunk_vector_store(
            raw_chunks=raw_chunks,
            embedding_model=emb_model,
        )

        save_chunk_vector_store(
            chunk_index,
            chunk_lookup,
            batch_paths["chunk_index_path"],
            batch_paths["chunk_metadata_path"],
        )

        print("[4/11] Chunk vector store saved.")

        # -----------------------------------------------------------------
        # 5. Process chunks.
        # -----------------------------------------------------------------

        print("\n[5/11] Processing chunks...")

        processed_chunks = process_chunks(
            raw_chunks=raw_chunks
        )

        print(
            f"[5/11] Chunk processing complete: "
            f"{len(processed_chunks)} chunks retained."
        )

    # -----------------------------------------------------------------
    # 6. Extract assertions.
    # -----------------------------------------------------------------

    if resume_stage <= 6:

        print("\n[6/11] Extracting assertions...")

        extracted_assertions, extraction_errors = (
            await extract_assertions(
                client=client,
                processed_chunks=processed_chunks,
            )
        )

        save_pickle_atomic(
            extracted_assertions,
            batch_paths["extracted_checkpoint"],
        )

        save_json(
            extraction_errors,
            batch_paths["extraction_errors_path"],
        )

    elif resume_stage == 7:

        extracted_assertions = load_pickle(
            batch_paths["extracted_checkpoint"]
        )

        print(
            f"\n[6/11] Loaded extraction checkpoint: "
            f"{len(extracted_assertions):,} results."
        )


    # -----------------------------------------------------------------
    # 7. Normalize assertions.
    # -----------------------------------------------------------------

    if resume_stage <= 7:

        print("\n[7/11] Normalizing assertions...")

        normalized_assertions = normalize_assertions(
            extracted_assertions
        )

        save_pickle_atomic(
            normalized_assertions,
            batch_paths["normalized_checkpoint"],
        )

    elif resume_stage == 8:

        normalized_assertions = load_pickle(
            batch_paths["normalized_checkpoint"]
        )

        print(
            f"\n[7/11] Loaded normalization checkpoint: "
            f"{len(normalized_assertions):,} assertions."
        )


    # -----------------------------------------------------------------
    # 8. Semantic matching.
    # -----------------------------------------------------------------

    if resume_stage <= 8:

        print("\n[8/11] Semantically matching assertions...")

        scored_assertions = match_assertions(
            normalized_assertions,
            schema["classes"],
            schema["object_properties"],
            schema["datatype_properties"],
            schema["resource_metadata"],
            emb_model=emb_model,
        )

        save_pickle_atomic(
            scored_assertions,
            batch_paths["scored_checkpoint"],
        )

    elif resume_stage == 9:

        scored_assertions = load_pickle(
            batch_paths["scored_checkpoint"]
        )

        print(
            f"\n[8/11] Loaded semantic-match checkpoint: "
            f"{len(scored_assertions):,} assertions."
        )

    # -----------------------------------------------------------------
    # 9. Entity-relation resolution.
    # -----------------------------------------------------------------

    if resume_stage <= 9:

        print("\n[9/11] Resolving entities and relations...")

        resolved_assertions, resolution_metadata = (
            await resolve_assertions(
                client=client,
                scored_assertions=scored_assertions,
                emb_model=emb_model,
            )
        )

        save_pickle_atomic(
            resolved_assertions,
            batch_paths["resolved_checkpoint"],
        )

        save_json(
            resolution_metadata,
            batch_paths["resolution_metadata_path"],
        )

    else:

        resolved_assertions = load_pickle(
            batch_paths["resolved_checkpoint"]
        )

        print(
            f"\n[9/11] Loaded resolution checkpoint: "
            f"{len(resolved_assertions):,} assertions."
        )

    # -----------------------------------------------------------------
    # 10. Validation.
    # -----------------------------------------------------------------

    print("\n[10/11] Validating assertions...")

    (
        validated_assertions,
        validation_errors,
        validation_stats,
    ) = run_assertion_validation(
        resolved_assertions,
        schema["resource_metadata"],
    )

    save_json(
        validation_errors,
        batch_paths["validation_errors_path"],
    )

    save_json(
        validation_stats,
        batch_paths["validation_stats_path"],
    )

    print(
        f"[10/11] Validation complete: "
        f"{len(validated_assertions)} valid/warning, "
        f"{len(validation_errors)} invalid."
    )

    # -----------------------------------------------------------------
    # 11. Serialize graph.
    # -----------------------------------------------------------------

    print("\n[11/11] Serializing RDF graph...")

    serialize_graph(
        validated_assertions,
        schema_namespaces=schema["namespaces"],
        output_file=str(batch_paths["graph_output_file"]),
    )

    print("[11/11] Graph serialization complete.")


async def main():

    # -----------------------------------------------------------------
    # Initialize shared resources.
    # -----------------------------------------------------------------

    print("\nLoading embedding model...")
    emb_model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Creating LLM client...")
    client = create_client()


    # -----------------------------------------------------------------
    # Load schema once.
    # -----------------------------------------------------------------

    print("\nLoading schema...")

    schema = load_schema(SCHEMA_DIR)

    print("Schema loaded.")

    # ---------------------------------------------------------------------
    # Discover processing batches.
    # ---------------------------------------------------------------------

    print("\nDiscovering processing batches...")

    batch_dirs = discover_batches()

    if not batch_dirs:
        raise RuntimeError(
            f"No batch directories found in {INPUT_DIR}."
        )

    print(
        f"Found {len(batch_dirs)} processing batches."
    )


    # -----------------------------------------------------------------
    # Process batches.
    # -----------------------------------------------------------------

    print("\nProcessing batches...")

    completed_batches = []
    skipped_batches = []
    failed_batches = []

    try:
        for batch_dir in batch_dirs:

            batch_name = batch_dir.name
            batch_paths = get_batch_paths(batch_dir)

            if is_batch_complete(batch_paths):
                print(
                    f"\nSkipping completed batch: {batch_name}"
                )
                skipped_batches.append(batch_name)
                continue

            try:
                await run_batch_pipeline(
                    batch_dir=batch_dir,
                    batch_paths=batch_paths,
                    schema=schema,
                    emb_model=emb_model,
                    client=client,
                )

                batch_paths["success_marker"].touch()

                print(
                    f"\n✓ {batch_name} completed successfully."
                )

                completed_batches.append(batch_name)

            except asyncio.CancelledError:
                print(
                    f"\n⚠ Processing interrupted during {batch_name}."
                )
                raise

            except Exception as exc:
                failed_batches.append(
                    {
                        "batch": batch_name,
                        "error": repr(exc),
                    }
                )

                print(
                    f"\n✗ {batch_name} failed: {exc}"
                )

                continue

    except asyncio.CancelledError:
        print(
            "\n\n⚠ Processing interrupted by user."
        )
        print(
            "The current batch will NOT be marked as complete."
        )
        print(
            "Rerun the pipeline to resume from the first "
            "unfinished batch."
        )
        raise

    # -----------------------------------------------------------------
    # Final report.
    # -----------------------------------------------------------------

    print("\n" + "=" * 80)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 80)

    print(f"\nCompleted: {len(completed_batches)}")
    print(f"Skipped:   {len(skipped_batches)}")
    print(f"Failed:    {len(failed_batches)}")

    if completed_batches:
        print("\nCompleted batches:")
        for batch_name in completed_batches:
            print(f"  - {batch_name}")

    if skipped_batches:
        print("\nSkipped batches:")
        for batch_name in skipped_batches:
            print(f"  - {batch_name}")

    if failed_batches:
        print("\nFailed batches:")
        for failure in failed_batches:
            print(
                f"  - {failure['batch']}: "
                f"{failure['error']}"
            )

    print()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(
            "\nJurisynth stopped by user."
        )
