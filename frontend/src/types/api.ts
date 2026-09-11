import type {
  Itinerary,
  ItineraryChange,
  Message,
  TripContext,
  WeatherSource,
} from "./domain";

export interface ChatRequest {
  message: string;
  history: Message[];
  trip_context: TripContext | null;
  itinerary?: import("./domain").Itinerary | null;
}

export interface ChatResponse {
  reply: string;
  itinerary: Itinerary | null;
  request_id: string;
  weather_source?: WeatherSource | null;
  model_used?: string | null;
  changes?: ItineraryChange[];
  trip_context?: TripContext | null;
}

export type ErrorCode =
  | "INVALID_REQUEST"
  | "PROVIDER_UNAVAILABLE"
  | "INVALID_PROVIDER_OUTPUT"
  | "INTERNAL_ERROR";

export interface ErrorEnvelope {
  error: {
    code: ErrorCode;
    message: string;
  };
  request_id: string;
}

export interface HealthStatus {
  status: string;
  model: string;
  llm_provider: "mock" | "google";
  weather_provider: string;
  llm_configured: boolean;
  request_id: string;
}
