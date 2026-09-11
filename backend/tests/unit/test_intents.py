from app.planner.intents import classify_intent, merge_trip_context
from app.schemas.message import Money
from app.schemas.trip import TripContext


def test_intent_classification_supports_planning_and_greetings() -> None:
    assert classify_intent("Hi") == "greeting"
    assert classify_intent("Plan a Goa trip") == "plan"
    assert classify_intent("What should I pack for Goa?") == "guide"
    assert classify_intent("Write Python code") == "guardrail"


def test_merge_context_preserves_existing_values() -> None:
    merged = merge_trip_context(
        TripContext(destination="Goa", duration=4, budget=Money(amount=25000, currency="INR")),
        TripContext(travellers=2, interests=["food"]),
    )

    assert merged.destination == "Goa"
    assert merged.duration == 4
    assert merged.travellers == 2
    assert merged.interests == ["food"]
