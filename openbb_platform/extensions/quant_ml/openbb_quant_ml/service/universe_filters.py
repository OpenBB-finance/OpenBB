"""Universe stage filtering and exclusion reason builders."""

from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_symbol(value: Any) -> str:
    return str(value or "").strip().upper()


def build_symbol_metrics(
    market_long: pd.DataFrame,
    security_master: pd.DataFrame,
    *,
    as_of_date: date,
) -> pd.DataFrame:
    """Build per-symbol market/liquidity metrics at T-1 cutoff."""
    if market_long.empty:
        metrics = security_master.copy()
        for col in (
            "price_20d_avg",
            "median_dollar_volume_63d",
            "trading_frequency_63d",
            "annual_turnover_ratio_252d",
            "adv20_usd",
            "two_year_dollar_volume",
        ):
            metrics[col] = float("nan")
        return metrics

    frame = market_long.copy()
    frame["date"] = pd.to_datetime(frame["date"]).dt.tz_localize(None)
    frame["symbol"] = frame["symbol"].map(_normalize_symbol)
    frame = frame[frame["date"].dt.date <= as_of_date]
    if frame.empty:
        metrics = security_master.copy()
        for col in (
            "price_20d_avg",
            "median_dollar_volume_63d",
            "trading_frequency_63d",
            "annual_turnover_ratio_252d",
            "adv20_usd",
            "two_year_dollar_volume",
        ):
            metrics[col] = float("nan")
        return metrics

    frame["close"] = pd.to_numeric(frame.get("close"), errors="coerce")
    frame["volume"] = pd.to_numeric(frame.get("volume"), errors="coerce").fillna(0.0)
    frame["dollar_volume"] = frame["close"] * frame["volume"]
    frame = frame.sort_values(["symbol", "date"])

    rows: list[dict[str, Any]] = []
    for symbol, group in frame.groupby("symbol", sort=False):
        tail_20 = group.tail(20)
        tail_63 = group.tail(63)
        tail_252 = group.tail(252)
        tail_504 = group.tail(504)
        price_20d_avg = float(pd.to_numeric(tail_20["close"], errors="coerce").mean())
        median_dollar_volume_63d = float(
            pd.to_numeric(tail_63["dollar_volume"], errors="coerce").median()
        )
        trading_frequency_63d = float((tail_63["volume"] > 0).mean()) if len(tail_63) else 0.0
        adv20_usd = float(pd.to_numeric(tail_20["dollar_volume"], errors="coerce").mean())
        two_year_dollar_volume = float(
            pd.to_numeric(tail_504["dollar_volume"], errors="coerce").sum()
        )
        annual_dollar_volume = float(
            pd.to_numeric(tail_252["dollar_volume"], errors="coerce").sum()
        )
        rows.append(
            {
                "symbol": symbol,
                "price_20d_avg": price_20d_avg,
                "median_dollar_volume_63d": median_dollar_volume_63d,
                "trading_frequency_63d": trading_frequency_63d,
                "adv20_usd": adv20_usd,
                "two_year_dollar_volume": two_year_dollar_volume,
                "annual_dollar_volume_252d": annual_dollar_volume,
            }
        )

    metric_frame = pd.DataFrame(rows)
    merged = security_master.merge(metric_frame, on="symbol", how="left")
    merged["float_mcap_usd"] = pd.to_numeric(
        merged.get("float_mcap_usd"), errors="coerce"
    ).fillna(0.0)
    merged["annual_turnover_ratio_252d"] = (
        pd.to_numeric(merged["annual_dollar_volume_252d"], errors="coerce").fillna(0.0)
        / (merged["float_mcap_usd"] + 1e-12)
    )
    return merged


def _exclude(
    excluded: list[dict[str, Any]],
    *,
    symbol: str,
    stage: str,
    as_of_date: date,
    company_id: str | None,
    reasons: list[str],
) -> None:
    if not reasons:
        return
    excluded.append(
        {
            "symbol": symbol,
            "stage": stage,
            "as_of_date": as_of_date.isoformat(),
            "company_id": company_id,
            "reasons": sorted(set(reasons)),
        }
    )


