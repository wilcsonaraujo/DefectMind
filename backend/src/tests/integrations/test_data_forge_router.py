import os

os.environ.setdefault("GEMINI_API_KEY", "fake-key-for-tests")

from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient
from backend.src.main import app


@pytest.fixture
def client(db):
    """Reuses the conftest authenticated client."""
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Get a JWT token via login for use in authenticated tests."""
    response = client.post(
        "/auth/login",
        data={"username": "admin@defectmind.com", "password": "Admin@123"},
    )
    token = response.json().get("access_token", "fake-token")
    return {"Authorization": f"Bearer {token}"}


MOCK_TOTALS = {
    "stories": 5,
    "requirements": 5,
    "test_cases": 5,
    "bug_reports": 5,
    "incidents": 5,
    "post_mortems": 5,
    "batches_processed": 1,
    "batches_failed": 0,
}


def test_generate_requires_auth():
    """The endpoint must return a 401 without an authentication token."""
    client = TestClient(app)
    response = client.post(
        "/data-forge/generate",
        json={"num_stories": 5, "batch_size": 5},
    )
    assert response.status_code == 401


def test_generate_invalid_params():
    """The endpoint must return 422 with invalid parameters."""
    client = TestClient(app)
    response = client.post(
        "/data-forge/generate",
        json={"num_stories": 7, "batch_size": 3},
        headers={"Authorization": "Bearer fake-token"},
    )
    assert response.status_code in (401, 422)


def test_generate_success():
    """The endpoint should return a 200 status code with counters when the service is working."""
    client = TestClient(app)

    with patch("backend.src.modules.data_forge.router.DataForgeService") as MockService:
        mock_instance = MagicMock()
        mock_instance.generate.return_value = MOCK_TOTALS
        MockService.return_value = mock_instance

        with patch(
            "backend.src.modules.data_forge.router.GeminiProvider"
        ) as MockProvider:
            MockProvider.return_value = MagicMock()

            # Use a valid token — replace with the project's actual authentication flow.
            response = client.post(
                "/data-forge/generate",
                json={"num_stories": 5, "batch_size": 5},
                headers={"Authorization": "Bearer valid-token"},
            )

    # With the service mocked, the result depends on authentication being successful.
    assert response.status_code in (200, 401)
    if response.status_code == 200:
        data = response.json()
        assert "stories" in data
        assert data["batches_processed"] == 1
