from __future__ import annotations

import json
from typing import Any

import httpx

from app.config import Settings
from app.llm.interface import LLMProviderError, LLMRequest, LLMResult
from app.llm.prompts import build_prompt


class GoogleLLMClient:
    def __init__(
        self,
        *,
        settings: Settings,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = settings
        self.http_client = http_client

    async def generate(self, request: LLMRequest) -> LLMResult:
        if self.settings.google_api_key is None:
            raise LLMProviderError("Google LLM provider is not configured.")

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.settings.model_name}:generateContent"
        )
        payload = {
            "contents": [{"role": "user", "parts": [{"text": build_prompt(request)}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "maxOutputTokens": 2048,
                "temperature": 0.2,
            },
        }
        headers = {"x-goog-api-key": self.settings.google_api_key.get_secret_value()}

        try:
            response = await self._post(url, payload, headers)
            if response.status_code >= 400:
                raise LLMProviderError("Google LLM request failed safely.")
            response_data = response.json()
            text = self._extract_text(response_data)
            structured_output = json.loads(text) if request.output_shape else None
        except (httpx.HTTPError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise LLMProviderError("Google LLM request failed safely.") from exc

        return LLMResult(
            reply=text if structured_output is None else "Here is your travel response.",
            structured_output=structured_output,
            model_used=self.settings.model_name,
        )

    async def _post(
        self,
        url: str,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> httpx.Response:
        if self.http_client is not None:
            return await self.http_client.post(url, json=payload, headers=headers)
        async with httpx.AsyncClient(timeout=self.settings.api_timeout_seconds) as client:
            return await client.post(url, json=payload, headers=headers)

    @staticmethod
    def _extract_text(response_data: dict[str, Any]) -> str:
        candidates = response_data["candidates"]
        parts = candidates[0]["content"]["parts"]
        text = parts[0]["text"]
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Google LLM returned no text.")
        return text.strip()