def select_one_pricing_vehicle_per_company(
    frame: pd.DataFrame,
    *,
    as_of_date: date,
    excluded: list[dict[str, Any]],
) -> pd.DataFrame:
    """Apply one-company-one-line rule by 2Y dollar volume."""
    if frame.empty:
        return frame
    out_rows: list[pd.Series] = []
    for _, group in frame.groupby("company_id", sort=False):
        ranked = group.sort_values(
            ["two_year_dollar_volume", "adv20_usd", "symbol"], ascending=[False, False, True]
        )
        keep = ranked.iloc[0]
        out_rows.append(keep)
        if len(ranked) > 1:
            for _, row in ranked.iloc[1:].iterrows():
                _exclude(
                    excluded,
                    symbol=str(row["symbol"]),
                    stage="u0",
                    as_of_date=as_of_date,
                    company_id=str(row.get("company_id") or ""),
                    reasons=["duplicate_company_non_primary_line"],
                )
    return pd.DataFrame(out_rows).reset_index(drop=True)


def apply_u0_filters(
    frame: pd.DataFrame,
    policy: dict[str, Any],
    *,
    as_of_date: date,
    missing_data_policy: str,
    excluded: list[dict[str, Any]],
) -> pd.DataFrame:
    """Apply U0 clean-universe filters."""
    cfg = policy.get("u0_filters", {}) if isinstance(policy, dict) else {}
    allowed_security_types = {
        str(item).strip().lower() for item in cfg.get("allowed_security_types", [])
    }
    excluded_security_types = {
        str(item).strip().lower() for item in cfg.get("excluded_security_types", [])
    }
    major_exchanges = {str(item).strip().upper() for item in cfg.get("major_exchanges", [])}
    excluded_exchanges = {
        str(item).strip().upper() for item in cfg.get("excluded_exchange_types", [])
    }
    min_price = _safe_float(cfg.get("min_price_20d_avg"), 5.0)
    min_free_float = _safe_float(cfg.get("min_free_float_ratio"), 0.10)
    min_float_mcap = _safe_float(cfg.get("min_float_mcap_usd"), 500_000_000.0)
    min_ipo_days = int(_safe_float(cfg.get("min_ipo_trading_days"), 60))

    keep_rows: list[pd.Series] = []
    for _, row in frame.iterrows():
        symbol = str(row.get("symbol", "")).strip().upper()
        reasons: list[str] = []
        security_type = str(row.get("security_type", "")).strip().lower()
        exchange = str(row.get("exchange", "")).strip().upper()
        price_20d_avg = pd.to_numeric(row.get("price_20d_avg"), errors="coerce")
        free_float = pd.to_numeric(row.get("free_float_ratio"), errors="coerce")
        float_mcap = pd.to_numeric(row.get("float_mcap_usd"), errors="coerce")
        ipo_days = pd.to_numeric(row.get("ipo_trading_days"), errors="coerce")

        if security_type in excluded_security_types:
            reasons.append(f"excluded_security_type:{security_type}")
        if allowed_security_types and security_type not in allowed_security_types:
            reasons.append(f"not_allowed_security_type:{security_type or 'unknown'}")
        if exchange in excluded_exchanges:
            reasons.append(f"excluded_exchange:{exchange}")
        if major_exchanges and exchange not in major_exchanges:
            reasons.append(f"non_major_exchange:{exchange or 'unknown'}")

        if pd.isna(price_20d_avg):
            reasons.append("missing_price_20d_avg")
        elif float(price_20d_avg) < min_price:
            reasons.append("price_below_min")
        if pd.isna(free_float):
            reasons.append("missing_free_float_ratio")
        elif float(free_float) < min_free_float:
            reasons.append("free_float_below_min")
        if pd.isna(float_mcap):
            reasons.append("missing_float_mcap_usd")
        elif float(float_mcap) < min_float_mcap:
            reasons.append("float_mcap_below_min")
        if pd.isna(ipo_days):
            reasons.append("missing_ipo_trading_days")
        elif float(ipo_days) < float(min_ipo_days):
            reasons.append("ipo_seasoning_too_short")

        if reasons:
            if missing_data_policy == "strict_exclude" or not all(
                reason.startswith("missing_") for reason in reasons
            ):
                _exclude(
                    excluded,
                    symbol=symbol,
                    stage="u0",
                    as_of_date=as_of_date,
                    company_id=str(row.get("company_id") or ""),
                    reasons=reasons,
                )
                continue
        keep_rows.append(row)
    return pd.DataFrame(keep_rows).reset_index(drop=True)


