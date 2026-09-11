from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.itinerary import Activity
from app.schemas.message import Message, Money
from app.schemas.requests import ChatRequest
from app.schemas.trip import TripContext


def user_message(content: str) -> Message:
    return Message(role="user", content=content, timestamp=datetime.now(UTC))


def test_message_boundaries_reject_empty_and_overlong_values() -> None:
    with pytest.raises(ValidationError):
        Message(role="user", content="")
    with pytest.raises(ValidationError):
        Message(role="user", content="x" * 4001)


def test_history_boundaries_reject_empty_and_more_than_fifty_messages() -> None:
    with pytest.raises(ValidationError):
        ChatRequest(history=[])
    with pytest.raises(ValidationError):
        ChatRequest(history=[user_message(str(index)) for index in range(51)])


@pytest.mark.parametrize(
    "context",
    [
        {"duration": 0},
        {"travellers": 0},
        {"budget": {"amount": 0, "currency": "INR"}},
    ],
)
def test_trip_boundaries_reject_non_positive_values(context: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        TripContext.model_validate(context)


def test_activity_boundaries_reject_missing_or_blank_required_fields() -> None:
    with pytest.raises(ValidationError):
        Activity(
            time="09:00",
            title=" ",
            description="Description",
            location="Goa",
            cost=Money(amount=10, currency="INR"),
            location_type="outdoor",
            weather_sensitive=True,
        )


def test_partial_trip_context_is_valid_during_clarification() -> None:
    context = TripContext(destination="Goa", interests=["food"])

    assert context.destination == "Goa"
    assert context.duration is None
    assert context.budget is None
