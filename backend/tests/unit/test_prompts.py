from app.llm.interface import LLMRequest
from app.llm.prompts import TRAVEL_SYSTEM_PROMPT, build_prompt


def test_prompt_requires_travel_scope_structured_output_and_grounded_weather() -> None:
    request = LLMRequest(task="plan", message="Plan Goa", history=[])
    prompt = build_prompt(request)

    assert "travel-focused" in TRAVEL_SYSTEM_PROMPT
    assert "JSON object" in prompt
    assert "weather_sensitive" in prompt
    assert "Never invent live weather" in prompt
    assert "Current user message: Plan Goa" in prompt