def apply_u1_filters(
    frame: pd.DataFrame,
    policy: dict[str, Any],
    *,
    as_of_date: date,
    missing_data_policy: str,
    excluded: list[dict[str, Any]],
) -> pd.DataFrame:
    """Apply U1 tradeability filters."""
    cfg = policy.get("u1_filters", {}) if isinstance(policy, dict) else {}
    min_mdv = _safe_float(cfg.get("min_median_dollar_volume_63d"), 5_000_000.0)
    min_freq = _safe_float(cfg.get("min_trading_frequency_63d"), 0.90)
    min_turnover = _safe_float(cfg.get("min_annual_turnover_ratio_252d"), 0.75)

    keep_rows: list[pd.Series] = []
    for _, row in frame.iterrows():
        symbol = str(row.get("symbol", "")).strip().upper()
        reasons: list[str] = []
        mdv = pd.to_numeric(row.get("median_dollar_volume_63d"), errors="coerce")
        freq = pd.to_numeric(row.get("trading_frequency_63d"), errors="coerce")
        turnover = pd.to_numeric(row.get("annual_turnover_ratio_252d"), errors="coerce")

        if pd.isna(mdv):
            reasons.append("missing_median_dollar_volume_63d")
        elif float(mdv) < min_mdv:
            reasons.append("mdv_63d_below_min")
        if pd.isna(freq):
            reasons.append("missing_trading_frequency_63d")
        elif float(freq) < min_freq:
            reasons.append("trading_frequency_63d_below_min")
        if pd.isna(turnover):
            reasons.append("missing_annual_turnover_ratio_252d")
        elif float(turnover) < min_turnover:
            reasons.append("annual_turnover_ratio_252d_below_min")

        if reasons:
            if missing_data_policy == "strict_exclude" or not all(
                reason.startswith("missing_") for reason in reasons
            ):
                _exclude(
                    excluded,
                    symbol=symbol,
                    stage="u1",
                    as_of_date=as_of_date,
                    company_id=str(row.get("company_id") or ""),
                    reasons=reasons,
                )
                continue
        keep_rows.append(row)
    return pd.DataFrame(keep_rows).reset_index(drop=True)


def apply_u2_filters(
    frame: pd.DataFrame,
    policy: dict[str, Any],
    *,
    as_of_date: date,
    portfolio_mode: str,
    excluded: list[dict[str, Any]],
) -> pd.DataFrame:
    """Apply U2 portfolio-eligible filters."""
    cfg = policy.get("u2_filters", {}) if isinstance(policy, dict) else {}
    max_halt_days = int(_safe_float(cfg.get("max_trading_halt_days"), 29))
    exclude_mgmt = bool(cfg.get("exclude_management_flag", True))
    exclude_delist = bool(cfg.get("exclude_delisting_pending_flag", True))
    exclude_special = bool(cfg.get("exclude_special_status_flag", True))
    exclude_htb = bool(cfg.get("exclude_hard_to_borrow_for_long_short", True))

    keep_rows: list[pd.Series] = []
    for _, row in frame.iterrows():
        symbol = str(row.get("symbol", "")).strip().upper()
        reasons: list[str] = []

        halt_days = int(_safe_float(row.get("trading_halt_days"), 0))
        if halt_days >= max_halt_days + 1:
            reasons.append("trading_halt_days_exceeded")

        if exclude_mgmt and bool(row.get("management_flag", False)):
            reasons.append("management_flag")
        if exclude_delist and bool(row.get("delisting_pending_flag", False)):
            reasons.append("delisting_pending_flag")
        if exclude_special and bool(row.get("special_status_flag", False)):
            reasons.append("special_status_flag")
        if (
            exclude_htb
            and str(portfolio_mode).strip().lower() == "long_short"
            and bool(row.get("hard_to_borrow_flag", False))
        ):
            reasons.append("hard_to_borrow")

        if reasons:
            _exclude(
                excluded,
                symbol=symbol,
                stage="u2",
                as_of_date=as_of_date,
                company_id=str(row.get("company_id") or ""),
                reasons=reasons,
            )
            continue
        keep_rows.append(row)
    return pd.DataFrame(keep_rows).reset_index(drop=True)
