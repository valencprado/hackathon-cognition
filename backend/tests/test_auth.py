"""Tests for Section 3 — Backend Authentication."""


STUDENT_PAYLOAD = {
    "email": "aluno@anhembi.edu.br",
    "password": "senha123",
    "name": "Maria Silva",
    "university_slug": "anhembi",
}


# -- 3.1 Student authentication -----------------------------------------------


class TestStudentRegister:
    def test_register_success(self, client):
        resp = client.post("/auth/student/register", json=STUDENT_PAYLOAD)
        assert resp.status_code == 201
        data = resp.get_json()
        assert "token" in data
        assert data["user"]["role"] == "student"
        assert data["user"]["email"] == STUDENT_PAYLOAD["email"]

    def test_register_duplicate_email(self, client):
        client.post("/auth/student/register", json=STUDENT_PAYLOAD)
        resp = client.post("/auth/student/register", json=STUDENT_PAYLOAD)
        assert resp.status_code == 409

    def test_register_missing_fields(self, client):
        resp = client.post("/auth/student/register", json={"email": "a@b.com"})
        assert resp.status_code == 400

    def test_register_invalid_email(self, client):
        payload = {**STUDENT_PAYLOAD, "email": "not-an-email"}
        resp = client.post("/auth/student/register", json=payload)
        assert resp.status_code == 400

    def test_register_short_password(self, client):
        payload = {**STUDENT_PAYLOAD, "password": "123"}
        resp = client.post("/auth/student/register", json=payload)
        assert resp.status_code == 400


class TestStudentLogin:
    def test_login_success(self, client):
        client.post("/auth/student/register", json=STUDENT_PAYLOAD)
        resp = client.post(
            "/auth/student/login",
            json={"email": STUDENT_PAYLOAD["email"], "password": STUDENT_PAYLOAD["password"]},
        )
        assert resp.status_code == 200
        assert "token" in resp.get_json()

    def test_login_wrong_password(self, client):
        client.post("/auth/student/register", json=STUDENT_PAYLOAD)
        resp = client.post(
            "/auth/student/login",
            json={"email": STUDENT_PAYLOAD["email"], "password": "errada"},
        )
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post(
            "/auth/student/login",
            json={"email": "nope@nope.com", "password": "whatever"},
        )
        assert resp.status_code == 401


# -- 3.2 Admin authentication -------------------------------------------------


class TestAdminLogin:
    def test_seed_admin_login(self, client):
        """The seeded Anhembi admin should be able to log in."""
        resp = client.post(
            "/auth/admin/login",
            json={"email": "admin@anhembi.edu.br", "password": "admin123"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["user"]["role"] == "admin"
        assert "token" in data

    def test_admin_login_wrong_password(self, client):
        resp = client.post(
            "/auth/admin/login",
            json={"email": "admin@anhembi.edu.br", "password": "wrong"},
        )
        assert resp.status_code == 401

    def test_student_cannot_login_as_admin(self, client):
        """A student's credentials must not work on the admin login endpoint."""
        client.post("/auth/student/register", json=STUDENT_PAYLOAD)
        resp = client.post(
            "/auth/admin/login",
            json={"email": STUDENT_PAYLOAD["email"], "password": STUDENT_PAYLOAD["password"]},
        )
        assert resp.status_code == 401


# -- 3.3 Role-based access control (RBAC) -------------------------------------


class TestRBAC:
    def _student_token(self, client):
        client.post("/auth/student/register", json=STUDENT_PAYLOAD)
        resp = client.post(
            "/auth/student/login",
            json={"email": STUDENT_PAYLOAD["email"], "password": STUDENT_PAYLOAD["password"]},
        )
        return resp.get_json()["token"]

    def _admin_token(self, client):
        resp = client.post(
            "/auth/admin/login",
            json={"email": "admin@anhembi.edu.br", "password": "admin123"},
        )
        return resp.get_json()["token"]

    def _auth_header(self, token):
        return {"Authorization": f"Bearer {token}"}

    # /auth/me — any authenticated user
    def test_me_with_student_token(self, client):
        token = self._student_token(client)
        resp = client.get("/auth/me", headers=self._auth_header(token))
        assert resp.status_code == 200
        assert resp.get_json()["user"]["role"] == "student"

    def test_me_with_admin_token(self, client):
        token = self._admin_token(client)
        resp = client.get("/auth/me", headers=self._auth_header(token))
        assert resp.status_code == 200
        assert resp.get_json()["user"]["role"] == "admin"

    def test_me_without_token(self, client):
        resp = client.get("/auth/me")
        assert resp.status_code == 401

    # Student-only endpoint
    def test_student_protected_with_student(self, client):
        token = self._student_token(client)
        resp = client.get("/auth/student/protected", headers=self._auth_header(token))
        assert resp.status_code == 200

    def test_student_protected_with_admin(self, client):
        token = self._admin_token(client)
        resp = client.get("/auth/student/protected", headers=self._auth_header(token))
        assert resp.status_code == 403

    # Admin-only endpoint
    def test_admin_protected_with_admin(self, client):
        token = self._admin_token(client)
        resp = client.get("/auth/admin/protected", headers=self._auth_header(token))
        assert resp.status_code == 200

    def test_admin_protected_with_student(self, client):
        token = self._student_token(client)
        resp = client.get("/auth/admin/protected", headers=self._auth_header(token))
        assert resp.status_code == 403
