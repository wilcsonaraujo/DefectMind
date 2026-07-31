from unittest.mock import MagicMock

import pytest

from backend.src.modules.quality_intelligence.release_readiness_service import (
    ReleaseReadinessService,
)
from backend.src.modules.quality_intelligence.schemas import StoryReadiness
from backend.src.tests.unit.conftest import make_neo4j_result


@pytest.fixture
def service(fake_db):
    return ReleaseReadinessService(neo4j_session=fake_db, ai_provider=MagicMock())


MOCK_STORY_IDS = ["story-001", "story-002", "story-003"]

MOCK_STORY_READINESS = [
    StoryReadiness(
        story_id="story-001",
        title="Sistema de Autenticação",
        verdict="NOT_READY",
        incidents_count=2,
        coverage_score=42.5,
        health_risk="HIGH",
        blockers=["cobertura de testes em 42.5% (mínimo 50%)"],
    ),
    StoryReadiness(
        story_id="story-002",
        title="Módulo de Pagamentos",
        verdict="NEEDS_ATTENTION",
        incidents_count=1,
        coverage_score=65.0,
        health_risk="MEDIUM",
        blockers=["cobertura de testes em 65.0% (ideal > 80%)"],
    ),
    StoryReadiness(
        story_id="story-003",
        title="Dashboard de Métricas",
        verdict="READY",
        incidents_count=0,
        coverage_score=95.0,
        health_risk="LOW",
        blockers=[],
    ),
]

MOCK_AI_RESPONSE = {
    "ai_analysis": "2 das 3 stories analisadas apresentam blockers críticos.",
    "recommendations": [
        "Priorizar a criação de testes para o módulo de Autenticação para atingir cobertura mínima de 50%",
        "Investigar os 2 incidentes sem postmortem no módulo de Autenticação",
    ],
}


class TestBuildReleaseReadiness:
    def test_validate_story_ids_some_missing(self, service, fake_db):
        """Test validate missing id's"""
        story_ids = ["story-001", "story-002", "story-003", "story-004"]
        mock_records = [
            {"found_id": "story-001"},
            {"found_id": "story-003"},
        ]

        fake_db.run.return_value = make_neo4j_result(mock_records)
        result = service._validate_story_ids(story_ids)

        expected = ["story-002", "story-004"]
        assert sorted(result) == sorted(expected)
        assert len(result) == 2
        assert "story-002" in result
        assert "story-004" in result

    def test_compute_verdict_ready(self, service):
        """Tests the verdict calculation verdict READY."""

        result = service._compute_verdict(
            coverage_score=90,
            health_risk="LOW",
            incidents_count=0,
        )
        assert result["verdict"] == "READY"

    def test_compute_verdict_needs_attention(self, service):
        """Tests the verdict calculation verdict NEEDS ATTENTION."""

        result = service._compute_verdict(
            coverage_score=70,
            health_risk="MEDIUM",
            incidents_count=10,
        )
        assert result["verdict"] == "NEEDS_ATTENTION"

    def test_compute_verdict_not_ready(self, service):
        """Tests the verdict calculation verdict NOT READY."""

        result = service._compute_verdict(
            coverage_score=20,
            health_risk="HIGH",
            incidents_count=0,
        )
        assert result["verdict"] == "NOT_READY"

    def test_get_release_readiness(self, service):
        """Test the full get_release_readiness happy path with multiple stories."""
        service._validate_story_ids = MagicMock(return_value=[])
        service._assess_story = MagicMock(side_effect=MOCK_STORY_READINESS)
        service.ai_provider.generate_json.return_value = MOCK_AI_RESPONSE

        response = service.get_release_readiness(MOCK_STORY_IDS)

        assert service._assess_story.call_count == 3
        service.ai_provider.generate_json.assert_called_once()

        assert response.results == MOCK_STORY_READINESS
        assert response.ai_analysis == MOCK_AI_RESPONSE["ai_analysis"]
        assert response.recommendations == MOCK_AI_RESPONSE["recommendations"]
