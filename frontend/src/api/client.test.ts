import { describe, expect, it, vi } from "vitest";
import { sendChat } from "./client";

const request = {
  message: "Plan Goa",
  history: [
    {
      role: "user" as const,
      content: "Plan Goa",
      timestamp: "2026-09-11T10:00:00Z",
    },
  ],
  trip_context: null,
};

describe("sendChat", () => {
  it("sends the canonical request and parses the typed response", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          reply: "Here is your plan.",
          itinerary: null,
          request_id: "request-1",
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json", "X-Request-ID": "request-1" },
        },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(sendChat(request)).resolves.toMatchObject({ request_id: "request-1" });
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/chat"),
      expect.objectContaining({ method: "POST", body: JSON.stringify(request) }),
    );
  });

  it("parses the documented error envelope and request ID", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            error: { code: "INVALID_REQUEST", message: "Check your input." },
            request_id: "request-2",
          }),
          {
            status: 400,
            headers: { "Content-Type": "application/json", "X-Request-ID": "request-2" },
          },
        ),
      ),
    );

    await expect(sendChat(request)).rejects.toMatchObject({
      code: "INVALID_REQUEST",
      requestId: "request-2",
      status: 400,
      message: "Check your input.",
    });
  });
});
