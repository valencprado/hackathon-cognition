"""Tests for the Researcher Agent."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from agents.researcher import ResearcherAgent
from tests.conftest import SAMPLE_TOP5, SAMPLE_TOPICOS


def _make_researcher(response_text: str) -> ResearcherAgent:
    mock_client = MagicMock()
    resp = MagicMock()
    resp.text = response_text
    mock_client.models.generate_content.return_value = resp
    return ResearcherAgent(client=mock_client)


class TestResearcherAgent:
    def test_returns_top5(self):
        raw = json.dumps({"top5": SAMPLE_TOP5})
        agent = _make_researcher(raw)
        result = agent.run(SAMPLE_TOPICOS, ["livro"])
        assert len(result["top5"]) == 5
        assert result["top5"][0]["titulo"] == "Supremacia da Máquina"

    def test_rejects_wrong_count(self):
        raw = json.dumps({"top5": SAMPLE_TOP5[:3]})
        agent = _make_researcher(raw)
        with pytest.raises(ValueError, match="exactly 5"):
            agent.run(SAMPLE_TOPICOS, ["livro"])

    def test_rejects_missing_keys(self):
        items = [{"titulo": "X", "autor": "Y"} for _ in range(5)]
        raw = json.dumps({"top5": items})
        agent = _make_researcher(raw)
        with pytest.raises(ValueError, match="missing keys"):
            agent.run(SAMPLE_TOPICOS, ["livro"])

    def test_temperature(self):
        assert ResearcherAgent.temperature == 0.2

    def test_topicos_in_prompt(self):
        raw = json.dumps({"top5": SAMPLE_TOP5})
        agent = _make_researcher(raw)
        agent.run(SAMPLE_TOPICOS, ["livro", "hq"])
        call_args = agent.client.models.generate_content.call_args
        prompt = call_args.kwargs["contents"]
        assert "livro, hq" in prompt
