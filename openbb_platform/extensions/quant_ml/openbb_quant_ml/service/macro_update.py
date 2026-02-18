"""Idempotent macro update runner for FRED series."""

from __future__ import annotations

import argparse
from collections.abc import Iterable
from datetime import date, timedelta

from openbb_quant_ml.service.macro_catalog import (
    all_default_series_ids,
    parse_date_input,
    resolve_catalog_item,
)
from openbb_quant_ml.service.macro_constants import load_macro_config
from openbb_quant_ml.service.macro_db import get_obs_date_bounds, upsert_observations
from openbb_quant_ml.service.macro_feature_engineering import update_macro_features_for_series
from openbb_quant_ml.service.macro_fred_client import FredApiKeyMissingError, FredClient, FredClientError


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

    client = FredClient()
    updated: list[str] = []
    for series_id in normalized:
        resolve_catalog_item(series_id, create_if_missing=True)
        fetch_start, fetch_end = _effective_window(series_id, start, end, stale_days)
        try:
            rows = client.get_series_observations(series_id, start=fetch_start, end=fetch_end)
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
