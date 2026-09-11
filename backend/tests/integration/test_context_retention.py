from fastapi.testclient import TestClient


def test_explicit_trip_context_drives_follow_up_without_repeating_destination(
    api_client: TestClient,
) -> None:
    request = {
        "message": "Make it cheaper",
        "history": [
            {
                "role": "user",
                "content": "Make it cheaper",
                "timestamp": "2026-09-11T10:00:00Z",
            }
        ],
        "trip_context": {
            "destination": "Goa",
            "duration": 2,
            "budget": {"amount": 1000, "currency": "INR"},
            "travellers": 2,
            "interests": [],
        },
    }

    response = api_client.post("/api/chat", json=request)

    assert response.status_code == 200
    assert response.json()["trip_context"]["destination"] == "Goa"


def test_history_only_request_uses_final_user_message(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/chat",
        json={
            "history": [
                {
                    "role": "assistant",
                    "content": "Where would you like to go?",
                    "timestamp": "2026-09-11T09:59:00Z",
                },
                {
                    "role": "user",
                    "content": "Plan a 2-day Goa trip for two people under INR 1000",
                    "timestamp": "2026-09-11T10:00:00Z",
                },
            ]
        },
    )

    assert response.status_code == 200
    assert response.json()["itinerary"]["destination"] == "Goa"


def test_invalid_context_bounds_use_invalid_request_envelope(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/chat",
        json={
            "message": "Plan a trip",
            "history": [
                {
                    "role": "user",
                    "content": "Plan a trip",
                    "timestamp": "2026-09-11T10:00:00Z",
                }
            ],
            "trip_context": {"duration": 0},
        },
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_REQUEST"
