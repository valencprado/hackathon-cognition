"""Tests for the books CRUD endpoints."""

import json


def _create_book(client, **overrides):
    payload = {
        "tenant": "test",
        "title": "Test Book",
        "author": "Test Author",
        "year": 2024,
        "format_type": "book",
    }
    payload.update(overrides)
    return client.post("/admin/books", json=payload)


class TestListBooks:
    def test_requires_tenant(self, client):
        resp = client.get("/admin/books")
        assert resp.status_code == 400

    def test_returns_empty_list(self, client):
        resp = client.get("/admin/books?tenant=test")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_lists_books_for_tenant(self, client):
        _create_book(client, tenant="a")
        _create_book(client, tenant="b")
        resp = client.get("/admin/books?tenant=a")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["tenant"] == "a"

    def test_filters_by_format(self, client):
        _create_book(client, format_type="book")
        _create_book(client, title="Comic", format_type="comic")
        resp = client.get("/admin/books?tenant=test&format_type=comic")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["format_type"] == "comic"


class TestCreateBook:
    def test_creates_book(self, client):
        resp = _create_book(client)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["title"] == "Test Book"
        assert "id" in data

    def test_creates_book_with_location(self, client):
        resp = _create_book(client, location={"x": 10.0, "y": 20.0, "label": "A1"})
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["location"]["x"] == 10.0
        assert data["location"]["label"] == "A1"

    def test_validation_errors(self, client):
        resp = client.post("/admin/books", json={})
        assert resp.status_code == 400
        errors = resp.get_json()["errors"]
        assert any("tenant" in e for e in errors)
        assert any("title" in e for e in errors)

    def test_invalid_format_type(self, client):
        resp = _create_book(client, format_type="invalid")
        assert resp.status_code == 400


class TestGetBook:
    def test_returns_book(self, client):
        create_resp = _create_book(client)
        book_id = create_resp.get_json()["id"]
        resp = client.get(f"/admin/books/{book_id}")
        assert resp.status_code == 200
        assert resp.get_json()["id"] == book_id

    def test_not_found(self, client):
        resp = client.get("/admin/books/99999")
        assert resp.status_code == 404


class TestUpdateBook:
    def test_updates_fields(self, client):
        create_resp = _create_book(client)
        book_id = create_resp.get_json()["id"]
        resp = client.put(f"/admin/books/{book_id}", json={"title": "Updated"})
        assert resp.status_code == 200
        assert resp.get_json()["title"] == "Updated"

    def test_adds_location(self, client):
        create_resp = _create_book(client)
        book_id = create_resp.get_json()["id"]
        resp = client.put(
            f"/admin/books/{book_id}", json={"location": {"x": 5.0, "y": 6.0}}
        )
        assert resp.status_code == 200
        assert resp.get_json()["location"]["x"] == 5.0

    def test_updates_existing_location(self, client):
        create_resp = _create_book(client, location={"x": 1.0, "y": 2.0})
        book_id = create_resp.get_json()["id"]
        resp = client.put(
            f"/admin/books/{book_id}", json={"location": {"x": 99.0}}
        )
        assert resp.status_code == 200
        assert resp.get_json()["location"]["x"] == 99.0

    def test_not_found(self, client):
        resp = client.put("/admin/books/99999", json={"title": "X"})
        assert resp.status_code == 404


class TestDeleteBook:
    def test_deletes_book(self, client):
        create_resp = _create_book(client)
        book_id = create_resp.get_json()["id"]
        resp = client.delete(f"/admin/books/{book_id}")
        assert resp.status_code == 200
        assert client.get(f"/admin/books/{book_id}").status_code == 404

    def test_not_found(self, client):
        resp = client.delete("/admin/books/99999")
        assert resp.status_code == 404
