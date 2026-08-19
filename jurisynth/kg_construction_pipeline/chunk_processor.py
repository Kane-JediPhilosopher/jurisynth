import re
import spacy

nlp = spacy.load("en_core_web_lg")

def strip_all_whitespace(text):
    return re.sub(r"\s+", " ", text).strip()

def process_chunks(raw_chunks):
    # ---------------------------------------------------------------------
    # Batch chunks
    # ---------------------------------------------------------------------

    docs = nlp.pipe(
        (item["chunk"].text for item in raw_chunks),
        batch_size=64,
        n_process=2
    )

    # ---------------------------------------------------------------------
    # Process chunks
    # ---------------------------------------------------------------------

    processed_chunks = list()

    for item, chunk in zip(raw_chunks, docs):

        filename = item["doc_id"]
        chunk_id = item["chunk_id"]

        filtered_sents = list()

        for sent in chunk.sents:
            text = sent.text.strip()

            if not text:
                continue

            # check for VERB or AUX in the sentence
            has_verb_or_aux = any(
                token.pos_ in {"VERB", "AUX"} for token in sent
            )

            if not has_verb_or_aux:
                continue

            filtered_sents.append(text)

        if not filtered_sents:
            continue

        processed_chunk = " ".join(filtered_sents)

        cleaned = strip_all_whitespace(processed_chunk)

        if cleaned:
            processed_chunks.append({
                "doc_id": filename,
                "chunk_id": chunk_id,
                "content": cleaned
            })

        print("CHUNK:", repr(cleaned))
        print("FILE:", filename, "\n")

        return processed_chunks