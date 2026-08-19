from llm_proc_utils import get_completion, wait_for_rate_limit

import json
import time
import random

import asyncio


# Triple extraction variables
extraction_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {

            "subject": {
                "type": "string",
                "minLength": 1
            },

            "predicate": {
                "type": "string",
                "minLength": 1
            },

            "object": {
                "type": "string",
                "minLength": 1
            },
        },

        "required": [
            "subject",
            "predicate",
            "object"
        ],

        "additionalProperties": False
    }
}

extraction_prompt = """
You will be given a chunk of text from an EU legal document.

Extract legal semantic triples as JSON.

## Extraction rules

1. Extract only facts that are explicitly stated or unambiguously defined in the text.

2. Prioritize precision over recall.
   If a relationship is unclear, omit the triple rather than guessing.

3. Resolve pronouns, demonstratives, and references to their actual entities.

4. Subjects and objects must be nouns or noun clauses.
   They must represent meaningful entities, concepts, actions, or values from the text.
   Do not use:
   - boolean values ("true", "false")
   - vague placeholders ("it", "this", "the above")
   - entire sentences as objects.

5. Use "type of" only when the text explicitly defines an entity's category.

   Valid examples:
   - (Regulation (EU) 2024/1234, type of, Regulation)
   - (Article 5, type of, Article)
   - (European Commission, type of, Institution)

6. Preserve the original meaning of legal predicates.
   Keep negations and polarity:
   - "does not apply" is different from "applies"
   - "is prohibited" is different from "is permitted"

7. Ignore:
   - document formatting
   - pagination
   - headers and footers
   - publication metadata
   - editorial information
   - chapter/section numbering unless it is explicitly referenced as a legal entity.

"""


# ---------------------------------------------------------------------
# Extraction worker
# ---------------------------------------------------------------------

async def extraction_worker(
    chunk_dict,
    semaphore,
    rate_lock,
    last_request_time,
    cooldown_until,
    current_rps,
    success_counter,
    max_rps,
    max_backoff=30,
    min_rps=0.25,
    recovery_step=0.10,
    success_threshold=20,
):

    attempt = 0

    while True:
        async with semaphore:
            await wait_for_rate_limit(
                rate_lock,
                last_request_time,
                cooldown_until,
                current_rps,
            )

            try:
                response = await get_completion(
                    system_prompt=extraction_prompt,
                    query=chunk_dict["content"],
                    schema=extraction_schema,
                )

                result = json.loads(response)

                # ------------------------------------------
                # Conservative recovery
                # ------------------------------------------

                async with rate_lock:
                    success_counter[0] += 1

                    if success_counter[0] >= success_threshold:
                        current_rps[0] = min(max_rps, current_rps[0] + recovery_step,)
                        success_counter[0] = 0

                return {
                    "doc_id": chunk_dict["doc_id"],
                    "chunk_id": chunk_dict["chunk_id"],
                    "triples": result,
                }

            except Exception as e:
                error_text = str(e)

                # ------------------------------------------
                # Retry indefinitely for transient errors
                # ------------------------------------------
                if (
                    "429" in error_text
                    or
                    "503" in error_text
                ):

                    backoff = min(2 ** attempt, max_backoff)
                    backoff += random.uniform(0, 1)

                    async with rate_lock:
                        cooldown_until[0] = max(cooldown_until[0], time.monotonic() + backoff)
                        current_rps[0] = max(min_rps, current_rps[0] / 2)
                        success_counter[0] = 0
                        current_rate = current_rps[0]

                    print(
                        f"[{chunk_dict['chunk_id']}] "
                        f"{error_text}\n"
                        f"Cooldown: {backoff:.1f}s | "
                        f"Current RPS: {current_rate:.2f}"
                    )

                    attempt += 1

                    continue

                # ------------------------------------------
                # Permanent failure
                # ------------------------------------------

                print(
                    f"Extraction failed "
                    f"({chunk_dict['chunk_id']}): {e}"
                )

                return {
                    "doc_id": chunk_dict["doc_id"],
                    "chunk_id": chunk_dict["chunk_id"],
                    "triples": list(),
                }


# ---------------------------------------------------------------------
# Batch extraction
# ---------------------------------------------------------------------

async def batch_extract(
    chunks,
    semaphore,
    requests_per_second=1,
    max_backoff=30,
):

    rate_lock = asyncio.Lock()

    last_request_time = [0.0]
    cooldown_until = [0.0]
    current_rps = [requests_per_second]
    success_counter = [0]

    tasks = [

        extraction_worker(
            chunk,
            semaphore,
            rate_lock,
            last_request_time,
            cooldown_until,
            current_rps,
            success_counter,
            requests_per_second,
            max_backoff,
        )

        for chunk in chunks

    ]

    return await asyncio.gather(*tasks)