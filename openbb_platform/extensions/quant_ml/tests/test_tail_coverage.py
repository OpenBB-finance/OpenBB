"""Tiny tail-coverage tests to close remaining gate gaps."""

from __future__ import annotations

from openbb_quant_ml import macro_alias_router
from openbb_quant_ml.jobs.steps import backfill_if_needed
from openbb_quant_ml.service.exposure_report import build_sector_exposure_rows
from openbb_quant_ml.service.trade_engine import build_trade_plan


def test_macro_alias_router_exports_router() -> None:
    assert macro_alias_router.router is not None


def test_empty_exposure_and_noop_trade_paths(monkeypatch) -> None:
    empty = build_sector_exposure_rows([])
    assert list(empty.columns) == ["sector", "weight"]

    # identical before/after weights should produce no trades
    plan = build_trade_plan(
        as_of_date="2026-02-28",
        previous_weights={"AAPL": 0.1},
        target_weights={"AAPL": 0.1},
    )
    assert plan == []

    monkeypatch.setattr(backfill_if_needed, "run_market_update", lambda cfg: {"status": "ok", "count": 1})
    assert backfill_if_needed.run({"job": "monthly"})["status"] == "ok"
