"""Inscription, connexion, jetons et journal d'actions."""

from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core import security
from app.core.config import get_settings

CREDS = {"username": "alice", "password": "mot-de-passe-solide"}


def test_parcours_complet(client: TestClient, auth_headers: dict[str, str]) -> None:
    me = client.get("/users/me", headers=auth_headers)
    assert me.status_code == 200
    assert me.json()["username"] == "alice"
    assert "password_hash" not in me.text

    actions = [a["action"] for a in client.get("/users/me/activity", headers=auth_headers).json()]
    assert set(actions) == {"register", "login"}


def test_nom_deja_pris(client: TestClient) -> None:
    client.post("/auth/register", json=CREDS)
    r = client.post("/auth/register", json=CREDS)
    assert r.status_code == 409


def test_mot_de_passe_trop_court(client: TestClient) -> None:
    r = client.post("/auth/register", json={"username": "bob", "password": "court"})
    assert r.status_code == 422


def test_inscription_fermee(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(get_settings(), "AUTH_ALLOW_REGISTRATION", False)
    assert client.post("/auth/register", json=CREDS).status_code == 403


@pytest.mark.parametrize("username", ["alice", "inconnu"])
def test_connexion_refusee_meme_message(client: TestClient, username: str) -> None:
    client.post("/auth/register", json=CREDS)
    r = client.post("/auth/login", json={"username": username, "password": "mauvais-mot-de-passe"})
    assert r.status_code == 401
    assert r.json()["error"]["message"] == "Identifiants invalides"


def test_echec_journalise(client: TestClient) -> None:
    client.post("/auth/register", json=CREDS)
    client.post("/auth/login", json={**CREDS, "password": "mauvais-mot-de-passe"})
    token = client.post("/auth/login", json=CREDS).json()["access_token"]
    activity = client.get("/users/me/activity", headers={"Authorization": f"Bearer {token}"})
    assert "login_failed" in [a["action"] for a in activity.json()]


@pytest.mark.parametrize(
    "headers",
    [{}, {"Authorization": "Bearer pas-un-jeton"}, {"Authorization": "Basic abc"}],
)
def test_route_protegee(client: TestClient, headers: dict[str, str]) -> None:
    r = client.get("/users/me", headers=headers)
    assert r.status_code == 401
    assert r.headers["WWW-Authenticate"] == "Bearer"


def test_jeton_expire(client: TestClient) -> None:
    client.post("/auth/register", json=CREDS)
    past = datetime.now(UTC) - timedelta(hours=2)
    token = jwt.encode(
        {"sub": "1", "iat": past, "exp": past + timedelta(minutes=5)},
        get_settings().API_SECRET_KEY,
        algorithm="HS256",
    )
    assert client.get("/users/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_jeton_signe_avec_une_autre_cle(client: TestClient) -> None:
    client.post("/auth/register", json=CREDS)
    token = jwt.encode({"sub": "1", "exp": datetime.now(UTC) + timedelta(minutes=5)}, "y" * 40)
    assert client.get("/users/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_cle_trop_courte_refusee(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(get_settings(), "API_SECRET_KEY", "court")
    with pytest.raises(RuntimeError, match="32 caracteres"):
        security.check_secret_key()


def test_hash_et_verification() -> None:
    h = security.hash_password("mot-de-passe-solide")
    assert security.verify_password("mot-de-passe-solide", h)
    assert not security.verify_password("autre", h)
    assert not security.verify_password("compte-inexistant", None)
    assert not security.verify_password("x", "pas-un-hash")
