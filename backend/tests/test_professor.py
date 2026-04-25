"""Tests for the Professor Agent."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from agents.professor import ProfessorAgent
from tests.conftest import SAMPLE_TOPICOS, SAMPLE_ANALISE


def _make_professor(response_text: str) -> ProfessorAgent:
    mock_client = MagicMock()
    resp = MagicMock()
    resp.text = response_text
    mock_client.models.generate_content.return_value = resp
    return ProfessorAgent(client=mock_client)


class TestProfessorAgent:
    def test_returns_topicos_and_analise(self):
        raw = json.dumps({"topicos": SAMPLE_TOPICOS, "analise": SAMPLE_ANALISE})
        agent = _make_professor(raw)
        result = agent.run("quero entender IA", ["livro", "revista"])
        assert result["topicos"] == SAMPLE_TOPICOS
        assert result["analise"] == SAMPLE_ANALISE

    def test_rejects_wrong_count(self):
        raw = json.dumps({"topicos": ["a", "b"], "analise": "ok. ok."})
        agent = _make_professor(raw)
        with pytest.raises(ValueError, match="exactly 4 topicos"):
            agent.run("test", ["livro"])

    def test_rejects_non_list_topicos(self):
        raw = json.dumps({"topicos": "not a list", "analise": "ok. ok."})
        agent = _make_professor(raw)
        with pytest.raises(ValueError, match="exactly 4 topicos"):
            agent.run("test", ["livro"])

    def test_rejects_missing_analise(self):
        raw = json.dumps({"topicos": SAMPLE_TOPICOS})
        agent = _make_professor(raw)
        with pytest.raises(ValueError, match="non-empty analise"):
            agent.run("test", ["livro"])

    def test_rejects_empty_analise(self):
        raw = json.dumps({"topicos": SAMPLE_TOPICOS, "analise": ""})
        agent = _make_professor(raw)
        with pytest.raises(ValueError, match="non-empty analise"):
            agent.run("test", ["livro"])

    def test_temperature(self):
        assert ProfessorAgent.temperature == 0.3

    def test_formats_in_prompt(self):
        raw = json.dumps({"topicos": SAMPLE_TOPICOS, "analise": SAMPLE_ANALISE})
        agent = _make_professor(raw)
        agent.run("test", ["livro", "hq"])
        call_args = agent.client.models.generate_content.call_args
        prompt = call_args.kwargs["contents"]
        assert "livro, hq" in prompt

    def test_retry_on_failure(self):
        good_response = json.dumps({"topicos": SAMPLE_TOPICOS, "analise": SAMPLE_ANALISE})
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = [
            Exception("transient error"),
            MagicMock(text=good_response),
        ]
        agent = ProfessorAgent(client=mock_client)
        result = agent.run("test", ["livro"])
        assert result["topicos"] == SAMPLE_TOPICOS
        assert mock_client.models.generate_content.call_count == 2
