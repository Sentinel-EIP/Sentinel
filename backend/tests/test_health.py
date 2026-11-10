from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_is_valid() -> None:
    """Test contract minimal : le schema OpenAPI se genere sans erreur."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "paths" in response.json()
