from fastapi.testclient import TestClient


def test_guidance_response_does_not_require_or_mutate_itinerary(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/chat",
        json={
            "message": "What local food should I try?",
            "history": [
                {
                    "role": "user",
                    "content": "What local food should I try?",
                    "timestamp": "2026-09-11T10:00:00Z",
                }
            ],
            "trip_context": {"destination": "Goa", "interests": []},
        },
    )

    assert response.status_code == 200
    assert response.json()["itinerary"] is None
    assert "Goa" in response.json()["reply"]
    assert response.json()["request_id"] == response.headers["X-Request-ID"]


def test_guidance_missing_destination_is_focused(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/chat",
        json={
            "message": "What should I pack?",
            "history": [
                {
                    "role": "user",
                    "content": "What should I pack?",
                    "timestamp": "2026-09-11T10:00:00Z",
                }
            ],
        },
    )

    assert response.status_code == 200
    assert response.json()["itinerary"] is None
    assert "destination" in response.json()["reply"].lower()
