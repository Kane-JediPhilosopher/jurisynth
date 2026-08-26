print("Importing modules...\n")

from pathlib import Path
from sentence_transformers import SentenceTransformer
import asyncio
import os

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

# ---------------------------------------------------------------------
# GLOBAL CONSTANTS
# ---------------------------------------------------------------------
EMB_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
CLIENT = create_client()

# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

SCHEMA_DIR = BASE_DIR.parent / "schema"

INPUT_DIR = BASE_DIR.parent.parent / "eu_legislation"

DATA_DIR = BASE_DIR / "data"
INTERMEDIATE_DIR = BASE_DIR / "intermediate"
OUTPUT_DIR = BASE_DIR / "output"

CONVERTED_DIR = DATA_DIR / "converted"

CHUNK_INDEX_DIR = INTERMEDIATE_DIR / "chunk_index"

GRAPH_OUTPUT_DIR = OUTPUT_DIR / "graph"
GRAPH_OUTPUT_FILE = GRAPH_OUTPUT_DIR / "jurisynth_graph.nq"

CHUNK_INDEX_PATH = CHUNK_INDEX_DIR / "chunk_index.faiss"
CHUNK_METADATA_PATH = CHUNK_INDEX_DIR / "chunk_metadata.pkl"


# ---------------------------------------------------------------------
# Create required output directories
# ---------------------------------------------------------------------

for directory in (
    CONVERTED_DIR,
    CHUNK_INDEX_DIR,
    GRAPH_OUTPUT_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)


async def main():

    # ---------------------------------------------------------------------
    # 1. Load the schema.
    # ---------------------------------------------------------------------
    print("\n[1/12] Loading schema...")
    schema = load_schema(SCHEMA_DIR)
    print("[1/12] Schema loaded.")

    # ---------------------------------------------------------------------
    # 2. Preprocess the documents.
    #
    #    This is handled by the Document Preprocessor on Colab
    #    for GPU utilisation.
    # ---------------------------------------------------------------------
    print("\n[2/12] Document preprocessing is handled externally.")

    # ---------------------------------------------------------------------
    # 3. Convert the HTML documents into markdown files.
    # ---------------------------------------------------------------------
    print("\n[3/12] Converting HTML documents to Markdown...")
    convert_documents(
        input_dir=INPUT_DIR,
        output_dir=CONVERTED_DIR
    )
    print("[3/12] Document conversion complete.")

    # ---------------------------------------------------------------------
    # 4. Chunk the documents using section-aware logic.
    # ---------------------------------------------------------------------
    print("\n[4/12] Chunking documents...")
    raw_chunks = chunk_documents(CONVERTED_DIR)
    print(f"[4/12] Chunking complete: {len(raw_chunks)} raw chunks.")

    # ---------------------------------------------------------------------
    # 5. Store the chunks in a FAISS vector store.
    #
    #    Raw chunks are stored instead of processed ones
    #    to preserve source content.
    # ---------------------------------------------------------------------
    print("\n[5/12] Building chunk vector store...")
    chunk_index, chunk_lookup = build_chunk_vector_store(
        raw_chunks=raw_chunks,
        embedding_model=EMB_MODEL,
    )

    save_chunk_vector_store(
        chunk_index,
        chunk_lookup,
        CHUNK_INDEX_PATH,
        CHUNK_METADATA_PATH
    )
    print("[5/12] Chunk vector store saved.")

    # ---------------------------------------------------------------------
    # 6. Filter out verbless sentences from the chunks.
    # ---------------------------------------------------------------------
    print("\n[6/12] Processing chunks...")
    processed_chunks = process_chunks(raw_chunks=raw_chunks)
    print(
        f"[6/12] Chunk processing complete: "
        f"{len(processed_chunks)} chunks retained."
    )

    # ---------------------------------------------------------------------
    # 7. Extract assertions from the chunks.
    #
    #    Basically, assertions in this context are triples that
    #    (may) have modifying clauses.
    #
    #    Modifiers provide context about the base triple/fact.
    #        A triple: (subject, predicate, object). 
    #        An assertion: (triple + modifier(s)).
    # ---------------------------------------------------------------------
    print("\n[7/12] Extracting assertions...")
    extracted_assertions, extraction_errors = await extract_assertions(
        client=CLIENT, 
        processed_chunks=processed_chunks
        )
    print(
        f"[7/12] Assertion extraction complete: "
        f"{len(extracted_assertions)} chunks processed, "
        f"{len(extraction_errors)} errors."
    )

    # ---------------------------------------------------------------------
    # 8. Normalize and clean up the assertions.
    # ---------------------------------------------------------------------
    print("\n[8/12] Normalizing assertions...")
    normalized_assertions = normalize_assertions(extracted_assertions)
    print(
        f"[8/12] Normalization complete: "
        f"{len(normalized_assertions)} assertions."
    )

    # ---------------------------------------------------------------------
    # 9. Match the assertion components (subjects, predicates, objects)
    #    to existing schema data.
    # ---------------------------------------------------------------------
    print("\n[9/12] Semantically matching assertions...")
    scored_assertions = match_assertions(
        normalized_assertions,
        schema["classes"],
        schema["object_properties"],
        schema["datatype_properties"],
        schema["resource_metadata"],
        emb_model=EMB_MODEL,
    )
    print("[9/12] Semantic matching complete.")

    # ---------------------------------------------------------------------
    # 10. Resolve/deduplicate assertion components.
    # ---------------------------------------------------------------------
    print("\n[10/12] Resolving entities and relations...")
    resolved_assertions, resolution_metadata = await resolve_assertions(
        client=CLIENT,
        scored_assertions=scored_assertions,
        emb_model=EMB_MODEL
    )
    print("[10/12] Entity-relation resolution complete.")

    # ---------------------------------------------------------------------
    # 11. Validate the assertions.
    # ---------------------------------------------------------------------
    print("\n[11/12] Validating assertions...")
    (
    validated_assertions,
    validation_errors,
    validation_stats,
    ) = run_assertion_validation(resolved_assertions, schema["resource_metadata"],)
    print(
        f"[11/12] Validation complete: "
        f"{len(validated_assertions)} valid/warning, "
        f"{len(validation_errors)} invalid."
    )

    # ---------------------------------------------------------------------
    # 12. Serialize the assertions into a hierarchical graph.
    #
    #     This results in an RDF graph, more specifically, a named graph.
    #     While a normal RDF graph holds triples, a named graph holds quads:
    #     (subject, predicate, object, graph).
    #     
    #     Source documents can be put into the 4th slot;
    #     This allows us to link triples to their source docs.
    # ---------------------------------------------------------------------
    print("\n[12/12] Serializing RDF graph...")
    dataset = serialize_graph(
        validated_assertions,
        schema_namespaces=schema["namespaces"],
        output_file=GRAPH_OUTPUT_FILE,
    )
    print("[12/12] Graph serialization complete.")

    # ---------------------------------------------------------------------
    # 13. Construct a community graph based on the entire KG.
    #     This graph is contructed after the entire corpus is processed.
    # ---------------------------------------------------------------------


if __name__ == "__main__":
    asyncio.run(main())