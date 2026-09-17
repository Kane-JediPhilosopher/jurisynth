"""Small, dependency-free records shared by E-R build and query code."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResourceRecord:
    uri: str
    label: str
    community_ids: tuple[str, ...] = ()
