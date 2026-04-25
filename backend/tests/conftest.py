"""Shared fixtures used across all test modules."""

from __future__ import annotations

import sys
import os

import pytest

# Ensure the backend package root is on sys.path so bare imports work
# (e.g. ``import config``, ``from agents import ...``).
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app as flask_app  # noqa: E402
from app_factory import create_app  # noqa: E402
from database import db as _db  # noqa: E402


# --- Fixtures for AI agents tests (section 1) ---


@pytest.fixture()
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
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


# --- Fixtures for admin CRUD tests (section 2) ---


@pytest.fixture()
def admin_app():
    app = create_app(testing=True)
    yield app


@pytest.fixture()
def admin_client(admin_app):
    return admin_app.test_client()


@pytest.fixture()
def db_session(admin_app):
    with admin_app.app_context():
        yield _db.session
        _db.session.rollback()
