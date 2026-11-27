"""Format d'erreur unique de l'API.

Toute erreur renvoie {"error": {"code": ..., "message": ...}} (plus "details"
pour une requete invalide). Une exception non prevue devient une 500 sans
detail interne : la trace part dans les logs, jamais dans la reponse.
"""

from collections.abc import Mapping
from http import HTTPStatus
from typing import Any, cast

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import log


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: Any = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    error: dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        error["details"] = details
    return JSONResponse(
        {"error": error}, status_code=status_code, headers=dict(headers) if headers else None
    )


def status_code_name(status_code: int) -> str:
    """404 -> not_found ; code inconnu -> http_<code>."""
    try:
        return HTTPStatus(status_code).phrase.lower().replace(" ", "_").replace("-", "_")
    except ValueError:
        return f"http_{status_code}"


# Starlette type les gestionnaires en (Request, Exception) : chacun n'est
# enregistre que pour son type d'exception, d'ou le cast.
async def http_error(_: Request, error: Exception) -> JSONResponse:
    exc = cast(StarletteHTTPException, error)
    return error_response(
        exc.status_code,
        status_code_name(exc.status_code),
        str(exc.detail),
        headers=exc.headers,
    )


async def validation_error(_: Request, error: Exception) -> JSONResponse:
    exc = cast(RequestValidationError, error)
    details = [
        {"loc": list(e.get("loc", ())), "message": e.get("msg", ""), "type": e.get("type", "")}
        for e in exc.errors()
    ]
    return error_response(422, "validation_error", "Requete invalide", jsonable_encoder(details))


async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    log.error(
        "api.unexpected_error",
        method=request.method,
        path=request.url.path,
        error=type(exc).__name__,
        exc_info=exc,
    )
    return error_response(500, "internal_error", "Erreur interne")


def install_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, http_error)
    app.add_exception_handler(RequestValidationError, validation_error)
    app.add_exception_handler(Exception, unexpected_error)
