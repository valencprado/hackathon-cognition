"""Google Books API client for fetching book metadata."""

from __future__ import annotations

from typing import Any

import requests

import config


def fetch_google_books_metadata(title: str, author: str) -> dict[str, Any]:
    """Search Google Books for a book and return enriched metadata.

    Returns a dict with keys: ``isbn``, ``publisher``, ``page_count``,
    ``description``, ``thumbnail``, ``info_link``.  Missing fields default
    to ``None``.
    """
    query = f"intitle:{title} inauthor:{author}"
    params: dict[str, Any] = {"q": query, "maxResults": 1}
    if config.GOOGLE_BOOKS_API_KEY:
        params["key"] = config.GOOGLE_BOOKS_API_KEY

    empty: dict[str, Any] = {
        "isbn": None,
        "publisher": None,
        "page_count": None,
        "description": None,
        "thumbnail": None,
        "info_link": None,
    }

    try:
        resp = requests.get(config.GOOGLE_BOOKS_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return empty

    items = data.get("items")
    if not items:
        return empty

    volume = items[0].get("volumeInfo", {})

    isbn = None
    for ident in volume.get("industryIdentifiers", []):
        id_type = ident.get("type")
        if id_type == "ISBN_13":
            isbn = ident["identifier"]
            break
        if id_type == "ISBN_10" and isbn is None:
            isbn = ident["identifier"]

    return {
        "isbn": isbn,
        "publisher": volume.get("publisher"),
        "page_count": volume.get("pageCount"),
        "description": volume.get("description"),
        "thumbnail": (volume.get("imageLinks") or {}).get("thumbnail"),
        "info_link": volume.get("infoLink"),
    }
