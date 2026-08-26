import os
import time
import openai
import asyncio

from dotenv import find_dotenv, load_dotenv

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

MODEL_ID = "nvidia/nemotron-3-ultra-550b-a55b"
API_KEY_ENV = "NEMOTRON_ULTRA_API_KEY"

MAX_TOKENS = 6000
TEMPERATURE = 0
TOP_P = 0.000001

MAX_CONCURRENT_REQUESTS = 30
DEFAULT_REQUESTS_PER_SECOND = 2

MAX_BACKOFF = 30
MIN_RPS = 0.25
RECOVERY_STEP = 0.10
SUCCESS_THRESHOLD = 20


# ---------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------

def create_client() -> openai.AsyncOpenAI:
    load_dotenv(find_dotenv())

    api_key = os.getenv(API_KEY_ENV)

    if not api_key:
        raise RuntimeError(
            f"Environment variable {API_KEY_ENV!r} is not set."
        )

    return openai.AsyncOpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key,
        max_retries=0,
    )


# ---------------------------------------------------------------------
# LLM completion
# ---------------------------------------------------------------------

async def get_completion(
    client: openai.AsyncOpenAI,
    query: str,
    system_prompt: str,
    schema:  dict
) -> str:

    completion = await client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": query,
            },
        ],
        temperature=TEMPERATURE,
        top_p=TOP_P,
        max_tokens=MAX_TOKENS,
        stream=False,
        reasoning_effort="none",
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": schema["name"],
                "strict": True,
                "schema": schema["schema"],
            },
        },
    )

    return completion.choices[0].message.content


# ---------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------

async def wait_for_rate_limit(
    rate_lock: asyncio.Lock,
    last_request_time: list[float],
    cooldown_until: list[float],
    current_rps: list[float],
) -> None:

    async with rate_lock:
        now = time.monotonic()

        if now < cooldown_until[0]:
            await asyncio.sleep(cooldown_until[0] - now)
            now = time.monotonic()

        delay = 1 / current_rps[0]
        elapsed = now - last_request_time[0]
        wait_time = delay - elapsed

        if wait_time > 0:
            await asyncio.sleep(wait_time)
            now = time.monotonic()

        last_request_time[0] = now