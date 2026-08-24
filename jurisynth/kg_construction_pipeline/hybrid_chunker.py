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
        tokenizer=AutoTokenizer.from_pretrained(CHUNK_TOKENIZER_MODEL),
        max_tokens=MAX_TOKENS,
    )

    chunker = HybridChunker(
        tokenizer=tokenizer,
        merge_peers=True,
    )

    digitalizer = DocumentConverter()

    raw_chunks = list()

    for doc_path in converted_docs_dir.iterdir():
        if not doc_path.is_file():
            continue

        doc_id = doc_path.stem
        document = digitalizer.convert(source=doc_path).document

        for i, chunk in enumerate(chunker.chunk(dl_doc=document)):
            raw_chunks.append(
                {
                    "doc_id": doc_id,
                    "chunk_id": f"chunk_{i + 1}",
                    "content": chunk,
                }
            )

    return raw_chunks