import pytest
from fastapi.testclient import TestClient

import app.main as app_main
from app.config import Settings
from app.dependencies import get_llm_client, get_weather_service
from app.llm.mock import MockLLMClient
from app.main import create_app
from app.weather.mock import MockWeatherService


@pytest.fixture
def settings() -> Settings:
    return Settings(
        llm_provider="mock",
        weather_provider="mock",
        mock_weather_scenario="rain",
        cors_origins="http://testserver",
    )


@pytest.fixture
def mock_llm_client() -> MockLLMClient:
    return MockLLMClient()


@pytest.fixture
def mock_weather_service() -> MockWeatherService:
    return MockWeatherService(scenario="rain")


@pytest.fixture
def request_id() -> str:
    return "test-request-id"


@pytest.fixture
def api_client(
    settings: Settings,
    mock_llm_client: MockLLMClient,
    mock_weather_service: MockWeatherService,
    request_id: str,
    monkeypatch: pytest.MonkeyPatch,
) -> TestClient:
    monkeypatch.setattr(app_main, "create_request_id", lambda: request_id)
    app = create_app(settings)
    app.dependency_overrides[get_llm_client] = lambda: mock_llm_client
    app.dependency_overrides[get_weather_service] = lambda: mock_weather_service
    return TestClient(app)
