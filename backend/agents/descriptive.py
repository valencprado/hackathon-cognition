"""Descriptive Agent — enriches books with metadata from external sources."""

from __future__ import annotations

from typing import Any

from agents.base import BaseAgent
from services.google_books import fetch_google_books_metadata


class DescriptiveAgent(BaseAgent):
    """Fetches additional metadata for each book from Google Books (and Amazon when available)."""

    system_prompt = ""  # Not used — this agent relies on API calls, not LLM.

    def run(self, books: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        enriched: list[dict[str, Any]] = []
        for book in books:
            metadata = fetch_google_books_metadata(
                title=book.get("title", ""),
                author=book.get("author", ""),
            )
            merged = {**book, **metadata}
            enriched.append(merged)
        return {"books": enriched}

    def _parse_response(self, raw: str) -> Any:
        raise NotImplementedError("DescriptiveAgent does not use LLM responses")
