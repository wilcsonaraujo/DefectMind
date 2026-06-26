import os
os.environ.setdefault("GEMINI_API_KEY", "fake-key-for-tests")

import pytest
from backend.src.core.ai.provider import AIProvider
from backend.src.modules.data_forge.service import DataForgeService


# --- Fixtures ---

VALID_BATCH = {
    "stories": [{"temp_id": 1, "title": "PIX Transfer", "description": "User sends PIX"}],
    "requirements": [{"temp_id": 1, "story_temp_id": 1, "description": "Validate CPF", "priority": "High"}],
    "testcases": [{"temp_id": 1, "requirement_temp_id": 1, "title": "TC-01", "steps": "Enter CPF", "expected_result": "CPF validated"}],
    "bug_reports": [{"temp_id": 1, "testcase_temp_id": 1, "title": "BUG-01", "description": "CPF not validated", "severity": "Critical"}],
    "incidents": [{"temp_id": 1, "bug_temp_id": 1, "title": "INC-01", "description": "System down", "impact": "High"}],
    "postmortems": [{"temp_id": 1, "incident_temp_id": 1, "root_cause": "Memory leak", "resolution": "Restart", "lessons_learned": "Add monitoring"}],
}


class FakeAIProvider(AIProvider):
    def generate_json(self, prompt: str, schema=None) -> dict:
        return VALID_BATCH

    def _call_model(self, prompt: str, config=None) -> str:
        return ""


class FakeNeo4jSession:
    def __init__(self):
        self.calls = []

    def run(self, query, **kwargs):
        self.calls.append((query, kwargs))
        return []


@pytest.fixture
def service():
    return DataForgeService(
        ai_provider=FakeAIProvider(),
        neo4j_session=FakeNeo4jSession(),
    )


# --- Tests ---

def test_generate_returns_counters(service):
    """generate() must return a dict with counters of the created entities."""
    result = service.generate(num_stories=1, batch_size=1)
    assert isinstance(result, dict)
    assert "stories" in result
    assert result["stories"] >= 1


def test_generate_calls_neo4j(service):
    """generate() must execute queries in Neo4j for each entity."""
    service.generate(num_stories=1, batch_size=1)
    assert len(service.db.calls) > 0


def test_generate_skips_invalid_batch():
    """generate() should skip batches with invalid JSON without throwing an exception."""

    class BrokenAIProvider(AIProvider):
        def generate_json(self, prompt: str, schema=None) -> dict:
            return {"invalid": "data"}  # it doesn't pass through DataForgeOutput

        def _call_model(self, prompt: str, config=None) -> str:
            return ""

    svc = DataForgeService(
        ai_provider=BrokenAIProvider(),
        neo4j_session=FakeNeo4jSession(),
    )
    # It must not throw an exception — it must silently skip the batch.
    result = svc.generate(num_stories=1, batch_size=1)
    assert isinstance(result, dict)
