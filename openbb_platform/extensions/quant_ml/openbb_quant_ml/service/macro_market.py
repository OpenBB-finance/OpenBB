"""Market ticker loader with tiered fallback."""

from __future__ import annotations

import json
import os
from datetime import date
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

from openbb_quant_ml.service.macro_constants import load_macro_config
from openbb_quant_ml.service.macro_db import load_observations, upsert_observations
from openbb_quant_ml.service.storage import utc_now_iso


def _parse_rows_to_series(rows: list[dict[str, Any]]) -> pd.Series:
    if not rows:
        return pd.Series(dtype=float)
    frame = pd.DataFrame(rows)
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame = frame.dropna(subset=["date"]).sort_values("date")
    values = pd.to_numeric(frame["value"], errors="coerce")
    series = pd.Series(values.to_numpy(dtype=float), index=frame["date"], dtype=float)
    series = series[~series.index.duplicated(keep="last")]
    return series.dropna()


def _rows_from_series(series: pd.Series) -> list[dict[str, Any]]:
    now_iso = utc_now_iso()
    return [
        {
            "date": idx.date().isoformat(),
            "value": float(value),
            "realtime_start": None,
            "realtime_end": None,
            "fetched_at": now_iso,
        }
        for idx, value in series.dropna().items()
    ]


def _fetch_yfinance(symbol: str, start: date | None, end: date | None) -> pd.Series:
    try:
        import yfinance as yf
    except Exception:  # noqa: BLE001
        return pd.Series(dtype=float)

    start_text = start.isoformat() if start else None
    end_text = end.isoformat() if end else None
    try:
        data = yf.download(
            symbol,
            start=start_text,
            end=end_text,
            auto_adjust=True,
            progress=False,
            actions=False,
            interval="1d",
            threads=False,
        )
    except Exception:  # noqa: BLE001
        return pd.Series(dtype=float)

    if data is None or data.empty:
        return pd.Series(dtype=float)
    close = data["Close"] if "Close" in data else data.iloc[:, 0]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close.index = pd.to_datetime(close.index).tz_localize(None)
    close = pd.to_numeric(close, errors="coerce")
    close = close.dropna()
    close.name = symbol.upper()
    return close


def _fetch_openbb_http(symbol: str, start: date | None, end: date | None) -> pd.Series:
    base_url = (os.getenv("OPENBB_API_BASE_URL") or "").strip().rstrip("/")
    if not base_url:
        return pd.Series(dtype=float)
    query = {
        "symbol": symbol,
        "provider": "yfinance",
    }
    if start:
        query["start_date"] = start.isoformat()
    if end:
        query["end_date"] = end.isoformat()
    url = f"{base_url}/api/v1/equity/price/historical?{urlencode(query)}"
    req = Request(url=url, method="GET", headers={"User-Agent": "openbb-quant-ml-macro/1.0"})
    try:
        with urlopen(req, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (HTTPError, URLError, TimeoutError, ValueError):
        return pd.Series(dtype=float)

    rows = payload.get("results", payload if isinstance(payload, list) else [])
    if not isinstance(rows, list) or not rows:
        return pd.Series(dtype=float)
    frame = pd.DataFrame(rows)
    if "date" not in frame.columns:
        return pd.Series(dtype=float)
    close_col = "close" if "close" in frame.columns else "adj_close" if "adj_close" in frame.columns else None
    if close_col is None:
        numeric_cols = [col for col in frame.columns if col not in {"date", "symbol"}]
        if not numeric_cols:
            return pd.Series(dtype=float)
        close_col = numeric_cols[0]
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame = frame.dropna(subset=["date"]).sort_values("date")
    values = pd.to_numeric(frame[close_col], errors="coerce")
    series = pd.Series(values.to_numpy(dtype=float), index=frame["date"], dtype=float).dropna()
    series.index = series.index.tz_localize(None)
    return series


def get_market_series(symbol: str, start: date | None, end: date | None) -> tuple[pd.Series, str, str | None]:
    """Load market series with configured fallback order."""
    symbol_norm = symbol.upper()
    cfg = load_macro_config()
    defaults = cfg.get("defaults", {})
    order = defaults.get("market_fallback_order", ["yfinance", "openbb_http", "cache"])
    aliases = defaults.get("market_symbol_aliases", {})
    symbol_for_fetch = str(aliases.get(symbol_norm, symbol_norm)).upper()

    cached_rows = load_observations("MARKET", symbol_norm, start.isoformat() if start else None, end.isoformat() if end else None)
    cached_series = _parse_rows_to_series(cached_rows)
    if not cached_series.empty:
        cached_series.name = symbol_norm

    warning: str | None = None
    for source in order:
        source_key = str(source).lower()
        if source_key == "yfinance":
            series = _fetch_yfinance(symbol_for_fetch, start, end)
            if not series.empty:
                series.name = symbol_norm
                upsert_observations("MARKET", symbol_norm, _rows_from_series(series))
                return series, "yfinance", warning
            warning = "market_yfinance_fetch_failed"
        elif source_key == "openbb_http":
            if symbol_for_fetch != symbol_norm and symbol_for_fetch.endswith("=F"):
                warning = "futures_symbol_openbb_http_not_supported"
                continue
            series = _fetch_openbb_http(symbol_for_fetch, start, end)
            if not series.empty:
                series.name = symbol_norm
                upsert_observations("MARKET", symbol_norm, _rows_from_series(series))
                return series, "openbb_http", warning
            warning = "market_openbb_http_fetch_failed"
        elif source_key == "cache":
            if not cached_series.empty:
                return cached_series, "cache", warning

    if not cached_series.empty:
        return cached_series, "cache", warning
    return pd.Series(dtype=float), "unavailable", warning or "market_data_unavailable"
