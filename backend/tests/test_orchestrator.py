"""Tests for the Orchestrator pipeline."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from pipeline.orchestrator import Orchestrator
from tests.conftest import SAMPLE_BOOKS, SAMPLE_BOOKS_WITH_SYNOPSIS, SAMPLE_SUBJECTS


MOCK_METADATA = {
    "isbn": "978-0132350884",
    "publisher": "Prentice Hall",
    "page_count": 464,
    "description": "Description.",
    "thumbnail": "http://thumb.jpg",
    "info_link": "http://info",
}


class TestOrchestrator:
    @patch("agents.descriptive.fetch_google_books_metadata")
    def test_full_pipeline(self, mock_fetch):
        mock_fetch.return_value = MOCK_METADATA

        mock_client = MagicMock()
        responses = [
            json.dumps({"subjects": SAMPLE_SUBJECTS}),
            json.dumps({"books": SAMPLE_BOOKS}),
            json.dumps({"books": SAMPLE_BOOKS_WITH_SYNOPSIS}),
        ]
        call_count = {"n": 0}

        def side_effect(*args, **kwargs):
            resp = MagicMock()
            resp.text = responses[call_count["n"]]
            call_count["n"] += 1
            return resp

        mock_client.models.generate_content.side_effect = side_effect

        orch = Orchestrator(client=mock_client)
        result = orch.run("I want to learn software engineering", ["book"])

        assert "subjects" in result
        assert len(result["subjects"]) == 4
        assert "books" in result
        assert len(result["books"]) <= 3
        assert result["books"][0]["isbn"] == "978-0132350884"

    @patch("agents.descriptive.fetch_google_books_metadata")
    def test_returns_max_three_books(self, mock_fetch):
        mock_fetch.return_value = MOCK_METADATA

        mock_client = MagicMock()
        responses = [
            json.dumps({"subjects": SAMPLE_SUBJECTS}),
            json.dumps({"books": SAMPLE_BOOKS}),
            json.dumps({"books": SAMPLE_BOOKS_WITH_SYNOPSIS}),
        ]
        call_count = {"n": 0}

        def side_effect(*args, **kwargs):
            resp = MagicMock()
            resp.text = responses[call_count["n"]]
            call_count["n"] += 1
            return resp

        mock_client.models.generate_content.side_effect = side_effect

        orch = Orchestrator(client=mock_client)
        result = orch.run("query", ["book"])

        assert len(result["books"]) == 3

    def test_orchestrator_creates_agents(self):
        mock_client = MagicMock()
        orch = Orchestrator(client=mock_client)

        assert orch.professor.client is mock_client
        assert orch.researcher.client is mock_client
        assert orch.educator.client is mock_client
        assert orch.descriptive.client is mock_client
