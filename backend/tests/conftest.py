"""Shared fixtures used across all test modules."""

from __future__ import annotations

import os
import sys

import pytest

# Ensure the backend package root is on sys.path so bare imports work
# (e.g. ``import config``, ``from agents import ...``).
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


SAMPLE_BOOKS = [
    {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "year": 2008,
        "format": "book",
    },
    {
        "title": "Design Patterns",
        "author": "Gang of Four",
        "year": 1994,
        "format": "book",
    },
    {
        "title": "Refactoring",
        "author": "Martin Fowler",
        "year": 1999,
        "format": "book",
    },
    {
        "title": "The Pragmatic Programmer",
        "author": "Andy Hunt",
        "year": 1999,
        "format": "book",
    },
    {
        "title": "Mythical Man-Month",
        "author": "Fred Brooks",
        "year": 1975,
        "format": "book",
    },
]

SAMPLE_BOOKS_WITH_SYNOPSIS = [
    {**b, "synopsis": f"A great book about {b['title'].lower()}."}
    for b in SAMPLE_BOOKS
]

SAMPLE_SUBJECTS = [
    "Software design principles",
    "Code readability patterns",
    "Agile development practices",
    "Software architecture fundamentals",
]
