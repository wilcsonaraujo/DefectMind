from unittest.mock import MagicMock

import pytest


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
