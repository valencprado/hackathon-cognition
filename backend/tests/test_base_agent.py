"""Tests for the BaseAgent class."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from agents.base import BaseAgent, _sanitize_json


class TestSanitizeJson:
    def test_removes_json_fence(self):
        raw = '```json\n{"key": "value"}\n```'
        assert _sanitize_json(raw) == '{"key": "value"}'

    def test_removes_plain_fence(self):
        raw = '```\n{"key": "value"}\n```'
        assert _sanitize_json(raw) == '{"key": "value"}'

    def test_trims_whitespace(self):
        raw = '  \n {"key": "value"}  \n '
        assert _sanitize_json(raw) == '{"key": "value"}'

    def test_passthrough_clean_json(self):
        raw = '{"key": "value"}'
        assert _sanitize_json(raw) == '{"key": "value"}'


class TestBaseAgent:
    @patch("agents.base._get_client")
    def test_run_parses_json(self, mock_get_client):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps({"result": 42})
        mock_client.models.generate_content.return_value = mock_response

        agent = BaseAgent(client=mock_client)
        result = agent.run("test prompt")

        assert result == {"result": 42}
        mock_client.models.generate_content.assert_called_once()

    @patch("agents.base._get_client")
    def test_run_handles_fenced_json(self, mock_get_client):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '```json\n{"result": 42}\n```'
        mock_client.models.generate_content.return_value = mock_response

        agent = BaseAgent(client=mock_client)
        result = agent.run("test prompt")

        assert result == {"result": 42}

    @patch("agents.base._get_client")
    def test_run_raises_on_bad_json(self, mock_get_client):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "not json at all"
        mock_client.models.generate_content.return_value = mock_response

        agent = BaseAgent(client=mock_client)
        with pytest.raises(json.JSONDecodeError):
            agent.run("test prompt")

    @patch("agents.base._get_client")
    def test_call_model_handles_none_text(self, mock_get_client):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = None
        mock_client.models.generate_content.return_value = mock_response

        agent = BaseAgent(client=mock_client)
        with pytest.raises(Exception):
            agent.run("test prompt")

    @patch("agents.base._get_client")
    def test_default_client_used(self, mock_get_client):
        mock_get_client.return_value = MagicMock()
        agent = BaseAgent()
        assert agent.client is mock_get_client.return_value
