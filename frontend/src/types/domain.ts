export type MessageRole = "user" | "assistant";

export interface Message {
  role: MessageRole;
  content: string;
  timestamp: string;
}

export interface Money {
  amount: number;
  currency: string;
}

export interface TripContext {
  destination?: string | null;
  duration?: number | null;
  budget?: Money | null;
  travellers?: number | null;
  interests: string[];
}

export type OutdoorRisk = "low" | "medium" | "high" | "unknown";
export type WeatherSource = "live" | "mock" | "unavailable";

export interface WeatherData {
  condition: string | null;
  temperature: number | null;
  outdoor_risk: OutdoorRisk;
  source: WeatherSource;
  forecast_date: string | null;
}

export type LocationType = "indoor" | "outdoor" | "mixed";

export interface Activity {
  time: string;
  title: string;
  description: string;
  location: string;
  cost: Money;
  location_type: LocationType;
  weather_sensitive: boolean;
}

export interface DayPlan {
  day_number: number;
  activities: Activity[];
  empty_reason?: string | null;
}

export interface Itinerary {
  destination: string;
  duration: number;
  budget: Money;
  travellers: number;
  days: DayPlan[];
}

export interface ItineraryChange {
  day_number: number;
  original_activity: string;
  replacement_activity: string | null;
  reason: string;
  weather_source: WeatherSource | "not_applicable";
}
