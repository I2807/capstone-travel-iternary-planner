from datetime import date

import httpx
import pytest

from app.config import Settings
from app.schemas.weather import WeatherQuery
from app.weather.mock import MockWeatherService
from app.weather.openweather import OpenWeatherService


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("scenario", "source", "risk"),
    [
        ("rain", "mock", "high"),
        ("safe_outdoor", "mock", "low"),
        ("unavailable", "unavailable", "unknown"),
    ],
)
async def test_mock_weather_provider_scenarios_are_explicit(scenario, source, risk) -> None:
    result = await MockWeatherService(scenario=scenario).get_weather(
        WeatherQuery(destination="Goa", forecast_date=date(2026, 9, 12), travellers=2)
    )

    assert result.source == source
    assert result.outdoor_risk == risk


@pytest.mark.asyncio
async def test_openweather_maps_live_response_without_network() -> None:
    class FakeClient:
        async def get(self, url, *, params):
            assert "weather" in url
            assert params["appid"] == "test-key"
            return httpx.Response(
                200,
                json={"weather": [{"main": "Rain"}], "main": {"temp": 28.5}},
            )

    service = OpenWeatherService(
        settings=Settings(weather_provider="openweather", weather_api_key="test-key"),
        http_client=FakeClient(),
    )
    result = await service.get_weather(
        WeatherQuery(destination="Goa", forecast_date=date(2026, 9, 12))
    )

    assert result.source == "live"
    assert result.condition == "Rain"
    assert result.temperature == 28.5
    assert result.outdoor_risk == "high"


@pytest.mark.asyncio
async def test_openweather_timeout_becomes_unavailable() -> None:
    class TimeoutClient:
        async def get(self, url, *, params):
            raise httpx.TimeoutException("timed out")

    service = OpenWeatherService(
        settings=Settings(weather_provider="openweather", weather_api_key="test-key"),
        http_client=TimeoutClient(),
    )
    result = await service.get_weather(WeatherQuery(destination="Goa"))

    assert result.source == "unavailable"
    assert result.outdoor_risk == "unknown"
    assert result.condition is None
