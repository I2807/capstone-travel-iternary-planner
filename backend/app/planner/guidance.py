from __future__ import annotations

import re

from app.schemas.trip import TripContext


def provide_guidance(message: str, context: TripContext) -> str:
    destination = context.destination or _destination_from_message(message)
    if not destination:
        return "Which destination should I tailor this guidance to?"

    normalized = message.lower()
    if "pack" in normalized:
        return (
            f"For {destination}, pack breathable layers, comfortable walking shoes, "
            "sun protection, "
            "and one light rain layer."
        )
    if "food" in normalized or "eat" in normalized:
        return (
            f"In {destination}, look for a local food market, a regional thali, "
            "and one small family-run "
            "restaurant away from the busiest tourist streets."
        )
    if "transport" in normalized or "get around" in normalized:
        return (
            f"For transport in {destination}, combine short walks with local taxis "
            "or public transit, "
            "and confirm late-evening availability before heading out."
        )
    if "family" in normalized or "children" in normalized or "kids" in normalized:
        return (
            f"{destination} can work well for families when you keep daily travel short, "
            "add regular breaks, "
            "and choose flexible activities with nearby indoor options."
        )
    return (
        f"For {destination}, start with one signature neighborhood, one local food stop, "
        "and one slower "
        "experience so the trip has room to breathe."
    )


def _destination_from_message(message: str) -> str | None:
    match = re.search(r"\b(?:in|to|for)\s+([A-Z][A-Za-z-]*)\b", message)
    return match.group(1) if match else None
