from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_models_inventory() -> None:
    body = client.get("/models").json()
    assert "available" in body
