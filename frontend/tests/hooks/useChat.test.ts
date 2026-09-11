import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError, sendChat } from "../../src/api/client";
import { useChat } from "../../src/hooks/useChat";

vi.mock("../../src/api/client", async () => {
  const actual = await vi.importActual<typeof import("../../src/api/client")>(
    "../../src/api/client",
  );
  return {
    ...actual,
    sendChat: vi.fn(),
  };
});

const sendChatMock = vi.mocked(sendChat);

beforeEach(() => {
  sendChatMock.mockReset();
});

describe("useChat", () => {
  it("sends a user message, appends the assistant reply, and stores context", async () => {
    sendChatMock.mockResolvedValue({
      reply: "Here is your Goa plan.",
      itinerary: null,
      request_id: "request-1",
      trip_context: { destination: "Goa", interests: [] },
    });
    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage("Plan Goa");
    });

    expect(sendChatMock).toHaveBeenCalledWith(
      expect.objectContaining({ message: "Plan Goa", history: expect.any(Array) }),
    );
    expect(result.current.messages.map((message) => message.role)).toEqual([
      "user",
      "assistant",
    ]);
    expect(result.current.tripContext?.destination).toBe("Goa");
    expect(result.current.error).toBeNull();
  });

  it("retries a failed request without duplicating the user message", async () => {
    sendChatMock
      .mockRejectedValueOnce(new ApiError("Try again.", { code: "PROVIDER_UNAVAILABLE", requestId: "request-2", status: 503 }))
      .mockResolvedValueOnce({
        reply: "Recovered plan.",
        itinerary: null,
        request_id: "request-3",
      });
    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage("Plan Goa");
    });
    expect(result.current.messages).toHaveLength(1);
    expect(result.current.canRetry).toBe(true);

    await act(async () => {
      await result.current.retry();
    });

    expect(sendChatMock).toHaveBeenCalledTimes(2);
    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[0].role).toBe("user");
    expect(result.current.messages[1].content).toBe("Recovered plan.");
    expect(result.current.canRetry).toBe(false);
  });
});
