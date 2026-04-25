"""Base agent class following the BookMatch pipeline architecture."""

from __future__ import annotations

import json
import logging
from typing import Any

from google import genai

import config

logger = logging.getLogger(__name__)

MAX_RETRIES = 2


def _get_client() -> genai.Client:
    return genai.Client(api_key=config.GEMINI_API_KEY)


def _sanitize_json(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```json"):
        text = text[len("```json"):]
    elif text.startswith("```"):
        text = text[len("```"):]
    if text.endswith("```"):
        text = text[: -len("```")]
    return text.strip()


class BaseAgent:
    """Abstract base for every AI agent in the pipeline.

    Sub-classes must set ``system_prompt`` and may override ``temperature``.
    """

    system_prompt: str = ""
    temperature: float = 0.3

    def __init__(self, client: genai.Client | None = None) -> None:
        self.client = client or _get_client()

    def _call_model(self, user_prompt: str) -> str:
        response = self.client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=user_prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                temperature=self.temperature,
                response_mime_type="application/json",
            ),
        )
        return response.text or ""

    def _parse_response(self, raw: str) -> Any:
        return json.loads(_sanitize_json(raw))

    def run(self, user_prompt: str) -> Any:
        last_error: Exception | None = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                raw = self._call_model(user_prompt)
                return self._parse_response(raw)
            except Exception as exc:
                logger.warning("Attempt %d failed: %s", attempt, exc)
                last_error = exc
        raise last_error  # type: ignore[misc]
