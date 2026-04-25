"""Tests for the Google Books service."""

from __future__ import annotations

from unittest.mock import patch, MagicMock

import requests

from services.google_books import fetch_google_books_metadata


GOOGLE_BOOKS_RESPONSE = {
    "items": [
        {
            "volumeInfo": {
                "title": "Clean Code",
                "authors": ["Robert C. Martin"],
                "publisher": "Prentice Hall",
                "pageCount": 464,
                "description": "A handbook of agile software craftsmanship.",
                "industryIdentifiers": [
                    {"type": "ISBN_13", "identifier": "9780132350884"},
                    {"type": "ISBN_10", "identifier": "0132350882"},
                ],
                "imageLinks": {
                    "thumbnail": "http://books.google.com/thumb.jpg"
                },
                "infoLink": "http://books.google.com/info",
            }
        }
    ]
}


class TestFetchGoogleBooksMetadata:
    @patch("services.google_books.requests.get")
    def test_returns_metadata(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = GOOGLE_BOOKS_RESPONSE
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result = fetch_google_books_metadata("Clean Code", "Robert C. Martin")

        assert result["isbn"] == "9780132350884"
        assert result["publisher"] == "Prentice Hall"
        assert result["page_count"] == 464
        assert result["thumbnail"] == "http://books.google.com/thumb.jpg"
        assert result["info_link"] == "http://books.google.com/info"

    @patch("services.google_books.requests.get")
    def test_returns_empty_on_no_items(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"items": None}
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result = fetch_google_books_metadata("Unknown", "Nobody")

        assert result["isbn"] is None
        assert result["publisher"] is None

    @patch("services.google_books.requests.get")
    def test_returns_empty_on_request_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("timeout")

        result = fetch_google_books_metadata("Test", "Author")

        assert result["isbn"] is None

    @patch("services.google_books.requests.get")
    def test_returns_empty_on_json_error(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.side_effect = ValueError("bad json")
        mock_get.return_value = mock_resp

        result = fetch_google_books_metadata("Test", "Author")

        assert result["isbn"] is None

    @patch("services.google_books.requests.get")
    def test_handles_missing_image_links(self, mock_get):
        response = {
            "items": [
                {
                    "volumeInfo": {
                        "title": "Test",
                        "pageCount": 100,
                    }
                }
            ]
        }
        mock_resp = MagicMock()
        mock_resp.json.return_value = response
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result = fetch_google_books_metadata("Test", "Author")

        assert result["thumbnail"] is None
        assert result["isbn"] is None
        assert result["page_count"] == 100

    @patch("services.google_books.requests.get")
    def test_prefers_isbn_13(self, mock_get):
        response = {
            "items": [
                {
                    "volumeInfo": {
                        "industryIdentifiers": [
                            {"type": "ISBN_10", "identifier": "111"},
                            {"type": "ISBN_13", "identifier": "222"},
                        ]
                    }
                }
            ]
        }
        mock_resp = MagicMock()
        mock_resp.json.return_value = response
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        result = fetch_google_books_metadata("T", "A")
        # ISBN_13 is preferred over ISBN_10 even when ISBN_10 appears first
        assert result["isbn"] == "222"
