"""Tests for the UI configuration CRUD endpoints."""


def _create_config(client, **overrides):
    payload = {
        "tenant": "test",
        "university_name": "Test University",
        "primary_color": "#ff0000",
        "secondary_color": "#00ff00",
    }
    payload.update(overrides)
    return client.post("/admin/ui-config", json=payload)


class TestGetConfig:
    def test_requires_tenant(self, client):
        resp = client.get("/admin/ui-config")
        assert resp.status_code == 400

    def test_not_found(self, client):
        resp = client.get("/admin/ui-config?tenant=nonexistent")
        assert resp.status_code == 404

    def test_returns_config(self, client):
        _create_config(client)
        resp = client.get("/admin/ui-config?tenant=test")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["university_name"] == "Test University"
        assert data["primary_color"] == "#ff0000"


class TestCreateConfig:
    def test_creates_config(self, client):
        resp = _create_config(client)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["tenant"] == "test"

    def test_with_custom_labels(self, client):
        resp = _create_config(
            client, custom_labels={"greeting": "Bem-vindo"}
        )
        assert resp.status_code == 201
        assert resp.get_json()["custom_labels"]["greeting"] == "Bem-vindo"

    def test_duplicate_tenant(self, client):
        _create_config(client)
        resp = _create_config(client)
        assert resp.status_code == 409

    def test_requires_fields(self, client):
        resp = client.post("/admin/ui-config", json={})
        assert resp.status_code == 400

        resp = client.post("/admin/ui-config", json={"tenant": "t"})
        assert resp.status_code == 400


class TestUpdateConfig:
    def test_updates_config(self, client):
        _create_config(client)
        resp = client.put(
            "/admin/ui-config?tenant=test",
            json={"university_name": "Updated Uni", "primary_color": "#000000"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["university_name"] == "Updated Uni"
        assert data["primary_color"] == "#000000"

    def test_updates_custom_labels(self, client):
        _create_config(client)
        resp = client.put(
            "/admin/ui-config?tenant=test",
            json={"custom_labels": {"new_key": "value"}},
        )
        assert resp.status_code == 200
        assert resp.get_json()["custom_labels"]["new_key"] == "value"

    def test_not_found(self, client):
        resp = client.put(
            "/admin/ui-config?tenant=nonexistent", json={"university_name": "X"}
        )
        assert resp.status_code == 404

    def test_requires_tenant(self, client):
        resp = client.put("/admin/ui-config", json={"university_name": "X"})
        assert resp.status_code == 400


class TestDeleteConfig:
    def test_deletes_config(self, client):
        _create_config(client)
        resp = client.delete("/admin/ui-config?tenant=test")
        assert resp.status_code == 200
        assert client.get("/admin/ui-config?tenant=test").status_code == 404

    def test_not_found(self, client):
        resp = client.delete("/admin/ui-config?tenant=nonexistent")
        assert resp.status_code == 404
