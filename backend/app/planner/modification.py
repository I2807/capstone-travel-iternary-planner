from __future__ import annotations

import re
from dataclasses import dataclass

from app.errors import AppError
from app.schemas.itinerary import Activity, Itinerary, ItineraryChange
from app.schemas.message import Money


@dataclass(slots=True)
class ModificationResult:
    itinerary: Itinerary
    reply: str
    changes: list[ItineraryChange]


def modify_itinerary(
    itinerary: Itinerary,
    message: str,
) -> tuple[Itinerary, str, list[ItineraryChange]]:
    normalized = message.strip().lower()
    days = [day.model_copy(deep=True) for day in itinerary.days]
    changes: list[ItineraryChange] = []
    target_day = _target_day(normalized)

    if (
        "less busy" in normalized
        or "less intense" in normalized
        or "reduce intensity" in normalized
    ):
        day = _get_day(days, target_day)
        if len(day.activities) > 1:
            removed = day.activities.pop()
            changes.append(
                _change(
                    day.day_number,
                    removed.title,
                    None,
                    f"Removed {removed.title} to make Day {day.day_number} less busy.",
                )
            )
        else:
            return itinerary, f"Day {day.day_number} is already lightly planned.", []
        reply = f"I made Day {day.day_number} less busy and kept the other days unchanged."
    elif "remove" in normalized and "museum" in normalized:
        removed_count = 0
        for day in days:
            retained: list[Activity] = []
            for activity in day.activities:
                if "museum" in f"{activity.title} {activity.description}".lower():
                    removed_count += 1
                    changes.append(
                        _change(
                            day.day_number,
                            activity.title,
                            None,
                            f"Removed {activity.title} at your request.",
                        )
                    )
                else:
                    retained.append(activity)
            day.activities = retained
            if not day.activities:
                day.empty_reason = "No museum activity remains after your update."
        reply = (
            "I removed the museum activities and preserved the rest of the itinerary."
            if removed_count
            else "There were no museum activities to remove."
        )
    elif "cheaper" in normalized or "reduce" in normalized and "budget" in normalized:
        candidate = _most_expensive(days)
        if candidate is None or candidate[1].cost.amount <= 0:
            raise AppError.create(
                "INVALID_REQUEST",
                "The current itinerary has no cost that can be reduced.",
            )
        day_number, activity_index = candidate[0], candidate[2]
        day = _get_day(days, day_number)
        activity = day.activities[activity_index]
        reduced_cost = round(activity.cost.amount * 0.5, 2)
        day.activities[activity_index] = activity.model_copy(
            update={"cost": Money(amount=reduced_cost, currency=activity.cost.currency)}
        )
        changes.append(
            _change(
                day_number,
                activity.title,
                activity.title,
                f"Reduced the estimate for {activity.title} to lower the trip cost.",
            )
        )
        reply = "I reduced the highest activity estimate and kept the rest of the itinerary intact."
    elif "family" in normalized:
        day = _get_day(days, target_day or 1)
        activity = Activity(
            time="15:00",
            title="Family-friendly local experience",
            description="A flexible, low-intensity activity suitable for different ages.",
            location=itinerary.destination,
            cost=Money(amount=0, currency=itinerary.budget.currency),
            location_type="mixed",
            weather_sensitive=False,
        )
        day.activities.append(activity)
        changes.append(
            _change(
                day.day_number,
                "Day schedule",
                activity.title,
                f"Added {activity.title.lower()} on Day {day.day_number}.",
            )
        )
        reply = "I added a family-friendly option and kept the existing activities."
    elif "food" in normalized:
        day = _get_day(days, target_day or 1)
        activity = Activity(
            time="19:00",
            title="Local food experience",
            description="Taste regional dishes with a local food-focused stop.",
            location=itinerary.destination,
            cost=Money(amount=0, currency=itinerary.budget.currency),
            location_type="indoor",
            weather_sensitive=False,
        )
        day.activities.append(activity)
        changes.append(
            _change(
                day.day_number,
                "Day schedule",
                activity.title,
                f"Added {activity.title.lower()} on Day {day.day_number}.",
            )
        )
        reply = "I added a local food experience and kept the other days unchanged."
    else:
        raise AppError.create(
            "INVALID_REQUEST",
            "Tell me which activity, day, budget, or travel style you would like to change.",
        )

    updated = Itinerary.model_validate(itinerary.model_copy(update={"days": days}).model_dump())
    return updated, reply, changes


def _target_day(message: str) -> int | None:
    match = re.search(r"\bday\s*(\d+)\b", message)
    return int(match.group(1)) if match else None


def _get_day(days: list, day_number: int | None):
    selected_day = day_number or 1
    for day in days:
        if day.day_number == selected_day:
            return day
    raise AppError.create("INVALID_REQUEST", f"Day {selected_day} is not in the itinerary.")


def _most_expensive(days: list) -> tuple[int, Activity, int] | None:
    candidate: tuple[int, Activity, int] | None = None
    for day in days:
        for index, activity in enumerate(day.activities):
            if candidate is None or activity.cost.amount > candidate[1].cost.amount:
                candidate = (day.day_number, activity, index)
    return candidate


def _change(
    day_number: int,
    original_activity: str,
    replacement_activity: str | None,
    reason: str,
) -> ItineraryChange:
    return ItineraryChange(
        day_number=day_number,
        original_activity=original_activity,
        replacement_activity=replacement_activity,
        reason=reason,
        weather_source="not_applicable",
    )
