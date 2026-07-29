import os

from backend.src.core.dependencies import get_current_user
from backend.src.modules.quality_intelligence.schemas import (
    KnowledgeGap,
    KnowledgeGapsResponse,
    KnowledgeGapType,
)

os.environ.setdefault("GEMINI_API_KEY", "fake-key-for-tests")

from unittest.mock import MagicMock, patch

from starlette.testclient import TestClient

from backend.src.main import app
from backend.src.tests.integrations.conftest import mock_user

MOCK_KNOWLEDGE_GAP = KnowledgeGapsResponse(
    gaps=[
        KnowledgeGap(
            node_id="bug-001",
            title="Falha na autenticação com OAuth",
            label="BugReport",
            gap_type=KnowledgeGapType.BUG_WITHOUT_TEST_CASE,
        ),
        KnowledgeGap(
            node_id="inc-002",
            title="Falha na integração com API de frete",
            label="Incident",
            gap_type=KnowledgeGapType.INCIDENT_WITHOUT_POSTMORTEM,
        ),
        KnowledgeGap(
            node_id="req-004",
            title="Requisito de cache distribuído",
            label="Requirement",
            gap_type=KnowledgeGapType.REQUIREMENT_WITHOUT_STORY,
        ),
        KnowledgeGap(
            node_id="story-001",
            title="Dashboard de Monitoramento",
            label="Story",
            gap_type=KnowledgeGapType.STORY_WITHOUT_REQUIREMENT,
        ),
    ],
    ai_analysis="fake-analysis",
    recommendations=["fake-recommendation-1", "fake-recommendation-2"],
)


def test_generate_requires_auth():
    """The endpoint must return a 401 without an authentication token."""
    client = TestClient(app)
    response = client.get("/api/v1/quality-intelligence/coverage-analysis")
    assert response.status_code == 401


def test_generate_success():
    client = TestClient(app)

    with patch(
        "backend.src.modules.quality_intelligence.router.KnowledgeGapsService"
    ) as MockService:
        mock_instance = MagicMock()
        mock_instance.get_knowledge_gaps.return_value = MOCK_KNOWLEDGE_GAP
        MockService.return_value = mock_instance
        app.dependency_overrides[get_current_user] = mock_user

        response = client.get(
            "/api/v1/quality-intelligence/knowledge-gaps",
            headers={"Authorization": "Bearer valid-token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert "gaps" in data
    assert "ai_analysis" in data
    assert "recommendations" in data
    app.dependency_overrides.clear()
