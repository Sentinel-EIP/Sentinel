"""/health/ready : 200 si tout repond, 503 sinon, sans detail d'erreur."""

from typing import Any

import httpx
import pytest
from fastapi.testclient import TestClient

from app.api.routes import health
from app.main import app

client = TestClient(app)


def fake_ml(status_code: int | None) -> type:
    """Client httpx factice : repond status_code, ou leve si None."""

    class FakeClient:
        def __init__(self, **_: Any) -> None:
            pass

        async def __aenter__(self) -> "FakeClient":
            return self

        async def __aexit__(self, *_: Any) -> None:
            pass

        async def get(self, url: str) -> httpx.Response:
            if status_code is None:
                raise httpx.ConnectError("injoignable")
            return httpx.Response(status_code)

    return FakeClient


def db_ok() -> None:
    pass


def db_down() -> None:
    raise ConnectionError("secret interne")


@pytest.mark.parametrize(
    ("db", "ml_status", "code", "checks"),
    [
        (db_ok, 200, 200, {"database": "ok", "ml": "ok"}),
        (db_down, 200, 503, {"database": "error", "ml": "ok"}),
        (db_ok, 500, 503, {"database": "ok", "ml": "error"}),
        (db_ok, None, 503, {"database": "ok", "ml": "error"}),
    ],
)
def test_ready(
    monkeypatch: pytest.MonkeyPatch,
    db: Any,
    ml_status: int | None,
    code: int,
    checks: dict[str, str],
) -> None:
    monkeypatch.setattr(health, "_check_database", db)
    monkeypatch.setattr(health.httpx, "AsyncClient", fake_ml(ml_status))
    response = client.get("/health/ready")
    assert response.status_code == code
    assert response.json()["checks"] == checks
    assert "secret" not in response.text
