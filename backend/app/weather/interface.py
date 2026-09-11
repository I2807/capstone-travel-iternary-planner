from typing import Protocol

from app.schemas.weather import WeatherData, WeatherQuery


class WeatherService(Protocol):
    async def get_weather(self, query: WeatherQuery) -> WeatherData:
        """Return normalized weather data without exposing provider payloads."""
