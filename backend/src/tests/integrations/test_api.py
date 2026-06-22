import pytest
from fastapi.testclient import TestClient
from backend.src.main import app

client = TestClient(app)


@pytest.mark.parametrize("endpoint", ["/", "/health"])
def test_endpoint(endpoint):
    
    """Test the endpoint returns status 200"""
    response = client.get(endpoint)
    assert response.status_code == 200
