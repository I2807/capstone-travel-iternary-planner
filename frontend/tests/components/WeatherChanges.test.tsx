import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ItineraryView } from "../../src/components/ItineraryView";

const itinerary = {
  destination: "Goa",
  duration: 1,
  budget: { amount: 1000, currency: "INR" },
  travellers: 2,
  days: [
    {
      day_number: 1,
      activities: [
        {
          time: "09:00",
          title: "Indoor market",
          description: "Browse local crafts.",
          location: "Goa",
          cost: { amount: 200, currency: "INR" },
          location_type: "indoor" as const,
          weather_sensitive: false,
        },
        {
          time: "18:00",
          title: "Cooking class",
          description: "Learn local recipes.",
          location: "Goa",
          cost: { amount: 150, currency: "INR" },
          location_type: "indoor" as const,
          weather_sensitive: false,
        },
      ],
    },
  ],
};

describe("WeatherChanges", () => {
  it("announces replacement, preserved activity, reason, and source", () => {
    render(
      <ItineraryView
        itinerary={itinerary}
        weatherSource="mock"
        changes={[
          {
            day_number: 1,
            original_activity: "Beach walk",
            replacement_activity: "Indoor market",
            reason: "Rain risk was high, so the beach walk was replaced.",
            weather_source: "mock",
          },
        ]}
      />,
    );

    expect(screen.getByText("Indoor market")).toBeVisible();
    expect(screen.getByText("Cooking class")).toBeVisible();
    expect(screen.getByText(/Rain risk was high/)).toBeVisible();
    expect(screen.getByRole("status")).toHaveTextContent("Weather source: mock");
    expect(screen.getByRole("heading", { name: "What changed" })).toBeVisible();
  });
});
