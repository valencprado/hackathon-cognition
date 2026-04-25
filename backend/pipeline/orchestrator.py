"""Orchestrator — chains Professor → Researcher → Educator → Descriptive."""

from __future__ import annotations

from typing import Any

from google import genai

from agents.professor import ProfessorAgent
from agents.researcher import ResearcherAgent
from agents.educator import EducatorAgent
from agents.descriptive import DescriptiveAgent


class Orchestrator:
    """Runs the full BookMatch AI pipeline and returns the top 3 enriched items."""

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
            List of format filters (e.g. ``["livro", "hq"]``).

        Returns
        -------
        dict with ``topicos``, ``analise``, and ``books`` (list of up to 3
        enriched items with resumo, conexao_tema, and full ficha data).
        """
        professor_result = self.professor.run(query, formats)
        topicos: list[str] = professor_result["topicos"]
        analise: str = professor_result["analise"]

        researcher_result = self.researcher.run(topicos, formats)
        top5: list[dict[str, Any]] = researcher_result["top5"]

        educator_result = self.educator.run(query, top5)
        resumos: list[dict[str, Any]] = educator_result["resumos"]

        descriptive_result = self.descriptive.run(top5)
        fichas: list[dict[str, Any]] = descriptive_result["fichas"]

        books: list[dict[str, Any]] = []
        for i, item in enumerate(top5[:3]):
            merged = {**item}
            if i < len(resumos):
                merged["resumo"] = resumos[i].get("resumo", "")
                merged["conexao_tema"] = resumos[i].get("conexao_tema", "")
            if i < len(fichas):
                merged["sinopse"] = fichas[i].get("sinopse", "")
                merged["faixa_etaria"] = fichas[i].get("faixa_etaria", "")
                merged["temas"] = fichas[i].get("temas", [])
                merged["onde_encontrar"] = fichas[i].get("onde_encontrar", "")
            books.append(merged)

        return {
            "topicos": topicos,
            "analise": analise,
            "books": books,
        }
