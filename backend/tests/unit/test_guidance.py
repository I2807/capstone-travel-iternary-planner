import pytest

from app.planner.guidance import provide_guidance
from app.schemas.trip import TripContext


@pytest.mark.parametrize(
    ("message", "keyword"),
    [
        ("What should I pack?", "pack"),
        ("What should I see there?", "explore"),
        ("What local food should I try?", "food"),
        ("How should I get around?", "transport"),
        ("Is Goa suitable for children?", "family"),
    ],
)
def test_guidance_categories_are_destination_aware(message: str, keyword: str) -> None:
    reply = provide_guidance(message, TripContext(destination="Goa", interests=[]))

    assert "Goa" in reply
    assert keyword in reply.lower()


def test_guidance_without_destination_asks_only_for_destination() -> None:
    reply = provide_guidance("What should I pack?", TripContext(interests=[]))

    assert "destination" in reply.lower()
    assert "itinerary" not in reply.lower()
