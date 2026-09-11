from app.planner.replanning import replan_itinerary
from app.schemas.itinerary import Activity, DayPlan, Itinerary
from app.schemas.message import Money
from app.schemas.weather import WeatherData


def make_itinerary() -> Itinerary:
    return Itinerary(
        destination="Goa",
        duration=2,
        budget=Money(amount=1000, currency="INR"),
        travellers=2,
        days=[
            DayPlan(
                day_number=1,
                activities=[
                    Activity(
                        time="09:00",
                        title="Beach walk",
                        description="Walk the coast.",
                        location="Goa",
                        cost=Money(amount=200, currency="INR"),
                        location_type="outdoor",
                        weather_sensitive=True,
                    ),
                    Activity(
                        time="18:00",
                        title="Cooking class",
                        description="Learn local recipes.",
                        location="Goa",
                        cost=Money(amount=150, currency="INR"),
                        location_type="indoor",
                        weather_sensitive=False,
                    ),
                ],
            ),
            DayPlan(
                day_number=2,
                activities=[
                    Activity(
                        time="10:00",
                        title="Museum visit",
                        description="Explore local history.",
                        location="Goa",
                        cost=Money(amount=100, currency="INR"),
                        location_type="indoor",
                        weather_sensitive=False,
                    )
                ],
            ),
        ],
    )


def test_rain_replaces_only_affected_day_activities() -> None:
    original = make_itinerary()
    replanned, changes = replan_itinerary(
        original,
        WeatherData(condition="Rain", outdoor_risk="high", source="mock"),
        day_number=1,
    )

    assert replanned.days[0].activities[0].location_type == "indoor"
    assert replanned.days[0].activities[1] == original.days[0].activities[1]
    assert replanned.days[1] == original.days[1]
    assert len(changes) == 1
    assert changes[0].weather_source == "mock"
    assert changes[0].replacement_activity


def test_safe_or_unavailable_weather_preserves_itinerary() -> None:
    original = make_itinerary()
    for weather in (
        WeatherData(condition="Clear", outdoor_risk="low", source="mock"),
        WeatherData(condition=None, outdoor_risk="unknown", source="unavailable"),
    ):
        replanned, changes = replan_itinerary(original, weather, day_number=1)
        assert replanned == original
        assert changes == []
