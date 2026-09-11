from typing import Annotated

from fastapi import Depends

from app.config import Settings, get_settings
from app.llm.fallback import FallbackLLMClient
from app.llm.google import GoogleLLMClient
from app.llm.interface import LLMClient
from app.llm.mock import MockLLMClient
from app.weather.interface import WeatherService
from app.weather.mock import MockWeatherService

SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_llm_client(settings: SettingsDep) -> LLMClient:
    if settings.llm_provider == "mock":
        return MockLLMClient(model_used=settings.model_name)

    primary = GoogleLLMClient(settings=settings)
    fallback_settings = settings.model_copy(update={"model_name": settings.fallback_model_name})
    fallback = GoogleLLMClient(settings=fallback_settings)
    return FallbackLLMClient(primary, fallback)


def get_weather_service(settings: SettingsDep) -> WeatherService:
    if settings.weather_provider == "mock":
        return MockWeatherService(scenario=settings.mock_weather_scenario)

    from app.weather.openweather import OpenWeatherService

    return OpenWeatherService(settings=settings)


LLMClientDep = Annotated[LLMClient, Depends(get_llm_client)]
WeatherServiceDep = Annotated[WeatherService, Depends(get_weather_service)]
