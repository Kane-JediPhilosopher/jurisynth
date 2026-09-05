"""Typed internal models for the V1 deterministic orchestration layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal

from jurisynth.contracts import EvidenceBundle


class NodeStatus(StrEnum):
    WAITING = "waiting"
    READY = "ready"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"
    BLOCKED = "blocked"


ClaimStatus = Literal["supported", "partially_supported", "insufficient_evidence"]


@dataclass(slots=True, frozen=True)
class LeafNode:
    """A QCompiler leaf normalized at the Reasoner's boundary."""

    query_id: str
    query: str
    dependency_ids: tuple[str, ...] = ()
    contextual_facts: tuple[str, ...] = ()
    constraints: dict[str, object] = field(default_factory=dict)
    optional_dependency_ids: tuple[str, ...] = ()


@dataclass(slots=True)
class Claim:
    claim_id: str | None
    text: str
    evidence_refs: list[str]
    status: ClaimStatus = "supported"


@dataclass(slots=True)
class LeafAnswer:
    query_id: str
    status: ClaimStatus
    answer_text: str
    claims: list[Claim]
    evidence_bundle: EvidenceBundle
    raw_output: object | None = None


@dataclass(slots=True)
class NodeResult:
    status: NodeStatus
    answer: LeafAnswer | None = None
    error: str | None = None
