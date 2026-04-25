"""Seed / mock data for the Anhembi Morumbi MVP demo.

Run standalone:  python seed.py
Or call seed_database(app) programmatically.
"""

from __future__ import annotations

from database import db
from models.book import Book
from models.library_map import LibraryMap, BookLocation
from models.ui_config import UIConfig

TENANT = "anhembi"

BOOKS = [
    {
        "title": "Engenharia de Software",
        "author": "Ian Sommerville",
        "year": 2019,
        "isbn": "9788543024974",
        "format_type": "book",
        "synopsis": "Referencia classica em engenharia de software cobrindo processos, modelagem e gerenciamento de projetos.",
        "location": {"x": 120.0, "y": 340.0, "label": "Estante A3", "shelf": "A3-Prateleira 2", "section": "Computacao", "aisle": "Corredor A", "floor": "Terreo"},
    },
    {
        "title": "Estruturas de Dados e Algoritmos em Java",
        "author": "Robert Lafore",
        "year": 2004,
        "isbn": "9788536501635",
        "format_type": "book",
        "synopsis": "Guia pratico de estruturas de dados com exemplos em Java.",
        "location": {"x": 200.0, "y": 340.0, "label": "Estante A4", "shelf": "A4-Prateleira 1", "section": "Computacao", "aisle": "Corredor A", "floor": "Terreo"},
    },
    {
        "title": "Redes de Computadores",
        "author": "Andrew Tanenbaum",
        "year": 2011,
        "isbn": "9788576059240",
        "format_type": "book",
        "synopsis": "Abordagem abrangente sobre redes de computadores e protocolos de comunicacao.",
        "location": {"x": 280.0, "y": 200.0, "label": "Estante B1", "shelf": "B1-Prateleira 3", "section": "Redes e Telecomunicacoes", "aisle": "Corredor B", "floor": "1o Andar"},
    },
    {
        "title": "Turma da Monica - Classicos",
        "author": "Mauricio de Sousa",
        "year": 2020,
        "isbn": "9786555121001",
        "format_type": "comic",
        "synopsis": "Coletanea de historias classicas da Turma da Monica.",
        "location": {"x": 350.0, "y": 150.0, "label": "Estante C2", "shelf": "C2-Prateleira 1", "section": "Quadrinhos e HQs", "aisle": "Corredor C", "floor": "Terreo"},
    },
    {
        "title": "Revista Brasileira de Ciencias Sociais",
        "author": "ANPOCS",
        "year": 2023,
        "isbn": None,
        "format_type": "journal",
        "synopsis": "Periodico academico com artigos sobre ciencias sociais no Brasil.",
        "location": {"x": 400.0, "y": 100.0, "label": "Periodicos P1", "shelf": "P1-Prateleira 4", "section": "Periodicos Academicos", "aisle": "Corredor P", "floor": "Terreo"},
    },
]


def seed_database(app):
    """Insert demo data inside *app* context. Skips if data already exists."""
    with app.app_context():
        if UIConfig.query.filter_by(tenant=TENANT).first():
            return  # already seeded

        # UI config
        config = UIConfig(
            tenant=TENANT,
            university_name="Universidade Anhembi Morumbi",
            logo_url="https://upload.wikimedia.org/wikipedia/commons/thumb/3/31/Anhembi_Morumbi_logo.svg/320px-Anhembi_Morumbi_logo.svg.png",
            primary_color="#00205b",
            secondary_color="#e31837",
        )
        config.custom_labels = {
            "search_placeholder": "O que voce gostaria de estudar hoje?",
            "results_title": "Livros recomendados",
            "map_button": "Ver no Mapa",
        }
        db.session.add(config)

        # Library map
        lib_map = LibraryMap(
            tenant=TENANT,
            image_url="https://via.placeholder.com/800x600.png?text=Mapa+Biblioteca+Anhembi",
            width=800,
            height=600,
        )
        db.session.add(lib_map)

        # Books + locations
        for bdata in BOOKS:
            fields = {k: v for k, v in bdata.items() if k != "location"}
            loc_data = bdata.get("location")
            book = Book(tenant=TENANT, **fields)
            db.session.add(book)
            db.session.flush()

            if loc_data:
                loc = BookLocation(book_id=book.id, **loc_data)
                db.session.add(loc)

        db.session.commit()


if __name__ == "__main__":
    from app_factory import create_app

    app = create_app()
    seed_database(app)
    print("Seed data inserted for tenant:", TENANT)
