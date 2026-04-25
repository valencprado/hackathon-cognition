"""Tests for the Educator Agent."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from agents.educator import EducatorAgent
from tests.conftest import SAMPLE_TOP5, SAMPLE_RESUMOS


def _make_educator(response_text: str) -> EducatorAgent:
    mock_client = MagicMock()
    resp = MagicMock()
    resp.text = response_text
    mock_client.models.generate_content.return_value = resp
    return EducatorAgent(client=mock_client)


class TestEducatorAgent:
    def test_returns_resumos(self):
        raw = json.dumps({"resumos": SAMPLE_RESUMOS})
        agent = _make_educator(raw)
        result = agent.run("quero entender IA", SAMPLE_TOP5)
        assert len(result["resumos"]) == 5

    def test_rejects_empty_resumos(self):
        raw = json.dumps({"resumos": []})
        agent = _make_educator(raw)
        with pytest.raises(ValueError, match="at least one resumo"):
            agent.run("test", SAMPLE_TOP5)

    def test_rejects_missing_resumo_field(self):
        bad = [{"titulo": "X", "conexao_tema": "ok"}]
        raw = json.dumps({"resumos": bad})
        agent = _make_educator(raw)
        with pytest.raises(ValueError, match="missing resumo"):
            agent.run("test", SAMPLE_TOP5)

    def test_rejects_missing_conexao_tema(self):
        bad = [{"titulo": "X", "resumo": "ok"}]
        raw = json.dumps({"resumos": bad})
        agent = _make_educator(raw)
        with pytest.raises(ValueError, match="missing conexao_tema"):
            agent.run("test", SAMPLE_TOP5)

    def test_temperature(self):
        assert EducatorAgent.temperature == 0.5

    def test_query_in_prompt(self):
        raw = json.dumps({"resumos": SAMPLE_RESUMOS})
        agent = _make_educator(raw)
        agent.run("quero entender IA sem matemática", SAMPLE_TOP5)
        call_args = agent.client.models.generate_content.call_args
        prompt = call_args.kwargs["contents"]
        assert "quero entender IA sem matemática" in prompt
