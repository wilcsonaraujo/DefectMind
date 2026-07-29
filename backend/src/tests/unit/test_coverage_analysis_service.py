import json
from unittest.mock import ANY, MagicMock, call  # noqa: F401

import pytest

from backend.src.modules.quality_intelligence.coverage_analysis_service import (
    CoverageAnalysisService,
)
from backend.src.modules.quality_intelligence.schemas import CoverageGap, GapType


def make_record(**kwargs):
    """Creates an object that simulates a Neo4j record (key-based access)."""
    return kwargs


def make_neo4j_result(records: list):
    """Creates a mock result for db.run() that iterates like a list."""
    mock = MagicMock()
    mock.__iter__ = MagicMock(return_value=iter(records))
    mock.single = MagicMock(return_value=records[0] if records else None)
    return mock


@pytest.fixture
def fake_db():
    return MagicMock()


@pytest.fixture
def service(fake_db):
    return CoverageAnalysisService(neo4j_session=fake_db, ai_provider=MagicMock())


MOCK_UNCOVERED_REQUIREMENTS_ROWS = [
    {
        "node_id": "req-001",
        "title": "Autenticação com OAuth 2.0",
        "label": "Requirement",
        "gap_type": "NO_TEST_CASE",
    },
    {
        "node_id": "req-002",
        "title": "Sistema de Notificações por Email",
        "label": "Requirement",
        "gap_type": "NO_TEST_CASE",
    },
    {
        "node_id": "req-003",
        "title": "Relatório de Auditoria",
        "label": "Requirement",
        "gap_type": "NO_TEST_CASE",
    },
]
MOCK_UNCOVERED_REQUIREMENTS = [CoverageGap(**row) for row in MOCK_UNCOVERED_REQUIREMENTS_ROWS]

MOCK_UNCOVERED_STORIES_ROWS = [
    {
        "node_id": "story-001",
        "title": "Módulo de Pagamentos",
        "label": "Story",
        "gap_type": "NO_FUNCTIONAL_COVERAGE",
    },
    {
        "node_id": "story-002",
        "title": "Dashboard de Métricas",
        "label": "Story",
        "gap_type": "NO_FUNCTIONAL_COVERAGE",
    }
]
MOCK_UNCOVERED_STORIES = [CoverageGap(**row) for row in MOCK_UNCOVERED_STORIES_ROWS]

MOCK_ORPHAN_TEST_CASES_ROWS = [
    {
        "node_id": "tc-001",
        "title": "Teste de Pagamento com Cartão",
        "label": "TestCase",
        "gap_type": "ORPHAN_TEST_CASE",
    },
    {
        "node_id": "tc-002",
        "title": "Teste de Autenticação Legacy",
        "label": "TestCase",
        "gap_type": "ORPHAN_TEST_CASE",
    },
    {
        "node_id": "tc-003",
        "title": "Teste de Performance Antigo",
        "label": "TestCase",
        "gap_type": "ORPHAN_TEST_CASE",
    },
    {
        "node_id": "tc-004",
        "title": "Teste de API Depreciada",
        "label": "TestCase",
        "gap_type": "ORPHAN_TEST_CASE",
    },
]
MOCK_ORPHAN_TEST_CASES = [CoverageGap(**row) for row in MOCK_ORPHAN_TEST_CASES_ROWS]


class TestBuildCoveragePrompt:
    def test_coverage_score(self, service, fake_db):
        """Coverage gap calculation test"""
        fake_db.run.return_value = make_neo4j_result(
            [{"total_requirements": 0, "uncovered_requirements": 0}]
        )
        result = service._compute_coverage_score()

        assert result == 100.0

    def test_get_uncovered_requirements(self, service, fake_db):
        """Test uncovered requirements query"""
        fake_db.run.return_value = make_neo4j_result(MOCK_UNCOVERED_REQUIREMENTS_ROWS)

        result = service._get_uncovered_requirements()

        assert len(result) == 3
        assert isinstance(result[0], CoverageGap)
        assert result[0].node_id == "req-001"
        assert result[0].title == "Autenticação com OAuth 2.0"
        assert result[0].label == "Requirement"
        assert result[0].gap_type == GapType.NO_TEST_CASE

        assert result[1].node_id == "req-002"
        assert result[1].title == "Sistema de Notificações por Email"
        assert result[1].label == "Requirement"
        assert result[1].gap_type == GapType.NO_TEST_CASE

        # Verify if the query was called
        fake_db.run.assert_called_once()

    def test_get_uncovered_stories(self, service, fake_db):
        """Test uncovered stories query"""
        fake_db.run.return_value = make_neo4j_result(MOCK_UNCOVERED_STORIES_ROWS)

        result = service._get_uncovered_stories()

        assert len(result) == 2
        assert isinstance(result[0], CoverageGap)
        assert result[0].node_id == "story-001"
        assert result[0].title == "Módulo de Pagamentos"
        assert result[0].label == "Story"
        assert result[0].gap_type == GapType.NO_FUNCTIONAL_COVERAGE

        fake_db.run.assert_called_once()

    def test_get_orphan_test_cases(self, service, fake_db):
        """Test uncovered test cases query"""
        fake_db.run.return_value = make_neo4j_result(MOCK_ORPHAN_TEST_CASES_ROWS)

        result = service._get_orphan_test_cases()

        assert len(result) == 4
        assert isinstance(result[0], CoverageGap)
        assert result[2].node_id == "tc-003"
        assert result[2].title == "Teste de Performance Antigo"
        assert result[2].label == "TestCase"
        assert result[2].gap_type == GapType.ORPHAN_TEST_CASE

        fake_db.run.assert_called_once()

    def test_get_all_gaps_chain(self, service, fake_db):
        """Test validate the list of coverage gap junctions"""

        service._get_uncovered_requirements = MagicMock(
            return_value=MOCK_UNCOVERED_REQUIREMENTS
        )
        service._get_uncovered_stories = MagicMock(return_value=MOCK_UNCOVERED_STORIES)
        service._get_orphan_test_cases = MagicMock(return_value=MOCK_ORPHAN_TEST_CASES)

        result = service._get_all_gaps_chain()

        service._get_uncovered_requirements.assert_called_once()
        service._get_uncovered_stories.assert_called_once()
        service._get_orphan_test_cases.assert_called_once()

        expected_total = (
            len(MOCK_UNCOVERED_REQUIREMENTS)
            + len(MOCK_UNCOVERED_STORIES)
            + len(MOCK_ORPHAN_TEST_CASES)
        )

        assert len(result) == expected_total
        assert result[0].gap_type == GapType.NO_TEST_CASE
        assert result[3].gap_type == GapType.NO_FUNCTIONAL_COVERAGE
        assert result[5].gap_type == GapType.ORPHAN_TEST_CASE

    def test_get_coverage_analysis_no_gaps_skips_llm(self, service, fake_db):
        """No gap in any category -> empty response, LLM not called."""
        fake_db.run.return_value = make_neo4j_result([])

        result = service.get_coverage_analysis()

        assert result.coverage_score == 100.0
        assert result.gaps == []
        assert result.ai_analysis == ""
        assert result.recommendations == []

        service.ai_provider.generate_json.assert_not_called()
