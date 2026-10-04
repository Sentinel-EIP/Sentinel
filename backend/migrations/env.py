"""Environnement Alembic.

Les migrations tournent avec le role APPLICATIF, jamais en superutilisateur
(docs/adr/0001-schema-applicatif-postgres.md) : les tables et la table
alembic_version sont creees dans le schema du role, premier de son search_path
("$user", public). Une connexion superutilisateur est refusee.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection, engine_from_config, pool, text
from sqlmodel import SQLModel

import app.models  # noqa: F401 - enregistre les tables dans SQLModel.metadata
from app.core.config import get_settings

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", get_settings().database_url.replace("%", "%%"))
target_metadata = SQLModel.metadata


def refuse_superuser(connection: Connection) -> None:
    is_super = connection.execute(
        text("SELECT rolsuper FROM pg_roles WHERE rolname = current_user")
    ).scalar()
    # Termine la transaction ouverte par cette requete : sinon celle des
    # migrations s'y imbrique et n'est jamais validee (rollback a la fermeture).
    connection.commit()
    if is_super:
        raise SystemExit(
            "Migrations refusees en superutilisateur : utiliser le role applicatif "
            "(APP_DB_USER). Voir docs/adr/0001-schema-applicatif-postgres.md."
        )


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        refuse_superuser(connection)
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
