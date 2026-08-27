import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import llm_utils

# =====================================================================
# Client creation
# =====================================================================

def test_create_client_requires_api_key():
    with patch("llm_utils.load_dotenv"), \
         patch("llm_utils.find_dotenv", return_value=""), \
         patch("llm_utils.os.getenv", return_value=None):

        with pytest.raises(RuntimeError, match="NEMOTRON_ULTRA_API_KEY"):
            llm_utils.create_client()

def test_create_client_configures_openai_client():
    with patch("llm_utils.load_dotenv"), \
         patch("llm_utils.find_dotenv", return_value=""), \
         patch("llm_utils.os.getenv", return_value="test-key"), \
         patch("llm_utils.openai.AsyncOpenAI") as mock_client:

        result = llm_utils.create_client()

    mock_client.assert_called_once_with(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key="test-key",
        max_retries=0,
    )

    assert result == mock_client.return_value


# =====================================================================
# LLM calls
# =====================================================================

@pytest.mark.asyncio
async def test_get_completion_returns_message_content():
    client = MagicMock()

    response = MagicMock()
    response.choices = [
        MagicMock(
            message=MagicMock(
                content='{"answer": "test"}'
            )
        )
    ]

    client.chat.completions.create = AsyncMock(
        return_value=response
    )

    result = await llm_utils.get_completion(
        client=client,
        query="What is the answer?",
        system_prompt="You are a test assistant.",
        schema={
            "name": "test_schema",
            "schema": {
                "type": "object"
            },
        },
    )

    assert result == '{"answer": "test"}'


@pytest.mark.asyncio
async def test_get_completion_sends_expected_request():
    client = MagicMock()

    response = MagicMock()
    response.choices = [
        MagicMock(
            message=MagicMock(
                content="{}"
            )
        )
    ]

    client.chat.completions.create = AsyncMock(
        return_value=response
    )

    schema = {
        "name": "test_schema",
        "schema": {
            "type": "object"
        },
    }

    await llm_utils.get_completion(
        client=client,
        query="test query",
        system_prompt="test system prompt",
        schema=schema,
    )

    client.chat.completions.create.assert_awaited_once_with(
        model=llm_utils.MODEL_ID,
        messages=[
            {
                "role": "system",
                "content": "test system prompt",
            },
            {
                "role": "user",
                "content": "test query",
            },
        ],
        temperature=llm_utils.TEMPERATURE,
        top_p=llm_utils.TOP_P,
        max_tokens=llm_utils.MAX_TOKENS,
        stream=False,
        reasoning_effort="none",
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "test_schema",
                "strict": True,
                "schema": schema["schema"],
            },
        },
    )


# =====================================================================
# Rate-limiting
# =====================================================================

@pytest.mark.asyncio
async def test_wait_for_rate_limit_enforces_request_interval():
    rate_lock = asyncio.Lock()

    last_request_time = [100.0]
    cooldown_until = [0.0]
    current_rps = [2.0]

    with patch(
        "llm_utils.time.monotonic",
        side_effect=[
            100.0,  # initial now
            100.5,  # after sleep
        ],
    ), patch(
        "llm_utils.asyncio.sleep",
        new=AsyncMock(),
    ) as mock_sleep:

        await llm_utils.wait_for_rate_limit(
            rate_lock,
            last_request_time,
            cooldown_until,
            current_rps,
        )

    mock_sleep.assert_awaited_once_with(0.5)
    assert last_request_time[0] == 100.5


@pytest.mark.asyncio
async def test_wait_for_rate_limit_respects_cooldown():
    rate_lock = asyncio.Lock()

    last_request_time = [0.0]
    cooldown_until = [110.0]
    current_rps = [2.0]

    with patch(
        "llm_utils.time.monotonic",
        side_effect=[
            100.0,  # initial now
            110.0,  # after cooldown sleep
            110.0,  # after rate-limit calculation
        ],
    ), patch(
        "llm_utils.asyncio.sleep",
        new=AsyncMock(),
    ) as mock_sleep:

        await llm_utils.wait_for_rate_limit(
            rate_lock,
            last_request_time,
            cooldown_until,
            current_rps,
        )

    mock_sleep.assert_awaited_once_with(10.0)
    assert last_request_time[0] == 110.0


# =====================================================================
# Exception propagation
# =====================================================================

@pytest.mark.asyncio
async def test_get_completion_propagates_api_error():
    client = MagicMock()

    error = RuntimeError("intentional API failure")

    client.chat.completions.create = AsyncMock(
        side_effect=error
    )

    with pytest.raises(RuntimeError, match="intentional API failure"):
        await llm_utils.get_completion(
            client=client,
            query="test query",
            system_prompt="test system prompt",
            schema={
                "name": "test_schema",
                "schema": {
                    "type": "object"
                },
            },
        )


# =====================================================================
# Concurrency handling
# =====================================================================

@pytest.mark.asyncio
async def test_wait_for_rate_limit_serializes_concurrent_callers():
    rate_lock = asyncio.Lock()

    last_request_time = [0.0]
    cooldown_until = [0.0]
    current_rps = [2.0]

    first_sleep_started = asyncio.Event()
    release_first_sleep = asyncio.Event()

    async def controlled_sleep(delay):
        if not first_sleep_started.is_set():
            first_sleep_started.set()
            await release_first_sleep.wait()

    with patch(
        "llm_utils.time.monotonic",
        return_value=0.0,
    ), patch(
        "llm_utils.asyncio.sleep",
        side_effect=controlled_sleep,
    ):
        first = asyncio.create_task(
            llm_utils.wait_for_rate_limit(
                rate_lock,
                last_request_time,
                cooldown_until,
                current_rps,
            )
        )

        await first_sleep_started.wait()

        second = asyncio.create_task(
            llm_utils.wait_for_rate_limit(
                rate_lock,
                last_request_time,
                cooldown_until,
                current_rps,
            )
        )

        await asyncio.sleep(0)

        # The first caller still owns the lock, so the second
        # caller must still be waiting.
        assert not second.done()

        release_first_sleep.set()

        await asyncio.gather(
            first,
            second,
        )