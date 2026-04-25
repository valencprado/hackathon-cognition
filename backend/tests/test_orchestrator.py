"""Tests for the Orchestrator pipeline."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from pipeline.orchestrator import Orchestrator
from tests.conftest import (
    SAMPLE_TOPICOS,
    SAMPLE_ANALISE,
    SAMPLE_TOP5,
    SAMPLE_RESUMOS,
    SAMPLE_FICHAS,
)


def _mock_orchestrator() -> Orchestrator:
    mock_client = MagicMock()
    orch = Orchestrator(client=mock_client)

    orch.professor.run = MagicMock(
        return_value={"topicos": SAMPLE_TOPICOS, "analise": SAMPLE_ANALISE}
    )
    orch.researcher.run = MagicMock(return_value={"top5": SAMPLE_TOP5})
    orch.educator.run = MagicMock(return_value={"resumos": SAMPLE_RESUMOS})
    orch.descriptive.run = MagicMock(return_value={"fichas": SAMPLE_FICHAS})
    return orch


class TestOrchestrator:
    def test_full_pipeline(self):
        orch = _mock_orchestrator()
        result = orch.run("quero entender IA", ["livro"])

        assert result["topicos"] == SAMPLE_TOPICOS
        assert result["analise"] == SAMPLE_ANALISE
        assert len(result["books"]) == 3

        book = result["books"][0]
        assert book["titulo"] == "Supremacia da Máquina"
        assert "resumo" in book
        assert "conexao_tema" in book
        assert "sinopse" in book
        assert "faixa_etaria" in book
        assert "temas" in book
        assert "onde_encontrar" in book

    def test_passes_query_to_educator(self):
        orch = _mock_orchestrator()
        orch.run("quero entender IA", ["livro"])
        orch.educator.run.assert_called_once_with("quero entender IA", SAMPLE_TOP5)

    def test_passes_formats_to_professor(self):
        orch = _mock_orchestrator()
        orch.run("test", ["livro", "hq"])
        orch.professor.run.assert_called_once_with("test", ["livro", "hq"])

    def test_passes_topicos_to_researcher(self):
        orch = _mock_orchestrator()
        orch.run("test", ["livro"])
        orch.researcher.run.assert_called_once_with(SAMPLE_TOPICOS, ["livro"])

    def test_professor_error_propagates(self):
        orch = _mock_orchestrator()
        orch.professor.run.side_effect = ValueError("bad")
        with pytest.raises(ValueError, match="bad"):
            orch.run("test", ["livro"])
