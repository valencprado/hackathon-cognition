"""Tests for the Professor Agent."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from agents.professor import ProfessorAgent


def _make_agent(response_text: str) -> ProfessorAgent:
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = response_text
    mock_client.models.generate_content.return_value = mock_response
    return ProfessorAgent(client=mock_client)


class TestProfessorAgent:
    def test_returns_four_subjects(self):
        subjects = ["Topic A", "Topic B", "Topic C", "Topic D"]
        agent = _make_agent(json.dumps({"subjects": subjects}))
        result = agent.run("I want to learn Python")
        assert result == {"subjects": subjects}

    def test_raises_on_wrong_count(self):
        agent = _make_agent(json.dumps({"subjects": ["A", "B"]}))
        with pytest.raises(ValueError, match="exactly 4 subjects"):
            agent.run("query")

    def test_raises_on_missing_key(self):
        agent = _make_agent(json.dumps({"topics": ["A", "B", "C", "D"]}))
        with pytest.raises(ValueError, match="exactly 4 subjects"):
            agent.run("query")

    def test_coerces_non_string_subjects(self):
        agent = _make_agent(json.dumps({"subjects": [1, 2, 3, 4]}))
        result = agent.run("query")
        assert result == {"subjects": ["1", "2", "3", "4"]}

    def test_raises_on_non_list_subjects(self):
        agent = _make_agent(json.dumps({"subjects": 42}))
        with pytest.raises(ValueError, match="exactly 4 subjects"):
            agent.run("query")

    def test_system_prompt_is_set(self):
        agent = ProfessorAgent(client=MagicMock())
        assert "Professor Agent" in agent.system_prompt
        assert "4 essential subjects" in agent.system_prompt
