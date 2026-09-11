import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ItineraryView } from "../../src/components/ItineraryView";
import type { Itinerary } from "../../src/types/domain";

const itinerary: Itinerary = {
  destination: "Goa",
  duration: 2,
  budget: { amount: 1000, currency: "INR" },
  travellers: 2,
  days: [
    {
      day_number: 1,
      activities: [
        {
          time: "09:00",
          title: "Old Quarter",
          description: "Explore the old quarter.",
          location: "Goa",
          cost: { amount: 100, currency: "INR" },
          location_type: "outdoor",
          weather_sensitive: true,
        },
      ],
    },
    {
      day_number: 2,
      activities: [
        {
          time: "10:00",
          title: "Indoor market",
          description: "Browse local crafts.",
          location: "Goa",
          cost: { amount: 200, currency: "INR" },
          location_type: "indoor",
          weather_sensitive: false,
        },
      ],
    },
  ],
};

describe("ItineraryView", () => {
  it("renders changed and unchanged days with cost and classification", () => {
    render(
      <ItineraryView
        itinerary={itinerary}
        changes={[
          {
            day_number: 2,
            original_activity: "Beach walk",
            replacement_activity: "Indoor market",
            reason: "The plan was made less exposed to weather.",
            weather_source: "not_applicable",
          },
        ]}
      />,
    );

    expect(screen.getByRole("heading", { name: "Goa" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Day 1" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Day 2" })).toBeVisible();
    expect(screen.getByText("Old Quarter")).toBeVisible();
    expect(screen.getByText("Indoor market")).toBeVisible();
    expect(screen.getAllByText(/INR/).length).toBeGreaterThanOrEqual(3);
    expect(screen.getByText("indoor")).toBeVisible();
    expect(screen.getByText(/made less exposed/)).toBeVisible();
  });
});
