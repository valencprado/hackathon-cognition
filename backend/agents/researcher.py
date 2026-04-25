"""Researcher Agent — searches for books based on subjects and format filters."""

from __future__ import annotations

from typing import Any

from agents.base import BaseAgent


class ResearcherAgent(BaseAgent):
    """Takes subjects and format filters, returns five candidate books."""

    system_prompt = (
        "You are the Researcher Agent for a university library chatbot.\n"
        "Given a set of subjects and format filters (e.g. books, comics/HQs, journals),\n"
        "recommend exactly 5 real books that best cover those subjects.\n"
        "Respect the format filters: only suggest items that match the selected formats.\n"
        "For each book provide: title, author, year, and format.\n\n"
        "RETURN ONLY JSON in this exact format:\n"
        '{"books": [\n'
        '  {"title": "...", "author": "...", "year": 2020, "format": "book"},\n'
        "  ...\n"
        "]}\n"
    )

    def run(self, subjects: list[str], formats: list[str]) -> dict[str, list[dict[str, Any]]]:
        prompt = (
            f"Subjects: {', '.join(subjects)}\n"
            f"Allowed formats: {', '.join(formats)}\n"
            "Recommend exactly 5 items matching the subjects and formats."
        )
        raw = self._call_model(prompt)
        return self._parse_response(raw)

    def _parse_response(self, raw: str) -> dict[str, list[dict[str, Any]]]:
        data: dict[str, Any] = super()._parse_response(raw)
        books = data.get("books", [])
        if not isinstance(books, list) or len(books) == 0:
            raise ValueError("Researcher Agent must return at least one book")
        required_keys = {"title", "author", "year", "format"}
        for book in books:
            missing = required_keys - set(book.keys())
            if missing:
                raise ValueError(f"Book missing keys: {missing}")
        return {"books": books}
