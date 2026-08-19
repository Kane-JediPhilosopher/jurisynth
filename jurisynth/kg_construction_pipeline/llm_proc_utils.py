from dotenv import load_dotenv, find_dotenv
import asyncio
import openai
import time
import os


# Security Measure
_ = load_dotenv(find_dotenv()) # read local .env file

# Options:
# gpt-oss-120b:               OPENAI_API_KEY
# nemotron-3-super-120b-a12b: NEMOTRON_API_KEY
# nemotron-3-ultra-550b-a55b: NEMOTRON_ULTRA_API_KEY

openai.api_key  = os.getenv('NEMOTRON_ULTRA_API_KEY')

# Batch processing variables (MIGHT MOVE TO main.py)
SEMAPHORE = asyncio.Semaphore(30)

# Client
client = openai.AsyncOpenAI(
    base_url = "https://integrate.api.nvidia.com/v1",
    api_key = openai.api_key,
    max_retries=0
    )

async def get_completion(
        system_prompt="",
        query="",
        schema=None
        ):
    
    completion = await client.chat.completions.create(
        # Model Options:
        # openai/gpt-oss-120b
        # nvidia/nemotron-3-nano-30b-a3b
        # nvidia/nemotron-3-super-120b-a12b
        # nvidia/nemotron-3-ultra-550b-a55b
        # nvidia/llama-3.3-nemotron-super-49b-v1.5
        # z-ai/glm-5.2

        model="nvidia/nemotron-3-ultra-550b-a55b",
        messages=[
           {'role':'system', 'content': system_prompt},
           {'role':'user', 'content': query}
           ],
        temperature=0,
        top_p=0.000001, # Test different values
        max_tokens=6000,
        stream=False,
        reasoning_effort="none",
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "schema",
                "strict": True,
                "schema": schema
                }
            }
        )

    return completion.choices[0].message.content


# ---------------------------------------------------------------------
# Global rate limiter
# ---------------------------------------------------------------------

async def wait_for_rate_limit(
    rate_lock,
    last_request_time,
    cooldown_until,
    current_rps,
):

    async with rate_lock:
        now = time.monotonic()

        # ----------------------------------------------------------
        # Global cooldown
        # ----------------------------------------------------------

        if now < cooldown_until[0]:
            await asyncio.sleep(cooldown_until[0] - now)
            now = time.monotonic()

        # ----------------------------------------------------------
        # Request spacing
        # ----------------------------------------------------------

        delay = 1 / current_rps[0]
        elapsed = (now - last_request_time[0])
        wait_time = delay - elapsed

        if wait_time > 0:
            await asyncio.sleep(wait_time)
            now = time.monotonic()

        last_request_time[0] = now