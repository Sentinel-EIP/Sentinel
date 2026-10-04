"""Tables : utilisateurs, journal d'actions, bougies (hypertable), resultats IA.

Revision ID: 0001
Revises:
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TS = sa.DateTime(timezone=True)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False),
        sa.Column("created_at", TS, nullable=False),
    )
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("detail", sa.JSON, nullable=False),
        sa.Column("created_at", TS, nullable=False),
    )
    op.create_index("ix_audit_logs_user_created", "audit_logs", ["user_id", "created_at"])

    op.create_table(
        "candles",
        sa.Column("symbol", sa.String(20), primary_key=True),
        sa.Column("timeframe", sa.String(8), primary_key=True),
        sa.Column("ts", TS, primary_key=True),
        sa.Column("open", sa.Float, nullable=False),
        sa.Column("high", sa.Float, nullable=False),
        sa.Column("low", sa.Float, nullable=False),
        sa.Column("close", sa.Float, nullable=False),
        sa.Column("volume", sa.Float, nullable=False),
    )
    # Hypertable TimescaleDB, partitionnee par mois. La cle primaire (symbol,
    # timeframe, ts) sert d'index aux lectures par symbole et periode : pas
    # d'index par defaut en plus (et `alembic check` reste sans ecart).
    # Les fonctions TimescaleDB vivent dans public, la table dans le schema du
    # role applicatif (ADR 0001) : noms non qualifies, resolus par search_path.
    op.execute(
        "SELECT create_hypertable('candles', 'ts', "
        "chunk_time_interval => INTERVAL '30 days', create_default_indexes => false)"
    )
    # Compression des bougies de plus de 30 jours : ~10x moins de disque, et
    # les lectures par symbole restent rapides (segmentby).
    op.execute(
        "ALTER TABLE candles SET (timescaledb.compress, "
        "timescaledb.compress_segmentby = 'symbol, timeframe', "
        "timescaledb.compress_orderby = 'ts DESC')"
    )
    op.execute("SELECT add_compression_policy('candles', INTERVAL '30 days')")

    op.create_table(
        "ai_results",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("symbol", sa.String(20), nullable=False),
        sa.Column("model_version", sa.String(32), nullable=False),
        sa.Column("confidence", sa.Float, nullable=False),
        sa.Column("reliability", sa.Float),
        sa.Column("explanation", sa.Text, nullable=False),
        sa.Column("value", sa.JSON, nullable=False),
        sa.Column("requested_by", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", TS, nullable=False),
    )
    op.create_index(
        "ix_ai_results_symbol_kind_created", "ai_results", ["symbol", "kind", "created_at"]
    )


def downgrade() -> None:
    op.drop_table("ai_results")
    op.execute("SELECT remove_compression_policy('candles', if_exists => true)")
    op.drop_table("candles")
    op.drop_table("audit_logs")
    op.drop_table("users")
