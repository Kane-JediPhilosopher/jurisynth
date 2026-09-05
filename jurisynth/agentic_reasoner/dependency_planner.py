"""One-call semantic dependency planning over parser-validated QCompiler leaves."""

from __future__ import annotations

import json
from dataclasses import replace
from dataclasses import dataclass

from jurisynth.agentic_reasoner.llm import ChatModel
from jurisynth.agentic_reasoner.models import LeafNode


_SYSTEM_PROMPT = """Determine information-flow dependencies between Jurisynth leaf queries.
Return JSON only: {"dependencies":{"q001":[],"q002":["q001"]}}.
Only list an upstream ID when its result is required to execute the target leaf.
AST ordering and logical nesting alone are not dependencies. Do not add IDs, self
dependencies, explanations, or any other fields."""


@dataclass(slots=True)
class SemanticDependencyPlanner:
    model: ChatModel
    max_tokens: int = 400

    async def plan(self, leaves: tuple[LeafNode, ...]) -> tuple[LeafNode, ...]:
        payload = {"leaves": [{"query_id": leaf.query_id, "query": leaf.query} for leaf in leaves]}
        response = await self.model.complete(system=_SYSTEM_PROMPT, user=json.dumps(payload), max_tokens=self.max_tokens)
        dependencies = _parse_dependencies(response, {leaf.query_id for leaf in leaves})
        return tuple(replace(leaf, dependency_ids=tuple(dependencies[leaf.query_id])) for leaf in leaves)


def _parse_dependencies(response: str, valid_ids: set[str]) -> dict[str, list[str]]:
    try:
        payload = json.loads(response)
    except json.JSONDecodeError as exc:
        raise ValueError("Dependency planner response is not valid JSON.") from exc
    raw = payload.get("dependencies") if isinstance(payload, dict) else None
    if not isinstance(raw, dict) or set(raw) != valid_ids:
        raise ValueError("Dependency planner must provide exactly one dependency list per leaf ID.")
    planned: dict[str, list[str]] = {}
    for query_id, values in raw.items():
        if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
            raise ValueError("Dependency planner values must be lists of leaf IDs.")
        if query_id in values or not set(values).issubset(valid_ids):
            raise ValueError("Dependency planner returned an invalid dependency ID.")
        planned[query_id] = list(dict.fromkeys(values))
    return planned
