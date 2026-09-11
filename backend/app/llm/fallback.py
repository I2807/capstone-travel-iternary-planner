from __future__ import annotations

from app.llm.interface import (
    InvalidLLMOutputError,
    LLMClient,
    LLMProviderError,
    LLMRequest,
    LLMResult,
)
from app.schemas.itinerary import Itinerary


class FallbackLLMClient:
    def __init__(self, primary: LLMClient, fallback: LLMClient) -> None:
        self.primary = primary
        self.fallback = fallback

    async def generate(self, request: LLMRequest) -> LLMResult:
        try:
            primary_result = await self.primary.generate(request)
            self._validate_result(request, primary_result)
            return primary_result
        except (LLMProviderError, InvalidLLMOutputError):
            return await self._generate_fallback(request)

    async def _generate_fallback(self, request: LLMRequest) -> LLMResult:
        try:
            fallback_result = await self.fallback.generate(request)
            self._validate_result(request, fallback_result)
        except (LLMProviderError, InvalidLLMOutputError) as exc:
            if isinstance(exc, InvalidLLMOutputError):
                raise exc
            raise LLMProviderError("Primary and fallback LLM providers are unavailable.") from exc
        return fallback_result.model_copy(update={"attempt": "fallback"})

    @staticmethod
    def _validate_result(request: LLMRequest, result: LLMResult) -> None:
        if request.output_shape == "itinerary":
            try:
                Itinerary.model_validate(result.structured_output)
            except Exception as exc:
                raise InvalidLLMOutputError("LLM itinerary output is invalid.") from exc
