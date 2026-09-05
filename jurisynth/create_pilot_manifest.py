"""Create a pre-run reproducibility manifest for the batch_0009 pilot."""

from __future__ import annotations

from pathlib import Path

from jurisynth.reproducibility_manifest import write_manifest


def main() -> None:
    write_manifest(
        Path("jurisynth/evaluation_artifacts/pilot_manifest.json"),
        artifacts={
            "natural_query_seeds": Path("jurisynth/evaluation_artifacts/batch_0009_natural_query_seeds.jsonl"),
            "retrieval_mechanism": Path("jurisynth/retrieval_mech/mechanism.py"),
            "direct_rdf_retriever": Path("jurisynth/retrieval_mech/rdf_retriever.py"),
            "agentic_workflow": Path("jurisynth/agentic_reasoner/workflow.py"),
        },
        commands=[
            "python -m jurisynth.run_natural_evaluation",
            "python -m jurisynth.run_pilot_evaluation --limit 50",
            "python -m jurisynth.main <question> --output <path>",
        ],
        models={"embedder": "all-MiniLM-L6-v2", "nim_default": "nvidia/nemotron-3-ultra-550b-a55b"},
        config={"pilot_batch": "batch_0009", "schema": "pre-run"},
    )


if __name__ == "__main__":
    main()
