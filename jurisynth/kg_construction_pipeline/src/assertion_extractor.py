import asyncio
import json
import logging
import os
import random
import time
from typing import Any

import openai

from llm_utils import (
    get_completion,
    wait_for_rate_limit,
    MAX_CONCURRENT_REQUESTS,
    DEFAULT_REQUESTS_PER_SECOND,
    MAX_BACKOFF,
    MIN_RPS,
    RECOVERY_STEP,
    SUCCESS_THRESHOLD,
)

_LOG = logging.getLogger(__name__)


# ---------------------------------------------------------------------
# Extraction schema
# ---------------------------------------------------------------------

EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "assertions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "assertion": {
                        "type": "object",
                        "properties": {
                            "subject": {
                                "type": "string",
                            },
                            "predicate": {
                                "type": "string",
                            },
                            "object": {
                                "oneOf": [
                                    {"type": "string"},
                                    {"type": "null"},
                                    {
                                        "type": "object",
                                        "properties": {
                                            "type": {
                                                "const": "assertion",
                                            }
                                        },
                                        "required": ["type"],
                                        "additionalProperties": False,
                                    },
                                ],
                            },
                        },
                        "required": [
                            "subject",
                            "predicate",
                            "object",
                        ],
                        "additionalProperties": False,
                    },
                    "modifiers": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                    },
                },
                "required": [
                    "assertion",
                    "modifiers",
                ],
                "additionalProperties": False,
            },
        }
    },
    "required": ["assertions"],
    "additionalProperties": False,
}


# ---------------------------------------------------------------------
# Extraction prompt
# ---------------------------------------------------------------------

