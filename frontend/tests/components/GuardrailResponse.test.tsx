import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MessageList } from "../../src/components/MessageList";

describe("GuardrailResponse", () => {
  it("renders a redirect as safe assistant text without unsupported controls", () => {
    render(
      <MessageList
        messages={[
          {
            role: "assistant",
            content: "I can help with travel planning, destinations, and itineraries.",
            timestamp: "2026-09-11T10:00:00Z",
          },
        ]}
      />
    );

    expect(screen.getByText(/travel planning/)).toBeVisible();
    expect(screen.queryByRole("button", { name: /book|pay|code/i })).toBeNull();
  });
});
