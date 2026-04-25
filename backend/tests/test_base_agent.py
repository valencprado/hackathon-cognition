"""Tests for the BaseAgent class and helper functions."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from agents.base import BaseAgent, _sanitize_json, MAX_RETRIES


class TestSanitizeJson:
    def test_plain_json(self):
        assert _sanitize_json('{"a": 1}') == '{"a": 1}'

    def test_strips_json_fence(self):
        assert _sanitize_json('```json\n{"a": 1}\n```') == '{"a": 1}'

    def test_strips_plain_fence(self):
        assert _sanitize_json('```\n{"a": 1}\n```') == '{"a": 1}'

    def test_strips_whitespace(self):
        assert _sanitize_json('  {"a": 1}  ') == '{"a": 1}'

    def test_trailing_fence_only(self):
        assert _sanitize_json('{"a": 1}```') == '{"a": 1}'


class TestBaseAgent:
    def _make_agent(self, response_text: str = '{"ok": true}') -> BaseAgent:
        mock_client = MagicMock()
        resp = MagicMock()
        resp.text = response_text
        mock_client.models.generate_content.return_value = resp
        agent = BaseAgent(client=mock_client)
        return agent

    def test_run_returns_parsed_json(self):
        agent = self._make_agent('{"ok": true}')
        assert agent.run("test") == {"ok": True}

    def test_run_with_json_fence(self):
        agent = self._make_agent('```json\n{"ok": true}\n```')
        assert agent.run("test") == {"ok": True}

    def test_temperature_default(self):
        assert BaseAgent.temperature == 0.3

    def test_custom_temperature(self):
        class CustomAgent(BaseAgent):
            temperature = 0.9
        assert CustomAgent.temperature == 0.9

    def test_response_mime_type_set(self):
        mock_client = MagicMock()
        resp = MagicMock()
        resp.text = '{"ok": true}'
        mock_client.models.generate_content.return_value = resp
        agent = BaseAgent(client=mock_client)
        agent.run("test")
        call_kwargs = mock_client.models.generate_content.call_args
        cfg = call_kwargs.kwargs["config"]
        assert cfg.response_mime_type == "application/json"

    def test_retry_on_failure(self):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = [
            Exception("fail"),
            MagicMock(text='{"ok": true}'),
        ]
        agent = BaseAgent(client=mock_client)
        result = agent.run("test")
        assert result == {"ok": True}
        assert mock_client.models.generate_content.call_count == 2

    def test_retry_exhausted_raises(self):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("fail")
        agent = BaseAgent(client=mock_client)
        with pytest.raises(Exception, match="fail"):
            agent.run("test")
        assert mock_client.models.generate_content.call_count == MAX_RETRIES

    def test_empty_response_raises(self):
        mock_client = MagicMock()
        resp = MagicMock()
        resp.text = ""
        mock_client.models.generate_content.return_value = resp
        agent = BaseAgent(client=mock_client)
        with pytest.raises(Exception):
            agent.run("test")