EXTRACTION_PROMPT = """
Extract molecular legal assertions from the text.

Rules:

1. Extract each complete legal proposition as one assertion. Keep the
   subject, predicate, and object concise, but preserve all information
   necessary to identify the proposition's legal meaning.

2. Preserve the legal modality expressed by the text, such as shall, must,
   may, may not, shall not, is entitled to, is required to, or is prohibited
   from. Do not weaken, strengthen, or otherwise change the modality.

3. Keep the predicate limited to the legal relation and its modality.
   Do not absorb a prepositional phrase, infinitival complement, or clause
   into the predicate merely because it follows the verb.

4. Identify the semantic object of the predicate, rather than mechanically
   treating every phrase following the verb as part of the predicate or
   object.

5. Move only external conditions, exceptions, circumstances, temporal
   restrictions, purposes, or other qualifications of the complete
   proposition into "modifiers".

6. Do not move information into "modifiers" merely because it is long.
   Relative clauses, prepositional phrases, and other information necessary
   to identify the subject or object should remain attached to that entity.

7. Split coordinated or sequential clauses when they express independent
   legal propositions, especially when they contain separate legal
   modalities or obligations.

8. Coordinated subjects or objects should be represented so that they can be
   expanded safely downstream.

9. Resolve a reference only when its antecedent is explicitly identifiable
   from the provided text. Otherwise preserve the reference as written.
   Do not guess or invent an antecedent.

10. Do not invent an object merely to force an assertion into a
    subject-predicate-object structure. Some legal predicates are naturally
    objectless. For such propositions, set "object" to null.

11. Distinguish the semantic object of an assertion from external
    qualifications of that proposition.

12. A modifier may be long when the legal condition is genuinely complex.
    Do not shorten or discard legally meaningful details merely to satisfy
    a length preference.

13. Do not split a single coherent legal condition into multiple assertions
    unless it contains independent legal propositions.

14. Preserve explicit legal references such as Articles, paragraphs,
    sections, annexes, and other cited provisions.

15. Prefer conservative extraction over speculative interpretation.
    Extract the legal structure expressed by the text; do not rewrite a
    proposition into a different legal formulation merely to make it more
    concise or natural.

Structural conventions:

- The predicate should normally contain the modal/legal relation and its
  governing verb or predicate complement, e.g. "shall submit", "may approve",
  "shall not disclose", or "is entitled to receive".

- A noun phrase that identifies what is acted upon should normally be the
  object, even when that noun phrase is long.

- Relative clauses and other phrases that identify or qualify an entity
  should remain attached to the subject or object when they are part of that
  entity's description.

- Conditions, exceptions, temporal restrictions, purposes, and circumstances
  governing when or under what circumstances the proposition applies should
  normally be represented as modifiers.

- Do not treat an objectless passive construction as having an invented
  object. For example, "The register shall be maintained" has object = null.

- Do not convert legal framing into a different modality. For example,
  do not transform "is prohibited from" into "shall not", or "may" into
  "is entitled to", unless the text itself expresses that relation.

- When a verb governs an infinitival or clausal complement that expresses the
  action required, permitted, or prohibited, keep the legal relation coherent
  rather than splitting the complement into an unrelated predicate.

Examples:

Input:
"Any undertaking established within the territory must maintain records
relating to goods supplied to its customers."

Output:
{
  "assertions": [
    {
      "assertion": {
        "subject": "undertaking established within the territory",
        "predicate": "must maintain",
        "object": "records relating to goods supplied to its customers"
      },
      "modifiers": []
    }
  ]
}

---

Input:
"Where the authority considers that the application is incomplete,
the applicant must provide the missing information within thirty days."

Output:
{
  "assertions": [
    {
      "assertion": {
        "subject": "applicant",
        "predicate": "must provide",
        "object": "missing information"
      },
      "modifiers": [
        "Where the authority considers that the application is incomplete",
        "within thirty days"
      ]
    }
  ]
}

---

Input:
"The authority shall inform the applicant of the reasons for its
decision and shall provide a copy of the decision."

Output:
{
  "assertions": [
    {
      "assertion": {
        "subject": "authority",
        "predicate": "shall inform",
        "object": "applicant of the reasons for its decision"
      },
      "modifiers": []
    },
    {
      "assertion": {
        "subject": "authority",
        "predicate": "shall provide",
        "object": "a copy of the decision"
      },
      "modifiers": []
    }
  ]
}

---

Input:
"The authorisation may be withdrawn if the holder fails to comply
with the applicable requirements."

Output:
{
  "assertions": [
    {
      "assertion": {
        "subject": "authorisation",
        "predicate": "may be withdrawn",
        "object": null
      },
      "modifiers": [
        "if the holder fails to comply with the applicable requirements"
      ]
    }
  ]
}

---

Input:
"The authority shall verify the documents submitted by applicants
and may reject applications that do not satisfy the requirements."

Output:
{
  "assertions": [
    {
      "assertion": {
        "subject": "authority",
        "predicate": "shall verify",
        "object": "documents submitted by applicants"
      },
      "modifiers": []
    },
    {
      "assertion": {
        "subject": "authority",
        "predicate": "may reject",
        "object": "applications that do not satisfy the requirements"
      },
      "modifiers": []
    }
  ]
}

---

Text:
"""


# ---------------------------------------------------------------------
# Single-chunk extraction
# ---------------------------------------------------------------------

