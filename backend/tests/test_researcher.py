"""Tests for the Researcher Agent."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from agents.researcher import ResearcherAgent
from tests.conftest import SAMPLE_BOOKS


def _make_agent(response_text: str) -> ResearcherAgent:
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = response_text
    mock_client.models.generate_content.return_value = mock_response
    return ResearcherAgent(client=mock_client)


class TestResearcherAgent:
    def test_returns_books(self):
        agent = _make_agent(json.dumps({"books": SAMPLE_BOOKS}))
        result = agent.run(["subj1", "subj2"], ["book"])
        assert len(result["books"]) == 5
        assert result["books"][0]["title"] == "Clean Code"

    def test_raises_on_empty_books(self):
        agent = _make_agent(json.dumps({"books": []}))
        with pytest.raises(ValueError, match="at least one book"):
            agent.run(["subj1"], ["book"])

    def test_raises_on_missing_keys(self):
        bad_book = [{"title": "No Author"}]
        agent = _make_agent(json.dumps({"books": bad_book}))
        with pytest.raises(ValueError, match="missing keys"):
            agent.run(["subj1"], ["book"])

    def test_prompt_includes_subjects_and_formats(self):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = json.dumps({"books": SAMPLE_BOOKS})
        mock_client.models.generate_content.return_value = mock_response

        agent = ResearcherAgent(client=mock_client)
        agent.run(["Machine Learning", "Neural Networks"], ["book", "journal"])

        call_args = mock_client.models.generate_content.call_args
        prompt = call_args.kwargs.get("contents") or call_args[1].get("contents", "")
        assert "Machine Learning" in prompt
        assert "journal" in prompt

    def test_system_prompt_is_set(self):
        agent = ResearcherAgent(client=MagicMock())
        assert "Researcher Agent" in agent.system_prompt
