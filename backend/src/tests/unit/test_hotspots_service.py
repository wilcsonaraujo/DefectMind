import json
from unittest.mock import ANY, MagicMock, call  # noqa: F401

import pytest

from backend.src.modules.quality_intelligence.hotspots_service import (
    HotspotsService,
)
from backend.src.modules.quality_intelligence.schemas import HotspotItem

mock_records = [
    {
        "node_id": "story-1",
        "title": "First",
        "label": "Story",
        "bug_count": 20,
        "critical_bug_count": 5,
        "incident_count": 8,
        "postmortem_count": 3,
        "score": 100.0,
    },
    {
        "node_id": "story-2",
        "title": "Second",
        "label": "Story",
        "bug_count": 15,
        "critical_bug_count": 3,
        "incident_count": 5,
        "postmortem_count": 2,
        "score": 65.0,
    },
]

hotspots = [
    HotspotItem(
        node_id="story-123",
        title="Sistema de Autenticação",
        label="Story",
        bug_count=15,
        critical_bug_count=4,
        incident_count=3,
        postmortem_count=2,
        score=37.0,
    )
]


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
    return HotspotsService(
        neo4j_session=fake_db, ai_provider=MagicMock())


class TestBuildHotspotsPrompt:
    def test_get_hotspots_empty_scenarios(self, service, fake_db):
        """
        Tests scenarios where no hotspots are returned.

        This test covers two business scenarios with the same behavior:
        1. There are no Stories in the graph.
        2. There are Stories, but none have defects (score = 0).
        """
        fake_db.run.return_value = make_neo4j_result([])
        result = service.get_hotspots(limit=10)

        assert result.hotspots == []
        assert result.total == 0
        assert result.ai_analysis == ""
        assert result.recommendations == []

        service.ai_provider.generate_json.assert_not_called()

        fake_db.run.assert_called_once()
        call_args = fake_db.run.call_args[1]
        assert call_args["limit"] == 10

    def test_get_hotspots_maps_single_row_to_hotspot_item(self, service, fake_db):
        """Tests the mapping of a single Neo4j row to HotspotItem."""
        fake_db.run.return_value = make_neo4j_result(mock_records)
        service.ai_provider.generate_json.return_value = {
            "ai_analysis": "Análise mock para teste",
            "recommendations": ["Recomendação 1", "Recomendação 2"],
        }

        result = service.get_hotspots(limit=10)

        assert len(result.hotspots) == 2
        for i, record in enumerate(mock_records):
            hotspot = result.hotspots[i]
            assert isinstance(hotspot, HotspotItem)
            assert hotspot.node_id == record["node_id"]
            assert hotspot.title == record["title"]
            assert hotspot.bug_count == record["bug_count"]
            assert hotspot.critical_bug_count == record["critical_bug_count"]
            assert hotspot.incident_count == record["incident_count"]
            assert hotspot.postmortem_count == record["postmortem_count"]
            assert hotspot.score == record["score"]

        assert [h.node_id for h in result.hotspots] == ["story-1", "story-2"]
        assert [h.score for h in result.hotspots] == [100.0, 65.0]


class TestGetHotspotPrompt:
    def test_get_hotspot_context(self, service):
        """Tests the formatting of a single hotspot."""
        result = service._build_hotspots_context(hotspots)

        assert "[Story] title: Sistema de Autenticação" in result
        assert "Bug Count: 15" in result
        assert "Critical Bug Count: 4" in result
        assert "Incident Count: 3" in result
        assert "Postmortem Count: 2" in result
        assert "Score: 37.0" in result
        assert "---" not in result

    def test_get_hotspot_prompt(self, service):
        """Tests the consistency of the prompt format."""
        context = "Hotspot 1: Test (Story) bug_count: 10 score: 50.0"
        result = service._build_hotspots_prompt(context)

        lines = result.strip().split("\n")
        assert len(lines) > 0

        assert "context" in result.lower()

        assert "ai_analysis" in result
        assert "recommendations" in result
        assert "json" in result.lower()


class TestAIResponse:
    def test_call_llm_returns_expected_response(self, service):
        prompt = "Sample prompt"
        expected_response = '{"hotspots": [], "total": 0, "ai_analysis": "Analysis", "recommendations": []}'
        service.ai_provider.generate_json.return_value = expected_response
        response = service._call_llm(prompt)
        assert response == expected_response
        service.ai_provider.generate_json.assert_called_once_with(ANY, temperature=0.1)

    def test_call_llm_with_exception(self, service):
        prompt = "Sample prompt"
        service.ai_provider.generate_json.side_effect = Exception(
            "Error occurred while calling LLM"
        )
        with pytest.raises(Exception) as excinfo:
            service._call_llm(prompt)
        assert "Error occurred while calling LLM" in str(excinfo.value)

    def test_call_llm_propagates_json_decode_error(self, service):
        prompt = "Sample prompt"
        service.ai_provider.generate_json.side_effect = json.JSONDecodeError(
            "Expecting value", "not json", 0
        )
        with pytest.raises(json.JSONDecodeError):
            service._call_llm(prompt)
