import type { ChatRequest, ChatResponse, ErrorEnvelope } from "../types/api";

const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
const normalizedApiOrigin = configuredApiBaseUrl?.replace(/\/$/, "");
const apiBaseUrl = normalizedApiOrigin
  ? normalizedApiOrigin.endsWith("/api")
    ? normalizedApiOrigin
    : `${normalizedApiOrigin}/api`
  : "/api";

export class ApiError extends Error {
  readonly code: ErrorEnvelope["error"]["code"] | "UNKNOWN_ERROR";
  readonly requestId: string | null;
  readonly status: number;

  constructor(
    message: string,
    options: { code: ApiError["code"]; requestId: string | null; status: number },
  ) {
    super(message);
    this.name = "ApiError";
    this.code = options.code;
    this.requestId = options.requestId;
    this.status = options.status;
  }
}

function getRequestId(response: Response): string | null {
  return response.headers.get("X-Request-ID");
}

export async function sendChat(request: ChatRequest): Promise<ChatResponse> {
  let response: Response;

  try {
    response = await fetch(`${apiBaseUrl}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });
  } catch {
    throw new ApiError("Unable to reach the travel planning service.", {
      code: "UNKNOWN_ERROR",
      requestId: null,
      status: 0,
    });
  }

  const requestId = getRequestId(response);
  const payload: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    const errorPayload = payload as Partial<ErrorEnvelope> | null;
    throw new ApiError(
      errorPayload?.error?.message || "The travel planning service returned an error.",
      {
        code: errorPayload?.error?.code || "UNKNOWN_ERROR",
        requestId: errorPayload?.request_id || requestId,
        status: response.status,
      },
    );
  }

  const chatResponse = payload as Partial<ChatResponse> | null;
  if (!chatResponse?.reply || !chatResponse.request_id) {
    throw new ApiError("The travel planning service returned an invalid response.", {
      code: "UNKNOWN_ERROR",
      requestId,
      status: response.status,
    });
  }

  return chatResponse as ChatResponse;
}
