from fastapi.testclient import TestClient


def canonical_request() -> dict[str, object]:
    message = {
        "role": "user",
        "content": "Plan a 4-day Goa trip for two people under INR 25000",
        "timestamp": "2026-09-11T10:00:00Z",
    }
    return {
        "message": message["content"],
        "history": [message],
        "trip_context": None,
    }


def test_canonical_chat_request_returns_validated_itinerary(api_client: TestClient) -> None:
    response = api_client.post("/api/chat", json=canonical_request())
    payload = response.json()

    assert response.status_code == 200
    assert payload["itinerary"]["destination"] == "Goa"
    assert payload["itinerary"]["duration"] == 4
    assert len(payload["itinerary"]["days"]) == 4
    assert payload["request_id"] == response.headers["X-Request-ID"]
    assert payload["model_used"] == "mock-model"


def test_history_only_request_derives_current_message(api_client: TestClient) -> None:
    request = canonical_request()
    request.pop("message")

    response = api_client.post("/api/chat", json=request)

    assert response.status_code == 200
    assert response.json()["itinerary"]["destination"] == "Goa"


def test_chat_returns_focused_clarification_when_details_are_missing(
    api_client: TestClient,
) -> None:
    request = canonical_request()
    request["message"] = "Plan a Goa trip"
    request["history"][0]["content"] = "Plan a Goa trip"

    response = api_client.post("/api/chat", json=request)

    assert response.status_code == 200
    assert response.json()["itinerary"] is None
    assert "duration" in response.json()["reply"].lower()


def test_chat_validation_uses_documented_error_envelope(api_client: TestClient) -> None:
    response = api_client.post("/api/chat", json={"history": []})
    payload = response.json()

    assert response.status_code == 400
    assert payload["error"]["code"] == "INVALID_REQUEST"
    assert payload["request_id"] == response.headers["X-Request-ID"]
