from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.schemas.message import Message
from app.schemas.requests import ChatRequest
from app.schemas.responses import ChatResponse, ErrorEnvelope, HealthStatus


def message(content: str, role: str = "user") -> Message:
    return Message(role=role, content=content, timestamp=datetime.now(UTC))


def test_chat_request_derives_history_only_message() -> None:
    request = ChatRequest(history=[message("Plan Goa")])

    assert request.current_message == "Plan Goa"


def test_chat_request_requires_matching_final_user_message() -> None:
    with pytest.raises(ValidationError):
        ChatRequest(message="Plan Kerala", history=[message("Plan Goa")])
    with pytest.raises(ValidationError):
        ChatRequest(history=[message("assistant reply", role="assistant")])


def test_chat_request_enforces_history_bounds() -> None:
    history = [message(f"Message {index}") for index in range(51)]

    with pytest.raises(ValidationError):
        ChatRequest(history=history)


def test_response_envelopes_preserve_request_metadata() -> None:
    response = ChatResponse(reply="Welcome to Voyager.", request_id="request-1")
    error = ErrorEnvelope(
        error={"code": "INVALID_REQUEST", "message": "Check your input."},
        request_id="request-1",
    )
    health = HealthStatus(
        status="ok",
        model="mock-model",
        llm_provider="mock",
        weather_provider="mock",
        llm_configured=True,
        request_id="request-1",
    )

    assert response.request_id == error.request_id == "request-1"
    assert health.weather_provider == "mock"
