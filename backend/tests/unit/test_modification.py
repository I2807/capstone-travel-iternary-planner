from app.planner.modification import modify_itinerary
from app.schemas.itinerary import Activity, DayPlan, Itinerary
from app.schemas.message import Money


def activity(title: str, cost: float, location_type: str = "outdoor") -> Activity:
    return Activity(
        time="09:00",
        title=title,
        description=f"Experience {title}.",
        location="Goa",
        cost=Money(amount=cost, currency="INR"),
        location_type=location_type,
        weather_sensitive=location_type == "outdoor",
    )


def itinerary() -> Itinerary:
    return Itinerary(
        destination="Goa",
        duration=3,
        budget=Money(amount=1000, currency="INR"),
        travellers=2,
        days=[
            DayPlan(day_number=1, activities=[activity("Old Quarter", 100)]),
            DayPlan(
                day_number=2,
                activities=[activity("Beach walk", 200), activity("Museum visit", 300, "indoor")],
            ),
            DayPlan(day_number=3, activities=[activity("Market", 100)]),
        ],
    )


def test_less_busy_targets_one_day_and_preserves_other_days() -> None:
    original = itinerary()
    updated, explanation, changes = modify_itinerary(original, "Make Day 2 less busy")

    assert len(updated.days[1].activities) == 1
    assert updated.days[0] == original.days[0]
    assert updated.days[2] == original.days[2]
    assert "Day 2" in explanation
    assert changes[0].day_number == 2


def test_add_food_experience_preserves_unaffected_days() -> None:
    original = itinerary()
    updated, _, _ = modify_itinerary(original, "Add local food experiences")

    assert any("food" in activity.title.lower() for activity in updated.days[0].activities)
    assert updated.days[1:] == original.days[1:]


def test_remove_museums_and_reduce_cost() -> None:
    original = itinerary()
    removed, _, _ = modify_itinerary(original, "Remove museums")
    cheaper, _, _ = modify_itinerary(original, "Make it cheaper")

    assert all(
        "museum" not in activity.title.lower()
        for day in removed.days
        for activity in day.activities
    )
    assert sum(activity.cost.amount for day in cheaper.days for activity in day.activities) < sum(
        activity.cost.amount for day in original.days for activity in day.activities
    )


def test_family_friendly_request_adds_appropriate_activity() -> None:
    updated, explanation, _ = modify_itinerary(itinerary(), "Add family-friendly options")

    assert any("family" in activity.title.lower() for activity in updated.days[0].activities)
    assert "family" in explanation.lower()
