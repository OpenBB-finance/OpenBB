"""Walk-forward backtest service tests."""

from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import pytest

from openbb_quant_ml.models import WalkForwardBacktestRequest
from openbb_quant_ml.service import walkforward_backtest as wf


def _build_predictions(start: str, end: str) -> pd.DataFrame:
    dates = pd.date_range(start, end, freq="B")
    rows: list[dict[str, object]] = []
    for idx, date_value in enumerate(dates):
        for symbol, base in [("AAA", 0.02), ("BBB", 0.01), ("CCC", -0.005)]:
            rows.append(
                {
                    "date": date_value,
                    "symbol": symbol,
                    "predicted_return": float(base + (idx % 5) * 0.001),
                }
            )
    return pd.DataFrame(rows)


def _build_market(start: str, end: str) -> pd.DataFrame:
    dates = pd.date_range(start, end, freq="B")
    rows: list[dict[str, object]] = []
    for date_idx, date_value in enumerate(dates):
        for symbol, px in [("AAA", 100.0), ("BBB", 80.0), ("CCC", 60.0)]:
            close = float(px + date_idx * 0.1)
            rows.append(
                {
                    "date": date_value,
                    "symbol": symbol,
                    "open": close * 0.998,
                    "close": close,
                }
            )
    return pd.DataFrame(rows)


def test_build_walkforward_predictions_has_no_lookahead():
    predictions = _build_predictions("2025-01-01", "2025-06-30")
    trade_dates = pd.DatetimeIndex(pd.date_range("2025-03-01", "2025-06-30", freq="B"))
    _, windows = wf._build_walkforward_predictions(
        predictions=predictions,
        trade_dates=trade_dates,
        start_date=pd.Timestamp("2025-03-01").date(),
        end_date=pd.Timestamp("2025-06-30").date(),
        min_history_days=126,
    )
    assert windows
    for row in windows:
        assert row["train_until"] < row["rebalance_date"]


def test_walkforward_submit_and_status(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    run_id = "trn-260219-001"
    run_dir = tmp_path / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    _build_predictions("2025-01-01", "2025-08-31").to_parquet(
        run_dir / "predictions_lgbm_ranker.parquet",
        index=False,
    )
    _build_market("2025-01-01", "2025-08-31").to_parquet(
        run_dir / "market_data.parquet",
        index=False,
    )

    monkeypatch.setattr(wf, "WALKFORWARD_JOBS_PATH", tmp_path / "walkforward_jobs.json")
    monkeypatch.setattr(
        wf, "get_run_dir", lambda rid: run_dir if rid == run_id else tmp_path / rid
    )

    submit = wf.submit_walkforward_backtest(
        WalkForwardBacktestRequest(
            run_id=run_id,
            model_name="lgbm_ranker",
            start_date=pd.Timestamp("2025-03-01").date(),
            end_date=pd.Timestamp("2025-08-31").date(),
            min_history_days=126,
        )
    )
    assert submit.status == "queued"

    deadline = time.time() + 8.0
    status = wf.get_walkforward_backtest_status(submit.job_id)
    while status.status in {"queued", "running"} and time.time() < deadline:
        time.sleep(0.05)
        status = wf.get_walkforward_backtest_status(submit.job_id)

    assert status.status == "completed"
    assert status.metrics is not None
    assert status.train_windows
