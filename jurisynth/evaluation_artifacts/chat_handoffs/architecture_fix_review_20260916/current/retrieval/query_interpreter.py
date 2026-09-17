"""Constrained NIM query interpretation for Retrieval Mech concept matching."""

from __future__ import annotations

import json
from dataclasses import dataclass

from jurisynth.agentic_reasoner.llm import ChatModel
from jurisynth.agentic_reasoner.schemas import QUERY_INTERPRETER_SCHEMA
from jurisynth.contracts import RetrievalRequest
from jurisynth.retrieval_mech.er_matcher import Concept


_SYSTEM_PROMPT = """Interpret one retrieval request for THIS leaf only. Return JSON only:
{"entity_concepts":[{"concept":"...","variants":["..."]}],"relation_concepts":[{"concept":"...","variants":["..."]}]}.
Extract the minimum sufficient entity and relation concepts needed to retrieve
evidence for the leaf_query. contextual_facts and constraints may disambiguate
the leaf, but they are not an invitation to perform broad legal issue spotting:
do not extract scenario actors, statutes, facts, or duties that this leaf does
not ask about. Concepts must be lexical retrieval anchors stated in the
leaf_query or its explicit constraints; do not predict or enumerate the legal
rules that might answer the question. For example, a request for an actor's
"obligations" should preserve that actor, the named instrument, and the
pre/post-market distinction, but should not invent CE marking, incident
reporting, quality-management, cybersecurity, or other possible duties unless
the request names them. Use at most 3 variants per concept. Do not produce chunk keywords,
RDF URIs, SPARQL, community IDs, legal conclusions, or explanations. When a
named entity, country, institution, instrument title, or article identifier is
relevant to this leaf, preserve it verbatim as its own entity concept; do not
replace it with a semantically similar entity. Do not impose an arbitrary number
of concepts: prefer the smallest set that still preserves every retrieval-critical
actor, instrument, provision, object, and relationship in this leaf."""


@dataclass(slots=True)
class NIMQueryInterpreter:
    model: ChatModel
    max_tokens: int = 2048
    max_variants: int = 3
    invalid_output_attempts: int = 3

    async def interpret(self, request: RetrievalRequest) -> tuple[list[Concept], list[Concept]]:
        payload = {
            "leaf_query": request.leaf_query,
            "contextual_facts": request.contextual_facts,
            "constraints": request.constraints,
        }
        if min(self.max_tokens, self.max_variants, self.invalid_output_attempts) < 1:
            raise ValueError("Query Interpreter budgets must be positive.")
        for attempt in range(self.invalid_output_attempts):
            response = await self.model.complete(
                system=_SYSTEM_PROMPT, user=json.dumps(payload), max_tokens=self.max_tokens,
                response_schema=QUERY_INTERPRETER_SCHEMA,
            )
            try:
                return self._parse_response(response)
            except ValueError as exc:
                if attempt + 1 == self.invalid_output_attempts:
                    raise
                payload["validation_error"] = str(exc)
                payload["repair_instruction"] = "Return a complete JSON object with both concept arrays. Keep concepts concise and close all arrays/objects."
        raise RuntimeError("Query Interpreter validation did not return concepts.")

    def _parse_response(self, response: str) -> tuple[list[Concept], list[Concept]]:
        try:
            parsed = json.loads(_extract_json_object(response))
        except json.JSONDecodeError as exc:
            raise ValueError("Query Interpreter response is not valid JSON.") from exc
        if not isinstance(parsed, dict):
            raise ValueError("Query Interpreter response must be a JSON object.")
        if set(parsed) != {"entity_concepts", "relation_concepts"}:
            raise ValueError("Query Interpreter requires exactly entity_concepts and relation_concepts.")
        return (
            _concepts(parsed.get("entity_concepts", []), "entity", self.max_variants),
            _concepts(parsed.get("relation_concepts", []), "relation", self.max_variants),
        )


def _extract_json_object(response: str) -> str:
    """Accept an otherwise-valid object wrapped in a model code fence/prose."""
    candidate = response.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        candidate = "\n".join(lines).strip()
    if candidate.startswith("{") and candidate.endswith("}"):
        return candidate
    start, end = candidate.find("{"), candidate.rfind("}")
    return candidate[start:end + 1] if start >= 0 and end > start else candidate


def _concepts(raw_concepts: object, prefix: str, max_variants: int) -> list[Concept]:
    if not isinstance(raw_concepts, list):
        raise ValueError(f"{prefix}_concepts must be a list.")
    concepts: list[Concept] = []
    seen: set[str] = set()
    for raw in raw_concepts:
        if not isinstance(raw, dict) or not isinstance(raw.get("concept"), str):
            raise ValueError(f"Each {prefix} concept requires a string 'concept'.")
        concept = raw["concept"].strip()
        if not concept or concept.casefold() in seen:
            continue
        variants = raw.get("variants", [])
        if not isinstance(variants, list) or not all(isinstance(value, str) for value in variants):
            raise ValueError(f"{prefix} concept variants must be a list of strings.")
        normalized_variants: list[str] = []
        for variant in variants:
            cleaned = variant.strip()
            if cleaned and cleaned.casefold() != concept.casefold() and cleaned.casefold() not in {value.casefold() for value in normalized_variants}:
                normalized_variants.append(cleaned)
            if len(normalized_variants) == max_variants:
                break
        seen.add(concept.casefold())
        concepts.append(Concept(f"{prefix}_{len(concepts) + 1}", concept, tuple(normalized_variants)))
    return concepts
