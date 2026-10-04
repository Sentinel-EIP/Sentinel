"""Fixtures communes. Les tests tournent sur SQLite en memoire : les routes
n'utilisent que du SQL portable. Ce qui est propre a TimescaleDB (hypertable,
compression) est verifie par le smoke test de la CI (migrations + alembic check)."""

import os
from collections.abc import Generator

import pytest
from sqlalchemy import Engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401 - enregistre les tables

os.environ.setdefault("API_SECRET_KEY", "test-" + "x" * 40)


@pytest.fixture
def engine() -> Generator[Engine, None, None]:
    eng = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def session(engine: Engine) -> Generator[Session, None, None]:
    with Session(engine) as s:
        yield s
