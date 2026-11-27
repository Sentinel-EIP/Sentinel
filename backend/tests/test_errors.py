"""Format d'erreur unique, et aucune fuite d'information sur une 500."""

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.errors import install_error_handlers, status_code_name
from app.main import app as main_app

demo = FastAPI()
install_error_handlers(demo)


class Payload(BaseModel):
    n: int


@demo.get("/boom")
def boom() -> None:
    raise RuntimeError("mot de passe secret dans le message")


@demo.get("/teapot")
def teapot() -> None:
    raise HTTPException(
        status_code=401, detail="Jeton absent", headers={"WWW-Authenticate": "Bearer"}
    )


@demo.post("/payload")
def payload(body: Payload) -> int:
    return body.n


client = TestClient(demo, raise_server_exceptions=False)


def test_erreur_inattendue_sans_detail() -> None:
    r = client.get("/boom")
    assert r.status_code == 500
    assert r.json() == {"error": {"code": "internal_error", "message": "Erreur interne"}}
    assert "secret" not in r.text


def test_http_exception_garde_ses_en_tetes() -> None:
    r = client.get("/teapot")
    assert r.status_code == 401
    assert r.json()["error"] == {"code": "unauthorized", "message": "Jeton absent"}
    assert r.headers["WWW-Authenticate"] == "Bearer"


def test_requete_invalide() -> None:
    r = client.post("/payload", json={"n": "pas un entier"})
    assert r.status_code == 422
    body = r.json()["error"]
    assert body["code"] == "validation_error"
    assert body["details"][0]["loc"] == ["body", "n"]


def test_route_inconnue_sur_l_api() -> None:
    r = TestClient(main_app).get("/nexiste-pas")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "not_found"


def test_nom_de_code_inconnu() -> None:
    assert status_code_name(599) == "http_599"
