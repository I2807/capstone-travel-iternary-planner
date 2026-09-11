from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, ValidationError, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigurationError(RuntimeError):
    """Raised when environment-backed provider configuration is unsafe to use."""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    google_api_key: SecretStr | None = None
    weather_api_key: SecretStr | None = None
    model_name: str = "gemma-4-26b-a4b-it"
    fallback_model_name: str = "gemini-3.6-flash"
    llm_provider: Literal["mock", "google"] = "mock"
    weather_provider: Literal["mock", "openweather"] = "mock"
    mock_weather_scenario: Literal["rain", "safe_outdoor", "unavailable"] = "rain"
    cors_origins: str = "http://localhost:5173"
    api_timeout_seconds: float = Field(default=30.0, gt=0, le=120)
    max_conversation_messages: int = Field(default=50, ge=1, le=50)
    log_level: str = "INFO"

    @field_validator("model_name", "fallback_model_name", "log_level", mode="before")
    @classmethod
    def strip_text_values(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def normalize_origins(cls, value: object) -> str:
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, list):
            return ",".join(str(origin).strip() for origin in value)
        return value

    @model_validator(mode="after")
    def validate_provider_configuration(self) -> "Settings":
        if self.llm_provider == "google" and not self.google_api_key:
            raise ValueError("Google LLM provider requires GOOGLE_API_KEY.")
        if self.weather_provider == "openweather" and not self.weather_api_key:
            raise ValueError("OpenWeather provider requires WEATHER_API_KEY.")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def llm_configured(self) -> bool:
        return self.llm_provider == "mock" or self.google_api_key is not None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    try:
        return Settings()
    except (ValidationError, ValueError):
        raise ConfigurationError("Provider configuration is invalid or incomplete.") from None
