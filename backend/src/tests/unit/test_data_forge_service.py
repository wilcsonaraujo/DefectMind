from unittest.mock import MagicMock

import pytest

from backend.src.modules.data_forge.service import DataForgeService

FAKE_EMBEDDING = [0.1] * 384

FAKE_BATCH = {
    "stories": [{"temp_id": 1, "title": "Login Story", "description": "User login flow"}],
    "requirements": [{"temp_id": 1, "story_temp_id": 1, "title": "Login requirement", "description": "Must validate credentials", "priority": "High"}],
    "testcases": [{"temp_id": 1, "requirement_temp_id": 1, "title": "Test login", "steps": "Open app", "expected_result": "Logged in"}],
    "bug_reports": [{"temp_id": 1, "testcase_temp_id": 1, "title": "Login fails", "description": "Error on submit", "severity": "High"}],
    "incidents": [{"temp_id": 1, "bug_temp_id": 1, "title": "Prod incident", "description": "Users locked out", "impact": "Critical"}],
    "postmortems": [{"temp_id": 1, "incident_temp_id": 1, "title": "Postmortem Title", "root_cause": "DB timeout", "resolution": "Scaled DB", "lessons_learned": "Add alerts"}],
}


@pytest.fixture
def service():
    fake_ai = MagicMock()
    fake_ai.generate_json.return_value = FAKE_BATCH

    fake_neo4j = MagicMock()
    fake_neo4j.run.return_value = []

    fake_embedding = MagicMock()
    fake_embedding.encode.return_value = FAKE_EMBEDDING

    return DataForgeService(
        ai_provider=fake_ai,
        neo4j_session=fake_neo4j,
        embedding_service=fake_embedding,
    )


def test_generate_returns_counters(service):
    """generate() deve retornar dict com contadores das entidades criadas."""
    result = service.generate(num_stories=1, batch_size=1)
    assert isinstance(result, dict)
    assert result["stories"] >= 1
    assert result["batches_processed"] == 1


def test_generate_calls_embedding_service(service):
    """generate() deve chamar o EmbeddingService para cada entidade do lote."""
    service.generate(num_stories=1, batch_size=1)
    # 6 entidades × 1 lote = pelo menos 6 chamadas ao encode
    assert service.embedding.encode.call_count >= 6


def test_generate_calls_neo4j(service):
    """generate() deve executar queries no Neo4j."""
    service.generate(num_stories=1, batch_size=1)
    assert service.db.run.call_count > 0


def test_generate_skips_invalid_batch():
    """generate() deve pular lotes com JSON inválido sem lançar exceção."""
    fake_ai = MagicMock()
    fake_ai.generate_json.return_value = {"invalid": "data"}

    fake_embedding = MagicMock()
    fake_embedding.encode.return_value = FAKE_EMBEDDING

    svc = DataForgeService(
        ai_provider=fake_ai,
        neo4j_session=MagicMock(),
        embedding_service=fake_embedding,
    )
    result = svc.generate(num_stories=1, batch_size=1)
    assert isinstance(result, dict)
    assert result["batches_failed"] == 1
