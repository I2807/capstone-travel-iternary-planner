from __future__ import annotations

import logging as stdlib_logging

LOGGER_NAME = "voyager"


def configure_logging(level: str) -> None:
    normalized_level = getattr(stdlib_logging, level.upper(), stdlib_logging.INFO)
    stdlib_logging.basicConfig(
        level=normalized_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def get_logger(name: str | None = None) -> stdlib_logging.Logger:
    return stdlib_logging.getLogger(name or LOGGER_NAME)


def log_provider_event(
    logger: stdlib_logging.Logger,
    *,
    event: str,
    request_id: str,
    provider: str,
    outcome: str,
) -> None:
    logger.info(
        "provider_event=%s request_id=%s provider=%s outcome=%s",
        event,
        request_id,
        provider,
        outcome,
    )
