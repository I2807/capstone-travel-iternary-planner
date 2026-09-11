import pytest

from app.errors import AppError
from app.llm.mock import MockLLMClient
from app.planner.engine import PlannerEngine
from app.planner.intents import extract_trip_context
from app.schemas.message import Message
from app.schemas.trip import TripContext
from app.weather.mock import MockWeatherService


def test_extract_trip_context_from_natural_language() -> None:
    context = extract_trip_context(
        "Plan a 4-day Goa trip for two people under INR 25000 with food and beaches."
    )

    assert context.destination == "Goa"
    assert context.duration == 4
    assert context.travellers == 2
    assert context.budget is not None
    assert context.budget.amount == 25000
    assert context.budget.currency == "INR"
    assert {interest.lower() for interest in context.interests} >= {"food", "beaches"}


@pytest.mark.asyncio
async def test_engine_asks_only_for_required_missing_trip_details() -> None:
    engine = PlannerEngine(MockLLMClient(), MockWeatherService())

    result = await engine.handle(
        message="Plan a Goa trip",
        history=[Message(role="user", content="Plan a Goa trip")],
        trip_context=None,
    )

    assert result.itinerary is None
    assert "duration" in result.reply.lower()
    assert "budget" in result.reply.lower()
    assert "travell" in result.reply.lower()


@pytest.mark.asyncio
async def test_engine_generates_a_valid_itinerary_with_constraints() -> None:
    engine = PlannerEngine(MockLLMClient(), MockWeatherService())
    context = TripContext(
        destination="Goa",
        duration=4,
        travellers=2,
        budget={"amount": 25000, "currency": "INR"},
        interests=["food"],
    )

    result = await engine.handle(
        message="Plan it",
        history=[Message(role="user", content="Plan it")],
        trip_context=context,
    )

    assert result.itinerary is not None
    assert result.itinerary.destination == "Goa"
    assert result.itinerary.duration == 4
    assert result.itinerary.travellers == 2
    assert len(result.itinerary.days) == 4
    assert result.model_used == "mock-model"


@pytest.mark.asyncio
async def test_invalid_provider_output_becomes_stable_error() -> None:
    engine = PlannerEngine(MockLLMClient(scenario="invalid"), MockWeatherService())
    context = TripContext(
        destination="Goa",
        duration=2,
        travellers=2,
        budget={"amount": 25000, "currency": "INR"},
    )

    with pytest.raises(AppError) as error:
        await engine.handle(
            message="Plan it",
            history=[Message(role="user", content="Plan it")],
            trip_context=context,
        )

    assert error.value.code == "INVALID_PROVIDER_OUTPUT"
