"""Tests for the maps CRUD endpoints."""


def _create_map(client, **overrides):
    payload = {
        "tenant": "test",
        "image_url": "https://example.com/map.png",
        "width": 800,
        "height": 600,
    }
    payload.update(overrides)
    return client.post("/admin/maps", json=payload)


class TestGetMap:
    def test_requires_tenant(self, client):
        resp = client.get("/admin/maps")
        assert resp.status_code == 400

    def test_not_found(self, client):
        resp = client.get("/admin/maps?tenant=nonexistent")
        assert resp.status_code == 404

    def test_returns_map(self, client):
        _create_map(client)
        resp = client.get("/admin/maps?tenant=test")
        assert resp.status_code == 200
        assert resp.get_json()["image_url"] == "https://example.com/map.png"


class TestCreateOrUpdateMap:
    def test_creates_map(self, client):
        resp = _create_map(client)
        assert resp.status_code == 201

    def test_updates_existing_map(self, client):
        _create_map(client)
        resp = _create_map(client, image_url="https://example.com/new.png")
        assert resp.status_code == 200
        assert resp.get_json()["image_url"] == "https://example.com/new.png"

    def test_requires_fields(self, client):
        resp = client.post("/admin/maps", json={})
        assert resp.status_code == 400

        resp = client.post("/admin/maps", json={"tenant": "t"})
        assert resp.status_code == 400


class TestDeleteMap:
    def test_deletes_map(self, client):
        _create_map(client)
        resp = client.delete("/admin/maps?tenant=test")
        assert resp.status_code == 200
        assert client.get("/admin/maps?tenant=test").status_code == 404

    def test_not_found(self, client):
        resp = client.delete("/admin/maps?tenant=nonexistent")
        assert resp.status_code == 404


class TestLocations:
    def test_list_locations(self, client):
        # Create a book with location first
        book_resp = client.post(
            "/admin/books",
            json={
                "tenant": "test",
                "title": "Book",
                "author": "Author",
                "location": {"x": 10.0, "y": 20.0, "label": "A1"},
            },
        )
        resp = client.get("/admin/maps/locations?tenant=test")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["x"] == 10.0

    def test_update_location(self, client):
        book_resp = client.post(
            "/admin/books",
            json={
                "tenant": "test",
                "title": "Book",
                "author": "Author",
                "location": {"x": 10.0, "y": 20.0},
            },
        )
        loc_id = book_resp.get_json()["location"]["id"]
        resp = client.put(f"/admin/maps/locations/{loc_id}", json={"x": 99.0})
        assert resp.status_code == 200
        assert resp.get_json()["x"] == 99.0

    def test_update_location_not_found(self, client):
        resp = client.put("/admin/maps/locations/99999", json={"x": 1.0})
        assert resp.status_code == 404
