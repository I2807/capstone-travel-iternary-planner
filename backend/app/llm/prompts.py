from app.llm.interface import LLMRequest

TRAVEL_SYSTEM_PROMPT = """
You are Voyager AI, a travel-focused conversational assistant.
Stay within travel planning and travel guidance. Handle greetings warmly and redirect unrelated
requests toward travel help. Never perform unrelated tasks.

For itinerary tasks, return only a JSON object matching the requested itinerary shape. Include a
complete day-by-day plan with time, title, description, location, cost amount and currency,
location_type, and weather_sensitive for every activity. Respect destination, duration, budget,
traveller count, and interests. Ask a focused clarification only for required missing information.
Preserve unaffected itinerary sections when modifying a plan.

Never invent live weather. Use only supplied weather data and identify whether it is live, mock, or
unavailable. When weather causes a replacement, explain every change and preserve unaffected
activities.
""".strip()


TASK_INSTRUCTIONS = {
    "plan": "Create or complete a new travel itinerary.",
    "modify": "Modify only the requested itinerary scope and explain what changed.",
    "guide": "Give concise, destination-aware travel guidance without changing the itinerary.",
    "replan": "Replan weather-sensitive activities while preserving unaffected activities.",
    "guardrail": "Politely redirect the request toward travel assistance.",
    "greeting": "Welcome the traveler and offer practical travel-planning help.",
}


def build_prompt(request: LLMRequest) -> str:
    context = request.trip_context.model_dump(mode="json") if request.trip_context else None
    itinerary = request.itinerary.model_dump(mode="json") if request.itinerary else None
    weather = request.weather.model_dump(mode="json") if request.weather else None
    return "\n\n".join(
        (
            TRAVEL_SYSTEM_PROMPT,
            f"Task: {TASK_INSTRUCTIONS[request.task]}",
            f"Current user message: {request.message}",
            f"Trip context: {context}",
            f"Existing itinerary: {itinerary}",
            f"Weather data: {weather}",
            f"Required output shape: {request.output_shape or 'reply text'}",
        )
    )
