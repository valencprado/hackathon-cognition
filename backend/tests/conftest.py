"""Shared fixtures used across all test modules."""

from __future__ import annotations

import os
import sys

import pytest

# Ensure the backend package root is on sys.path so bare imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app  # noqa: E402
from auth.models import db  # noqa: E402
from config import Config  # noqa: E402


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


@pytest.fixture()
def app():
    application = create_app(TestConfig)
    yield application


@pytest.fixture()
def client(app):
    with app.test_client() as c:
        yield c


SAMPLE_TOPICOS = [
    "Conceitos de IA explicados para leigos",
    "História e evolução da inteligência artificial",
    "Impactos da IA na sociedade e no trabalho",
    "Ética e riscos das tecnologias de IA",
]

SAMPLE_ANALISE = (
    "O usuário busca compreender IA de forma acessível, sem barreiras técnicas. "
    "A busca deve focar em obras que traduzam conceitos complexos para linguagem simples."
)

SAMPLE_TOP5 = [
    {
        "titulo": "Supremacia da Máquina",
        "autor": "Nick Bostrom",
        "formato": "livro",
        "ano": 2014,
        "nota_amazon": 4.3,
        "topico_relacionado": "Ética e riscos das tecnologias de IA",
        "isbn": "",
    },
    {
        "titulo": "Armas de Destruição Matemática",
        "autor": "Cathy O'Neil",
        "formato": "livro",
        "ano": 2016,
        "nota_amazon": 4.4,
        "topico_relacionado": "Impactos da IA na sociedade e no trabalho",
        "isbn": "",
    },
    {
        "titulo": "Inteligência Artificial",
        "autor": "Kai-Fu Lee",
        "formato": "livro",
        "ano": 2018,
        "nota_amazon": 4.5,
        "topico_relacionado": "Conceitos de IA explicados para leigos",
        "isbn": "",
    },
    {
        "titulo": "Homo Deus",
        "autor": "Yuval Noah Harari",
        "formato": "livro",
        "ano": 2015,
        "nota_amazon": 4.6,
        "topico_relacionado": "História e evolução da inteligência artificial",
        "isbn": "",
    },
    {
        "titulo": "A Era da IA",
        "autor": "Henry Kissinger",
        "formato": "livro",
        "ano": 2021,
        "nota_amazon": 4.1,
        "topico_relacionado": "Impactos da IA na sociedade e no trabalho",
        "isbn": "",
    },
]

SAMPLE_RESUMOS = [
    {
        "titulo": item["titulo"],
        "resumo": f"Este livro explora {item['topico_relacionado'].lower()} de forma acessível.",
        "conexao_tema": f"Conecta com {item['topico_relacionado'].lower()}.",
    }
    for item in SAMPLE_TOP5
]

SAMPLE_FICHAS = [
    {
        "titulo": item["titulo"],
        "autor": item["autor"],
        "sinopse": f"Uma obra fascinante sobre {item['topico_relacionado'].lower()}.",
        "faixa_etaria": "A partir de 16 anos",
        "temas": ["IA", "Tecnologia", "Sociedade"],
        "opinioes_amazon": [
            {"texto": "Excelente leitura!", "estrelas": 5},
            {"texto": "Bom, mas denso.", "estrelas": 4},
        ],
        "onde_encontrar": "Amazon, Kindle, Livraria Cultura",
    }
    for item in SAMPLE_TOP5
]
