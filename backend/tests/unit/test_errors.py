import logging

from app.errors import AppError, create_request_id, safe_error_message
from app.logging import get_logger, log_provider_event


def test_app_error_has_stable_code_status_and_request_id() -> None:
    request_id = create_request_id()
    error = AppError.create("PROVIDER_UNAVAILABLE", "retry", request_id)

    assert len(request_id) == 32
    assert error.code == "PROVIDER_UNAVAILABLE"
    assert error.status_code == 503
    assert error.request_id == request_id
    assert str(error) == "retry"


def test_safe_error_messages_never_include_provider_details() -> None:
    message = safe_error_message("INVALID_PROVIDER_OUTPUT")

    assert "api" not in message.lower()
    assert "key" not in message.lower()


def test_provider_logging_emits_only_safe_fields(caplog) -> None:
    logger = get_logger("test-provider")

    with caplog.at_level(logging.INFO, logger="test-provider"):
        log_provider_event(
            logger,
            event="generation",
            request_id="request-123",
            provider="mock",
            outcome="success",
        )

    assert "request-123" in caplog.text
    assert "mock" in caplog.text
    assert "raw_payload" not in caplog.text
    assert "api_key" not in caplog.text
