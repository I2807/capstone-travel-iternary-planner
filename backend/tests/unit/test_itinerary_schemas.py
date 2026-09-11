import pytest
from pydantic import ValidationError

from app.schemas.itinerary import Activity, DayPlan, Itinerary, ItineraryChange
from app.schemas.message import Money
from app.schemas.weather import WeatherData, WeatherQuery


def make_activity(cost: float = 100) -> Activity:
    return Activity(
        time="09:00",
        title="Beach walk",
        description="A relaxed morning walk.",
        location="Baga Beach",
        cost=Money(amount=cost, currency="INR"),
        location_type="outdoor",
        weather_sensitive=True,
    )


def test_weather_data_distinguishes_provider_source() -> None:
    weather = WeatherData(
        condition="Rain",
        outdoor_risk="high",
        source="mock",
    )

    assert weather.source == "mock"
    assert weather.outdoor_risk == "high"


def test_weather_query_requires_destination_and_positive_travellers() -> None:
    with pytest.raises(ValidationError):
        WeatherQuery(destination="Goa", travellers=0)


def test_empty_day_requires_an_explanation() -> None:
    with pytest.raises(ValidationError):
        DayPlan(day_number=1)


def test_itinerary_requires_ordered_days_and_respects_budget() -> None:
    itinerary = Itinerary(
        destination="Goa",
        duration=2,
        budget=Money(amount=250, currency="INR"),
        travellers=2,
        days=[
            DayPlan(day_number=1, activities=[make_activity(100)]),
            DayPlan(day_number=2, activities=[make_activity(150)]),
        ],
    )

    assert [day.day_number for day in itinerary.days] == [1, 2]

    with pytest.raises(ValidationError):
        Itinerary(
            destination="Goa",
            duration=2,
            budget=Money(amount=100, currency="INR"),
            travellers=2,
            days=[
                DayPlan(day_number=1, activities=[make_activity(100)]),
                DayPlan(day_number=2, activities=[make_activity(150)]),
            ],
        )


def test_itinerary_change_requires_weather_source() -> None:
    change = ItineraryChange(
        day_number=2,
        original_activity="Beach walk",
        replacement_activity="Museum visit",
        reason="Rain risk is high.",
        weather_source="mock",
    )

    assert change.replacement_activity == "Museum visit"
