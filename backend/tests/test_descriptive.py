"""Tests for the Descriptive Agent."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from agents.descriptive import DescriptiveAgent
from tests.conftest import SAMPLE_TOP5, SAMPLE_FICHAS


def _make_descriptive(response_text: str) -> DescriptiveAgent:
    mock_client = MagicMock()
    resp = MagicMock()
    resp.text = response_text
    mock_client.models.generate_content.return_value = resp
    return DescriptiveAgent(client=mock_client)


class TestDescriptiveAgent:
    def test_returns_fichas(self):
        raw = json.dumps({"fichas": SAMPLE_FICHAS})
        agent = _make_descriptive(raw)
        result = agent.run(SAMPLE_TOP5)
        assert len(result["fichas"]) == 5
        assert result["fichas"][0]["titulo"] == "Supremacia da Máquina"
        assert "sinopse" in result["fichas"][0]
        assert "opinioes_amazon" in result["fichas"][0]

    def test_rejects_empty_fichas(self):
        raw = json.dumps({"fichas": []})
        agent = _make_descriptive(raw)
        with pytest.raises(ValueError, match="at least one ficha"):
            agent.run(SAMPLE_TOP5)

    def test_rejects_missing_keys(self):
        bad = [{"titulo": "X", "sinopse": "ok"}]
        raw = json.dumps({"fichas": bad})
        agent = _make_descriptive(raw)
        with pytest.raises(ValueError, match="missing keys"):
            agent.run(SAMPLE_TOP5)

    def test_temperature(self):
        assert DescriptiveAgent.temperature == 0.4

    def test_pt_br_in_system_prompt(self):
        assert "português do Brasil" in DescriptiveAgent.system_prompt
