from fastapi.testclient import TestClient

from app.dependencies import get_weather_service
from app.schemas.itinerary import Activity, DayPlan, Itinerary
from app.schemas.message import Money
from app.schemas.weather import WeatherData, WeatherQuery


class UnavailableWeatherService:
    async def get_weather(self, query: WeatherQuery) -> WeatherData:
        return WeatherData(source="unavailable", outdoor_risk="unknown")


def itinerary_payload() -> dict[str, object]:
    return Itinerary(
        destination="Goa",
        duration=1,
        budget=Money(amount=1000, currency="INR"),
        travellers=2,
        days=[
            DayPlan(
                day_number=1,
                activities=[
                    Activity(
                        time="09:00",
                        title="Beach walk",
                        description="Walk the coast.",
                        location="Goa",
                        cost=Money(amount=200, currency="INR"),
                        location_type="outdoor",
                        weather_sensitive=True,
                    )
                ],
            )
        ],
    ).model_dump(mode="json")


def request(message: str) -> dict[str, object]:
    return {
        "message": message,
        "history": [
            {"role": "user", "content": message, "timestamp": "2026-09-11T10:00:00Z"}
        ],
        "trip_context": {
            "destination": "Goa",
            "duration": 1,
            "budget": {"amount": 1000, "currency": "INR"},
            "travellers": 2,
            "interests": [],
        },
        "itinerary": itinerary_payload(),
    }


def test_mock_rain_replans_affected_activity(api_client: TestClient) -> None:
    response = api_client.post("/api/chat", json=request("It will rain. Replan Day 1."))
    payload = response.json()

    assert response.status_code == 200
    assert payload["weather_source"] == "mock"
    assert payload["changes"]
    assert payload["itinerary"]["days"][0]["activities"][0]["location_type"] == "indoor"


def test_unavailable_live_weather_preserves_itinerary(api_client: TestClient) -> None:
    api_client.app.dependency_overrides[get_weather_service] = lambda: UnavailableWeatherService()
    response = api_client.post("/api/chat", json=request("It will rain. Replan Day 1."))
    payload = response.json()

    assert response.status_code == 200
    assert payload["weather_source"] == "unavailable"
    assert payload["changes"] == []
    assert "verified" in payload["reply"].lower() or "unavailable" in payload["reply"].lower()
    assert "forecast" not in payload["reply"].lower()
