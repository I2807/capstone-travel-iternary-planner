from app.config import Settings
from app.dependencies import get_llm_client, get_weather_service
from app.llm.fallback import FallbackLLMClient
from app.llm.google import GoogleLLMClient
from app.llm.mock import MockLLMClient
from app.weather.mock import MockWeatherService


def test_dependency_composition_selects_deterministic_mock_providers() -> None:
    settings = Settings(
        llm_provider="mock",
        weather_provider="mock",
        mock_weather_scenario="safe_outdoor",
    )

    llm = get_llm_client(settings)
    weather = get_weather_service(settings)

    assert isinstance(llm, MockLLMClient)
    assert isinstance(weather, MockWeatherService)
    assert weather.scenario == "safe_outdoor"


def test_google_composition_keeps_gemma_primary_and_configures_fallback() -> None:
    settings = Settings(
        llm_provider="google",
        google_api_key="test-key",
        weather_provider="mock",
    )

    client = get_llm_client(settings)

    assert isinstance(client, FallbackLLMClient)
    assert isinstance(client.primary, GoogleLLMClient)
    assert isinstance(client.fallback, GoogleLLMClient)
    assert client.primary.settings.model_name == "gemma-4-26b-a4b-it"
    assert client.fallback.settings.model_name == "gemini-3.6-flash"
