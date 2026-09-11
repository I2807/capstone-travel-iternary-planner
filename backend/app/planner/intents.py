from __future__ import annotations

import re
from typing import Literal

from app.schemas.message import Money
from app.schemas.trip import TripContext

IntentName = Literal["plan", "modify", "guide", "replan", "greeting", "guardrail"]

_CURRENCY_SYMBOLS = {"₹": "INR", "$": "USD", "€": "EUR", "£": "GBP"}
_NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
_STOP_INTERESTS = {"a", "an", "the", "trip", "travel", "holiday", "vacation"}
_UNRELATED_TERMS = ("code", "math problem", "homework", "essay", "debug", "javascript")


def extract_trip_context(message: str) -> TripContext:
    normalized = " ".join(message.strip().split())
    lower_message = normalized.lower()

    destination = _extract_destination(normalized)
    duration_match = re.search(r"\b(\d+)\s*[- ]?day(?:s)?\b", lower_message)
    travellers_match = re.search(
        r"\b(?:for|with)\s+(\d+|one|two|three|four|five)\s+"
        r"(?:people|person|travellers?|travelers?|adults?)\b",
        lower_message,
    )
    budget_match = re.search(
        r"\b(?:under|below|within)\s+(?:(inr|usd|eur|gbp|cad|aud|₹|\$|€|£)\s*)?([\d,]+(?:\.\d+)?)",
        lower_message,
    )

    budget = None
    if budget_match:
        raw_currency = budget_match.group(1) or "INR"
        currency = _CURRENCY_SYMBOLS.get(raw_currency, raw_currency.upper())
        budget = Money(amount=float(budget_match.group(2).replace(",", "")), currency=currency)

    interests = _extract_interests(normalized)
    return TripContext(
        destination=destination,
        duration=int(duration_match.group(1)) if duration_match else None,
        budget=budget,
        travellers=_parse_traveller_count(travellers_match.group(1)) if travellers_match else None,
        interests=interests,
    )


def merge_trip_context(existing: TripContext | None, extracted: TripContext) -> TripContext:
    if existing is None:
        return extracted
    return TripContext(
        destination=extracted.destination or existing.destination,
        duration=extracted.duration or existing.duration,
        budget=extracted.budget or existing.budget,
        travellers=extracted.travellers or existing.travellers,
        interests=list(dict.fromkeys([*existing.interests, *extracted.interests])),
    )


def missing_required_trip_details(context: TripContext) -> list[str]:
    missing: list[str] = []
    if not context.destination:
        missing.append("destination")
    if context.duration is None:
        missing.append("duration")
    if context.budget is None:
        missing.append("budget")
    if context.travellers is None:
        missing.append("traveller count")
    return missing


def classify_intent(message: str, *, has_itinerary: bool = False) -> IntentName:
    normalized = message.strip().lower()
    if any(term in normalized for term in _UNRELATED_TERMS):
        return "guardrail"
    if re.fullmatch(r"(?:hi|hello|hey|good morning|good afternoon|good evening)[!. ]*", normalized):
        return "greeting"
    if any(term in normalized for term in ("rain", "weather", "replan", "forecast")) and (
        has_itinerary or "day" in normalized
    ):
        return "replan"
    if has_itinerary and any(
        term in normalized
        for term in (
            "make it",
            "remove",
            "add ",
            "cheaper",
            "budget",
            "less busy",
            "family-friendly",
        )
    ):
        return "modify"
    if any(
        term in normalized
        for term in (
            "pack",
            "local food",
            "what food",
            "transport",
            "suitable for children",
            "family",
        )
    ):
        return "guide"
    if any(
        term in normalized
        for term in ("trip", "travel", "itinerary", "holiday", "vacation", "plan ", "visit ")
    ):
        return "plan"
    return "guardrail"


def _extract_destination(message: str) -> str | None:
    patterns = (
        r"\b\d+\s*[- ]?day(?:s)?\s+([A-Za-z][A-Za-z-]*)\s+trip\b",
        r"\b(?:a|an|the)\s+([A-Za-z][A-Za-z-]*)\s+trip\b",
        (
            r"\b(?:trip|travel|holiday|vacation)\s+(?:to|in)\s+"
            r"([A-Za-z][A-Za-z -]*?)(?=\s+(?:for|under|below|with|on)\b|[.,!?]|$)"
        ),
        (
            r"\b(?:to|in)\s+([A-Za-z][A-Za-z -]*?)"
            r"(?=\s+(?:for|under|below|with|on)\b|[.,!?]|$)"
        ),
    )
    for pattern in patterns:
        match = re.search(pattern, message, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip(" ,.-").title()
    return None


def _extract_interests(message: str) -> list[str]:
    match = re.search(r"\bwith\s+(.+?)(?:[.!?]|$)", message, flags=re.IGNORECASE)
    if not match:
        return []
    candidates = re.split(r",|\band\b|&", match.group(1), flags=re.IGNORECASE)
    return [
        candidate.strip().lower()
        for candidate in candidates
        if candidate.strip() and candidate.strip().lower() not in _STOP_INTERESTS
    ]


def _parse_traveller_count(value: str) -> int:
    if value in _NUMBER_WORDS:
        return _NUMBER_WORDS[value]
    return int(value)
