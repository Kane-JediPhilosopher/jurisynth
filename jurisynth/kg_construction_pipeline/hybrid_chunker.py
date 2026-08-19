from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from docling.document_converter import DocumentConverter
from transformers import AutoTokenizer

def main():
    # Options:
    # "openai/gpt-oss-120b"
    # nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16
    EMBED_MODEL_ID = "nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16"

    MAX_TOKENS = 1024

    tokenizer = HuggingFaceTokenizer(
        tokenizer=AutoTokenizer.from_pretrained(EMBED_MODEL_ID),
        max_tokens=MAX_TOKENS,
    )

    chunker = HybridChunker(
        tokenizer=tokenizer,
        merge_peers=True,
    )

    digitalizer = DocumentConverter()

    conv_docs_folder = Path("./converted_docs")
    conv_doc_paths = [file_path for file_path in conv_docs_folder.iterdir()]

    raw_chunks = list()

    for doc_path in conv_doc_paths:

        filename = os.path.basename(doc_path)
        doc = digitalizer.convert(source=doc_path).document
        chunks = chunker.chunk(dl_doc=doc)

        for i, chunk in enumerate(chunks):
            raw_chunks.append(
                {
                    "doc_id": filename,
                    "chunk_id": f"chunk_{i + 1}",
                    "chunk": chunk
                }
            )

if __name__ == "__main__":
    main()