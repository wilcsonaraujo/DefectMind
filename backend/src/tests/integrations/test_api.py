class TestHealth:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_body(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert data["neo4j"] in ("connected", "disconnected")
        assert "version" in data


class TestRegister:
    def test_register_success(self, client):
        response = client.post(
            "/auth/register",
            json={
                "email": "test@defectmind.com",
                "password": "MinhaSenh@123",
                "full_name": "Test User",
                "role": "viewer",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@defectmind.com"
        assert "hashed_password" not in data

    def test_register_duplicate_email_returns_409(self, client):
        payload = {
            "email": "dup@defectmind.com",
            "password": "MinhaSenh@123",
            "role": "viewer",
        }
        client.post("/auth/register", json=payload)
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 409

    def test_register_invalid_email_returns_422(self, client):
        response = client.post(
            "/auth/register",
            json={
                "email": "nao-e-um-email",
                "password": "MinhaSenh@123",
                "role": "viewer",
            },
        )
        assert response.status_code == 422


class TestLogin:
    def test_login_success_returns_token(self, client):
        client.post(
            "/auth/register",
            json={
                "email": "login@defectmind.com",
                "password": "MinhaSenh@123",
                "role": "viewer",
            },
        )
        response = client.post(
            "/auth/login",
            json={"email": "login@defectmind.com", "password": "MinhaSenh@123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password_returns_401(self, client):
        client.post(
            "/auth/register",
            json={
                "email": "wrong@defectmind.com",
                "password": "MinhaSenh@123",
                "role": "viewer",
            },
        )
        response = client.post(
            "/auth/login",
            json={"email": "wrong@defectmind.com", "password": "SenhaErrada"},
        )
        assert response.status_code == 401

    def test_login_nonexistent_user_returns_401(self, client):
        response = client.post(
            "/auth/login",
            json={"email": "naoexiste@defectmind.com", "password": "MinhaSenh@123"},
        )
        assert response.status_code == 401


class TestUsers:
    def test_list_users_returns_200(self, client):
        response = client.get("/api/v1/users")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_user_not_found_returns_404(self, client):
        import uuid

        response = client.get(f"/api/v1/users/{uuid.uuid4()}")
        assert response.status_code == 404


class TestAuthMe:
    def test_me_without_token_returns_401(self, client):
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_me_with_invalid_token_returns_401(self, client):
        response = client.get(
            "/auth/me", headers={"Authorization": "Bearer token_invalido"}
        )
        assert response.status_code == 401

    def test_me_with_valid_token_returns_user(self, client):
        client.post(
            "/auth/register",
            json={
                "email": "me@defectmind.com",
                "password": "MinhaSenh@123",
                "role": "viewer",
            },
        )
        login = client.post(
            "/auth/login",
            json={"email": "me@defectmind.com", "password": "MinhaSenh@123"},
        )
        token = login.json()["access_token"]
        response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["email"] == "me@defectmind.com"


class TestArtifacts:
    def _get_token(self, client) -> str:
        client.post(
            "/auth/register",
            json={
                "email": "artifacts@defectmind.com",
                "password": "MinhaSenh@123",
                "role": "analyst",
            },
        )
        response = client.post(
            "/auth/login",
            json={
                "email": "artifacts@defectmind.com",
                "password": "MinhaSenh@123",
            },
        )
        return response.json()["access_token"]

    def test_get_stories_returns_200(self, client):
        token = self._get_token(client)
        response = client.get(
            "/api/v1/stories",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

    def test_get_stories_without_token_returns_401(self, client):
        response = client.get("/api/v1/stories")
        assert response.status_code == 401

    def test_get_story_by_id_not_found_returns_404(self, client):
        token = self._get_token(client)
        response = client.get(
            "/api/v1/stories/id-inexistente",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 404

    def test_get_requirements_returns_200(self, client):
        token = self._get_token(client)
        response = client.get(
            "/api/v1/requirements",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

    def test_get_requirements_without_token_returns_401(self, client):
        response = client.get("/api/v1/requirements")
        assert response.status_code == 401
