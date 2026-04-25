"""Tests for the Flask application endpoints."""

from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

import pytest

from tests.conftest import SAMPLE_TOPICOS, SAMPLE_ANALISE, SAMPLE_TOP5


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        rv = client.get("/health")
        assert rv.status_code == 200
        assert rv.get_json() == {"status": "ok"}


class TestSearchEndpoint:
    def test_empty_query_returns_400(self, client):
        rv = client.post("/search", json={"query": ""})
        assert rv.status_code == 400
        assert rv.get_json()["error"] == "Query is required"

    def test_whitespace_query_returns_400(self, client):
        rv = client.post("/search", json={"query": "   "})
        assert rv.status_code == 400

    def test_no_body_returns_400(self, client):
        rv = client.post("/search", content_type="application/json", data="{}")
        assert rv.status_code == 400

    @patch("app.Orchestrator")
    def test_success(self, mock_orch_cls, client):
        mock_orch = MagicMock()
        mock_orch.run.return_value = {
            "topicos": SAMPLE_TOPICOS,
            "analise": SAMPLE_ANALISE,
            "books": SAMPLE_TOP5[:3],
        }
        mock_orch_cls.return_value = mock_orch

        rv = client.post("/search", json={"query": "IA"})
        assert rv.status_code == 200
        data = rv.get_json()
        assert data["topicos"] == SAMPLE_TOPICOS
        assert len(data["books"]) == 3

    @patch("app.Orchestrator")
    def test_default_formats(self, mock_orch_cls, client):
        mock_orch = MagicMock()
        mock_orch.run.return_value = {"topicos": [], "analise": "", "books": []}
        mock_orch_cls.return_value = mock_orch

        client.post("/search", json={"query": "test"})
        mock_orch.run.assert_called_once_with("test", ["livro", "revista", "hq"])

    @patch("app.Orchestrator")
    def test_custom_formats(self, mock_orch_cls, client):
        mock_orch = MagicMock()
        mock_orch.run.return_value = {"topicos": [], "analise": "", "books": []}
        mock_orch_cls.return_value = mock_orch

        client.post("/search", json={"query": "test", "formats": ["livro", "hq"]})
        mock_orch.run.assert_called_once_with("test", ["livro", "hq"])

    @patch("app.Orchestrator")
    def test_orchestrator_error(self, mock_orch_cls, client):
        mock_orch = MagicMock()
        mock_orch.run.side_effect = RuntimeError("API down")
        mock_orch_cls.return_value = mock_orch

        rv = client.post("/search", json={"query": "test"})
        assert rv.status_code == 500
        assert "API down" in rv.get_json()["error"]
