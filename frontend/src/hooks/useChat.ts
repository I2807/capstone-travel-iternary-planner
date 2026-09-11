import { useState } from "react";
import { ApiError, sendChat } from "../api/client";
import type { ChatRequest } from "../types/api";
import type { Itinerary, Message, TripContext } from "../types/domain";
import { useSessionStorage } from "./useSessionStorage";

interface ChatErrorState {
  message: string;
  requestId: string | null;
  code: string;
}

interface FailedRequest {
  request: ChatRequest;
  messages: Message[];
}

export interface ChatState {
  messages: Message[];
  tripContext: TripContext | null;
  itinerary: Itinerary | null;
  isLoading: boolean;
  error: ChatErrorState | null;
  canRetry: boolean;
  sendMessage: (content: string) => Promise<void>;
  retry: () => Promise<void>;
  newChat: () => void;
}

export function useChat(): ChatState {
  const {
    messages,
    tripContext,
    setMessages,
    setTripContext,
    clearSession,
  } = useSessionStorage();
  const [itinerary, setItinerary] = useState<Itinerary | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<ChatErrorState | null>(null);
  const [failedRequest, setFailedRequest] = useState<FailedRequest | null>(null);

  const submitRequest = async (request: ChatRequest, baseMessages: Message[]) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await sendChat(request);
      const assistantMessage: Message = {
        role: "assistant",
        content: response.reply,
        timestamp: new Date().toISOString(),
      };
      setMessages([...baseMessages, assistantMessage]);
      setTripContext(response.trip_context ?? request.trip_context);
      setItinerary(response.itinerary);
      setFailedRequest(null);
    } catch (caughtError) {
      const apiError = caughtError instanceof ApiError ? caughtError : null;
      setError({
        message: apiError?.message || "Unable to complete the travel request.",
        requestId: apiError?.requestId ?? null,
        code: apiError?.code || "UNKNOWN_ERROR",
      });
      setFailedRequest({ request, messages: baseMessages });
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async (content: string) => {
    const normalizedContent = content.trim();
    if (!normalizedContent || isLoading) {
      return;
    }

    const userMessage: Message = {
      role: "user",
      content: normalizedContent,
      timestamp: new Date().toISOString(),
    };
    const nextMessages = [...messages, userMessage].slice(-50);
    const request: ChatRequest = {
      message: normalizedContent,
      history: nextMessages,
      trip_context: tripContext,
      itinerary,
    };
    setMessages(nextMessages);
    await submitRequest(request, nextMessages);
  };

  const retry = async () => {
    if (!failedRequest || isLoading) {
      return;
    }
    await submitRequest(failedRequest.request, failedRequest.messages);
  };

  const newChat = () => {
    clearSession();
    setItinerary(null);
    setError(null);
    setFailedRequest(null);
  };

  return {
    messages,
    tripContext,
    itinerary,
    isLoading,
    error,
    canRetry: failedRequest !== null,
    sendMessage,
    retry,
    newChat,
  };
}
