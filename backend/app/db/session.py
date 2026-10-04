from collections.abc import Generator

from sqlmodel import Session, create_engine

from app.core.config import get_settings

# connect_timeout : sans lui, libpq attend indefiniment une base injoignable.
engine = create_engine(
    get_settings().database_url,
    pool_pre_ping=True,
    echo=False,
    connect_args={"connect_timeout": 3},
)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
