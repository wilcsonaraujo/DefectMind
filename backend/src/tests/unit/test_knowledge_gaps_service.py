from unittest.mock import ANY, MagicMock, call  # noqa: F401

import pytest

from backend.src.modules.quality_intelligence.knowledge_gaps_service import (
    KnowledgeGapsService,
)
from backend.src.modules.quality_intelligence.schemas import (
    KnowledgeGap,
    KnowledgeGapType,
)
from backend.src.tests.unit.conftest import make_neo4j_result


@pytest.fixture
def service(fake_db):
    return KnowledgeGapsService(neo4j_session=fake_db, ai_provider=MagicMock())


MOCK_BUGS_WITHOUT_TEST_CASE_ROWS = [
    {
        "node_id": "bug-001",
        "title": "Falha na autenticação com OAuth",
        "label": "BugReport",
        "gap_type": "BUG_WITHOUT_TEST_CASE",
    },
    {
        "node_id": "bug-002",
        "title": "Erro no cálculo de frete para regiões Norte",
        "label": "BugReport",
        "gap_type": "BUG_WITHOUT_TEST_CASE",
    },
    {
        "node_id": "bug-003",
        "title": "Timeout no endpoint de relatórios",
        "label": "BugReport",
        "gap_type": "BUG_WITHOUT_TEST_CASE",
    },
]
MOCK_BUGS_WITHOUT_TEST_CASE = [
    KnowledgeGap(**row) for row in MOCK_BUGS_WITHOUT_TEST_CASE_ROWS
]

MOCK_INCIDENTS_WITHOUT_POSTMORTEM_ROWS = [
    {
        "node_id": "inc-001",
        "title": "Indisponibilidade do sistema de pagamentos",
        "label": "Incident",
        "gap_type": "INCIDENT_WITHOUT_POSTMORTEM",
    },
    {
        "node_id": "inc-002",
        "title": "Falha na integração com API de frete",
        "label": "Incident",
        "gap_type": "INCIDENT_WITHOUT_POSTMORTEM",
    },
]
MOCK_INCIDENTS_WITHOUT_POSTMORTEM = [
    KnowledgeGap(**row) for row in MOCK_INCIDENTS_WITHOUT_POSTMORTEM_ROWS
]

MOCK_REQUIREMENTS_WITHOUT_STORY_ROWS = [
    {
        "node_id": "req-001",
        "title": "Requisito de autenticação biométrica",
        "label": "Requirement",
        "gap_type": "REQUIREMENT_WITHOUT_STORY",
    },
    {
        "node_id": "req-002",
        "title": "Requisito de integração com ERP",
        "label": "Requirement",
        "gap_type": "REQUIREMENT_WITHOUT_STORY",
    },
    {
        "node_id": "req-003",
        "title": "Requisito de relatórios em tempo real",
        "label": "Requirement",
        "gap_type": "REQUIREMENT_WITHOUT_STORY",
    },
    {
        "node_id": "req-004",
        "title": "Requisito de cache distribuído",
        "label": "Requirement",
        "gap_type": "REQUIREMENT_WITHOUT_STORY",
    },
]
MOCK_REQUIREMENTS_WITHOUT_STORY = [
    KnowledgeGap(**row) for row in MOCK_REQUIREMENTS_WITHOUT_STORY_ROWS
]

MOCK_STORIES_WITHOUT_REQUIREMENTS_ROWS = [
    {
        "node_id": "story-001",
        "title": "Dashboard de Monitoramento",
        "label": "Story",
        "gap_type": "STORY_WITHOUT_REQUIREMENT",
    },
    {
        "node_id": "story-002",
        "title": "Sistema de Notificações Push",
        "label": "Story",
        "gap_type": "STORY_WITHOUT_REQUIREMENT",
    },
]
MOCK_STORIES_WITHOUT_REQUIREMENTS = [
    KnowledgeGap(**row) for row in MOCK_STORIES_WITHOUT_REQUIREMENTS_ROWS
]


