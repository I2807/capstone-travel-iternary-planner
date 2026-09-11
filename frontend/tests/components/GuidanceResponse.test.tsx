import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MessageList } from "../../src/components/MessageList";
import { StatusBanner } from "../../src/components/StatusBanner";

describe("GuidanceResponse", () => {
  it("renders guidance beside the conversation with accessible status support", () => {
    render(
      <>
        <MessageList
          messages={[
            {
              role: "assistant",
              content: "In Goa, try local seafood and seasonal vegetarian thalis.",
              timestamp: "2026-09-11T10:00:00Z",
            },
          ]}
        />
        <StatusBanner message="Guidance ready" />
      </>,
    );

    expect(screen.getByText(/local seafood/)).toBeVisible();
    expect(screen.getByRole("status", { name: "" })).toHaveTextContent("Guidance ready");
  });
});
