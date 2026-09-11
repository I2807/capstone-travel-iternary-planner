from fastapi.testclient import TestClient


def test_unrelated_request_is_redirected_without_provider_call(
    api_client: TestClient,
    mock_llm_client,
) -> None:
    response = api_client.post(
        "/api/chat",
        json={
            "message": "Write Python code",
            "history": [
                {
                    "role": "user",
                    "content": "Write Python code",
                    "timestamp": "2026-09-11T10:00:00Z",
                }
            ],
        },
    )

    assert response.status_code == 200
    assert "travel" in response.json()["reply"].lower()
    assert response.json()["itinerary"] is None
    assert mock_llm_client.requests == []
    assert response.json()["request_id"] == response.headers["X-Request-ID"]
