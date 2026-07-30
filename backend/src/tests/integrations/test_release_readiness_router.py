import os

from backend.src.core.dependencies import get_current_user
from backend.src.modules.quality_intelligence.release_readiness_service import (
    StoryNotFoundError,
)
from backend.src.modules.quality_intelligence.schemas import (
    ReleaseReadinessResponse,
    RiskLevelEnum,
    StoryReadiness,
    VerdictEnum,
)

os.environ.setdefault("GEMINI_API_KEY", "fake-key-for-tests")

from unittest.mock import MagicMock, patch

from starlette.testclient import TestClient

from backend.src.main import app
from backend.src.tests.integrations.conftest import mock_user

MOCK_RELEASE_READINESS = ReleaseReadinessResponse(
    results=[
        StoryReadiness(
            story_id="story-001",
            title="Sistema de Autenticação",
            verdict=VerdictEnum.NOT_READY,
            incidents_count=2,
            coverage_score=42.5,
            health_risk=RiskLevelEnum.HIGH,
            blockers=["cobertura de testes em 42.5% (mínimo 50%)"],
        ),
        StoryReadiness(
            story_id="story-002",
            title="Módulo de Pagamentos",
            verdict=VerdictEnum.NEEDS_ATTENTION,
            incidents_count=1,
            coverage_score=65.0,
            health_risk=RiskLevelEnum.MEDIUM,
            blockers=["cobertura de testes em 65.0% (ideal > 80%)"],
        ),
        StoryReadiness(
            story_id="story-003",
            title="Dashboard de Métricas",
            verdict=VerdictEnum.READY,
            incidents_count=0,
            coverage_score=95.0,
            health_risk=RiskLevelEnum.LOW,
            blockers=["todos os critérios atendidos"],
        ),
    ],
    ai_analysis="2 das 3 stories analisadas apresentam blockers críticos.",
    recommendations=[
        "Priorizar a criação de testes para o módulo de Autenticação para atingir cobertura mínima de 50%",
        "Investigar os 2 incidentes sem postmortem no módulo de Autenticação",
    ],
)


def test_generate_requires_auth():
    """The endpoint must return a 401 without an authentication token."""
    client = TestClient(app)
    response = client.post(
        "/api/v1/quality-intelligence/release-readiness",
        json={"story_ids": ["some-story-id-1"]},
    )
    assert response.status_code == 401


def test_generate_success_200():
    client = TestClient(app)
    with patch(
        "backend.src.modules.quality_intelligence.router.ReleaseReadinessService"
    ) as MockService:
        mock_instance = MagicMock()
        mock_instance.get_release_readiness.return_value = MOCK_RELEASE_READINESS
        MockService.return_value = mock_instance
        app.dependency_overrides[get_current_user] = mock_user

        response = client.post(
            "/api/v1/quality-intelligence/release-readiness",
            headers={"Authorization": "Bearer valid-token"},
            json={"story_ids": ["some-story-id-1", "some-story-id-2"]},
        )

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "ai_analysis" in data
    assert "recommendations" in data
    app.dependency_overrides.clear()


def test_generate_release_readiness_returns_422_empty_story_ids():
    """Testing send a empty story id's list"""
    client = TestClient(app)
    app.dependency_overrides[get_current_user] = mock_user
    response = client.post(
        "/api/v1/quality-intelligence/release-readiness",
        headers={"Authorization": "Bearer valid-token"},
        json={"story_ids": []},
    )
    assert response.status_code == 422
    app.dependency_overrides.clear()


def test_generate_release_readiness_returns_404_story_not_found():
    """Testing return story not found"""
    client = TestClient(app)
    with patch(
        "backend.src.modules.quality_intelligence.router.ReleaseReadinessService"
    ) as MockService:
        mock_instance = MagicMock()
        mock_instance.get_release_readiness.side_effect = StoryNotFoundError(
            ["story-999"]
        )
        MockService.return_value = mock_instance
        app.dependency_overrides[get_current_user] = mock_user

        response = client.post(
            "/api/v1/quality-intelligence/release-readiness",
            headers={"Authorization": "Bearer valid-token"},
            json={"story_ids": ["story-999"]},
        )

    assert response.status_code == 404
    app.dependency_overrides.clear()
