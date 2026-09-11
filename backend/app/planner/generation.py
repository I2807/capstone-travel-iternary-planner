from __future__ import annotations

from pydantic import ValidationError

from app.errors import AppError
from app.llm.interface import LLMClient, LLMProviderError, LLMRequest, LLMResult
from app.schemas.itinerary import Itinerary


async def generate_itinerary(
    llm_client: LLMClient,
    request: LLMRequest,
) -> tuple[Itinerary, LLMResult]:
    try:
        result = await llm_client.generate(request)
    except LLMProviderError as exc:
        raise AppError.create(
            "PROVIDER_UNAVAILABLE",
            "The travel planning service is temporarily unavailable. Please try again.",
        ) from exc

    try:
        itinerary = Itinerary.model_validate(result.structured_output)
    except (ValidationError, TypeError, ValueError) as exc:
        raise AppError.create(
            "INVALID_PROVIDER_OUTPUT",
            "The travel planning service returned an invalid plan. Please try again.",
        ) from exc
    return itinerary, result
