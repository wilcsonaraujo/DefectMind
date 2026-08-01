import os

from backend.src.core.dependencies import get_current_user
from backend.src.modules.quality_intelligence.schemas import (
    EvidenceItem,
    RiskReportResponse,
)

os.environ.setdefault("GEMINI_API_KEY", "fake-key-for-tests")

from unittest.mock import MagicMock, patch

from starlette.testclient import TestClient

from backend.src.main import app
from backend.src.tests.integrations.conftest import mock_user

MOCK_RISK_REPORT = RiskReportResponse(
    risks=[
        EvidenceItem(
            artifact="Sistema de Autenticação",
            type="BugReport",
            justification="4 bugs críticos identificados no módulo de autenticação",
        ),
        EvidenceItem(
            artifact="Módulo de Pagamentos",
            type="Incident",
            justification="3 incidentes registrados sem postmortem",
        ),
    ],
    ai_analysis="Bugs críticos e incidentes sem postmortem são os principais fatores de risco.",
    recommendations=[
        "Priorizar correção dos bugs críticos no módulo de autenticação",
        "Criar postmortems para os 3 incidentes do módulo de pagamentos",
    ],
)


def test_generate_requires_auth():
    """The endpoint must return a 401 without an authentication token."""
    client = TestClient(app)
    response = client.post(
        "/api/v1/quality-intelligence/risk-report",
        json={"node_id": "some-node-id"},
    )
    assert response.status_code == 401


def test_generate_risk_report_returns_404_none():
    """Test return 404 get risk report = None"""
    client = TestClient(app)
    with patch(
        "backend.src.modules.quality_intelligence.router.RiskReportService"
    ) as MockService:
        mock_instance = MagicMock()
        mock_instance.get_risk_report.return_value = None
        MockService.return_value = mock_instance
        app.dependency_overrides[get_current_user] = mock_user

        response = client.post(
            "/api/v1/quality-intelligence/risk-report",
            headers={"Authorization": "Bearer valid-token"},
            json={"node_id": "some-node-id"},
        )

    assert response.status_code == 404
    app.dependency_overrides.clear()


def test_generate_risk_report_success_200():
    client = TestClient(app)
    with patch(
        "backend.src.modules.quality_intelligence.router.RiskReportService"
    ) as MockService:
        mock_instance = MagicMock()
        mock_instance.get_risk_report.return_value = MOCK_RISK_REPORT
        MockService.return_value = mock_instance
        app.dependency_overrides[get_current_user] = mock_user

        response = client.post(
            "/api/v1/quality-intelligence/risk-report",
            headers={"Authorization": "Bearer valid-token"},
            json={"node_id": "some-node-id"},
        )

    assert response.status_code == 200
    data = response.json()
    assert "risks" in data
    assert "ai_analysis" in data
    assert "recommendations" in data
    app.dependency_overrides.clear()
