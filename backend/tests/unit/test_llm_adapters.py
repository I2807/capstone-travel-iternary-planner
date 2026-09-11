import httpx
import pytest

from app.config import Settings
from app.llm.fallback import FallbackLLMClient
from app.llm.google import GoogleLLMClient
from app.llm.interface import LLMProviderError, LLMRequest
from app.llm.mock import MockLLMClient
from app.schemas.message import Message
from app.schemas.trip import TripContext


def itinerary_request() -> LLMRequest:
    return LLMRequest(
        task="plan",
        message="Plan Goa",
        history=[Message(role="user", content="Plan Goa")],
        trip_context=TripContext(
            destination="Goa",
            duration=2,
            travellers=2,
            budget={"amount": 25000, "currency": "INR"},
        ),
        output_shape="itinerary",
    )


@pytest.mark.asyncio
async def test_fallback_retries_provider_failure_once() -> None:
    primary = MockLLMClient(scenario="provider_error")
    fallback = MockLLMClient(model_used="fallback-model")
    client = FallbackLLMClient(primary, fallback)

    result = await client.generate(itinerary_request())

    assert result.attempt == "fallback"
    assert result.model_used == "fallback-model"
    assert len(primary.requests) == 1
    assert len(fallback.requests) == 1


@pytest.mark.asyncio
async def test_fallback_retries_invalid_structured_output_once() -> None:
    primary = MockLLMClient(scenario="invalid")
    fallback = MockLLMClient(model_used="fallback-model")

    result = await FallbackLLMClient(primary, fallback).generate(itinerary_request())

    assert result.attempt == "fallback"
    assert len(primary.requests) == 1
    assert len(fallback.requests) == 1


@pytest.mark.asyncio
async def test_fallback_returns_safe_provider_error_after_both_fail() -> None:
    client = FallbackLLMClient(
        MockLLMClient(scenario="provider_error"),
        MockLLMClient(scenario="provider_error"),
    )

    with pytest.raises(LLMProviderError, match="unavailable"):
        await client.generate(itinerary_request())


@pytest.mark.asyncio
async def test_google_adapter_maps_structured_response_without_live_network() -> None:
    class FakeClient:
        async def post(self, url, *, json, headers):
            assert "generateContent" in url
            assert "x-goog-api-key" in headers
            assert json["generationConfig"]["responseMimeType"] == "application/json"
            assert json["generationConfig"]["maxOutputTokens"] == 2048
            assert json["generationConfig"]["temperature"] == 0.2
            return httpx.Response(
                200,
                json={"candidates": [{"content": {"parts": [{"text": '{"ok": true}'}]}}]},
            )

    settings = Settings(llm_provider="google", google_api_key="test-key")
    result = await GoogleLLMClient(settings=settings, http_client=FakeClient()).generate(
        LLMRequest(task="guide", message="What should I pack?", history=[])
    )

    assert result.structured_output is None
    assert result.reply == '{"ok": true}'
    assert result.model_used == settings.model_name
