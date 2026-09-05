"""NVIDIA NIM configuration for optional visual processing.

This is intentionally separate from :mod:`llm_utils`: that module is the
locked Nemotron Ultra configuration for textual KG assertion extraction.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import openai
from dotenv import find_dotenv, load_dotenv


NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_IMAGE_MODEL_ID = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
IMAGE_API_KEY_ENV = "NEMOTRON_NANO_OMNI_API_KEY"
SHARED_NIM_API_KEY_ENV = "JURISYNTH_NIM_API_KEY"
IMAGE_MODEL_ENV = "NEMOTRON_NANO_OMNI_MODEL"
IMAGE_BASE_URL_ENV = "NEMOTRON_NANO_OMNI_BASE_URL"
SHARED_NIM_BASE_URL_ENV = "JURISYNTH_NIM_BASE_URL"


@dataclass(frozen=True, slots=True)
class VisionNIMConfig:
    """Provider configuration for captions; never inherits an Ultra model ID."""

    api_key: str
    base_url: str
    model_id: str

    @classmethod
    def from_environment(cls) -> "VisionNIMConfig":
        dotenv_path = find_dotenv()
        if dotenv_path:
            load_dotenv(dotenv_path)
        # Reuse the existing provider-level key only when the operator has not
        # supplied a dedicated vision key.  Ultra's model variable is ignored.
        reasoner_env = Path(__file__).resolve().parents[2] / "agentic_reasoner" / ".env"
        if reasoner_env.is_file():
            load_dotenv(reasoner_env)
        api_key = os.getenv(IMAGE_API_KEY_ENV) or os.getenv(SHARED_NIM_API_KEY_ENV)
        if not api_key:
            raise RuntimeError(
                f"Environment variable {IMAGE_API_KEY_ENV!r} (or {SHARED_NIM_API_KEY_ENV!r}) is not set."
            )
        return cls(
            api_key=api_key,
            base_url=os.getenv(IMAGE_BASE_URL_ENV) or os.getenv(SHARED_NIM_BASE_URL_ENV) or NIM_BASE_URL,
            model_id=os.getenv(IMAGE_MODEL_ENV) or DEFAULT_IMAGE_MODEL_ID,
        )


def create_vision_client(config: VisionNIMConfig) -> openai.AsyncOpenAI:
    return openai.AsyncOpenAI(base_url=config.base_url, api_key=config.api_key, max_retries=0)
