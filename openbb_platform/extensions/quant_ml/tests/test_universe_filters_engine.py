"""Universe metrics/snapshot hardening tests."""

from __future__ import annotations

from datetime import date

import pandas as pd
from openbb_quant_ml.service.universe_engine import build_universe_snapshot
from openbb_quant_ml.service.universe_filters import build_symbol_metrics


def test_build_symbol_metrics_handles_missing_volume_column() -> None:
    market_long = pd.DataFrame(
        [
            {"date": "2026-02-20", "symbol": "AAPL", "close": 100.0},
            {"date": "2026-02-21", "symbol": "AAPL", "close": 102.0},
        ]
    )
    security_master = pd.DataFrame(
        [
            {
                "symbol": "AAPL",
                "company_id": "AAPL",
                "float_mcap_usd": 2_000_000_000.0,
                "sector_l1": "technology",
                "country": "US",
            }
        ]
    )

    out = build_symbol_metrics(
        market_long=market_long,
        security_master=security_master,
        as_of_date=date(2026, 2, 21),
    )
    assert len(out) == 1
    row = out.iloc[0]
    assert float(row["adv20_usd"]) == 0.0
    assert float(row["trading_frequency_63d"]) == 0.0
    assert float(row["annual_turnover_ratio_252d"]) == 0.0


def test_build_universe_snapshot_sanitizes_nan_adv20(
    monkeypatch, tmp_path
) -> None:
    run_dir = tmp_path / "run-1"
    metric_frame = pd.DataFrame(
        [
            {
                "symbol": "AAPL",
                "company_id": "AAPL",
                "sector_l1": "technology",
                "country": "US",
                "adv20_usd": float("nan"),
            }
        ]
    )

    monkeypatch.setattr(
        "openbb_quant_ml.service.universe_engine.get_run_dir",
        lambda _run_id: run_dir,
    )
    monkeypatch.setattr(
        "openbb_quant_ml.service.universe_engine.load_security_master",
        lambda symbols, run_dir: pd.DataFrame({"symbol": list(symbols)}),
    )
    monkeypatch.setattr(
        "openbb_quant_ml.service.universe_engine.build_symbol_metrics",
        lambda **_kwargs: metric_frame.copy(),
    )
    monkeypatch.setattr(
        "openbb_quant_ml.service.universe_engine.apply_u0_filters",
        lambda frame, *_args, **_kwargs: frame.copy(),
    )
    monkeypatch.setattr(
        "openbb_quant_ml.service.universe_engine.select_pricing_vehicle",
        lambda frame, **_kwargs: frame.copy(),
    )
    monkeypatch.setattr(
        "openbb_quant_ml.service.universe_engine.apply_u1_filters",
        lambda frame, *_args, **_kwargs: frame.copy(),
    )
    monkeypatch.setattr(
        "openbb_quant_ml.service.universe_engine.apply_u2_filters",
        lambda frame, *_args, **_kwargs: frame.copy(),
    )
    monkeypatch.setattr(
        "openbb_quant_ml.service.universe_engine.append_exclusions",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "openbb_quant_ml.service.universe_engine.get_universe_policy",
        lambda: {"missing_data_policy": "strict_exclude", "rebalance_policy": {}},
    )

    payload = build_universe_snapshot(
        run_id="run-1",
        universe_id="default",
        as_of_date=date(2026, 2, 21),
        portfolio_mode="long_only",
        market_long=pd.DataFrame(
            [{"date": "2026-02-21", "symbol": "AAPL", "close": 100.0}]
        ),
    )

    assert payload["symbol_metrics"]["AAPL"]["adv20_usd"] == 0.0
