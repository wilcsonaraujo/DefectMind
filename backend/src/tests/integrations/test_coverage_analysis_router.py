import os

from backend.src.core.dependencies import get_current_user
from backend.src.modules.quality_intelligence.schemas import (
    CoverageAnalysisResponse,
    CoverageGap,
    GapType,
)

os.environ.setdefault("GEMINI_API_KEY", "fake-key-for-tests")

from unittest.mock import MagicMock, patch

from starlette.testclient import TestClient

from backend.src.main import app
from backend.src.tests.integrations.conftest import mock_user

MOCK_COVERAGE = CoverageAnalysisResponse(
    coverage_score=75.5,
    gaps=[
        CoverageGap(
            node_id="req-001",
            title="Autenticação com OAuth",
            label="Requirement",
            gap_type=GapType.NO_TEST_CASE,
        ),
        CoverageGap(
            node_id="story-001",
            title="Módulo de Pagamentos",
            label="Story",
            gap_type=GapType.NO_FUNCTIONAL_COVERAGE,
        ),
        CoverageGap(
            node_id="tc-001",
            title="Teste de Pagamento com Cartão",
            label="TestCase",
            gap_type=GapType.ORPHAN_TEST_CASE,
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
        "backend.src.modules.quality_intelligence.router.CoverageAnalysisService"
    ) as MockService:
        mock_instance = MagicMock()
        mock_instance.get_coverage_analysis.return_value = MOCK_COVERAGE
        MockService.return_value = mock_instance
        app.dependency_overrides[get_current_user] = mock_user

        response = client.get(
            "/api/v1/quality-intelligence/coverage-analysis",
            headers={"Authorization": "Bearer valid-token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert "coverage_score" in data
    assert "gaps" in data
    assert "ai_analysis" in data
    assert "recommendations" in data
    app.dependency_overrides.clear()
