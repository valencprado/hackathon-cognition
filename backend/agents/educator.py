"""Educator Agent — generates a short synopsis for each candidate book."""

from __future__ import annotations

import json
from typing import Any

from agents.base import BaseAgent


class EducatorAgent(BaseAgent):
    """Creates a short synopsis for each candidate book."""

    system_prompt = (
        "You are the Educator Agent for a university library chatbot.\n"
        "Given a list of books (title, author, year, format), write a short synopsis\n"
        "(2-3 sentences) for each book explaining why it is useful for the student.\n\n"
        "RETURN ONLY JSON in this exact format:\n"
        '{"books": [\n'
        '  {"title": "...", "author": "...", "year": 2020, "format": "book", '
        '"synopsis": "A 2-3 sentence synopsis..."},\n'
        "  ...\n"
        "]}\n"
    )

    def run(self, books: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        prompt = (
            "Write a short synopsis for each of the following books:\n"
            f"{json.dumps(books, ensure_ascii=False)}"
        )
        raw = self._call_model(prompt)
        return self._parse_response(raw)

    def _parse_response(self, raw: str) -> dict[str, list[dict[str, Any]]]:
        data: dict[str, Any] = super()._parse_response(raw)
        books = data.get("books", [])
        if not isinstance(books, list) or len(books) == 0:
            raise ValueError("Educator Agent must return at least one book")
        for book in books:
            if "synopsis" not in book:
                raise ValueError(f"Book '{book.get('title', '?')}' missing synopsis")
        return {"books": books}
