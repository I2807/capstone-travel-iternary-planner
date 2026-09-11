from __future__ import annotations

from typing import Literal

from app.llm.interface import LLMProviderError, LLMRequest, LLMResult

MockLLMScenario = Literal["valid", "invalid", "provider_error", "unavailable"]


class MockLLMClient:
    def __init__(
        self,
        *,
        scenario: MockLLMScenario = "valid",
        model_used: str = "mock-model",
    ) -> None:
        self.scenario = scenario
        self.model_used = model_used
        self.requests: list[LLMRequest] = []

    async def generate(self, request: LLMRequest) -> LLMResult:
        self.requests.append(request)
        if self.scenario in {"provider_error", "unavailable"}:
            raise LLMProviderError("Mock LLM provider unavailable.")
        if self.scenario == "invalid":
            return LLMResult(
                reply="The mock provider returned an invalid candidate.",
                structured_output={"invalid": True},
                model_used=self.model_used,
            )

        context = request.trip_context
        destination = context.destination if context and context.destination else "Goa"
        duration = context.duration if context and context.duration else 2
        travellers = context.travellers if context and context.travellers else 2
        budget = context.budget.model_dump(mode="json") if context and context.budget else {
            "amount": 25000,
            "currency": "INR",
        }
        days = []
        for day_number in range(1, duration + 1):
            activities = [
                {
                    "time": "09:00",
                    "title": f"{destination} local discovery",
                    "description": "Explore a memorable local highlight at a comfortable pace.",
                    "location": destination,
                    "cost": {"amount": 0, "currency": budget["currency"]},
                    "location_type": "mixed",
                    "weather_sensitive": False,
                },
            ]
            if day_number <= 2:
                activities.append(
                    {
                        "time": "18:00",
                        "title": f"{destination} evening food experience",
                        "description": (
                            "Try a local dish and learn about the destination's food culture."
                        ),
                        "location": destination,
                        "cost": {"amount": 0, "currency": budget["currency"]},
                        "location_type": "indoor",
                        "weather_sensitive": False,
                    }
                )
            days.append({"day_number": day_number, "activities": activities})
        return LLMResult(
            reply=f"Here is a {duration}-day travel plan for {destination}.",
            structured_output={
                "destination": destination,
                "duration": duration,
                "budget": budget,
                "travellers": travellers,
                "days": days,
            },
            model_used=self.model_used,
        )
