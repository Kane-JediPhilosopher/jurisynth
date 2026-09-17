"""Run Jurisynth's offline suites in separate processes to bound peak memory.

The runner deliberately excludes tests marked ``integration`` by default:
those parse persisted corpus artifacts or call optional external services and
should be an explicit, separately provisioned step.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys


SUITES = (
    "jurisynth/agentic_reasoner/tests",
    "jurisynth/retrieval_mech/tests",
    "jurisynth/tests",
    "jurisynth/kg_construction_pipeline/tests",
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run bounded-memory Jurisynth offline tests.")
    parser.add_argument("--include-integration", action="store_true", help="Also run opt-in persisted-artifact integration tests.")
    args = parser.parse_args()
    marker = "integration and not live_nim" if args.include_integration else "not integration and not live_nim"
    environment = os.environ.copy()
    # A user may have enabled live smoke tests in their shell.  This runner is
    # explicitly offline, so never inherit that opt-in flag accidentally.
    environment["JURISYNTH_RUN_LIVE_NIM"] = "0"
    for suite in SUITES:
        command = [sys.executable, "-m", "pytest", suite, "-q", "-m", marker]
        print(f"\n==> {' '.join(command)}", flush=True)
        completed = subprocess.run(command, check=False, env=environment)
        if completed.returncode:
            raise SystemExit(completed.returncode)
    print("\nOffline test suites passed.")


if __name__ == "__main__":
    main()
