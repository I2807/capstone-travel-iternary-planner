from typing import Literal

from app.schemas.weather import WeatherData, WeatherQuery

MockWeatherScenario = Literal["rain", "safe_outdoor", "unavailable"]


class MockWeatherService:
    def __init__(self, *, scenario: MockWeatherScenario = "rain") -> None:
        self.scenario = scenario
        self.queries: list[WeatherQuery] = []

    async def get_weather(self, query: WeatherQuery) -> WeatherData:
        self.queries.append(query)
        if self.scenario == "rain":
            return WeatherData(
                condition="Rain",
                outdoor_risk="high",
                source="mock",
                forecast_date=query.forecast_date,
            )
        if self.scenario == "safe_outdoor":
            return WeatherData(
                condition="Clear",
                outdoor_risk="low",
                source="mock",
                forecast_date=query.forecast_date,
            )
        return WeatherData(
            condition=None,
            outdoor_risk="unknown",
            source="unavailable",
            forecast_date=query.forecast_date,
        )
