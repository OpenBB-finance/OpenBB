"""Staged universe (U0/U1/U2) construction and artifact helpers."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from openbb_quant_ml.service.exclusions_logger import append_exclusions
from openbb_quant_ml.service.pricing_vehicle import select_pricing_vehicle
from openbb_quant_ml.service.security_master import load_security_master
from openbb_quant_ml.service.storage import get_run_dir, save_json, save_parquet_atomic
from openbb_quant_ml.service.universe_filters import (
    apply_u0_filters,
    apply_u1_filters,
    apply_u2_filters,
    build_symbol_metrics,
)
from openbb_quant_ml.service.universe_policy import get_universe_policy


def universe_snapshot_dir(run_dir: Path, as_of_date: date) -> Path:
    """Return per-date universe snapshot directory."""
    return run_dir / "universe" / as_of_date.isoformat()


def _write_frame(path: Path, frame: pd.DataFrame) -> None:
    if frame.empty:
        empty = pd.DataFrame(columns=list(frame.columns) if hasattr(frame, "columns") else [])
        save_parquet_atomic(path, empty, index=False)
        return
    save_parquet_atomic(path, frame, index=False)


def _as_symbols(frame: pd.DataFrame) -> list[str]:
    if frame.empty or "symbol" not in frame.columns:
        return []
    return sorted({str(item).strip().upper() for item in frame["symbol"].tolist() if str(item).strip()})


def build_universe_snapshot(
    *,
    run_id: str,
    universe_id: str,
    as_of_date: date,
    portfolio_mode: str,
    market_long: pd.DataFrame,
) -> dict[str, Any]:
    """Build and persist one staged universe snapshot."""
    run_dir = get_run_dir(run_id)
    policy = get_universe_policy()
    missing_data_policy = str(policy.get("missing_data_policy", "strict_exclude")).strip().lower()

    symbols = sorted(
        {
            str(item).strip().upper()
            for item in market_long.get("symbol", pd.Series(dtype=str)).tolist()
            if str(item).strip()
        }
    )
    security_master = load_security_master(symbols=symbols, run_dir=run_dir)
    metric_frame = build_symbol_metrics(
        market_long=market_long,
        security_master=security_master,
        as_of_date=as_of_date,
    )
    excluded: list[dict[str, Any]] = []
    u0 = apply_u0_filters(
        metric_frame,
        policy,
        as_of_date=as_of_date,
        missing_data_policy=missing_data_policy,
        excluded=excluded,
    )
    u0 = select_pricing_vehicle(u0, as_of_date=as_of_date, excluded=excluded)
    u1 = apply_u1_filters(
        u0,
        policy,
        as_of_date=as_of_date,
        missing_data_policy=missing_data_policy,
        excluded=excluded,
    )
    u2 = apply_u2_filters(
        u1,
        policy,
        as_of_date=as_of_date,
        portfolio_mode=portfolio_mode,
        excluded=excluded,
    )

    stage_counts = {
        "u0": int(len(u0)),
        "u1": int(len(u1)),
        "u2": int(len(u2)),
        "excluded": int(len(excluded)),
    }

    snap_dir = universe_snapshot_dir(run_dir, as_of_date)
    snap_dir.mkdir(parents=True, exist_ok=True)
    _write_frame(snap_dir / "u0_snapshot.parquet", u0)
    _write_frame(snap_dir / "u1_snapshot.parquet", u1)
    _write_frame(snap_dir / "u2_snapshot.parquet", u2)
    excluded_frame = pd.DataFrame(excluded)
    if excluded_frame.empty:
        excluded_frame = pd.DataFrame(columns=["symbol", "stage", "as_of_date", "company_id", "reasons"])
    _write_frame(snap_dir / "excluded_with_reasons.parquet", excluded_frame)
    append_exclusions(run_id, as_of_date, excluded)

    snapshot_payload = {
        "run_id": run_id,
        "universe_id": universe_id,
        "as_of_date": as_of_date.isoformat(),
        "stage_counts": stage_counts,
        "u0_symbols": _as_symbols(u0),
        "u1_symbols": _as_symbols(u1),
        "u2_symbols": _as_symbols(u2),
        "symbol_metrics": {
            str(row["symbol"]).strip().upper(): {
                "sector_l1": str(row.get("sector_l1", "other")),
                "country": str(row.get("country", "US")).upper(),
                "adv20_usd": float(row.get("adv20_usd", 0.0) or 0.0),
            }
            for _, row in u2.iterrows()
        },
        "excluded": excluded,
        "policy": {
            "mode": policy.get("mode", "global_unified"),
            "missing_data_policy": policy.get("missing_data_policy", "strict_exclude"),
            "rebalance_policy": policy.get("rebalance_policy", {}),
        },
    }
    save_json(snap_dir / "snapshot.json", snapshot_payload)
    return snapshot_payload


def _list_snapshot_dates(run_dir: Path) -> list[str]:
    base = run_dir / "universe"
    if not base.exists():
        return []
    dates = [path.name for path in base.iterdir() if path.is_dir()]
    return sorted(dates)


def load_latest_universe_snapshot(run_id: str) -> dict[str, Any] | None:
    """Load latest available snapshot json."""
    run_dir = get_run_dir(run_id)
    dates = _list_snapshot_dates(run_dir)
    if not dates:
        return None
    path = run_dir / "universe" / dates[-1] / "snapshot.json"
    if not path.exists():
        return None
    try:
        import json

        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def load_latest_universe_exclusions(run_id: str) -> list[dict[str, Any]]:
    """Load latest exclusion rows for API response."""
    snapshot = load_latest_universe_snapshot(run_id)
    if not snapshot:
        return []
    rows = snapshot.get("excluded", [])
    if not isinstance(rows, list):
        return []
    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        out.append(
            {
                "symbol": str(row.get("symbol", "")).strip().upper(),
                "stage": str(row.get("stage", "u0")).strip().lower(),
                "reasons": [str(item) for item in row.get("reasons", []) if str(item).strip()],
                "as_of_date": str(row.get("as_of_date", "")) or None,
                "company_id": str(row.get("company_id", "")) or None,
            }
        )
    return out
