from unittest.mock import MagicMock

import pytest

from backend.src.modules.quality_intelligence.risk_report_service import (
    RiskReportService,
)
from backend.src.modules.quality_intelligence.schemas import (
    EvidenceItem,
    RiskReportResponse,
)
from backend.src.modules.search.schemas import SearchResult
from backend.src.tests.unit.conftest import make_neo4j_result


@pytest.fixture
def service(fake_db):
    return RiskReportService(
        neo4j_session=fake_db,
        ai_provider=MagicMock(),
        semantic_search_service=MagicMock(),
    )


MOCK_NODE_ID_DICT = [
    {
        "node_id": "story-001",
        "title": "Módulo de Pagamentos",
        "label": "Story",
        "severity": "High",
        "impact": "Medium",
    },
    {
        "node_id": "story-003",
        "title": "Sistema de Autenticação",
        "label": "Requirement",
        "severity": "Low",
        "impact": "High",
    },
]

MOCK_NODE_ID_DICT_NONE = [
    {
        "node_id": None,
        "title": None,
        "label": None,
        "severity": None,
        "impact": None,
    }
]

MOCK_SEMANTIC_SEARCH = SearchResult(
    id="story-001",
    label="Story",
    properties={"title": "Módulo de Pagamentos", "description": "Módulo de Pagamentos"},
    score=0.80,
)

MOCK_RISK_RESPONSE_EMPTY = RiskReportResponse(
    risks=[], ai_analysis="Nenhum risco identificado.", recommendations=[]
)

MOCK_RISK_RESPONSE = RiskReportResponse(
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


class TestBuildRiskReport:
    def test_get_direct_risk_evidence_confirm_dict(self, service, fake_db):
        """Test searching for noisy neighbors (BugReport and Incident) starting from a node."""
        mock_node_id = "story-001"

        fake_db.run.return_value = make_neo4j_result(MOCK_NODE_ID_DICT)
        result = service._get_direct_risk_evidence(mock_node_id)

        assert result[0]["node_id"] == "story-001"
        assert result[0]["title"] == "Módulo de Pagamentos"
        assert result[0]["label"] == "Story"
        assert result[0]["severity"] == "High"
        assert result[0]["impact"] == "Medium"

    def test_get_direct_risk_evidence_node_none(self, service, fake_db):
        """Test searching for noisy neighbors from node None"""
        mock_node_id = "story-002"

        fake_db.run.return_value = make_neo4j_result(MOCK_NODE_ID_DICT_NONE)
        result = service._get_direct_risk_evidence(mock_node_id)

        assert result == []

    def test_get_semantic_risk_evidence_node_discarted(self, service):
        """Test confirming that self-match (node id) is discarded"""
        mock_node_id = "story-001"
        mock_title = "Módulo de Pagamentos"

        service.semantic_search._search = MagicMock(
            side_effect=[[MOCK_SEMANTIC_SEARCH], [], []]
        )
        result = service._get_semantic_risk_evidence(mock_node_id, mock_title)

        assert result == []

    def test_get_semantic_risk_evidence(self, service):
        mock_node_id = "requirement-002"
        mock_title = "Módulo de Pagamentos por aproximação"

        service.semantic_search._search = MagicMock(return_value=[MOCK_SEMANTIC_SEARCH])
        result = service._get_semantic_risk_evidence(mock_node_id, mock_title)

        assert len(result) == 3
        assert result[0]["title"] == "Módulo de Pagamentos"
        assert result[0]["label"] == "Story"
        assert result[0]["score"] == 0.80


class TestResponseRiskReport:
    def test_get_risk_report_node_non_existent(self, service, fake_db):
        """Test risk resport with node id non-existent"""
        mock_node_id = "requirement-003"
        fake_db.run.return_value = make_neo4j_result([])

        result = service.get_risk_report(mock_node_id)

        assert result is None
        service.ai_provider.generate_json.assert_not_called()

    def test_get_risk_report_node_without_evidences(self, service, fake_db):
        """Test risk resport with node id without evidences"""
        mock_node_id = "requirement-004"
        fake_db.run.return_value = make_neo4j_result(
            [{"title": "Requirement de Teste"}]
        )
        service._get_direct_risk_evidence = MagicMock(return_value=[])
        service._get_semantic_risk_evidence = MagicMock(return_value=[])

        result = service.get_risk_report(mock_node_id)

        assert result.risks == []
        assert result.ai_analysis == "Nenhum risco identificado."
        assert result.recommendations == []
        service.ai_provider.generate_json.assert_not_called()

    def test_get_risk_report_node_valid(self, service, fake_db):
        mock_node_id = "requirement-004"
        fake_db.run.return_value = make_neo4j_result(
            [{"title": "Requirement de Teste"}]
        )
        service._get_direct_risk_evidence = MagicMock(
            return_value=[
                {
                    "node_id": "bug-001",
                    "title": "Sistema de Autenticação",
                    "label": "BugReport",
                    "severity": "Critical",
                    "impact": None,
                }
            ]
        )
        service._get_semantic_risk_evidence = MagicMock(return_value=[])
        service.ai_provider.generate_json.return_value = MOCK_RISK_RESPONSE.model_dump()
        response = service.get_risk_report(mock_node_id)
        service.ai_provider.generate_json.assert_called_once()

        assert response.risks == MOCK_RISK_RESPONSE.risks
        assert response.ai_analysis == MOCK_RISK_RESPONSE.ai_analysis
        assert response.recommendations == MOCK_RISK_RESPONSE.recommendations
