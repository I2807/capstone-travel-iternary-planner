import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MessageList } from "../../src/components/MessageList";
import type { Message } from "../../src/types/domain";

const messages: Message[] = [
  {
    role: "user",
    content: "Plan Goa",
    timestamp: "2026-09-11T10:00:00Z",
  },
  {
    role: "assistant",
    content: "I can help plan that trip.",
    timestamp: "2026-09-11T10:00:01Z",
  },
];

describe("MessageList", () => {
  it("renders user and assistant messages with accessible labels", () => {
    render(<MessageList messages={messages} />);

    expect(screen.getByText("Plan Goa")).toBeVisible();
    expect(screen.getByText("I can help plan that trip.")).toBeVisible();
    expect(screen.getByLabelText("User message")).toBeVisible();
    expect(screen.getByLabelText("Assistant message")).toBeVisible();
  });

  it("shows travel suggestions when the conversation is empty", () => {
    render(<MessageList messages={[]} suggestedPrompts={["Plan a Goa trip"]} />);

    expect(screen.getByRole("button", { name: "Plan a Goa trip" })).toBeVisible();
  });
});
