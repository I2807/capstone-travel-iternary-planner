from datetime import date

import pytest

from app.llm.interface import LLMProviderError, LLMRequest
from app.llm.mock import MockLLMClient
from app.schemas.message import Message
from app.schemas.trip import TripContext
from app.schemas.weather import WeatherQuery
from app.weather.mock import MockWeatherService


@pytest.mark.asyncio
async def test_mock_llm_returns_valid_structured_output() -> None:
    client = MockLLMClient()
    result = await client.generate(
        LLMRequest(
            task="plan",
            message="Plan Goa",
            history=[Message(role="user", content="Plan Goa")],
            trip_context=TripContext(destination="Goa", duration=2, travellers=2),
        )
    )

    assert result.structured_output is not None
    assert result.structured_output["destination"] == "Goa"
    assert len(client.requests) == 1


@pytest.mark.asyncio
async def test_mock_llm_can_return_invalid_output_or_provider_failure() -> None:
    invalid = await MockLLMClient(scenario="invalid").generate(
        LLMRequest(task="plan", message="Plan Goa", history=[])
    )
    assert invalid.structured_output == {"invalid": True}

    with pytest.raises(LLMProviderError):
        await MockLLMClient(scenario="provider_error").generate(
            LLMRequest(task="plan", message="Plan Goa", history=[])
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("scenario", "source", "risk"),
    [
        ("rain", "mock", "high"),
        ("safe_outdoor", "mock", "low"),
        ("unavailable", "unavailable", "unknown"),
    ],
)
async def test_mock_weather_scenarios_are_explicit(
    scenario: str,
    source: str,
    risk: str,
) -> None:
    service = MockWeatherService(scenario=scenario)  # type: ignore[arg-type]
    result = await service.get_weather(
        WeatherQuery(destination="Goa", forecast_date=date(2026, 9, 12), travellers=2)
    )

    assert result.source == source
    assert result.outdoor_risk == risk
