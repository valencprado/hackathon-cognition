"""Researcher Agent — curates top 5 real media items based on topics."""

from __future__ import annotations

from typing import Any

from agents.base import BaseAgent


class ResearcherAgent(BaseAgent):
    """Takes topics and format filters, returns five real media items."""

    temperature = 0.2

    system_prompt = (
        "Você é o Agente Pesquisador do BookMatch, sistema de recomendação de leituras.\n\n"
        "Você é especialista em curadoria de livros, revistas e HQs. Seu trabalho "
        "é receber tópicos já analisados e encontrar as 5 mídias reais que melhor "
        "os atendem.\n\n"
        "REGRAS ABSOLUTAS:\n"
        "1. Responda SOMENTE com JSON puro e válido. Sem texto antes ou depois.\n"
        "2. Recomende APENAS mídias que realmente existem. Nunca invente título ou autor.\n"
        "3. Respeite RIGOROSAMENTE os formatos permitidos pelo usuário.\n"
        '4. O campo "formato" deve ser EXATAMENTE: "livro", "revista" ou "hq".\n'
        '5. "nota_amazon" deve ser decimal entre 1.0 e 5.0. Se não souber a nota '
        "real, estime com base na popularidade (clássicos: entre 4.0 e 4.8).\n"
        "6. Prefira obras reconhecidas e disponíveis no mercado brasileiro.\n"
        '7. O array "top5" deve ter EXATAMENTE 5 itens. Nem mais, nem menos.\n'
        "8. Distribua os itens entre os 4 tópicos quando possível.\n"
    )

    def run(self, topicos: list[str], formats: list[str]) -> dict[str, list[dict[str, Any]]]:
        prompt = (
            "Com base nos tópicos identificados pelo Agente Professor:\n\n"
            f"TÓPICOS: {', '.join(topicos)}\n\n"
            "FORMATOS PERMITIDOS (só inclua mídias nestes formatos):\n"
            f"{', '.join(formats)}\n\n"
            "Monte um TOP 5 de mídias REAIS que melhor cobrem esses tópicos.\n"
            "Varie as abordagens: uma mais técnica, uma mais narrativa, etc."
        )
        return self._run_with_retry(prompt)

    def _parse_response(self, raw: str) -> dict[str, list[dict[str, Any]]]:
        data: dict[str, Any] = super()._parse_response(raw)
        top5 = data.get("top5", [])
        if not isinstance(top5, list) or len(top5) != 5:
            raise ValueError(
                f"Researcher Agent must return exactly 5 items in top5, got {len(top5) if isinstance(top5, list) else top5!r}"
            )
        required_keys = {"titulo", "autor", "formato",  "nota_amazon"}
        for item in top5:
            missing = required_keys - set(item.keys())
            if missing:
                raise ValueError(f"Item missing keys: {missing}")
        return {"top5": top5}