class TestBuildKnowledge:
    def test_get_bugs_without_test_case(self, service, fake_db):
        """Test bugs without test case"""
        fake_db.run.return_value = make_neo4j_result(MOCK_BUGS_WITHOUT_TEST_CASE_ROWS)
        result = service._get_bugs_without_test_case()

        assert len(result) == 3
        assert isinstance(result[1], KnowledgeGap)
        assert result[1].node_id == "bug-002"
        assert result[1].title == "Erro no cálculo de frete para regiões Norte"
        assert result[1].label == "BugReport"
        assert result[1].gap_type == KnowledgeGapType.BUG_WITHOUT_TEST_CASE

    def test_get_incidents_without_postmortem(self, service, fake_db):
        """Test incident without postmortem"""
        fake_db.run.return_value = make_neo4j_result(
            MOCK_INCIDENTS_WITHOUT_POSTMORTEM_ROWS
        )
        result = service._get_incidents_without_postmortem()

        assert len(result) == 2
        assert isinstance(result[0], KnowledgeGap)
        assert result[0].node_id == "inc-001"
        assert result[0].title == "Indisponibilidade do sistema de pagamentos"
        assert result[0].label == "Incident"
        assert result[0].gap_type == KnowledgeGapType.INCIDENT_WITHOUT_POSTMORTEM

    def test_get_requirements_without_story(self, service, fake_db):
        """Test requirement without story"""
        fake_db.run.return_value = make_neo4j_result(
            MOCK_REQUIREMENTS_WITHOUT_STORY_ROWS
        )
        result = service._get_requirements_without_story()

        assert len(result) == 4
        assert isinstance(result[2], KnowledgeGap)
        assert result[2].node_id == "req-003"
        assert result[2].title == "Requisito de relatórios em tempo real"
        assert result[2].label == "Requirement"
        assert result[2].gap_type == KnowledgeGapType.REQUIREMENT_WITHOUT_STORY

    def test_get_stories_without_requirements(self, service, fake_db):
        """Test stories without requirements"""
        fake_db.run.return_value = make_neo4j_result(
            MOCK_STORIES_WITHOUT_REQUIREMENTS_ROWS
        )
        result = service._get_stories_without_requirements()

        assert len(result) == 2
        assert isinstance(result[1], KnowledgeGap)
        assert result[1].node_id == "story-002"
        assert result[1].title == "Sistema de Notificações Push"
        assert result[1].label == "Story"
        assert result[1].gap_type == KnowledgeGapType.STORY_WITHOUT_REQUIREMENT

    def test_get_knowledge_analysis_no_gaps(self, service):
        """Test validate the list of knowledge gap junctions"""
        service._get_bugs_without_test_case = MagicMock(
            return_value=MOCK_BUGS_WITHOUT_TEST_CASE
        )
        service._get_incidents_without_postmortem = MagicMock(
            return_value=MOCK_INCIDENTS_WITHOUT_POSTMORTEM
        )
        service._get_requirements_without_story = MagicMock(
            return_value=MOCK_REQUIREMENTS_WITHOUT_STORY
        )
        service._get_stories_without_requirements = MagicMock(
            return_value=MOCK_STORIES_WITHOUT_REQUIREMENTS
        )

        result = service._get_all_gaps_chain()

        service._get_bugs_without_test_case.assert_called_once()
        service._get_incidents_without_postmortem.assert_called_once()
        service._get_requirements_without_story.assert_called_once()
        service._get_stories_without_requirements.assert_called_once()

        expected_total = (
            len(MOCK_BUGS_WITHOUT_TEST_CASE)
            + len(MOCK_INCIDENTS_WITHOUT_POSTMORTEM)
            + len(MOCK_REQUIREMENTS_WITHOUT_STORY)
            + len(MOCK_STORIES_WITHOUT_REQUIREMENTS)
        )

        assert len(result) == expected_total
        assert result[0].gap_type == KnowledgeGapType.BUG_WITHOUT_TEST_CASE
        assert result[3].gap_type == KnowledgeGapType.INCIDENT_WITHOUT_POSTMORTEM
        assert result[5].gap_type == KnowledgeGapType.REQUIREMENT_WITHOUT_STORY
        assert result[9].gap_type == KnowledgeGapType.STORY_WITHOUT_REQUIREMENT

    def test_get_knowledge_gap_skips_llm(self, service, fake_db):
        """No gap in any category -> empty response, LLM not called."""
        fake_db.run.return_value = make_neo4j_result([])

        result = service.get_knowledge_gaps()

        assert result.gaps == []
        assert result.ai_analysis == ""
        assert result.recommendations == []

        service.ai_provider.generate_json.assert_not_called()
