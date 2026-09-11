from datetime import UTC

import pytest
from pydantic import ValidationError

from app.schemas.message import Message, Money
from app.schemas.trip import TripContext


def test_message_normalizes_content_and_timestamp() -> None:
    message = Message(role="user", content="  Plan Goa  ", timestamp="2026-09-11T10:00:00")

    assert message.content == "Plan Goa"
    assert message.timestamp.tzinfo == UTC


def test_message_rejects_blank_and_overlong_content() -> None:
    with pytest.raises(ValidationError):
        Message(role="user", content="   ")
    with pytest.raises(ValidationError):
        Message(role="user", content="a" * 4001)


def test_money_normalizes_currency_and_allows_zero_activity_cost() -> None:
    money = Money(amount=0, currency=" inr ")

    assert money.amount == 0
    assert money.currency == "INR"


def test_trip_context_allows_partial_values_and_normalizes_interests() -> None:
    context = TripContext(destination=" Goa ", interests=["food", " food ", " "])

    assert context.destination == "Goa"
    assert context.interests == ["food"]


def test_trip_context_rejects_non_positive_constraints() -> None:
    with pytest.raises(ValidationError):
        TripContext(duration=0)
    with pytest.raises(ValidationError):
        TripContext(travellers=-1)
    with pytest.raises(ValidationError):
        TripContext(budget=Money(amount=0, currency="INR"))
