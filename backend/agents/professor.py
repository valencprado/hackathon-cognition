"""Professor Agent — identifies four essential subjects from a student query."""

from __future__ import annotations

from typing import Any

from agents.base import BaseAgent


class ProfessorAgent(BaseAgent):
    """Receives a natural-language query and returns four key subjects."""

    system_prompt = (
        "You are the Professor Agent for a university library chatbot.\n"
        "Given a student's natural-language query about a topic they want to study,\n"
        "identify exactly 4 essential subjects that are most relevant to the query.\n"
        "Each subject should be a concise phrase (3-8 words) that captures a core\n"
        "aspect of the topic.\n\n"
        "RETURN ONLY JSON in this exact format:\n"
        '{"subjects": ["subject1", "subject2", "subject3", "subject4"]}\n'
    )

    def _parse_response(self, raw: str) -> dict[str, list[str]]:
        data: dict[str, Any] = super()._parse_response(raw)
        subjects = data.get("subjects", [])
        if not isinstance(subjects, list) or len(subjects) != 4:
            raise ValueError(
                f"Professor Agent must return exactly 4 subjects, got {len(subjects)}"
            )
        return {"subjects": [str(s) for s in subjects]}
