import os

# MUST be set before any project imports — config.py reads these at module load time
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("APP_NAME", "DefectMind")
os.environ.setdefault("APP_VERSION", "0.1.0")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-insecure")
os.environ.setdefault("NEO4J_URI", "")
os.environ.setdefault("NEO4J_USER", "")
os.environ.setdefault("NEO4J_PASSWORD", "")


import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import sessionmaker
from backend.src.core.database import Base, get_db
from backend.src.main import app
from backend.src.core.neo4j_db import get_neo4j_session
from unittest.mock import MagicMock, patch
from backend.src.core.ai.gemini_provider import GeminiProvider

# Import models to ensure they are registered with SQLAlchemy
import backend.src.models  # noqa: F401

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a new database session for a test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Test client that uses the test database session."""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


class FakeNeo4jSession:
    def run(self, query, **kwargs):
        return []


@pytest.fixture(scope="function", autouse=True)
def override_neo4j(client):
    def fake_session():
        yield FakeNeo4jSession()

    app.dependency_overrides[get_neo4j_session] = fake_session
    yield
    app.dependency_overrides.pop(get_neo4j_session, None)


@pytest.fixture
def provider():
    with patch("google.genai.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        yield GeminiProvider(api_key="fake-key")
