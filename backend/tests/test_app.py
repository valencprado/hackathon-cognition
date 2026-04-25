"""Tests for the Flask application endpoints."""

from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

from tests.conftest import SAMPLE_SUBJECTS, SAMPLE_BOOKS_WITH_SYNOPSIS


MOCK_METADATA = {
    "isbn": "978-0132350884",
    "publisher": "Prentice Hall",
    "page_count": 464,
    "description": "Description.",
    "thumbnail": "http://thumb.jpg",
    "info_link": "http://info",
}


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.get_json() == {"status": "ok"}


class TestSearchEndpoint:
    def test_missing_query_returns_400(self, client):
        resp = client.post("/search", json={})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_empty_query_returns_400(self, client):
        resp = client.post("/search", json={"query": "   "})
        assert resp.status_code == 400

    def test_no_body_returns_400(self, client):
        resp = client.post("/search", content_type="application/json", data="")
        assert resp.status_code == 400

    @patch("app.Orchestrator")
    def test_successful_search(self, MockOrch, client):
        mock_instance = MagicMock()
        mock_instance.run.return_value = {
            "subjects": SAMPLE_SUBJECTS,
            "books": SAMPLE_BOOKS_WITH_SYNOPSIS[:3],
        }
        MockOrch.return_value = mock_instance

        resp = client.post("/search", json={"query": "software engineering"})
        assert resp.status_code == 200

        data = resp.get_json()
        assert len(data["subjects"]) == 4
        assert len(data["books"]) == 3

    @patch("app.Orchestrator")
    def test_search_with_formats(self, MockOrch, client):
        mock_instance = MagicMock()
        mock_instance.run.return_value = {
            "subjects": SAMPLE_SUBJECTS,
            "books": SAMPLE_BOOKS_WITH_SYNOPSIS[:3],
        }
        MockOrch.return_value = mock_instance

        resp = client.post(
            "/search",
            json={"query": "AI", "formats": ["journal", "comic"]},
        )
        assert resp.status_code == 200
        mock_instance.run.assert_called_once_with("AI", ["journal", "comic"])

    @patch("app.Orchestrator")
    def test_search_exception_returns_500(self, MockOrch, client):
        mock_instance = MagicMock()
        mock_instance.run.side_effect = RuntimeError("boom")
        MockOrch.return_value = mock_instance

        resp = client.post("/search", json={"query": "test"})
        assert resp.status_code == 500
        assert "boom" in resp.get_json()["error"]

    @patch("app.Orchestrator")
    def test_default_formats_used(self, MockOrch, client):
        mock_instance = MagicMock()
        mock_instance.run.return_value = {
            "subjects": SAMPLE_SUBJECTS,
            "books": [],
        }
        MockOrch.return_value = mock_instance

        client.post("/search", json={"query": "test"})
        mock_instance.run.assert_called_once_with("test", ["book", "journal", "comic"])
