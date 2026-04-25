"""Tests for multi-tenant middleware and public endpoints."""

from seed import seed_database


class TestTenantMiddleware:
    def test_resolves_from_header(self, admin_app, admin_client):
        seed_database(admin_app)
        resp = admin_client.get("/api/config", headers={"X-Tenant": "anhembi"})
        assert resp.status_code == 200
        assert resp.get_json()["tenant"] == "anhembi"

    def test_resolves_from_query_param(self, admin_app, admin_client):
        seed_database(admin_app)
        resp = admin_client.get("/api/config?tenant=anhembi")
        assert resp.status_code == 200
        assert resp.get_json()["tenant"] == "anhembi"

    def test_no_tenant_returns_error(self, admin_client):
        resp = admin_client.get("/api/config")
        assert resp.status_code == 400


class TestPublicEndpoints:
    def test_get_map(self, admin_app, admin_client):
        seed_database(admin_app)
        resp = admin_client.get("/api/map", headers={"X-Tenant": "anhembi"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["tenant"] == "anhembi"
        assert data["width"] == 800

    def test_get_book_location(self, admin_app, admin_client):
        seed_database(admin_app)
        # Look up an actual book id from the seeded data
        books_resp = admin_client.get("/admin/books?tenant=anhembi")
        book_id = books_resp.get_json()[0]["id"]
        resp = admin_client.get(
            f"/api/map/book/{book_id}", headers={"X-Tenant": "anhembi"}
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "location" in data
        assert "map" in data


class TestSeedData:
    def test_seed_creates_data(self, admin_app, admin_client):
        seed_database(admin_app)
        # Verify books
        resp = admin_client.get("/admin/books?tenant=anhembi")
        assert resp.status_code == 200
        books = resp.get_json()
        assert len(books) == 5

        # Verify UI config
        resp = admin_client.get("/admin/ui-config?tenant=anhembi")
        assert resp.status_code == 200
        config = resp.get_json()
        assert config["university_name"] == "Universidade Anhembi Morumbi"

        # Verify map
        resp = admin_client.get("/admin/maps?tenant=anhembi")
        assert resp.status_code == 200

    def test_seed_is_idempotent(self, admin_app, admin_client):
        seed_database(admin_app)
        seed_database(admin_app)
        resp = admin_client.get("/admin/books?tenant=anhembi")
        assert len(resp.get_json()) == 5
