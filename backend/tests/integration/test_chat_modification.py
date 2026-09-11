from fastapi.testclient import TestClient

from app.schemas.itinerary import Activity, DayPlan, Itinerary
from app.schemas.message import Money


def existing_itinerary() -> dict[str, object]:
    return Itinerary(
        destination="Goa",
        duration=3,
        budget=Money(amount=1000, currency="INR"),
        travellers=2,
        days=[
            DayPlan(
                day_number=1,
                activities=[
                    Activity(
                        time="09:00",
                        title="Old Quarter",
                        description="Explore the old quarter.",
                        location="Goa",
                        cost=Money(amount=100, currency="INR"),
                        location_type="outdoor",
                        weather_sensitive=True,
                    )
                ],
            ),
            DayPlan(
                day_number=2,
                activities=[
                    Activity(
                        time="09:00",
                        title="Beach walk",
                        description="Walk the beach.",
                        location="Goa",
                        cost=Money(amount=200, currency="INR"),
                        location_type="outdoor",
                        weather_sensitive=True,
                    ),
                    Activity(
                        time="18:00",
                        title="Museum visit",
                        description="Visit a museum.",
                        location="Goa",
                        cost=Money(amount=300, currency="INR"),
                        location_type="indoor",
                        weather_sensitive=False,
                    ),
                ],
            ),
            DayPlan(
                day_number=3,
                activities=[
                    Activity(
                        time="10:00",
                        title="Market",
                        description="Visit the market.",
                        location="Goa",
                        cost=Money(amount=100, currency="INR"),
                        location_type="outdoor",
                        weather_sensitive=True,
                    )
                ],
            ),
        ],
    ).model_dump(mode="json")


def test_modification_api_preserves_unaffected_days(
    api_client: TestClient,
) -> None:
    request = {
        "message": "Make Day 2 less busy",
        "history": [
            {
                "role": "user",
                "content": "Make Day 2 less busy",
                "timestamp": "2026-09-11T10:00:00Z",
            }
        ],
        "trip_context": {
            "destination": "Goa",
            "duration": 3,
            "budget": {"amount": 1000, "currency": "INR"},
            "travellers": 2,
            "interests": [],
        },
        "itinerary": existing_itinerary(),
    }

    response = api_client.post("/api/chat", json=request)
    payload = response.json()

    assert response.status_code == 200
    assert len(payload["itinerary"]["days"][1]["activities"]) == 1
    assert payload["itinerary"]["days"][0] == request["itinerary"]["days"][0]
    assert payload["itinerary"]["days"][2] == request["itinerary"]["days"][2]
    assert payload["changes"]
    assert "Day 2" in payload["reply"]
