"""Descriptive Agent — builds complete pt-BR fact sheets for each recommended item."""

from __future__ import annotations

import json
from typing import Any

from agents.base import BaseAgent


class DescriptiveAgent(BaseAgent):
    """Creates rich fact sheets (sinopse, faixa etária, temas, and where to
    buy) for each recommended item.  All output is in Brazilian Portuguese."""

    temperature = 0.4

    system_prompt = (
        "Você é o Agente Descritivo do BookMatch, sistema de recomendação de leituras.\n\n"
        "Sua função é criar fichas completas e ricas para cada mídia recomendada. "
        "Essas fichas ajudam o usuário a decidir se aquela obra é para ele antes de comprar.\n\n"
        "REGRAS ABSOLUTAS:\n"
        "1. Responda SOMENTE com JSON puro e válido. Sem texto antes ou depois.\n"
        '2. O array "fichas" deve ter EXATAMENTE a mesma quantidade de itens do '
        "Top 5 recebido, na mesma ordem.\n"
        '3. "sinopse": entre 3 e 4 frases. Tom convidativo, não técnico.\n'
        '4. "faixa_etaria": string descritiva. Ex: "A partir de 16 anos", "Adultos", '
        '"14+", "Todos os públicos".\n'
        '5. "temas": array com 3 a 6 strings curtas das temáticas centrais.\n'
        '6. "onde_encontrar": plataformas reais separadas por vírgula. '
        'Ex: "Amazon, Kindle, Livraria Cultura, Estante Virtual".\n'
        "7. Escreva em português do Brasil.\n"
    )

    def run(self, top5: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
        prompt = (
            "Monte fichas completas para cada uma das seguintes mídias:\n"
            f"TOP 5: {json.dumps(top5, ensure_ascii=False)}\n\n"
            "Para cada obra, crie:\n"
            "- Sinopse de 3-4 frases convidativa\n"
            "- Faixa etária recomendada\n"
            "- 3 a 6 temas centrais da obra\n"
            "- Plataformas onde encontrar no Brasil\n\n"
            "Seja específico e fiel às características reais de cada obra.\n"
            "Não use descrições genéricas."
        )
        return self._run_with_retry(prompt)

    def _parse_response(self, raw: str) -> dict[str, list[dict[str, Any]]]:
        data: dict[str, Any] = super()._parse_response(raw)
        fichas = data.get("fichas", [])
        if not isinstance(fichas, list) or len(fichas) == 0:
            raise ValueError("Descriptive Agent must return at least one ficha")
        required_keys = {"titulo", "sinopse", "faixa_etaria", "temas", "onde_encontrar"}
        for ficha in fichas:
            missing = required_keys - set(ficha.keys())
            if missing:
                raise ValueError(f"Ficha '{ficha.get('titulo', '?')}' missing keys: {missing}")
        return {"fichas": fichas}
