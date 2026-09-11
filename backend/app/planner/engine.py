from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.llm.interface import LLMClient, LLMRequest
from app.planner.generation import generate_itinerary
from app.planner.guidance import provide_guidance
from app.planner.intents import (
    classify_intent,
    extract_trip_context,
    merge_trip_context,
    missing_required_trip_details,
)
from app.planner.modification import modify_itinerary
from app.planner.replanning import replan_itinerary
from app.schemas.itinerary import Itinerary, ItineraryChange
from app.schemas.message import Message
from app.schemas.trip import TripContext
from app.schemas.weather import WeatherData, WeatherQuery, WeatherSource
from app.weather.interface import WeatherService


@dataclass(slots=True)
class PlannerResult:
    reply: str
    itinerary: Itinerary | None = None
    trip_context: TripContext | None = None
    model_used: str | None = None
    weather_source: WeatherSource | None = None
    changes: list[ItineraryChange] = field(default_factory=list)


class PlannerEngine:
    def __init__(self, llm_client: LLMClient, weather_service: WeatherService) -> None:
        self.llm_client = llm_client
        self.weather_service = weather_service

    async def handle(
        self,
        *,
        message: str,
        history: list[Message],
        trip_context: TripContext | None,
        itinerary: Itinerary | None = None,
    ) -> PlannerResult:
        intent = classify_intent(message, has_itinerary=itinerary is not None)
        if intent == "guardrail":
            return PlannerResult(
                reply=(
                    "I can help with travel planning, destinations, itineraries, "
                    "and travel guidance."
                ),
                trip_context=trip_context,
            )
        merged_context = merge_trip_context(trip_context, extract_trip_context(message))
        if intent == "guide":
            return PlannerResult(
                reply=provide_guidance(message, merged_context),
                trip_context=merged_context,
            )
        if itinerary is not None:
            if intent == "modify":
                updated_itinerary, reply, changes = modify_itinerary(itinerary, message)
                return PlannerResult(
                    reply=reply,
                    itinerary=updated_itinerary,
                    trip_context=merged_context,
                    changes=changes,
                )
            if intent == "replan":
                return await self._handle_replan(message, itinerary, merged_context)
        missing = missing_required_trip_details(merged_context)
        if missing:
            return PlannerResult(
                reply=self._clarification_reply(missing),
                trip_context=merged_context,
            )

        llm_request = LLMRequest(
            task="plan",
            message=message,
            history=history,
            trip_context=merged_context,
            itinerary=itinerary,
            output_shape="itinerary",
        )
        generated_itinerary, result = await generate_itinerary(self.llm_client, llm_request)
        return PlannerResult(
            reply=result.reply,
            itinerary=generated_itinerary,
            trip_context=merged_context,
            model_used=result.model_used,
        )

    async def _handle_replan(
        self,
        message: str,
        itinerary: Itinerary,
        trip_context: TripContext,
    ) -> PlannerResult:
        day_number = _target_day(message) or 1
        query = WeatherQuery(
            destination=itinerary.destination,
            travellers=itinerary.travellers,
        )
        try:
            weather = await self.weather_service.get_weather(query)
        except Exception:
            weather = WeatherData(source="unavailable", outdoor_risk="unknown")

        if weather.source == "unavailable":
            return PlannerResult(
                reply=(
                    "No verified live weather was available, so I kept the "
                    "existing itinerary unchanged."
                ),
                itinerary=itinerary,
                trip_context=trip_context,
                weather_source="unavailable",
            )

        replanned, changes = replan_itinerary(
            itinerary,
            weather,
            day_number=day_number,
            interests=trip_context.interests,
        )
        if changes:
            return PlannerResult(
                reply=(
                    f"I replanned Day {day_number} using {weather.source} weather data "
                    f"and explained each replacement below."
                ),
                itinerary=replanned,
                trip_context=trip_context,
                weather_source=weather.source,
                changes=changes,
            )
        return PlannerResult(
            reply=(
                f"The {weather.source} weather result does not require changes, "
                "so I kept the itinerary unchanged."
            ),
            itinerary=itinerary,
            trip_context=trip_context,
            weather_source=weather.source,
        )

    @staticmethod
    def _clarification_reply(missing: list[str]) -> str:
        if len(missing) == 1:
            return f"What is the {missing[0]} for your trip?"
        missing_values = ", ".join(missing[:-1])
        return (
            f"Before I build the itinerary, please provide your {missing_values}, "
            f"and {missing[-1]}."
        )


def _target_day(message: str) -> int | None:
    match = re.search(r"\bday\s*(\d+)\b", message.lower())
    return int(match.group(1)) if match else None
