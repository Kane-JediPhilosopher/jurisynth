"""Constrained NIM query interpretation for Retrieval Mech concept matching."""

from __future__ import annotations

import json
from dataclasses import dataclass

from jurisynth.agentic_reasoner.llm import ChatModel
from jurisynth.contracts import RetrievalRequest
from jurisynth.retrieval_mech.er_matcher import Concept


_SYSTEM_PROMPT = """Interpret one retrieval request. Return JSON only:
{"entity_concepts":[{"concept":"...","variants":["..."]}],"relation_concepts":[{"concept":"...","variants":["..."]}]}.
Extract only a small set of useful entity and relation concepts. Use at most 3
variants per concept. Do not produce chunk keywords, RDF URIs, SPARQL, community
IDs, legal conclusions, or explanations. When a named entity, country,
institution, instrument title, or article identifier appears in the request,
preserve it verbatim as its own entity concept; do not replace it with a
semantically similar entity."""


@dataclass(slots=True)
class NIMQueryInterpreter:
    model: ChatModel
    max_tokens: int = 500
    max_variants: int = 3

    async def interpret(self, request: RetrievalRequest) -> tuple[list[Concept], list[Concept]]:
        payload = {
            "leaf_query": request.leaf_query,
            "contextual_facts": request.contextual_facts,
            "constraints": request.constraints,
        }
        response = await self.model.complete(system=_SYSTEM_PROMPT, user=json.dumps(payload), max_tokens=self.max_tokens)
        try:
            parsed = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError("Query Interpreter response is not valid JSON.") from exc
        if not isinstance(parsed, dict):
            raise ValueError("Query Interpreter response must be a JSON object.")
        return (
            _concepts(parsed.get("entity_concepts", []), "entity", self.max_variants),
            _concepts(parsed.get("relation_concepts", []), "relation", self.max_variants),
        )


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
