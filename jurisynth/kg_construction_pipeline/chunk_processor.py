import re

import spacy
from spacy.language import Language


NLP_MODEL = "en_core_web_lg"
DEFAULT_BATCH_SIZE = 64
DEFAULT_N_PROCESSES = 2


def process_chunks(
    raw_chunks: list[dict],
    nlp: Language | None = None,
    batch_size: int = DEFAULT_BATCH_SIZE,
    n_process: int = DEFAULT_N_PROCESSES,
) -> list[dict]:
    """Clean and filter chunk text using spaCy sentence processing."""

    if nlp is None:
        nlp = spacy.load(NLP_MODEL)

    docs = nlp.pipe(
        (item["content"].text for item in raw_chunks),
        batch_size=batch_size,
        n_process=n_process,
    )

    processed_chunks = []

    for item, doc in zip(raw_chunks, docs):
        filtered_sentences = []

        for sentence in doc.sents:
            text = sentence.text.strip()

            if not text:
                continue

            has_verb_or_aux = any(
                token.pos_ in {"VERB", "AUX"}
                for token in sentence
            )

            if not has_verb_or_aux:
                continue

            filtered_sentences.append(text)

        if not filtered_sentences:
            continue

        content = " ".join(filtered_sentences)
        content = re.sub(r"\s+", " ", content).strip()

        if content:
            processed_chunks.append(
                {
                    "doc_id": item["doc_id"],
                    "chunk_id": item["chunk_id"],
                    "content": content,
                }
            )

    return processed_chunks