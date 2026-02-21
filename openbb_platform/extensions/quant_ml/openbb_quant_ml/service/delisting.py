"""Delisting event helpers for backtest return adjustments."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from openbb_quant_ml.service.constants import ARTIFACT_ROOT

REFERENCE_DELISTING_EVENTS_PATH = ARTIFACT_ROOT / "reference" / "delisting_events.parquet"


def _normalize_symbol(value: Any) -> str:
    return str(value or "").strip().upper()


def load_delisting_events(run_dir: Path | None = None) -> pd.DataFrame:
    """Load delisting events from run-local or reference store."""
    candidates: list[Path] = []
    if run_dir is not None:
        candidates.append(run_dir / "delisting_events.parquet")
    candidates.append(REFERENCE_DELISTING_EVENTS_PATH)

    for path in candidates:
        if not path.exists():
            continue
        try:
            frame = pd.read_parquet(path)
        except Exception:  # noqa: BLE001
            continue
        if frame.empty or "symbol" not in frame.columns:
            continue
        out = frame.copy()
        out["symbol"] = out["symbol"].map(_normalize_symbol)
        if "effective_date" in out.columns:
            out["effective_date"] = pd.to_datetime(out["effective_date"]).dt.tz_localize(None)
        elif "date" in out.columns:
            out["effective_date"] = pd.to_datetime(out["date"]).dt.tz_localize(None)
        else:
            continue
        if "delisting_return" not in out.columns:
            if "return" in out.columns:
                out["delisting_return"] = pd.to_numeric(out["return"], errors="coerce")
            else:
                out["delisting_return"] = float("nan")
        out["event_type"] = out.get("event_type", "unknown")
        return out[["symbol", "effective_date", "delisting_return", "event_type"]]
    return pd.DataFrame(columns=["symbol", "effective_date", "delisting_return", "event_type"])


def apply_delisting_returns(
    returns: pd.DataFrame,
    events: pd.DataFrame,
) -> pd.DataFrame:
    """Overlay delisting returns into return panel."""
    if returns.empty or events.empty:
        return returns

    out = returns.copy()
    for _, row in events.iterrows():
        symbol = _normalize_symbol(row.get("symbol"))
        if symbol not in out.columns:
            continue
        event_date = pd.to_datetime(row.get("effective_date"), errors="coerce")
        if pd.isna(event_date):
            continue
        event_date = pd.Timestamp(event_date).tz_localize(None)
        if event_date not in out.index:
            continue

        value = pd.to_numeric(row.get("delisting_return"), errors="coerce")
        event_type = str(row.get("event_type", "")).strip().lower()
        if pd.isna(value):
            if event_type in {"bankrupt", "liquidation", "worthless"}:
                value = -1.0
            else:
                # Conservative fallback when delisting return is unknown.
                value = -1.0
        out.loc[event_date, symbol] = float(value)
    return out


def validate_delisting_events_required(
    *,
    close_panel: pd.DataFrame,
    events: pd.DataFrame,
    end_date: pd.Timestamp,
    min_missing_days: int = 30,
) -> None:
    """Fail when symbols vanish long before end-date without delisting event."""
    if close_panel.empty:
        return
    if not isinstance(events, pd.DataFrame):
        events = pd.DataFrame()
    event_symbols = set()
    if not events.empty and "symbol" in events.columns:
        event_symbols = {
            _normalize_symbol(item)
            for item in events["symbol"].tolist()
            if _normalize_symbol(item)
        }
    for symbol in close_panel.columns:
        series = close_panel[symbol]
        valid = series.dropna()
        if valid.empty:
            continue
        last_date = pd.Timestamp(valid.index.max()).tz_localize(None)
        gap_days = (pd.Timestamp(end_date).tz_localize(None) - last_date).days
        if gap_days < int(min_missing_days):
            continue
        normalized = _normalize_symbol(symbol)
        if normalized in event_symbols:
            continue
        raise ValueError("delisting_event_missing")
