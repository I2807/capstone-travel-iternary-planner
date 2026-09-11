from __future__ import annotations

from datetime import date
from typing import Any

import httpx

from app.config import Settings
from app.schemas.weather import WeatherData, WeatherQuery


class OpenWeatherService:
    endpoint = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(
        self,
        *,
        settings: Settings,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = settings
        self.http_client = http_client

    async def get_weather(self, query: WeatherQuery) -> WeatherData:
        if self.settings.weather_api_key is None:
            return self._unavailable(query.forecast_date)

        params = {
            "q": query.destination,
            "appid": self.settings.weather_api_key.get_secret_value(),
            "units": "metric",
        }
        try:
            response = await self._get(params)
            if response.status_code >= 400:
                return self._unavailable(query.forecast_date)
            payload = response.json()
            condition = str(payload["weather"][0]["main"])
            temperature = float(payload["main"]["temp"])
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError):
            return self._unavailable(query.forecast_date)

        return WeatherData(
            condition=condition,
            temperature=temperature,
            outdoor_risk=self._risk_for(condition),
            source="live",
            forecast_date=query.forecast_date,
        )

    async def _get(self, params: dict[str, Any]) -> httpx.Response:
        if self.http_client is not None:
            return await self.http_client.get(self.endpoint, params=params)
        async with httpx.AsyncClient(timeout=self.settings.api_timeout_seconds) as client:
            return await client.get(self.endpoint, params=params)

    @staticmethod
    def _risk_for(condition: str) -> str:
        normalized = condition.lower()
        if any(term in normalized for term in ("rain", "thunder", "snow", "storm")):
            return "high"
        if any(term in normalized for term in ("cloud", "mist", "fog")):
            return "medium"
        return "low"

    @staticmethod
    def _unavailable(forecast_date: date | None) -> WeatherData:
        return WeatherData(
            condition=None,
            temperature=None,
            outdoor_risk="unknown",
            source="unavailable",
            forecast_date=forecast_date,
        )
