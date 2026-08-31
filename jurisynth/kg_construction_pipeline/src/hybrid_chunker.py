from pathlib import Path
from transformers import AutoTokenizer
from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from docling.document_converter import DocumentConverter


CHUNK_TOKENIZER_MODEL = "nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-BF16"

MAX_TOKENS = 1024


def chunk_documents(
    converted_docs_dir: Path
) -> list[dict]:
    """Chunk converted documents using Docling's HybridChunker."""

    tokenizer = HuggingFaceTokenizer(
        tokenizer=AutoTokenizer.from_pretrained(
            CHUNK_TOKENIZER_MODEL
        ),
        max_tokens=MAX_TOKENS,
    )

    chunker = HybridChunker(
        tokenizer=tokenizer,
        merge_peers=True,
    )

    digitalizer = DocumentConverter()

    raw_chunks = list()

    document_paths = sorted(
        path
        for path in converted_docs_dir.iterdir()
        if path.is_file()
    )

    total_docs = len(document_paths)

    print("=" * 80)
    print(f"CHUNKING {total_docs} DOCUMENTS")
    print("=" * 80)

    for doc_number, doc_path in enumerate(
        document_paths,
        start=1,
    ):
        doc_id = doc_path.stem

        print()
        print(
            f"[{doc_number}/{total_docs}] "
            f"Chunking: {doc_id}"
        )

        document = digitalizer.convert(
            source=doc_path
        ).document

        doc_chunk_count = 0

        for i, chunk in enumerate(
            chunker.chunk(dl_doc=document)
        ):
            raw_chunks.append(
                {
                    "doc_id": doc_id,
                    "chunk_id": f"chunk_{i + 1}",
                    "content": chunk,
                }
            )

            doc_chunk_count += 1

        print(
            f"[{doc_number}/{total_docs}] "
            f"Completed: {doc_id} "
            f"({doc_chunk_count} chunks)"
        )

    print()
    print("=" * 80)
    print(
        f"CHUNKING COMPLETE — "
        f"{len(raw_chunks)} total chunks"
    )
    print("=" * 80)

    return raw_chunks