"""Tests for the Educator Agent."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from agents.educator import EducatorAgent
from tests.conftest import SAMPLE_BOOKS, SAMPLE_BOOKS_WITH_SYNOPSIS


def _make_agent(response_text: str) -> EducatorAgent:
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = response_text
    mock_client.models.generate_content.return_value = mock_response
    return EducatorAgent(client=mock_client)


class TestEducatorAgent:
    def test_returns_books_with_synopsis(self):
        agent = _make_agent(json.dumps({"books": SAMPLE_BOOKS_WITH_SYNOPSIS}))
        result = agent.run(SAMPLE_BOOKS)
        assert len(result["books"]) == 5
        for book in result["books"]:
            assert "synopsis" in book

    def test_raises_on_missing_synopsis(self):
        books_no_synopsis = [{"title": "Test", "author": "A", "year": 2000, "format": "book"}]
        agent = _make_agent(json.dumps({"books": books_no_synopsis}))
        with pytest.raises(ValueError, match="missing synopsis"):
            agent.run(books_no_synopsis)

    def test_raises_on_empty_books(self):
        agent = _make_agent(json.dumps({"books": []}))
        with pytest.raises(ValueError, match="at least one book"):
            agent.run([])

    def test_prompt_includes_book_data(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps({"books": SAMPLE_BOOKS_WITH_SYNOPSIS})
        mock_client.models.generate_content.return_value = mock_response

        agent = EducatorAgent(client=mock_client)
        agent.run(SAMPLE_BOOKS)

        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs.get("contents") or call_args[1].get("contents", "")
        assert "Clean Code" in prompt

    def test_system_prompt_is_set(self):
        agent = EducatorAgent(client=MagicMock())
        assert "Educator Agent" in agent.system_prompt
