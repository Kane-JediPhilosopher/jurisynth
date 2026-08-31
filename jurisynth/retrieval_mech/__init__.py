"""Opaque query-time retrieval interface for the Agentic Reasoner."""

from typing import TYPE_CHECKING

from jurisynth.contracts import EvidenceBundle, RetrievalRequest

if TYPE_CHECKING:
    from jurisynth.retrieval_mech.mechanism import RetrievalMechanism

__all__ = ["EvidenceBundle", "RetrievalMechanism", "RetrievalRequest"]


def __getattr__(name: str):
    """Avoid loading optional ML dependencies until retrieval is actually used."""
    if name == "RetrievalMechanism":
        from jurisynth.retrieval_mech.mechanism import RetrievalMechanism
        return RetrievalMechanism
    raise AttributeError(name)
