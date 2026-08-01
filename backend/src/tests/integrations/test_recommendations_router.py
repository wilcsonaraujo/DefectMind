import os

from backend.src.core.dependencies import get_current_user
from backend.src.modules.artifacts.schemas import PriorityEnum
from backend.src.modules.quality_intelligence.schemas import (
    RecommendationItem,
    RecommendationsResponse,
    RecommendationTypeEnum,
)

os.environ.setdefault("GEMINI_API_KEY", "fake-key-for-tests")

from unittest.mock import MagicMock, patch

from starlette.testclient import TestClient

from backend.src.main import app
from backend.src.tests.integrations.conftest import mock_user

MOCK_RECOMMENDATIONS_RESPONSE = RecommendationsResponse(
    recommendations=[
        RecommendationItem(
            type=RecommendationTypeEnum.EXECUTE_REGRESSION,
            priority=PriorityEnum.HIGH,
            justification="Módulo de autenticação teve 4 bugs críticos na última sprint - executar testes de regressão completos",
        ),
        RecommendationItem(
            type=RecommendationTypeEnum.INCREASE_COVERAGE,
            priority=PriorityEnum.HIGH,
            justification="Cobertura de testes no módulo de pagamentos está em 42% (mínimo 80%) - aumentar cobertura",
        ),
        RecommendationItem(
            type=RecommendationTypeEnum.CREATE_TEST_CASE,
            priority=PriorityEnum.MEDIUM,
            justification="Requisito de integração com OAuth não possui casos de teste associados",
        ),
        RecommendationItem(
            type=RecommendationTypeEnum.PRIORITIZE_INTEGRATION,
            priority=PriorityEnum.LOW,
            justification="Integração com API de frete está estável, mas deve ser priorizada para novos cenários",
        ),
    ],
    ai_analysis="Análise de recomendações: 2 recomendações de alta prioridade identificadas.",
)


def test_generate_requires_auth():
    """The endpoint must return a 401 without an authentication token."""
    client = TestClient(app)
    response = client.post(
        "/api/v1/quality-intelligence/recommendations",
        json={"node_id": "some-node-id"},
    )
    assert response.status_code == 401


def test_generate_recommendations_returns_404_none():
    """Test return 404 get recommendations = None"""
    client = TestClient(app)
    with patch(
        "backend.src.modules.quality_intelligence.router.RecommendationsService"
    ) as MockService:
        mock_instance = MagicMock()
        mock_instance.get_recommendations.return_value = None
        MockService.return_value = mock_instance
        app.dependency_overrides[get_current_user] = mock_user

        response = client.post(
            "/api/v1/quality-intelligence/recommendations",
            headers={"Authorization": "Bearer valid-token"},
            json={"node_id": "some-node-id"},
        )

    assert response.status_code == 404
    app.dependency_overrides.clear()


def test_generate_recommendations_success_200():
    client = TestClient(app)
    with patch(
        "backend.src.modules.quality_intelligence.router.RecommendationsService"
    ) as MockService:
        mock_instance = MagicMock()
        mock_instance.get_recommendations.return_value = MOCK_RECOMMENDATIONS_RESPONSE
        MockService.return_value = mock_instance
        app.dependency_overrides[get_current_user] = mock_user

        response = client.post(
            "/api/v1/quality-intelligence/recommendations",
            headers={"Authorization": "Bearer valid-token"},
            json={"node_id": "some-node-id"},
        )

    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert "ai_analysis" in data
    app.dependency_overrides.clear()
