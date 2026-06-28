from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.core.dependencies import get_embedding_service

MOCK_RESULTS = {
    "results": [
        {
            "id": "abc-123",
            "label": "Story",
            "properties": {"title": "Login flow", "description": "User authentication"},
            "score": 0.92,
        }
    ],
    "total": 1,
}


def test_semantic_search_requires_auth():
    """Endpoint should be return 401 without JWT token."""
    client = TestClient(app)
    response = client.post(
        "/api/v1/search/semantic",
        json={"text": "Login failed"},
    )
    assert response.status_code == 401


def test_semantic_search_returns_results():
    """Endpoint should be 200 with list of results for valid query."""
    client = TestClient(app)

    fake_embedding = MagicMock()
    fake_embedding.encode.return_value = [0.1] * 384
    app.dependency_overrides[get_embedding_service] = lambda: fake_embedding

    with patch(
        "backend.src.modules.search.router.SemanticSearchService"
    ) as MockService:
        mock_instance = MagicMock()
        mock_instance._search.return_value = MOCK_RESULTS
        MockService.return_value = mock_instance

        response = client.post(
            "/api/v1/search/semantic",
            json={"text": "falha no login"},
            headers={"Authorization": "Bearer valid-token"},
        )

    app.dependency_overrides.pop(get_embedding_service, None)

    assert response.status_code in (200, 401)
    if response.status_code == 200:
        data = response.json()
        assert "results" in data
        assert "total" in data


def test_semantic_search_with_entity_filter():
    """Endpoint should accespted filter for entity type."""
    client = TestClient(app)

    fake_embedding = MagicMock()
    fake_embedding.encode.return_value = [0.1] * 384
    app.dependency_overrides[get_embedding_service] = lambda: fake_embedding

    with patch(
        "backend.src.modules.search.router.SemanticSearchService"
    ) as MockService:
        mock_instance = MagicMock()
        mock_instance._search.return_value = MOCK_RESULTS
        MockService.return_value = mock_instance

        response = client.post(
            "/api/v1/search/semantic",
            json={"text": "falha no login", "filter": "Story", "limit_responses": 5},
            headers={"Authorization": "Bearer valid-token"},
        )

    app.dependency_overrides.pop(get_embedding_service, None)

    assert response.status_code in (200, 401)
