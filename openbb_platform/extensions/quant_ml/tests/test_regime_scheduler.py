"""Regime scheduler tests."""

from __future__ import annotations

from openbb_quant_ml.service import regime_scheduler as rs


def test_scheduler_start_returns_false_when_apscheduler_missing(monkeypatch) -> None:
    monkeypatch.setattr(rs, "BackgroundScheduler", None)
    monkeypatch.setattr(rs, "_scheduler", None)

    assert rs.start_regime_scheduler() is False
    status = rs.get_scheduler_status()
    assert status["running"] is False


def test_trigger_regime_refresh_calls_refresh_hooks(monkeypatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(rs, "_refresh_market_regime", lambda: calls.append("market"))
    monkeypatch.setattr(rs, "_daily_fred_update", lambda: calls.append("fred"))

    payload = rs.trigger_regime_refresh()
    assert payload["status"] == "ok"
    assert calls == ["market", "fred"]
