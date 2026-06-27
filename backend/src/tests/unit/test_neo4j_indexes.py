from unittest.mock import MagicMock, call # noqa: F401
import pytest # noqa: F401

from backend.src.core.neo4j_indexes import create_vector_indexes


def test_create_vector_indexes_calls_run_six_times():
    """Should be execute exactly 6 queries — one per label."""
    mock_session = MagicMock()

    create_vector_indexes(mock_session)

    assert mock_session.run.call_count == 6


def test_create_vector_indexes_uses_correct_labels():
    """Should be create indices for the 6 expected labels."""
    mock_session = MagicMock()

    create_vector_indexes(mock_session)

    calls_text = " ".join(str(c) for c in mock_session.run.call_args_list)

    for label in ["Story", "Requirement", "TestCase", "BugReport", "Incident", "PostMortem"]:
        assert label in calls_text, f"Label '{label}' don't found in executed queries"


def test_create_vector_indexes_continues_on_error():
    """If an index fails, the others should still be created."""
    mock_session = MagicMock()
    mock_session.run.side_effect = [Exception("Neo4j error"), None, None, None, None, None]

    # Não deve lançar exceção — o erro é capturado internamente
    create_vector_indexes(mock_session)

    assert mock_session.run.call_count == 6
