from app.llm.prompts import TRAVEL_SYSTEM_PROMPT
from app.planner.intents import classify_intent


def test_unrelated_and_mixed_requests_stay_outside_planner_scope() -> None:
    assert classify_intent("Write Python code") == "guardrail"
    assert classify_intent("Solve this math problem for my Goa trip") == "guardrail"
    assert classify_intent("Hi") == "greeting"
    assert classify_intent("Make Day 2 cheaper", has_itinerary=True) == "modify"


def test_guardrail_prompt_keeps_responses_travel_focused() -> None:
    assert "travel-focused" in TRAVEL_SYSTEM_PROMPT
    assert "redirect unrelated" in TRAVEL_SYSTEM_PROMPT
