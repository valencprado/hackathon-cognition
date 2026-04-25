"""Professor Agent — analyses the topic and identifies 4 key subjects."""

from __future__ import annotations

from typing import Any

from agents.base import BaseAgent


class ProfessorAgent(BaseAgent):
    """Receives a natural-language query and returns four key topics plus a
    two-sentence analysis."""

    temperature = 0.3

    system_prompt = (
        "Você é o Agente Professor do BookMatch, sistema de recomendação de leituras.\n\n"
        "Sua única função é analisar o tema ou necessidade descrita pelo usuário "
        "e extrair os 4 tópicos mais relevantes, distintos e úteis sobre esse "
        "assunto para guiar uma busca por livros, revistas e HQs.\n\n"
        "REGRAS ABSOLUTAS:\n"
        "1. Responda SOMENTE com JSON puro e válido. Sem texto antes ou depois.\n"
        "2. Não use blocos markdown. Não escreva ```json. Apenas o JSON bruto.\n"
        "3. Os 4 tópicos devem ser DIFERENTES entre si. Não repita ideias.\n"
        "4. Cada tópico deve ser uma frase curta e clara (máximo 8 palavras).\n"
        "5. A análise deve ter exatamente 2 frases. Nem mais, nem menos.\n"
        "6. Se o tema for vago, interprete da forma mais útil. Nunca retorne erro.\n"
        "7. Considere os formatos selecionados ao pensar nos tópicos.\n"
    )

    def run(self, query: str, formats: list[str]) -> dict[str, Any]:
        prompt = (
            "O usuário quer encontrar mídias para ler e descreveu assim:\n\n"
            f'NECESSIDADE: "{query}"\n'
            f"FORMATOS QUE O USUÁRIO QUER: {', '.join(formats)}\n\n"
            "Identifique os 4 tópicos mais importantes que vão guiar a busca.\n"
            "Os tópicos precisam ser úteis para encontrar livros, revistas ou HQs reais."
        )
        return self._run_with_retry(prompt)

    def _parse_response(self, raw: str) -> dict[str, Any]:
        data: dict[str, Any] = super()._parse_response(raw)
        topicos = data.get("topicos", [])
        if not isinstance(topicos, list) or len(topicos) != 4:
            raise ValueError(
                f"Professor Agent must return exactly 4 topicos, got {topicos!r}"
            )
        analise = data.get("analise", "")
        if not isinstance(analise, str) or not analise:
            raise ValueError("Professor Agent must return a non-empty analise string")
        return {"topicos": [str(t) for t in topicos], "analise": str(analise)}
