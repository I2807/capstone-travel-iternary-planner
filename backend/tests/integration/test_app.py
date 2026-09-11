from fastapi.testclient import TestClient

from app.config import Settings
from app.errors import AppError
from app.main import create_app


def test_health_and_error_responses_carry_matching_request_ids() -> None:
    app = create_app(Settings())
    client = TestClient(app)

    health_response = client.get("/api/health")
    health_payload = health_response.json()
    assert health_response.status_code == 200
    assert health_response.headers["X-Request-ID"] == health_payload["request_id"]
    assert health_payload["status"] == "ok"
    assert health_payload["llm_provider"] == "mock"
    assert health_payload["weather_provider"] == "mock"

    @app.get("/api/test-error")
    def raise_test_error() -> None:
        raise AppError.create("PROVIDER_UNAVAILABLE", "Try again.")

    error_response = client.get("/api/test-error")
    error_payload = error_response.json()
    assert error_response.status_code == 503
    assert error_response.headers["X-Request-ID"] == error_payload["request_id"]
    assert error_payload["error"]["code"] == "PROVIDER_UNAVAILABLE"
