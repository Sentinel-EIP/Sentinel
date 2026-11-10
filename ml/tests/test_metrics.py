from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_metrics_expose_les_requetes_http() -> None:
    client.get("/health")
    response = client.get("/metrics")
    assert response.status_code == 200
    assert 'http_requests_total{handler="/health"' in response.text
