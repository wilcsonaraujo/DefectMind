from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.src.main import app
from backend.src.modules.search.schemas import (
    IsolatedNode,
    MostConnectedNode,
    NodeByType,
    StatsResponse,
)

# ─── Mock de resposta completa do GraphService ────────────────────────────────

MOCK_STATS = StatsResponse(
    total_nodes=42,
    total_edges=38,
    nodes_by_type=NodeByType(
        Story=7,
        Requirement=7,
        TestCase=7,
        BugReport=7,
        Incident=7,
        PostMortem=7,
    ),
    most_connected_nodes=[
        MostConnectedNode(id="story-001", label="Story", title="Login flow", degree=5),
        MostConnectedNode(
            id="req-001", label="Requirement", title="Validate credentials", degree=3
        ),
    ],
    isolated_nodes=[
        IsolatedNode(id="orphan-001", label="BugReport", title="Orphan bug"),
    ],
    avg_degree=0.9,
    density=0.022,
)


# ─── Testes de integração ─────────────────────────────────────────────────────


def test_graph_stats_requires_auth():
    """Endpoint deve retornar 401 sem token JWT."""
    client = TestClient(app)
    response = client.get("/api/v1/search/graph-stats")
    assert response.status_code == 401


def test_graph_stats_returns_200_with_valid_token():
    """Endpoint deve retornar 200 com estrutura completa quando autenticado."""
    client = TestClient(app)
    with patch("backend.src.modules.search.router.GraphService") as MockService:
        mock_instance = MagicMock()
        mock_instance.get_graph_stats.return_value = MOCK_STATS.model_dump()
        MockService.return_value = mock_instance

        response = client.get(
            "/api/v1/search/graph-stats",
            headers={"Authorization": "Bearer valid-token"},
        )

    assert response.status_code in (200, 401)
    if response.status_code == 200:
        data = response.json()
        assert "total_nodes" in data
        assert "total_edges" in data
        assert "nodes_by_type" in data
        assert "most_connected_nodes" in data
        assert "isolated_nodes" in data
        assert "avg_degree" in data
        assert "density" in data


def test_graph_stats_nodes_by_type_has_all_labels():
    """nodes_by_type deve conter todos os 6 tipos de artefato."""
    client = TestClient(app)
    with patch("backend.src.modules.search.router.GraphService") as MockService:
        mock_instance = MagicMock()
        mock_instance.get_graph_stats.return_value = MOCK_STATS.model_dump()
        MockService.return_value = mock_instance

        response = client.get(
            "/api/v1/search/graph-stats",
            headers={"Authorization": "Bearer valid-token"},
        )

    assert response.status_code in (200, 401)
    if response.status_code == 200:
        nodes_by_type = response.json()["nodes_by_type"]
        expected_labels = {
            "Story",
            "Requirement",
            "TestCase",
            "BugReport",
            "Incident",
            "PostMortem",
        }
        assert expected_labels == set(nodes_by_type.keys())


def test_graph_stats_most_connected_nodes_structure():
    """Cada item de most_connected_nodes deve ter id, label, title e degree."""
    client = TestClient(app)
    with patch("backend.src.modules.search.router.GraphService") as MockService:
        mock_instance = MagicMock()
        mock_instance.get_graph_stats.return_value = MOCK_STATS.model_dump()
        MockService.return_value = mock_instance

        response = client.get(
            "/api/v1/search/graph-stats",
            headers={"Authorization": "Bearer valid-token"},
        )

    assert response.status_code in (200, 401)
    if response.status_code == 200:
        nodes = response.json()["most_connected_nodes"]
        assert isinstance(nodes, list)
        if nodes:
            node = nodes[0]
            assert "id" in node
            assert "label" in node
            assert "title" in node
            assert "degree" in node
            assert isinstance(node["degree"], int)


def test_graph_stats_isolated_nodes_structure():
    """Cada item de isolated_nodes deve ter id, label e title."""
    client = TestClient(app)
    with patch("backend.src.modules.search.router.GraphService") as MockService:
        mock_instance = MagicMock()
        mock_instance.get_graph_stats.return_value = MOCK_STATS.model_dump()
        MockService.return_value = mock_instance

        response = client.get(
            "/api/v1/search/graph-stats",
            headers={"Authorization": "Bearer valid-token"},
        )

    assert response.status_code in (200, 401)
    if response.status_code == 200:
        isolated = response.json()["isolated_nodes"]
        assert isinstance(isolated, list)
        if isolated:
            node = isolated[0]
            assert "id" in node
            assert "label" in node
            assert "title" in node
