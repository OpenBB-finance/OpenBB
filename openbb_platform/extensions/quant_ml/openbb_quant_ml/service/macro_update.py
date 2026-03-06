"""Idempotent macro update runner for FRED series."""

from __future__ import annotations

import argparse
import logging
from collections.abc import Iterable
from datetime import date, timedelta
from typing import Any

import pandas as pd

from openbb_quant_ml.service.macro_catalog import (
    all_default_series_ids,
    parse_date_input,
    resolve_catalog_item,
)
from openbb_quant_ml.service.macro_constants import load_macro_config
from openbb_quant_ml.service.macro_db import get_obs_date_bounds, upsert_observations
from openbb_quant_ml.service.macro_feature_engineering import update_macro_features_for_series
from openbb_quant_ml.service.macro_fred_client import FredApiKeyMissingError, FredClient, FredClientError
from openbb_quant_ml.service.macro_market import get_market_series

LOGGER = logging.getLogger(__name__)


def _normalize_series_ids(series_ids: Iterable[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for series_id in series_ids:
        sid = str(series_id or "").strip().upper()
        if not sid:
            continue
        if sid.startswith("FRED:"):
            sid = sid.split(":", 1)[1]
        if sid in seen:
            continue
        seen.add(sid)
        out.append(sid)
    return out


def _effective_window(
    series_id: str,
    start: date | None,
    end: date | None,
    stale_refresh_days: int,
) -> tuple[date | None, date | None]:
    req_start = start
    req_end = end or date.today()
    _, max_date_str = get_obs_date_bounds("FRED", series_id)
    if not max_date_str:
        return req_start, req_end

    try:
        max_date = date.fromisoformat(str(max_date_str))
    except ValueError:
        return req_start, req_end
    refresh_start = max_date - timedelta(days=max(1, int(stale_refresh_days)))
    if req_start is None:
        return refresh_start, req_end
    return max(req_start, refresh_start), req_end


def _extract_result_frame(result: Any) -> pd.DataFrame:
    if isinstance(result, pd.DataFrame):
        return result
    for method_name in ("to_df", "to_dataframe"):
        method = getattr(result, method_name, None)
        if callable(method):
            candidate = method()
            if isinstance(candidate, pd.DataFrame):
                return candidate
    return pd.DataFrame()


def _normalize_openbb_fred_rows(frame: pd.DataFrame) -> list[dict[str, Any]]:
    if frame.empty:
        return []
    normalized = frame.copy()
    normalized.columns = [str(col).lower() for col in normalized.columns]
    if "date" not in normalized.columns:
        for candidate in ("observation_date", "as_of_date"):
            if candidate in normalized.columns:
                normalized = normalized.rename(columns={candidate: "date"})
                break
    value_col = next(
        (col for col in ("value", "close", "last_price") if col in normalized.columns),
        None,
    )
    if "date" not in normalized.columns or value_col is None:
        return []
    normalized["date"] = pd.to_datetime(normalized["date"], errors="coerce").dt.tz_localize(None)
    normalized[value_col] = pd.to_numeric(normalized[value_col], errors="coerce")
    normalized = normalized.dropna(subset=["date"]).sort_values("date")
    fetched_at = pd.Timestamp.utcnow().replace(microsecond=0).isoformat().replace("+00:00", "Z")
    out: list[dict[str, Any]] = []
    for _, row in normalized.iterrows():
        raw_value = row.get(value_col)
        value = None if pd.isna(raw_value) else float(raw_value)
        out.append(
            {
                "date": pd.Timestamp(row["date"]).date().isoformat(),
                "value": value,
                "realtime_start": None,
                "realtime_end": None,
                "fetched_at": fetched_at,
            }
        )
    return out


def _fetch_openbb_fred_observations(
    series_id: str,
    start: date | None = None,
    end: date | None = None,
) -> list[dict[str, Any]]:
    try:
        from openbb import obb  # type: ignore[import-not-found]
    except Exception:
        return []

    kwargs: dict[str, Any] = {"symbol": series_id}
    if start is not None:
        kwargs["start_date"] = start.isoformat()
    if end is not None:
        kwargs["end_date"] = end.isoformat()
    try:
        result = obb.economy.fred_series(**kwargs)
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("OpenBB fred_series failed for %s: %s", series_id, exc)
        return []
    return _normalize_openbb_fred_rows(_extract_result_frame(result))


def update_series_ids(
    series_ids: list[str],
    start: date | None = None,
    end: date | None = None,
    compute_features: bool = True,
    features_lookback_days: int | None = None,
) -> list[str]:
    """Fetch and persist series data with stale-window refresh."""
    cfg = load_macro_config()
    stale_days = int(cfg.get("defaults", {}).get("stale_refresh_days", 30))

    normalized = _normalize_series_ids(series_ids)
    if not normalized:
        return []

    client: FredClient | None = None
    updated: list[str] = []
    for series_id in normalized:
        resolve_catalog_item(series_id, create_if_missing=True)
        fetch_start, fetch_end = _effective_window(series_id, start, end, stale_days)
        rows = _fetch_openbb_fred_observations(
            series_id,
            start=fetch_start,
            end=fetch_end,
        )
        if not rows:
            if client is None:
                client = FredClient()
            try:
                rows = client.get_series_observations(
                    series_id,
                    start=fetch_start,
                    end=fetch_end,
                )
            except FredApiKeyMissingError:
                # Cache-only mode; nothing to refresh.
                continue
            except FredClientError:
                # Skip but continue other series.
                continue

        if rows:
            upsert_observations("FRED", series_id, rows)
            updated.append(series_id)
    if updated and compute_features:
        feature_start = start
        if features_lookback_days is not None:
            end_anchor = end or date.today()
            lookback_start = end_anchor - timedelta(days=max(7, int(features_lookback_days)))
            if feature_start is None or feature_start > lookback_start:
                feature_start = lookback_start
        update_macro_features_for_series(
            updated,
            start=(feature_start.isoformat() if feature_start else None),
            end=(end.isoformat() if end else None),
        )
    return updated


def update_all_defaults(
    start: date | None = None,
    end: date | None = None,
    compute_features: bool = True,
    features_lookback_days: int | None = None,
) -> list[str]:
    """Refresh all default config series."""
    return update_series_ids(
        all_default_series_ids(),
        start=start,
        end=end,
        compute_features=compute_features,
        features_lookback_days=features_lookback_days,
    )


def update_macro_series(
    series_id: str,
    start_date: date | None = None,
    end_date: date | None = None,
    provider: str = "fred",
    compute_features: bool = True,
    features_lookback_days: int | None = None,
) -> list[str]:
    """Public helper for single-series incremental macro refresh."""
    if provider.lower() != "fred":
        return []
    return update_series_ids(
        [series_id],
        start=start_date,
        end=end_date,
        compute_features=compute_features,
        features_lookback_days=features_lookback_days,
    )


def update_macro_all(
    series_list: list[str] | None = None,
    end_date: date | None = None,
    lookback_years: int = 30,
    compute_features: bool = True,
    features_lookback_days: int | None = None,
) -> list[str]:
    """Public helper for full-list incremental macro refresh."""
    end_value = end_date or date.today()
    start_value = end_value - timedelta(days=max(1, int(lookback_years)) * 365)
    targets = series_list or all_default_series_ids()
    return update_series_ids(
        targets,
        start=start_value,
        end=end_value,
        compute_features=compute_features,
        features_lookback_days=features_lookback_days,
    )


def update_market_symbols(
    symbols: list[str],
    start: date | None = None,
    end: date | None = None,
) -> list[str]:
    """Refresh market symbols into macro DB cache."""
    updated: list[str] = []
    for symbol in symbols:
        key = str(symbol or "").strip().upper()
        if not key:
            continue
        series, _source, _warning = get_market_series(key, start=start, end=end)
        if series.empty:
            continue
        rows = [
            {
                "date": idx.date().isoformat(),
                "value": float(value),
                "realtime_start": None,
                "realtime_end": None,
            }
            for idx, value in series.dropna().items()
        ]
        if not rows:
            continue
        upsert_observations("MARKET", key, rows)
        updated.append(key)
    return updated


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update macro time series into local SQLite cache.")
    parser.add_argument("--series", nargs="*", default=None, help="Series IDs (e.g. UNRATE CPIAUCSL)")
    parser.add_argument("--start", default=None, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", default=None, help="End date (YYYY-MM-DD or today)")
    parser.add_argument("--all-default", action="store_true", help="Update all configured default series")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--also-features", action="store_true", help="Recompute macro features after obs update")
    group.add_argument("--skip-features", action="store_true", help="Skip macro feature update")
    parser.add_argument(
        "--features-lookback-days",
        type=int,
        default=None,
        help="When recomputing features, ensure this trailing window is recalculated",
    )
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""
    args = _parse_args()
    start = parse_date_input(args.start)
    end = parse_date_input(args.end)
    compute_features = not bool(args.skip_features)
    if args.also_features:
        compute_features = True
    if args.all_default:
        updated = update_all_defaults(
            start=start,
            end=end,
            compute_features=compute_features,
            features_lookback_days=args.features_lookback_days,
        )
    else:
        updated = update_series_ids(
            args.series or [],
            start=start,
            end=end,
            compute_features=compute_features,
            features_lookback_days=args.features_lookback_days,
        )
    print(f"Updated {len(updated)} series.")
    if updated:
        print(", ".join(updated))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
