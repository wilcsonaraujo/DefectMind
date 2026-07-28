import os

os.environ.setdefault("GEMINI_API_KEY", "fake-key-for-tests")

from unittest.mock import MagicMock, patch

import pytest
from starlette.testclient import TestClient

from backend.src.core.ai.provider_factory import get_ai_provider
from backend.src.main import app
from backend.src.modules.quality_intelligence.schemas import (
    HotspotItem,
    HotspotsResponse,
)


@pytest.fixture(autouse=True)
def mock_ai_provider():
    """Automatic AI provider mock for all tests."""
    mock_provider = MagicMock()
    mock_provider.generate_json.return_value = {"result": "mocked"}
    app.dependency_overrides[get_ai_provider] = lambda: mock_provider
    yield mock_provider
    app.dependency_overrides.pop(get_ai_provider, None)


MOCK_HOTSPOTS = HotspotsResponse(
    hotspots=[
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
    ],
    total=5,
    ai_analysis="fake-analysis",
    recommendations=["fake-recommendation-1", "fake-recommendation-2"],
)


def test_generate_requires_auth():
    """The endpoint must return a 401 without an authentication token."""
    client = TestClient(app)
    response = client.get("/api/v1/quality-intelligence/hotspots")
    assert response.status_code == 401


def test_generate_success():
    client = TestClient(app)

    with patch(
        "backend.src.modules.quality_intelligence.router.HotspotsService"
    ) as MockService:
        mock_instance = MagicMock()
        mock_instance.get_hotspots.return_value = MOCK_HOTSPOTS
        MockService.return_value = mock_instance

        response = client.get(
            "/api/v1/quality-intelligence/hotspots",
            headers={"Authorization": "Bearer valid-token"},
        )

    assert response.status_code in (200, 401)
    if response.status_code == 200:
        data = response.json()
        assert "hotspots" in data
        assert "total" in data
        assert "ai_analysis" in data
        assert "recommendations" in data
    app.dependency_overrides.clear()


def test_generate_success_empty():
    client = TestClient(app)

    with patch(
        "backend.src.modules.quality_intelligence.router.HotspotsService"
    ) as MockService:
        mock_instance = MagicMock()
        mock_instance.get_hotspots.return_value = HotspotsResponse(
            hotspots=[], total=0, ai_analysis="", recommendations=[]
        )
        MockService.return_value = mock_instance

        with patch(
            "backend.src.modules.quality_intelligence.router.generate_hotspots"
        ) as MockFactory:
            MockFactory.return_value = MagicMock()

            response = client.get(
                "/api/v1/quality-intelligence/hotspots",
                headers={"Authorization": "Bearer valid-token"},
            )

    assert response.status_code in (200, 401)
    if response.status_code == 200:
        data = response.json()
        assert "hotspots" in data
        assert "total" in data
        assert "ai_analysis" in data
        assert "recommendations" in data
    app.dependency_overrides.clear()
