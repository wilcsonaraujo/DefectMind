from unittest.mock import MagicMock

import pydantic
import pytest

from backend.src.modules.quality_intelligence.recommendations_service import (
    RecommendationsService,
)
from backend.src.modules.quality_intelligence.schemas import RecommendationItem
from backend.src.tests.unit.conftest import make_neo4j_result


@pytest.fixture
def service(fake_db):
    return RecommendationsService(
        neo4j_session=fake_db,
        ai_provider=MagicMock(),
        health_score_service=MagicMock(),
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


class TestBuildRecommendations:
    def test_get_recommendation_evidence_return_none(self, service, fake_db):
        """Test fetch the health score data for a node from the graph database to use in recommendations service."""
        mock_node_id = "story-022"
        service.health_score._fetch_health_score_data = MagicMock(return_value=None)

        result = service._get_recommendation_evidence(mock_node_id)

        assert result is None


class TestResponseRecommendations:
    def test_get_recommendation_node_non_existent(self, service, fake_db):
        """Test recommendations with node id non-existent"""
        mock_node_id = "story-022"
        service.health_score._fetch_health_score_data = MagicMock(return_value=None)

        result = service._get_recommendation_evidence(mock_node_id)

        assert result is None
        service.ai_provider.generate_json.assert_not_called()

    def test_recommendation_item_rejects_empty_justification(self):
        """Test that RecommendationItem rejects a recommendation without justification."""
        with pytest.raises(pydantic.ValidationError):
            RecommendationItem(
                type="INCREASE_COVERAGE",
                priority="High",
                justification="",
            )
