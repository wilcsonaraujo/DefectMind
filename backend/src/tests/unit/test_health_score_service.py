<<<<<<< HEAD
from urllib import response

import pytest
from unittest.mock import ANY, MagicMock, call  # noqa: F401
=======
import pytest
from unittest.mock import MagicMock, call  # noqa: F401
>>>>>>> c6ae0462dfa3aa5f71c316fd23779e58ce1f57ab
from backend.src.modules.quality_intelligence.health_score_service import (
    HealthScoreService,
)
from backend.src.modules.quality_intelligence.schemas import HealthScoreResponse


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
    return HealthScoreService(neo4j_session=fake_db, ai_provider=MagicMock())


class TestBuildHealthScorePrompt:
    def test_node_not_found(self, fake_db, service):
        fake_db.run.return_value = make_neo4j_result([])
        result = service._build_health_score_prompt("nonexistent_node_id")
        assert result is None

    def test_node_found_with_no_connected_nodes(self, fake_db, service):
        fake_db.run.return_value = make_neo4j_result(
            [
                {
                    "main_node": {
                        "id": "1",
                        "title": "Main Node",
                        "label": "Artifact",
                        "degree": 0,
                    },
                    "connected": [],
                    "relationships": [],
                    "degree": 0,
                    "total_edges": 0,
                }
            ]
        )
        result = service._build_health_score_prompt("1")
        assert result is not None
        assert result["main_node"]["id"] == "1"
        assert result["degree"] == 0
        assert result["total_edges"] == 0

    def test_node_found_with_connected_nodes(self, fake_db, service):
        fake_db.run.return_value = make_neo4j_result(
            [
                {
                    "main_node": {
                        "id": "1",
                        "title": "Main Node",
                        "label": "Artifact",
                        "degree": 2,
                    },
                    "connected": [
                        {"id": "2", "title": "Connected Node 1", "label": "Story"},
                        {"id": "3", "title": "Connected Node 2", "label": "Bug"},
                    ],
                    "relationships": ["rel1", "rel2"],
                    "degree": 2,
                    "total_edges": 2,
                }
            ]
        )
        result = service._build_health_score_prompt("1")
        assert result is not None
        assert result["main_node"]["id"] == "1"
        assert result["degree"] == 2
        assert result["total_edges"] == 2


class TestBuildPrompt:
    def test_build_prompt_structure(self, service):
        context = "Sample context"
        health_score_data = {
            "main_node": {"title": "Main Node", "label": "Artifact"},
            "nodes_by_type": {"Story": 2, "Bug": 1},
        }
        prompt = service._build_prompt(context, health_score_data)
        assert "context: Sample context" in prompt
        assert "Main Node: Main Node (Type: Artifact)" in prompt
        assert "Nodes by Type: {'Story': 2, 'Bug': 1}" in prompt
        assert "Answer strictly in JSON" in prompt

    def test_build_prompt_with_main_node_missing(self, service):
        context = "Sample context"
        health_score_data = {"main_node": {}, "nodes_by_type": {"Story": 2, "Bug": 1}}
        prompt = service._build_prompt(context, health_score_data)
        assert "Main Node: None (Type: None)" in prompt

    def test_build_prompt_with_json_instruction(self, service):
        context = "Sample context"
        health_score_data = {
            "main_node": {"title": "Main Node", "label": "Artifact"},
            "nodes_by_type": {"Story": 2, "Bug": 1},
        }
        prompt = service._build_prompt(context, health_score_data)
        assert "Answer strictly in JSON with the fields" in prompt


class TestAIResponse:
    def test_call_llm_returns_expected_response(self, service):
        prompt = "Sample prompt"
        expected_response = '{"evidence": [], "ai_analysis": "Analysis", "recommendations": [], "risk_classification": "LOW"}'
        service.ai_provider.generate_response.return_value = expected_response
        response = service._call_llm(prompt)
        assert response == expected_response
        service.ai_provider.generate_response.assert_called_once_with(
<<<<<<< HEAD
            ANY, temperature=0.1
=======
            prompt, temperature=0.1
>>>>>>> c6ae0462dfa3aa5f71c316fd23779e58ce1f57ab
        )

    def test_call_llm_with_exception(self, service):
        prompt = "Sample prompt"
        service.ai_provider.generate_response.side_effect = Exception(
            "Error occurred while calling LLM"
        )
        with pytest.raises(Exception) as excinfo:
            service._call_llm(prompt)
        assert "Error occurred while calling LLM" in str(excinfo.value)

    def test_call_llm_returns_non_json_response(self, service):
        prompt = "Sample prompt"
        non_json_response = "This is not a JSON response"
        service.ai_provider.generate_response.return_value = non_json_response
        response = service._call_llm(prompt)
        assert response == non_json_response

    def test_call_llm_returns_incomplete_json_response(self, service):
        prompt = "Sample prompt"
        incomplete_json_response = '{"evidence": [], "ai_analysis": "Analysis"}'  # Missing recommendations and risk_classification
        service.ai_provider.generate_response.return_value = incomplete_json_response
        response = service._call_llm(prompt)
        assert response == incomplete_json_response


class TestGetHealthScorePrompt:
    def test_get_health_score_prompt_with_valid_node(self, service, fake_db):
        fake_db.run.return_value = make_neo4j_result(
            [
                {
                    "main_node": {
                        "id": "1",
                        "title": "Main Node",
                        "label": "Artifact",
                        "degree": 2,
                    },
                    "connected": [
                        {"id": "2", "title": "Connected Node 1", "label": "Story"},
                        {"id": "3", "title": "Connected Node 2", "label": "Bug"},
                    ],
                    "relationships": ["rel1", "rel2"],
                    "degree": 2,
                    "total_edges": 2,
                }
            ]
        )
        result = service.build_health_score_prompt("1")
        assert result is not None
        assert isinstance(result, str)

    def test_get_health_score_prompt_node_not_found(self, service, fake_db):
        fake_db.run.return_value = make_neo4j_result([])
        result = service.build_health_score_prompt("nonexistent_node_id")
        assert result is None
