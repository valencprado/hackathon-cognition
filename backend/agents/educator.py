"""Educator Agent — writes short pt-BR summaries connecting each work to the user's need."""

from __future__ import annotations

import json
from typing import Any

from agents.base import BaseAgent


class EducatorAgent(BaseAgent):
    """Creates a short Brazilian Portuguese summary for each recommended item,
    explaining why it fits the user's specific need."""

    temperature = 0.5

    system_prompt = (
        "Você é o Agente Educador do BookMatch, sistema de recomendação de leituras.\n\n"
        "Seu trabalho é escrever resumos curtos e impactantes que expliquem como "
        "cada mídia recomendada se conecta com a necessidade real do usuário. "
        "Você faz a ponte entre a obra e a pessoa.\n\n"
        "REGRAS ABSOLUTAS:\n"
        "1. Responda SOMENTE com JSON puro e válido. Sem texto antes ou depois.\n"
        '2. O array "resumos" deve ter EXATAMENTE a mesma quantidade de itens '
        "que o Top 5 recebido, na mesma ordem.\n"
        '3. Cada "resumo" deve ter no máximo 3 linhas (~60 palavras). Seja direto.\n'
        '4. O "resumo" NÃO é uma sinopse genérica — ele explica por que essa obra '
        "serve especificamente para ESSA necessidade do usuário.\n"
        '5. "conexao_tema" deve ser uma frase curta e direta (máximo 15 palavras).\n'
        "6. Escreva em português do Brasil, linguagem acessível e empática.\n"
        "7. Não comece todos os resumos com a mesma estrutura. Varie o estilo.\n"
    )

    def run(self, query: str, top5: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        prompt = (
            "O usuário descreveu sua necessidade assim:\n"
            f'NECESSIDADE: "{query}"\n\n'
            "As seguintes mídias foram selecionadas para ele:\n"
            f"TOP 5: {json.dumps(top5, ensure_ascii=False)}\n\n"
            "Para cada mídia, escreva um resumo de até 3 linhas explicando como ela "
            "conversa diretamente com a necessidade do usuário. Seja específico — o "
            "usuário precisa entender POR QUE aquela obra é boa para ele."
        )
        return self._run_with_retry(prompt)

    def _parse_response(self, raw: str) -> dict[str, list[dict[str, Any]]]:
        data: dict[str, Any] = super()._parse_response(raw)
        resumos = data.get("resumos", [])
        if not isinstance(resumos, list) or len(resumos) == 0:
            raise ValueError("Educator Agent must return at least one resumo")
        for item in resumos:
            if "resumo" not in item:
                raise ValueError(f"Item '{item.get('titulo', '?')}' missing resumo")
            if "conexao_tema" not in item:
                raise ValueError(f"Item '{item.get('titulo', '?')}' missing conexao_tema")
        return {"resumos": resumos}
