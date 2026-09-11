import pytest
from fastapi.testclient import TestClient

from app.config import ConfigurationError, Settings, get_settings
from app.main import create_app


def test_health_returns_safe_fields_and_matching_request_id() -> None:
    client = TestClient(create_app(Settings()))

    response = client.get("/api/health")
    payload = response.json()

    assert response.status_code == 200
    assert payload["status"] == "ok"
    assert payload["model"] == "gemma-4-26b-a4b-it"
    assert payload["llm_provider"] == "mock"
    assert payload["weather_provider"] == "mock"
    assert payload["llm_configured"] is True
    assert response.headers["X-Request-ID"] == payload["request_id"]
    assert "api_key" not in response.text.lower()


def test_incomplete_live_configuration_fails_without_secret_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "google")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    get_settings.cache_clear()

    try:
        with pytest.raises(ConfigurationError, match="configuration is invalid"):
            get_settings()
    finally:
        get_settings.cache_clear()
