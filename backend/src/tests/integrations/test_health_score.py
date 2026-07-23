import os

from backend.src.core.dependencies import get_current_user
from backend.src.modules.quality_intelligence.schemas import (
    EvidenceItem,
    HealthScoreResponse,
)

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


MOCK_HEALTH_STATS = HealthScoreResponse(
    evidence=[
        EvidenceItem(
            artifact="fake-artifact",
            type="fake-type",
            justification="fake-justification",
        )
    ],
    ai_analysis="fake-analysis",
    recommendations=["fake-recommendation-1", "fake-recommendation-2"],
    risk_classification="LOW",
)


def mock_user():
    return {"username": "Admin", "password": "admin@123"}


def test_generate_requires_auth():
    """The endpoint must return a 401 without an authentication token."""
    client = TestClient(app)
    response = client.post(
        "/api/v1/quality-intelligence/health-score",
        json={"node_id": "some-node-id"},
    )
    assert response.status_code == 401

def test_health_score_returns_200_with_valid_token():
    """The endpoint must return a 200 with a complete structure when authenticated."""
    app.dependency_overrides[get_current_user] = mock_user
    client = TestClient(app)
    with patch(
        "backend.src.modules.quality_intelligence.router.HealthScoreService"
    ) as MockService:
        mock_instance = MagicMock()
        mock_instance.build_health_score_prompt.return_value = "Test Prompt"
        mock_instance.get_ai_response.return_value = MOCK_HEALTH_STATS.model_dump()
        mock_instance._build_health_score_prompt.return_value = {
            "main_node": {"id": "test-id"},
            "total_nodes": 10,
            "total_edges": 15,
            "nodes_by_type": {"Story": 5, "Bug": 3},
            "degree": 5,
            "connected_nodes": [],
            "connected_count": 9,
            "relationships_count": 15
        }
        
        MockService.return_value = mock_instance

        response = client.post(
            "/api/v1/quality-intelligence/health-score",
            json={"node_id": "some-node-id"},
            headers={"Authorization": "Bearer valid-token"},
        )

    assert response.status_code == 200
    if response.status_code == 200:
        data = response.json()
        assert "evidence" in data
        assert "ai_analysis" in data
        assert "recommendations" in data
        assert "risk_classification" in data

    app.dependency_overrides.clear()

def test_health_score_returns_404_for_nonexistent_node():
    """The endpoint must return a 404 when the node does not exist."""
    app.dependency_overrides[get_current_user] = mock_user
    client = TestClient(app)
    with patch(
        "backend.src.modules.quality_intelligence.router.HealthScoreService"
    ) as MockService:
        mock_instance = MagicMock()
        mock_instance.build_health_score_prompt.return_value = None
        MockService.return_value = mock_instance

        response = client.post(
            "/api/v1/quality-intelligence/health-score",
            json={"node_id": "nonexistent-node-id"},
            headers={"Authorization": "Bearer valid-token"},
        )

    assert response.status_code == 404
    app.dependency_overrides.clear()


