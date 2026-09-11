from __future__ import annotations

from app.errors import AppError
from app.schemas.itinerary import Activity, Itinerary, ItineraryChange
from app.schemas.message import Money
from app.schemas.weather import WeatherData


def replan_itinerary(
    itinerary: Itinerary,
    weather: WeatherData,
    *,
    day_number: int,
    interests: list[str] | None = None,
) -> tuple[Itinerary, list[ItineraryChange]]:
    if weather.source == "unavailable" or weather.outdoor_risk != "high":
        return itinerary, []

    days = [day.model_copy(deep=True) for day in itinerary.days]
    day = next((candidate for candidate in days if candidate.day_number == day_number), None)
    if day is None:
        raise AppError.create("INVALID_REQUEST", f"Day {day_number} is not in the itinerary.")

    changes: list[ItineraryChange] = []
    for index, activity in enumerate(day.activities):
        if not activity.weather_sensitive or activity.location_type == "indoor":
            continue
        replacement = _indoor_alternative(activity, itinerary, interests or [])
        day.activities[index] = replacement
        changes.append(
            ItineraryChange(
                day_number=day_number,
                original_activity=activity.title,
                replacement_activity=replacement.title,
                reason=(
                    f"Rain risk was high, so {activity.title} was replaced with "
                    f"{replacement.title}."
                ),
                weather_source=weather.source,
            )
        )

    if not changes:
        return itinerary, []
    updated = Itinerary.model_validate(itinerary.model_copy(update={"days": days}).model_dump())
    return updated, changes


def _indoor_alternative(
    activity: Activity,
    itinerary: Itinerary,
    interests: list[str],
) -> Activity:
    if any("food" in interest.lower() for interest in interests):
        title = "Local food hall"
        description = "Taste local dishes indoors while the weather is unsettled."
    else:
        title = f"Indoor alternative to {activity.title}"
        description = "Explore a comfortable indoor experience while the weather is unsettled."
    return activity.model_copy(
        update={
            "title": title,
            "description": description,
            "cost": Money(
                amount=activity.cost.amount,
                currency=itinerary.budget.currency,
            ),
            "location_type": "indoor",
            "weather_sensitive": False,
        }
    )
