from dataclasses import dataclass
from typing import Literal, Self
from uuid import uuid4

ErrorCode = Literal[
    "INVALID_REQUEST",
    "PROVIDER_UNAVAILABLE",
    "INVALID_PROVIDER_OUTPUT",
    "INTERNAL_ERROR",
]

ERROR_STATUS_CODES: dict[ErrorCode, int] = {
    "INVALID_REQUEST": 400,
    "PROVIDER_UNAVAILABLE": 503,
    "INVALID_PROVIDER_OUTPUT": 502,
    "INTERNAL_ERROR": 500,
}


@dataclass(slots=True)
class AppError(Exception):
    code: ErrorCode
    message: str
    status_code: int
    request_id: str | None = None

    def __post_init__(self) -> None:
        Exception.__init__(self, self.message)

    @classmethod
    def create(
        cls,
        code: ErrorCode,
        message: str,
        request_id: str | None = None,
    ) -> Self:
        return cls(code, message, ERROR_STATUS_CODES[code], request_id)

    def with_request_id(self, request_id: str) -> Self:
        self.request_id = request_id
        return self


def create_request_id() -> str:
    return uuid4().hex


def safe_error_message(code: ErrorCode) -> str:
    return {
        "INVALID_REQUEST": (
            "The request could not be accepted. Please check the details and try again."
        ),
        "PROVIDER_UNAVAILABLE": (
            "The travel planning service is temporarily unavailable. Please try again."
        ),
        "INVALID_PROVIDER_OUTPUT": (
            "The travel planning service returned an invalid plan. Please try again."
        ),
        "INTERNAL_ERROR": (
            "Something went wrong while preparing your travel response. Please try again."
        ),
    }[code]
