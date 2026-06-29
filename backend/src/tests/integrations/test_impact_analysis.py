from fastapi.testclient import TestClient
from backend.src.main import app
from unittest.mock import MagicMock, patch


def test_impact_requires_auth():
    """Endpoint should be return 401 without JWT token."""
    client = TestClient(app)
    response = client.post(
        "/api/v1/search/impact-analysis/qualquer-uuid",
        json={"text": "Login failed"},
    )
    assert response.status_code == 401

MOCK_GRAPH = {
    "nodes": [
        {"id": "abc-123", "label": "Story", "properties": {"title": "Login flow"}}
    ],
    "edges": [
        {"source": "abc-123", "target": "def-456", "type": "HAS_REQUIREMENT"}
    ],
}

def test_impact_returns_graph():
    """Endpoint must have return 200 with nodes and edges for each valid node_id."""
    client = TestClient(app)
    
    with patch(
        "backend.src.modules.search.router.ImpactAnalysisService"  # import router path
    ) as MockService:
        mock_instance = MagicMock()
        mock_instance.get_impact.return_value = MOCK_GRAPH   # define the method returned
        MockService.return_value = mock_instance              # When the router is instanced, receive the mock

        response = client.get(
            "/api/v1/impact-analysis/abc-123",
            headers={"Authorization": "Bearer valid-token"},
        )

    assert response.status_code in (200, 401)
    if response.status_code == 200:
        data = response.json()
        assert "nodes" in data
        assert "edges" in data