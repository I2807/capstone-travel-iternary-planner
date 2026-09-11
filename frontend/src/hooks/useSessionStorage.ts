import { useCallback, useEffect, useRef, useState } from "react";
import type { Message, TripContext } from "../types/domain";

const MESSAGES_KEY = "voyager.messages";
const TRIP_CONTEXT_KEY = "voyager.trip_context";
const MAX_MESSAGES = 50;

function readStoredValue<T>(key: string, fallback: T, isValid: (value: unknown) => value is T): T {
  if (typeof window === "undefined") {
    return fallback;
  }

  try {
    const rawValue = window.sessionStorage.getItem(key);
    if (!rawValue) {
      return fallback;
    }
    const parsed: unknown = JSON.parse(rawValue);
    return isValid(parsed) ? parsed : fallback;
  } catch {
    return fallback;
  }
}

function isMessage(value: unknown): value is Message {
  if (!value || typeof value !== "object") {
    return false;
  }
  const message = value as Partial<Message>;
  return (
    (message.role === "user" || message.role === "assistant") &&
    typeof message.content === "string" &&
    message.content.trim().length > 0 &&
    message.content.length <= 4000 &&
    typeof message.timestamp === "string"
  );
}

function isMessages(value: unknown): value is Message[] {
  return Array.isArray(value) && value.every(isMessage);
}

function isTripContext(value: unknown): value is TripContext {
  if (!value || typeof value !== "object") {
    return false;
  }
  const context = value as Partial<TripContext>;
  if (context.destination !== undefined && context.destination !== null && typeof context.destination !== "string") {
    return false;
  }
  if (context.duration !== undefined && context.duration !== null && (!Number.isInteger(context.duration) || context.duration <= 0)) {
    return false;
  }
  if (context.travellers !== undefined && context.travellers !== null && (!Number.isInteger(context.travellers) || context.travellers <= 0)) {
    return false;
  }
  if (context.budget !== undefined && context.budget !== null) {
    if (
      typeof context.budget !== "object" ||
      typeof context.budget.amount !== "number" ||
      context.budget.amount <= 0 ||
      typeof context.budget.currency !== "string"
    ) {
      return false;
    }
  }
  return context.interests === undefined || Array.isArray(context.interests);
}

function writeStoredValue(key: string, value: unknown): void {
  if (typeof window === "undefined") {
    return;
  }

  try {
    window.sessionStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Session storage can be unavailable in privacy-restricted browser contexts.
  }
}

export interface SessionStorageState {
  messages: Message[];
  tripContext: TripContext | null;
  setMessages: (messages: Message[]) => void;
  setTripContext: (tripContext: TripContext | null) => void;
  clearSession: () => void;
}

export function useSessionStorage(): SessionStorageState {
  const [messages, setMessagesState] = useState<Message[]>(() =>
    readStoredValue<Message[]>(MESSAGES_KEY, [], isMessages).slice(-MAX_MESSAGES),
  );
  const [tripContext, setTripContextState] = useState<TripContext | null>(() =>
    readStoredValue<TripContext | null>(TRIP_CONTEXT_KEY, null, (value): value is TripContext | null =>
      value === null || isTripContext(value),
    ),
  );
  const skipPersistenceRef = useRef(false);

  useEffect(() => {
    if (skipPersistenceRef.current) {
      window.sessionStorage.removeItem(MESSAGES_KEY);
      return;
    }
    writeStoredValue(MESSAGES_KEY, messages.slice(-MAX_MESSAGES));
  }, [messages]);

  useEffect(() => {
    if (skipPersistenceRef.current) {
      window.sessionStorage.removeItem(TRIP_CONTEXT_KEY);
      return;
    }
    if (tripContext === null) {
      if (typeof window !== "undefined") {
        window.sessionStorage.removeItem(TRIP_CONTEXT_KEY);
      }
      return;
    }
    writeStoredValue(TRIP_CONTEXT_KEY, tripContext);
  }, [tripContext]);

  const setMessages = useCallback((nextMessages: Message[]) => {
    skipPersistenceRef.current = false;
    setMessagesState(nextMessages.slice(-MAX_MESSAGES));
  }, []);

  const setTripContext = useCallback((nextTripContext: TripContext | null) => {
    skipPersistenceRef.current = false;
    setTripContextState(nextTripContext);
  }, []);

  const clearSession = useCallback(() => {
    skipPersistenceRef.current = true;
    setMessagesState([]);
    setTripContextState(null);
    if (typeof window !== "undefined") {
      try {
        window.sessionStorage.removeItem(MESSAGES_KEY);
        window.sessionStorage.removeItem(TRIP_CONTEXT_KEY);
      } catch {
        // Session storage can be unavailable in privacy-restricted browser contexts.
      }
    }
  }, []);

  return { messages, tripContext, setMessages, setTripContext, clearSession };
}
