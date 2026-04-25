"""Orchestrator — chains Professor → Researcher → Educator → Descriptive."""

from __future__ import annotations

from typing import Any

from google import genai

from agents.professor import ProfessorAgent
from agents.researcher import ResearcherAgent
from agents.educator import EducatorAgent
from agents.descriptive import DescriptiveAgent


class Orchestrator:
    """Runs the full AI pipeline and returns the top 3 enriched books."""

    def __init__(self, client: genai.Client | None = None) -> None:
        self.professor = ProfessorAgent(client=client)
        self.researcher = ResearcherAgent(client=client)
        self.educator = EducatorAgent(client=client)
        self.descriptive = DescriptiveAgent(client=client)

    def run(self, query: str, formats: list[str]) -> dict[str, Any]:
        """Execute the full pipeline.

        Parameters
        ----------
        query:
            Natural-language query from the student.
        formats:
            List of format filters (e.g. ``["book", "journal"]``).

        Returns
        -------
        dict with ``subjects`` (list[str]) and ``books`` (list[dict]) —
        the top 3 enriched books.
        """
        professor_result = self.professor.run(query)
        subjects: list[str] = professor_result["subjects"]

        researcher_result = self.researcher.run(subjects, formats)
        candidate_books: list[dict[str, Any]] = researcher_result["books"]

        educator_result = self.educator.run(candidate_books)
        books_with_synopsis: list[dict[str, Any]] = educator_result["books"]

        descriptive_result = self.descriptive.run(books_with_synopsis)
        enriched_books: list[dict[str, Any]] = descriptive_result["books"]

        top_books = enriched_books[:3]

        return {
            "subjects": subjects,
            "books": top_books,
        }
