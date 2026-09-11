import pytest

from app.config import ConfigurationError, Settings, get_settings


def test_settings_normalize_origins_and_expose_safe_defaults() -> None:
    settings = Settings(cors_origins="http://localhost:5173, http://localhost:4173")

    assert settings.cors_origin_list == ["http://localhost:5173", "http://localhost:4173"]
    assert settings.max_conversation_messages == 50
    assert settings.llm_configured is True


def test_live_provider_requires_credentials_without_exposing_values() -> None:
    with pytest.raises(ValueError, match="WEATHER_API_KEY") as error:
        Settings(weather_provider="openweather")

    assert "secret" not in str(error.value).lower()


def test_invalid_environment_provider_raises_safe_configuration_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WEATHER_PROVIDER", "invalid")
    get_settings.cache_clear()

    try:
        with pytest.raises(ConfigurationError, match="Provider configuration is invalid"):
            get_settings()
    finally:
        get_settings.cache_clear()
