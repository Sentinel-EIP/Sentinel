from datetime import UTC, datetime

from sqlmodel import Session, select

from app.models import AiResult, AuditLog, Candle, User


def test_tables_et_relations(session: Session) -> None:
    user = User(username="alice", password_hash="h")
    session.add(user)
    session.commit()
    session.refresh(user)

    ts = datetime(2026, 10, 1, tzinfo=UTC)
    session.add(
        Candle(
            symbol="BTCEUR", timeframe="1h", ts=ts, open=1, high=2, low=0.5, close=1.5, volume=10
        )
    )
    session.add(AuditLog(user_id=user.id, action="login", detail={"ok": True}))
    session.add(
        AiResult(
            kind="volatility_cone",
            symbol="BTCEUR",
            model_version="v1",
            confidence=0.8,
            explanation="test",
            value={"lower": 1.0, "upper": 2.0},
            requested_by=user.id,
        )
    )
    session.commit()

    assert session.exec(select(Candle)).one().close == 1.5
    assert session.exec(select(AuditLog)).one().detail == {"ok": True}
    result = session.exec(select(AiResult)).one()
    assert result.value["upper"] == 2.0
    assert result.created_at is not None
