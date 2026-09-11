from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.itinerary import Itinerary
from app.schemas.message import Message
from app.schemas.trip import TripContext
from app.schemas.weather import WeatherData

LLMTask = Literal["plan", "modify", "guide", "replan", "guardrail", "greeting"]


class LLMRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    task: LLMTask
    message: str = Field(min_length=1, max_length=4000)
    history: list[Message] = Field(max_length=50)
    trip_context: TripContext | None = None
    itinerary: Itinerary | None = None
    weather: WeatherData | None = None
    output_shape: str | None = None


class LLMResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    reply: str = Field(min_length=1)
    structured_output: dict[str, object] | None = None
    model_used: str = Field(min_length=1)
    attempt: Literal["primary", "fallback"] = "primary"


class LLMProviderError(RuntimeError):
    """A provider could not produce a result."""


class InvalidLLMOutputError(LLMProviderError):
    """A provider returned output that does not match the requested shape."""


class LLMClient(Protocol):
    async def generate(self, request: LLMRequest) -> LLMResult:
        """Generate a typed result for a planning task."""