async def extraction_worker(
    chunk: dict[str, Any],
    client: openai.AsyncOpenAI,
    semaphore: asyncio.Semaphore,
    rate_lock: asyncio.Lock,
    last_request_time: list[float],
    cooldown_until: list[float],
    current_rps: list[float],
    success_counter: list[int],
    max_rps: float,
    max_backoff: float = MAX_BACKOFF,
    min_rps: float = MIN_RPS,
    recovery_step: float = RECOVERY_STEP,
    success_threshold: int = SUCCESS_THRESHOLD,
) -> dict[str, Any]:

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
                    client=client,
                    query=chunk["content"],
                    system_prompt=EXTRACTION_PROMPT,
                    schema={
                        "name": "assertions",
                        "schema": EXTRACTION_SCHEMA
                        }
                )

                result = json.loads(response)

                async with rate_lock:
                    success_counter[0] += 1

                    if success_counter[0] >= success_threshold:
                        current_rps[0] = min(
                            max_rps,
                            current_rps[0] + recovery_step,
                        )
                        success_counter[0] = 0

                return {
                    "doc_id": chunk["doc_id"],
                    "chunk_id": chunk["chunk_id"],
                    "assertions": result.get("assertions", []),
                }

            except Exception as exc:
                error_text = str(exc)

                if "429" in error_text or "503" in error_text:
                    backoff = min(2 ** attempt, max_backoff)
                    backoff += random.uniform(0, 1)

                    async with rate_lock:
                        cooldown_until[0] = max(
                            cooldown_until[0],
                            time.monotonic() + backoff,
                        )
                        current_rps[0] = max(
                            min_rps,
                            current_rps[0] / 2,
                        )
                        success_counter[0] = 0
                        current_rate = current_rps[0]

                    _LOG.warning(
                        "[%s] %s | cooldown=%.1fs | rps=%.2f",
                        chunk["chunk_id"],
                        error_text,
                        backoff,
                        current_rate,
                    )

                    attempt += 1
                    continue

                _LOG.error(
                    "Extraction failed for %s: %s",
                    chunk["chunk_id"],
                    exc,
                )

                return {
                    "doc_id": chunk["doc_id"],
                    "chunk_id": chunk["chunk_id"],
                    "assertions": [],
                    "error": str(exc),
                }


# ---------------------------------------------------------------------
# Batch extraction
# ---------------------------------------------------------------------

async def batch_extract(
    chunks: list[dict[str, Any]],
    client: openai.AsyncOpenAI,
    max_concurrent_requests: int = MAX_CONCURRENT_REQUESTS,
    requests_per_second: float = DEFAULT_REQUESTS_PER_SECOND,
) -> list[dict[str, Any]]:

    semaphore = asyncio.Semaphore(max_concurrent_requests)

    rate_lock = asyncio.Lock()
    last_request_time = [0.0]
    cooldown_until = [0.0]
    current_rps = [requests_per_second]
    success_counter = [0]

    tasks = [
        extraction_worker(
            chunk=chunk,
            client=client,
            semaphore=semaphore,
            rate_lock=rate_lock,
            last_request_time=last_request_time,
            cooldown_until=cooldown_until,
            current_rps=current_rps,
            success_counter=success_counter,
            max_rps=requests_per_second,
        )
        for chunk in chunks
    ]

    return await asyncio.gather(*tasks)


# ---------------------------------------------------------------------
# Public module entry point
# ---------------------------------------------------------------------

async def extract_assertions(
    client: openai.AsyncOpenAI,
    processed_chunks: list[dict[str, Any]],
    requests_per_second: float = DEFAULT_REQUESTS_PER_SECOND,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:

    results = await batch_extract(
        processed_chunks,
        client,
        requests_per_second=requests_per_second,
    )

    extracted_assertions = []
    extraction_errors = []

    for result in results:
        doc_id = result["doc_id"]
        chunk_id = result["chunk_id"]

        if "error" in result:
            extraction_errors.append({
                "doc_id": doc_id,
                "chunk_id": chunk_id,
                "reason": "extraction_failed",
                "raw_result": result,
            })
            continue

        assertions = result.get("assertions")

        if not isinstance(assertions, list):
            extraction_errors.append({
                "doc_id": doc_id,
                "chunk_id": chunk_id,
                "reason": (
                    "invalid_assertions_type:"
                    f"{type(assertions).__name__}"
                ),
                "raw_result": result,
            })
            continue

        extracted_assertions.append({
            "doc_id": doc_id,
            "chunk_id": chunk_id,
            "assertions": assertions,
        })

    total_assertions = sum(
        len(item["assertions"])
        for item in extracted_assertions
    )

    _LOG.info(
        "Assertion extraction complete: "
        "%d results, %d valid chunks, %d errors, %d assertions.",
        len(results),
        len(extracted_assertions),
        len(extraction_errors),
        total_assertions,
    )

    return extracted_assertions, extraction_errors