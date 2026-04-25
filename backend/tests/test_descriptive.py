"""Tests for the Descriptive Agent."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from agents.descriptive import DescriptiveAgent
from tests.conftest import SAMPLE_BOOKS_WITH_SYNOPSIS


MOCK_METADATA = {
    "isbn": "978-0132350884",
    "publisher": "Prentice Hall",
    "page_count": 464,
    "description": "A handbook of agile software craftsmanship.",
    "thumbnail": "http://books.google.com/thumb.jpg",
    "info_link": "http://books.google.com/info",
}


class TestDescriptiveAgent:
    @patch("agents.descriptive.fetch_google_books_metadata")
    def test_enriches_all_books(self, mock_fetch):
        mock_fetch.return_value = MOCK_METADATA
        agent = DescriptiveAgent(client=MagicMock())
        result = agent.run(SAMPLE_BOOKS_WITH_SYNOPSIS)

        assert len(result["books"]) == 5
        for book in result["books"]:
            assert book["isbn"] == "978-0132350884"
            assert book["publisher"] == "Prentice Hall"
            assert "synopsis" in book  # original fields preserved

    @patch("agents.descriptive.fetch_google_books_metadata")
    def test_handles_empty_metadata(self, mock_fetch):
        empty = {
            "isbn": None,
            "publisher": None,
            "page_count": None,
            "description": None,
            "thumbnail": None,
            "info_link": None,
        }
        mock_fetch.return_value = empty
        agent = DescriptiveAgent(client=MagicMock())
        result = agent.run(SAMPLE_BOOKS_WITH_SYNOPSIS[:1])

        assert result["books"][0]["isbn"] is None
        assert result["books"][0]["title"] == "Clean Code"

    @patch("agents.descriptive.fetch_google_books_metadata")
    def test_calls_fetch_for_each_book(self, mock_fetch):
        mock_fetch.return_value = MOCK_METADATA
        agent = DescriptiveAgent(client=MagicMock())
        agent.run(SAMPLE_BOOKS_WITH_SYNOPSIS[:3])

        assert mock_fetch.call_count == 3
