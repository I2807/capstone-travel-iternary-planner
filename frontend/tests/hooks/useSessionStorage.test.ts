import { act, renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { useSessionStorage } from "../../src/hooks/useSessionStorage";
import type { Message } from "../../src/types/domain";

function message(index: number): Message {
  return {
    role: "user",
    content: `Message ${index}`,
    timestamp: `2026-09-11T10:${String(index % 60).padStart(2, "0")}:00Z`,
  };
}

describe("useSessionStorage", () => {
  it("hydrates messages and trip context after refresh", () => {
    window.sessionStorage.setItem("voyager.messages", JSON.stringify([message(1)]));
    window.sessionStorage.setItem(
      "voyager.trip_context",
      JSON.stringify({ destination: "Goa", duration: 4, travellers: 2, interests: ["food"] }),
    );

    const { result } = renderHook(() => useSessionStorage());

    expect(result.current.messages).toHaveLength(1);
    expect(result.current.messages[0].content).toBe("Message 1");
    expect(result.current.tripContext?.destination).toBe("Goa");
  });

  it("recovers safely from malformed stored JSON", () => {
    window.sessionStorage.setItem("voyager.messages", "not-json");
    window.sessionStorage.setItem("voyager.trip_context", "[invalid-context]");

    const { result } = renderHook(() => useSessionStorage());

    expect(result.current.messages).toEqual([]);
    expect(result.current.tripContext).toBeNull();
  });

  it("keeps only the latest fifty messages", () => {
    const { result } = renderHook(() => useSessionStorage());

    act(() => {
      result.current.setMessages(Array.from({ length: 55 }, (_, index) => message(index)));
    });

    expect(result.current.messages).toHaveLength(50);
    expect(result.current.messages[0].content).toBe("Message 5");
    expect(result.current.messages[49].content).toBe("Message 54");
  });

  it("clears messages, context, and persisted values for New Chat", () => {
    const { result } = renderHook(() => useSessionStorage());

    act(() => {
      result.current.setMessages([message(1)]);
      result.current.setTripContext({ destination: "Goa", interests: [] });
    });
    act(() => {
      result.current.clearSession();
    });

    expect(result.current.messages).toEqual([]);
    expect(result.current.tripContext).toBeNull();
    expect(window.sessionStorage.getItem("voyager.messages")).toBeNull();
    expect(window.sessionStorage.getItem("voyager.trip_context")).toBeNull();
  });
});
