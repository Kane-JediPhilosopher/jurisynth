"""Explicit opt-in smoke test for the local NVIDIA NIM configuration."""

import asyncio
import os

import pytest
from openai import InternalServerError

from jurisynth.agentic_reasoner.llm import EvidenceGroundedLeafGenerator, NIMConfig, NIMRetryPolicy, OpenAICompatibleNIM
from jurisynth.agentic_reasoner.models import LeafNode
from jurisynth.agentic_reasoner.qcompiler_translator import QCompilerTranslator
from jurisynth.contracts import Assertion, EvidenceBundle, EvidenceItem, SourceChunk


@pytest.mark.integration
@pytest.mark.live_nim
@pytest.mark.skipif(os.getenv("JURISYNTH_RUN_LIVE_NIM") != "1", reason="set JURISYNTH_RUN_LIVE_NIM=1 to call NVIDIA NIM")
def test_live_nim_translates_and_generates_evidence_grounded_claim(monkeypatch):
    async def smoke_test():
        config = NIMConfig.from_environment()
        model = OpenAICompatibleNIM(config, retry_policy=NIMRetryPolicy(max_attempts=2))
        try:
            compilation = await QCompilerTranslator(model).compile("What is the scope of Regulation (EU) 2016/679?")
            evidence = EvidenceBundle(
                "smoke_leaf",
                "success",
                [
                    EvidenceItem(
                        "E1",
                        Assertion("Regulation (EU) 2016/679", "has scope", "processing of personal data"),
                        [SourceChunk("smoke_chunk", "smoke_document", "Regulation (EU) 2016/679 concerns processing of personal data.")],
                    )
                ],
            )
            answer = await EvidenceGroundedLeafGenerator(model)(LeafNode("smoke_leaf", "What does the supplied regulation concern?"), [], evidence)
        finally:
            await model.aclose()
        return compilation, answer

    try:
        compilation, answer = asyncio.run(smoke_test())
    except InternalServerError as exc:
        pytest.xfail(f"NVIDIA NIM is temporarily overloaded: {exc.status_code}")
    assert compilation.leaves
    assert answer.claims
    assert all(reference == "E1" for claim in answer.claims for reference in claim.evidence_refs)


@pytest.mark.integration
@pytest.mark.live_nim
@pytest.mark.skipif(os.getenv("JURISYNTH_RUN_LIVE_NIM") != "1", reason="set JURISYNTH_RUN_LIVE_NIM=1 to call NVIDIA NIM")
@pytest.mark.parametrize(
    "prompt",
    [
        "What is the scope of Regulation (EU) 2016/679?",
        "Identify Directive 2010/13/EU and then explain what {Directive 2010/13/EU} regulates.",
        "What does a data controller do, and what must a processor do?",
    ],
)
def test_live_nim_translator_prompt_set(monkeypatch, prompt):
    async def smoke_test():
        model = OpenAICompatibleNIM(NIMConfig.from_environment(), retry_policy=NIMRetryPolicy(max_attempts=2))
        try:
            return await QCompilerTranslator(model).compile(prompt)
        finally:
            await model.aclose()

    try:
        compilation = asyncio.run(smoke_test())
    except InternalServerError as exc:
        pytest.xfail(f"NVIDIA NIM is temporarily overloaded: {exc.status_code}")
    assert compilation.expression
    assert compilation.leaves


@pytest.mark.integration
@pytest.mark.live_nim
@pytest.mark.skipif(os.getenv("JURISYNTH_RUN_LIVE_NIM") != "1", reason="set JURISYNTH_RUN_LIVE_NIM=1 to call NVIDIA NIM")
def test_live_nim_translator_accepts_multiline_legal_question():
    async def smoke_test():
        model = OpenAICompatibleNIM(NIMConfig.from_environment(), retry_policy=NIMRetryPolicy(max_attempts=2))
        try:
            return await QCompilerTranslator(model).compile(
                "First identify Regulation (EU) 2016/679.\n\n"
                "Then explain what it regulates.\n"
                "Finally, identify an obligation relevant to a data controller."
            )
        finally:
            await model.aclose()

    try:
        compilation = asyncio.run(smoke_test())
    except InternalServerError as exc:
        pytest.xfail(f"NVIDIA NIM is temporarily overloaded: {exc.status_code}")
    assert compilation.expression
    assert compilation.leaves
