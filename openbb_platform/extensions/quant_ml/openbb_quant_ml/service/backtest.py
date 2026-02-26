"""Portfolio construction and backtest helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize
from scipy.stats import spearmanr

from openbb_quant_ml.models import BacktestConstraints
from openbb_quant_ml.service.delisting import apply_delisting_returns
from openbb_quant_ml.service.portfolio_optimizer_v2 import optimize_weights_v2
from openbb_quant_ml.service.portfolio_policy import (
    apply_effective_max_weight,
    get_portfolio_policy,
)
from openbb_quant_ml.service.universe_policy import get_universe_policy


@dataclass
class BacktestResult:
    """Backtest output payload."""

    metrics: dict[str, float]
    equity_curve: list[dict[str, Any]]
    period_weights: list[dict[str, Any]]
    benchmark_symbol: str
    benchmark_curve: list[dict[str, Any]]
    base_index: float
    cost_breakdown: list[dict[str, Any]]
    consistency_checks: dict[str, float | bool]
    regime_mode_by_period: list[dict[str, str]]
    effective_constraints: dict[str, float | bool]
    cash_weight: float
    rebalance_history_summary: list[dict[str, Any]]
    constraint_violations: list[dict[str, Any]]
    liquidity_clip_ratio: float
    risk_contribution_max: float
    universe_stage_counts: dict[str, int]
    rebalance_reports: list[dict[str, Any]]


def _monthly_rebalance_dates(dates: pd.DatetimeIndex) -> list[pd.Timestamp]:
    if len(dates) == 0:
        return []
    grouped = pd.Series(dates, index=dates).groupby(dates.to_period("M")).first()
    return [pd.Timestamp(value) for value in grouped.values]


def _safe_initial_weights(
    asset_count: int, max_weight: float, *, allow_short: bool
) -> np.ndarray:
    if asset_count <= 0:
        return np.array([])
    equal = np.repeat(1.0 / asset_count, asset_count)
    if allow_short:
        return np.clip(equal, -max_weight, max_weight)
    clipped = np.minimum(equal, max_weight)
    clipped_sum = float(clipped.sum())
    if clipped_sum <= 0:
        return np.zeros(asset_count, dtype=float)
    if clipped_sum > 1.0:
        clipped = clipped / clipped_sum
    return clipped


def _apply_cov_shrinkage(cov: np.ndarray, shrinkage: float = 0.1) -> np.ndarray:
    """Apply Ledoit-Wolf style shrinkage toward diagonal."""
    n = cov.shape[0]
    if n == 0:
        return cov
    target = np.diag(np.diag(cov))
    return (1.0 - shrinkage) * cov + shrinkage * target


def _estimate_covariance(
    hist_returns: pd.DataFrame,
    method: str,
    ewma_halflife: int,
    shrinkage: float,
) -> np.ndarray:
    """Estimate covariance matrix with configurable method."""
    hist = hist_returns.copy()
    n_assets_hint = len(hist.columns)
    if hist.empty:
        if n_assets_hint <= 0:
            return np.zeros((0, 0), dtype=float)
        return np.eye(n_assets_hint, dtype=float) * 1e-8
    hist = hist.apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)
    arr = hist.to_numpy(dtype=float)
    n_obs, n_assets = arr.shape
    if n_assets == 0:
        return np.zeros((0, 0), dtype=float)
    if n_obs < 2:
        return np.eye(n_assets, dtype=float) * 1e-8

    method_key = str(method or "sample").strip().lower()
    if method_key == "sample":
        cov = np.cov(arr, rowvar=False, ddof=0)
    elif method_key == "ewma":
        halflife = max(int(ewma_halflife), 2)
        decay = np.exp(np.log(0.5) / float(halflife))
        weights = decay ** np.arange(n_obs - 1, -1, -1)
        weights = weights / max(float(weights.sum()), 1e-12)
        mean = np.sum(arr * weights[:, None], axis=0)
        centered = arr - mean
        cov = (centered * weights[:, None]).T @ centered
    elif method_key == "ledoit_wolf":
        try:
            from sklearn.covariance import LedoitWolf

            cov = LedoitWolf().fit(arr).covariance_
        except Exception:
            cov = np.cov(arr, rowvar=False, ddof=0)
    elif method_key == "ewma_shrink":
        ewma_cov = _estimate_covariance(
            hist_returns=hist,
            method="ewma",
            ewma_halflife=ewma_halflife,
            shrinkage=shrinkage,
        )
        cov = _apply_cov_shrinkage(ewma_cov, shrinkage=float(np.clip(shrinkage, 0.0, 1.0)))
    else:
        cov = np.cov(arr, rowvar=False, ddof=0)

    cov = np.asarray(cov, dtype=float)
    cov = np.nan_to_num(cov, nan=0.0, posinf=0.0, neginf=0.0)
    cov = 0.5 * (cov + cov.T)
    cov = cov + np.eye(n_assets, dtype=float) * 1e-8
    return cov


def _estimate_trade_cost_components(
    delta_w: np.ndarray,
    adv_usd: np.ndarray,
    commission_bps: float,
    half_spread_bps: float,
    impact_k: float,
    nav: float,
) -> dict[str, float]:
    """Estimate normalized trade cost components."""
    nav = max(float(nav), 1e-9)
    abs_delta = np.abs(np.asarray(delta_w, dtype=float))
    adv_arr = np.asarray(adv_usd, dtype=float)
    if adv_arr.size != abs_delta.size:
        adv_arr = np.ones(abs_delta.size, dtype=float)

    turnover = float(abs_delta.sum())
    commission = float((float(commission_bps) / 1e4) * turnover)
    spread = float((float(half_spread_bps) / 1e4) * turnover)

    adv_weight_capacity = np.clip(adv_arr / nav, 1e-6, None)
    impact = float((float(impact_k) / 1e4) * np.sum((abs_delta**2) / adv_weight_capacity))
    total = float(commission + spread + impact)
    return {
        "commission": commission,
        "spread": spread,
        "impact": impact,
        "total": total,
    }


def _optimize_weights(
    mu: np.ndarray,
    cov: np.ndarray,
    constraints: BacktestConstraints,
    *,
    allow_short: bool,
    max_weight: float,
    risk_aversion: float | None = None,
) -> np.ndarray:
    asset_count = len(mu)
    if asset_count == 0:
        return np.array([])

    weight_cap = max(float(max_weight), 1e-6)
    initial = _safe_initial_weights(asset_count, weight_cap, allow_short=allow_short)

    if float(np.abs(mu).max()) < 1e-12:
        return initial

    cov_stable = cov.copy()
    try:
        cond = float(np.linalg.cond(cov_stable))
    except (np.linalg.LinAlgError, FloatingPointError):
        cond = 1e15
    if cond > 1e10 or not np.isfinite(cond):
        cov_stable = _apply_cov_shrinkage(cov_stable, shrinkage=0.2)

    bounds = [
        (-weight_cap, weight_cap) if allow_short else (0.0, weight_cap)
        for _ in range(asset_count)
    ]

    def objective(weights: np.ndarray) -> float:
        risk_aversion_local = (
            float(risk_aversion)
            if risk_aversion is not None
            else float(constraints.risk_aversion)
        )
        mean_term = float(np.dot(mu, weights))
        risk_term = float(weights @ cov_stable @ weights)
        return -(mean_term - risk_aversion_local * risk_term)

    if allow_short:
        optimizer_constraints = [
            {"type": "eq", "fun": lambda w: float(np.sum(w) - 1.0)}
        ]
    else:
        optimizer_constraints = [
            {"type": "ineq", "fun": lambda w: float(1.0 - np.sum(w))}
        ]
    if allow_short:
        gross_cap = 1.5
        optimizer_constraints.append(
            {"type": "ineq", "fun": lambda w: float(gross_cap - np.sum(np.abs(w)))}
        )

    result = minimize(
        objective,
        initial,
        method="SLSQP",
        bounds=bounds,
        constraints=optimizer_constraints,
    )
    if result.success:
        clipped = np.clip(result.x, -weight_cap if allow_short else 0.0, weight_cap)
        if allow_short:
            gross = float(np.sum(np.abs(clipped)))
            if gross > 1.5 and gross > 0:
                clipped = clipped * (1.5 / gross)
            clipped = clipped + ((1.0 - float(np.sum(clipped))) / max(asset_count, 1))
            clipped = np.clip(clipped, -weight_cap, weight_cap)
        else:
            total = float(np.sum(clipped))
            if total > 1.0 and total > 0:
                clipped = clipped * (1.0 / total)
            clipped = np.clip(clipped, 0.0, weight_cap)
        return clipped

    positive = np.maximum(mu, 0.0)
    if allow_short:
        centered = mu - float(np.mean(mu))
        positive = np.maximum(centered, 0.0)
        negative = np.maximum(-centered, 0.0)
        if positive.sum() > 0 and negative.sum() > 0:
            short_budget = min(
                0.35, float(negative.sum() / (positive.sum() + negative.sum() + 1e-12))
            )
            long_w = positive / positive.sum()
            short_w = negative / negative.sum()
            fallback = long_w * (1.0 + short_budget) - short_w * short_budget
            fallback = np.clip(fallback, -weight_cap, weight_cap)
            fallback = fallback + (
                (1.0 - float(np.sum(fallback))) / max(asset_count, 1)
            )
            return np.clip(fallback, -weight_cap, weight_cap)
    if positive.sum() > 0:
        fallback = positive / positive.sum()
        fallback = np.clip(fallback, -weight_cap if allow_short else 0.0, weight_cap)
        if not allow_short:
            total = float(np.sum(fallback))
            if total > 1.0 and total > 0:
                fallback = fallback * (1.0 / total)
            fallback = np.clip(fallback, 0.0, weight_cap)
        return fallback
    return initial


def _compute_regime_series(
    close_panel: pd.DataFrame,
    dates: pd.DatetimeIndex,
    benchmark_symbol: str,
) -> pd.DataFrame:
    if len(dates) == 0:
        return pd.DataFrame(columns=["trend_regime", "vol_regime"])
    symbol = (
        benchmark_symbol
        if benchmark_symbol in close_panel.columns
        else str(close_panel.columns[0])
    )
    benchmark = close_panel[symbol].astype(float).reindex(dates).ffill().bfill()
    if benchmark.empty:
        return pd.DataFrame(
            index=dates, data={"trend_regime": "sideways", "vol_regime": "mid"}
        )
    ret = (
        benchmark.pct_change(fill_method=None)
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0.0)
    )
    ma200 = benchmark.rolling(200, min_periods=20).mean()
    trend = np.where(
        benchmark > ma200 * 1.01,
        "bull",
        np.where(benchmark < ma200 * 0.99, "bear", "sideways"),
    )
    vol20 = ret.rolling(20, min_periods=5).std(ddof=0) * np.sqrt(252)
    low_q = float(vol20.quantile(0.33))
    high_q = float(vol20.quantile(0.66))
    vol_regime = np.where(
        vol20 <= low_q, "low", np.where(vol20 >= high_q, "high", "mid")
    )
    return pd.DataFrame(
        index=dates,
        data={
            "trend_regime": trend,
            "vol_regime": vol_regime,
        },
    )


def _mixed_policy_allows_short(trend_regime: str, vol_regime: str) -> bool:
    return trend_regime == "bull" and vol_regime in {"low", "mid"}


def _dynamic_risk_budget_scale(
    trend_regime: str, vol_regime: str, current_drawdown: float
) -> float:
    """Return exposure scaling factor in mixed mode (0.30 ~ 1.00)."""
    trend_key = str(trend_regime or "sideways").lower()
    vol_key = str(vol_regime or "mid").lower()
    trend_scale = {"bull": 1.0, "sideways": 0.82, "bear": 0.62}.get(trend_key, 0.82)
    vol_scale = {"low": 1.0, "mid": 0.90, "high": 0.72}.get(vol_key, 0.9)
    dd = max(0.0, float(current_drawdown))
    dd_scale = max(0.35, 1.0 - dd * 3.0)
    return float(np.clip(trend_scale * vol_scale * dd_scale, 0.30, 1.0))


def _consistency_checks(
    period_weights: list[dict[str, Any]], turnover_values: list[float]
) -> dict[str, float | bool]:
    if not period_weights:
        return {
            "valid": False,
            "weight_sum_error_max": 0.0,
            "gross_exposure_max": 0.0,
            "net_exposure_min": 0.0,
            "net_exposure_max": 0.0,
            "turnover_mean": 0.0,
        }
    weight_sum_errors: list[float] = []
    gross_exposures: list[float] = []
    net_exposures: list[float] = []
    for row in period_weights:
        weights = [float(v) for v in row.get("weights", {}).values()]
        weight_sum = float(sum(weights))
        gross = float(sum(abs(v) for v in weights))
        net = float(sum(weights))
        weight_sum_errors.append(abs(weight_sum - 1.0))
        gross_exposures.append(gross)
        net_exposures.append(net)
    return {
        "valid": bool(max(weight_sum_errors) <= 1e-4 and max(gross_exposures) <= 1.51),
        "weight_sum_error_max": float(max(weight_sum_errors)),
        "gross_exposure_max": float(max(gross_exposures)),
        "net_exposure_min": float(min(net_exposures)),
        "net_exposure_max": float(max(net_exposures)),
        "turnover_mean": float(np.mean(turnover_values)) if turnover_values else 0.0,
    }


def _compute_metrics(
    daily_returns: pd.Series, equity_curve: pd.Series
) -> dict[str, float]:
    if daily_returns.empty:
        return {
            "cagr": 0.0,
            "sharpe": 0.0,
            "sortino": 0.0,
            "max_drawdown": 0.0,
            "volatility": 0.0,
            "turnover": 0.0,
        }

    trading_days = max(len(daily_returns), 1)
    total_return = float(equity_curve.iloc[-1] / equity_curve.iloc[0] - 1.0)
    cagr = (
        float((1 + total_return) ** (252 / trading_days) - 1)
        if trading_days > 0
        else 0.0
    )

    vol = float(daily_returns.std(ddof=0) * np.sqrt(252))
    sharpe = float(
        (daily_returns.mean() / (daily_returns.std(ddof=0) + 1e-12)) * np.sqrt(252)
    )
    downside = daily_returns[daily_returns < 0.0]
    downside_std = (
        float(downside.std(ddof=0) * np.sqrt(252)) if len(downside) > 0 else 0.0
    )
    sortino = float((daily_returns.mean() * np.sqrt(252)) / (downside_std + 1e-12))

    running_max = equity_curve.cummax()
    drawdown = equity_curve / (running_max + 1e-12) - 1.0
    max_drawdown = float(drawdown.min())
    return {
        "cagr": cagr,
        "sharpe": sharpe,
        "sortino": sortino,
        "max_drawdown": max_drawdown,
        "volatility": vol,
    }


def _normalize_downloaded_close(downloaded: pd.DataFrame) -> pd.Series:
    if downloaded.empty:
        return pd.Series(dtype=float)
    frame = downloaded.copy()
    if isinstance(frame.columns, pd.MultiIndex):
        close = frame["Close"]
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
    else:
        close = frame["Close"] if "Close" in frame.columns else frame.iloc[:, 0]
    series = close.astype(float)
    series.index = pd.to_datetime(series.index).tz_localize(None)
    return series.sort_index()


def _benchmark_curve(
    close_panel: pd.DataFrame,
    curve_dates: pd.DatetimeIndex,
    benchmark_symbol: str,
    base_index: float,
) -> list[dict[str, Any]]:
    if len(curve_dates) == 0:
        return []

    prices: pd.Series
    if benchmark_symbol in close_panel.columns:
        prices = close_panel[benchmark_symbol].dropna().astype(float)
        prices.index = pd.to_datetime(prices.index).tz_localize(None)
    else:
        start = (curve_dates.min() - timedelta(days=10)).date().isoformat()
        end = (curve_dates.max() + timedelta(days=10)).date().isoformat()
        downloaded = yf.download(
            tickers=benchmark_symbol,
            start=start,
            end=end,
            auto_adjust=False,
            progress=False,
            group_by="column",
            threads=False,
        )
        prices = _normalize_downloaded_close(downloaded)

    aligned = prices.reindex(curve_dates).ffill().bfill()
    if aligned.empty or aligned.isna().all():
        return [
            {"date": d.date().isoformat(), "benchmark": float(base_index)}
            for d in curve_dates
        ]

    first_price = float(aligned.iloc[0]) if float(aligned.iloc[0]) != 0 else 1.0
    index_values = (aligned / first_price) * base_index
    return [
        {"date": dt.date().isoformat(), "benchmark": float(value)}
        for dt, value in index_values.items()
    ]


def _execution_return_panel(
    open_panel: pd.DataFrame,
    close_panel: pd.DataFrame,
    entry_price: str,
    exit_price: str,
) -> pd.DataFrame:
    entry_panel, exit_panel = _resolve_entry_exit_prices(
        entry_mode=entry_price,
        exit_mode=exit_price,
        open_panel=open_panel,
        close_panel=close_panel,
    )
    return (exit_panel / (entry_panel + 1e-12) - 1.0).replace([np.inf, -np.inf], np.nan)


def _resolve_entry_exit_prices(
    *,
    entry_mode: str,
    exit_mode: str,
    open_panel: pd.DataFrame,
    close_panel: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Resolve normalized entry/exit price panels for one-period returns."""
    vwap = (open_panel + close_panel) / 2.0
    entry_key = str(entry_mode or "next_open").strip().lower()
    exit_key = str(exit_mode or "close").strip().lower()

    entry_map: dict[str, pd.DataFrame] = {
        "next_open": open_panel,
        "close": close_panel.shift(1),
        "vwap_proxy": vwap,
    }
    exit_map: dict[str, pd.DataFrame] = {
        "close": close_panel,
        "next_open": open_panel,
        "next_close": close_panel.shift(-1),
        "vwap_proxy": vwap,
    }
    entry_panel = entry_map.get(entry_key, open_panel)
    exit_panel = exit_map.get(exit_key, close_panel)
    return entry_panel, exit_panel


def run_backtest(
    predictions: pd.DataFrame,
    open_panel: pd.DataFrame,
    close_panel: pd.DataFrame,
    start_date: date,
    end_date: date,
    constraints: BacktestConstraints,
    cost_bps: float,
    slippage_bps: float = 2.0,
    entry_price: str = "next_open",
    exit_price: str = "close",
    benchmark_symbol: str = "SPY",
    portfolio_mode: str = "long_only",
    regime_policy: str = "fixed",
    rebalance_universe_context: dict[str, dict[str, Any]] | None = None,
    delisting_events: pd.DataFrame | None = None,
) -> BacktestResult:
    """Run monthly-rebalance mean-variance backtest with configurable execution prices."""
    if predictions.empty:
        raise ValueError("No predictions are available for backtest.")
    if close_panel.empty or open_panel.empty:
        raise ValueError("No price data is available for backtest.")

    pred = predictions.copy()
    pred["date"] = pd.to_datetime(pred["date"]).dt.tz_localize(None)
    score_col = "score" if "score" in pred.columns else "predicted_return"
    pred_wide = pred.pivot(
        index="date", columns="symbol", values=score_col
    ).sort_index()

    close_panel = close_panel.copy()
    close_panel.index = pd.to_datetime(close_panel.index).tz_localize(None)
    open_panel = open_panel.copy()
    open_panel.index = pd.to_datetime(open_panel.index).tz_localize(None)
    open_panel = open_panel.reindex(
        index=close_panel.index, columns=close_panel.columns
    ).ffill()

    returns = _execution_return_panel(
        open_panel=open_panel,
        close_panel=close_panel,
        entry_price=entry_price,
        exit_price=exit_price,
    ).fillna(0.0)
    returns = apply_delisting_returns(
        returns,
        delisting_events if delisting_events is not None else pd.DataFrame(),
    )

    window_mask = (returns.index.date >= start_date) & (returns.index.date <= end_date)
    trade_dates = returns.index[window_mask]
    if len(trade_dates) == 0:
        price_min = str(returns.index.min().date()) if len(returns.index) > 0 else "N/A"
        price_max = str(returns.index.max().date()) if len(returns.index) > 0 else "N/A"
        raise ValueError(
            f"No trading days found in the selected date range "
            f"({start_date} ~ {end_date}). "
            f"Price data covers {price_min} ~ {price_max}."
        )

    rebalance_dates = _monthly_rebalance_dates(trade_dates)
    if not rebalance_dates:
        raise ValueError("No rebalance dates were derived from trading dates.")

    symbols = sorted(list(set(pred_wide.columns).intersection(set(returns.columns))))
    if not symbols:
        pred_symbols_sample = list(pred_wide.columns[:5])
        price_symbols_sample = list(returns.columns[:5])
        raise ValueError(
            f"No overlapping symbols between predictions ({len(pred_wide.columns)} symbols) "
            f"and prices ({len(returns.columns)} symbols). "
            f"Sample prediction symbols: {pred_symbols_sample}. "
            f"Sample price symbols: {price_symbols_sample}. "
            f"Verify the same universe was used for training."
        )

    policy = get_portfolio_policy()
    universe_policy = get_universe_policy()
    cash_symbol = str(policy.get("cash_symbol", "CASH")).strip().upper() or "CASH"
    policy_max_weight = float(
        universe_policy.get("portfolio_constraints", {}).get("max_weight_per_stock", 0.04)
    )
    effective_max_weight = min(
        apply_effective_max_weight(constraints.max_weight),
        policy_max_weight,
    )

    daily_rows: list[dict[str, Any]] = []
    weight_rows: list[dict[str, Any]] = []
    current_weights = np.zeros(len(symbols))
    turnover_values: list[float] = []
    strategy_returns: list[float] = []
    gross_returns: list[float] = []
    trading_costs: list[float] = []
    commission_costs: list[float] = []
    spread_costs: list[float] = []
    impact_costs: list[float] = []
    borrow_costs: list[float] = []
    cost_breakdown: list[dict[str, Any]] = []
    regime_mode_rows: list[dict[str, str]] = []
    regime_frame = _compute_regime_series(close_panel, returns.index, benchmark_symbol)
    latest_cash_weight = 0.0
    rebalance_history_rows: list[dict[str, Any]] = []
    constraint_violations: list[dict[str, Any]] = []
    rebalance_reports: list[dict[str, Any]] = []
    liquidity_clip_values: list[float] = []
    risk_contribution_values: list[float] = []
    risk_budget_scales: list[float] = []
    gross_exposure_series: list[float] = []
    net_exposure_series: list[float] = []
    long_exposure_series: list[float] = []
    short_exposure_series: list[float] = []
    ic_values: list[float] = []
    rank_ic_values: list[float] = []
    universe_stage_counts_latest: dict[str, int] = {}

    base_index = 100.0
    equity = base_index
    max_equity_seen = float(base_index)
    first_trade_date = pd.Timestamp(trade_dates[0])
    daily_rows.append(
        {
            "date": first_trade_date.date().isoformat(),
            "daily_return": 0.0,
            "equity": equity,
        }
    )

    commission_bps = (
        float(constraints.commission_bps)
        if constraints.commission_bps is not None
        else float(cost_bps)
    )
    half_spread_bps = (
        float(constraints.half_spread_bps)
        if constraints.half_spread_bps is not None
        else float(slippage_bps) / 2.0
    )
    impact_k = float(getattr(constraints, "impact_k", 0.0))
    borrow_bps = float(getattr(constraints, "borrow_bps", 0.0))
    current_cash_weight = 1.0
    for idx, rebalance_date in enumerate(rebalance_dates):
        rebalance_key = rebalance_date.date().isoformat()
        context = (rebalance_universe_context or {}).get(rebalance_key, {})
        available_pred_dates = pred_wide.index[pred_wide.index <= rebalance_date]
        if len(available_pred_dates) == 0:
            continue
        signal_date = pd.Timestamp(available_pred_dates.max())
        if bool(getattr(constraints, "leakage_guard", True)) and signal_date > rebalance_date:
            raise ValueError(
                f"leakage_detected: prediction date {signal_date.date()} exceeds rebalance date {rebalance_date.date()}"
            )
        mu = pred_wide.loc[signal_date, symbols].fillna(0.0).values.astype(float)
        hist = returns.loc[returns.index < rebalance_date, symbols].tail(constraints.lookback_days)
        cov = _estimate_covariance(
            hist_returns=hist,
            method=str(getattr(constraints, "cov_method", "sample")),
            ewma_halflife=int(getattr(constraints, "cov_ewma_halflife", 42)),
            shrinkage=float(getattr(constraints, "cov_shrinkage", 0.15)),
        )
        trend_regime = "sideways"
        vol_regime = "mid"
        if not regime_frame.empty:
            regime_row = regime_frame.reindex([rebalance_date], method="ffill").iloc[0]
            trend_regime = str(regime_row.get("trend_regime", "sideways"))
            vol_regime = str(regime_row.get("vol_regime", "mid"))
        current_drawdown = max(0.0, 1.0 - float(equity / max(max_equity_seen, 1e-12)))
        risk_budget_scale = 1.0
        if regime_policy == "mixed":
            risk_budget_scale = _dynamic_risk_budget_scale(
                trend_regime=trend_regime,
                vol_regime=vol_regime,
                current_drawdown=current_drawdown,
            )
        risk_budget_scales.append(float(risk_budget_scale))
        dynamic_max_weight = max(0.005, float(effective_max_weight) * float(risk_budget_scale))
        dynamic_risk_aversion = float(constraints.risk_aversion) / max(
            float(risk_budget_scale), 0.35
        )
        allow_short = bool(portfolio_mode == "long_short" and not constraints.long_only)
        mode_used = "long_short" if allow_short else "long_only"
        if allow_short and regime_policy == "mixed":
            allow_short = _mixed_policy_allows_short(trend_regime, vol_regime)
            mode_used = "long_short" if allow_short else "long_only"

        binding_constraints: list[str] = []
        period_violations: list[dict[str, Any]] = []
        if allow_short:
            optimized = _optimize_weights(
                mu,
                cov,
                constraints,
                allow_short=allow_short,
                max_weight=dynamic_max_weight,
                risk_aversion=dynamic_risk_aversion,
            )
            optimized = np.clip(
                optimized,
                -dynamic_max_weight if allow_short else 0.0,
                dynamic_max_weight,
            )
            weight_sum = float(np.sum(optimized))
            cash_weight = 0.0
            if weight_sum != 1.0:
                optimized = optimized + ((1.0 - weight_sum) / max(len(optimized), 1))
                optimized = np.clip(optimized, -dynamic_max_weight, dynamic_max_weight)
            if regime_policy == "mixed" and risk_budget_scale < 0.999:
                binding_constraints.append("dynamic_risk_budget")
            liquidity_clip_values.append(0.0)
            risk_contribution_values.append(0.0)
        else:
            eligible_symbols = set(context.get("u2_symbols", symbols))
            universe_stage_counts_latest = dict(
                context.get(
                    "stage_counts",
                    universe_stage_counts_latest,
                )
            )
            active_indices = [i for i, symbol in enumerate(symbols) if symbol in eligible_symbols]
            optimized = np.zeros(len(symbols), dtype=float)
            if not active_indices:
                cash_weight = 1.0
                binding_constraints = ["no_eligible_symbols", "cash_buffer"]
                liquidity_clip_values.append(1.0)
                risk_contribution_values.append(0.0)
                period_violations.append(
                    {"type": "no_eligible_symbols", "date": rebalance_key}
                )
            else:
                active_symbols = [symbols[i] for i in active_indices]
                mu_active = mu[active_indices]
                cov_active = cov[np.ix_(active_indices, active_indices)]
                scenario_lookback = max(
                    int(getattr(constraints, "scenario_lookback_days", constraints.lookback_days)),
                    int(constraints.lookback_days),
                )
                scenario_frame = returns.loc[:rebalance_date, active_symbols].tail(
                    scenario_lookback
                )
                metric_rows = context.get("symbol_metrics", {})
                metadata_active: dict[str, dict[str, Any]] = {}
                for symbol in active_symbols:
                    metric_meta = {}
                    if isinstance(metric_rows, dict):
                        metric_meta = dict(metric_rows.get(symbol, {}))
                    if "adv20_usd" not in metric_meta:
                        price_hist = (
                            close_panel.loc[:rebalance_date, symbol].tail(20)
                            if symbol in close_panel.columns
                            else pd.Series(dtype=float)
                        )
                        px_mean = float(
                            pd.to_numeric(price_hist, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna().mean()
                        ) if not price_hist.empty else 0.0
                        metric_meta["adv20_usd"] = max(px_mean * 100_000.0, 10_000_000.0)
                    metric_meta.setdefault("sector_l1", "other")
                    metric_meta.setdefault(
                        "country", "KR" if symbol.endswith(".KS") or symbol.endswith(".KQ") else "US"
                    )
                    metadata_active[symbol] = metric_meta

                adv_active = np.array(
                    [
                        float(metadata_active.get(symbol, {}).get("adv20_usd", 10_000_000.0))
                        for symbol in active_symbols
                    ],
                    dtype=float,
                )
                beta_active = np.array(
                    [
                        float(
                            metadata_active.get(symbol, {}).get(
                                "beta_spy",
                                metadata_active.get(symbol, {}).get(
                                    "beta_market",
                                    metadata_active.get(symbol, {}).get("beta", 0.0),
                                ),
                            )
                        )
                        for symbol in active_symbols
                    ],
                    dtype=float,
                )
                current_active = current_weights[active_indices]
                cost_params = {
                    "commission_bps": commission_bps,
                    "half_spread_bps": half_spread_bps,
                    "impact_k": impact_k,
                    "turnover_penalty_mode": str(getattr(constraints, "turnover_penalty_mode", "none")),
                    "turnover_penalty": float(getattr(constraints, "turnover_penalty", 0.0)),
                }
                exposure_constraints = {
                    "allow_short": False,
                    "gross_exposure_max": float(getattr(constraints, "gross_exposure_max", 1.5)),
                    "net_exposure_min": float(getattr(constraints, "net_exposure_min", 0.0)),
                    "net_exposure_max": float(getattr(constraints, "net_exposure_max", 1.0)),
                    "sector_max_weight": float(getattr(constraints, "sector_max_weight", 0.35)),
                    "sector_neutral": bool(getattr(constraints, "sector_neutral", False)),
                    "beta_neutral": bool(getattr(constraints, "beta_neutral", False)),
                    "beta_tolerance": float(getattr(constraints, "beta_tolerance", 0.05)),
                    "target_beta": 0.0,
                }

                opt_result = optimize_weights_v2(
                    mu=mu_active,
                    cov=cov_active,
                    symbols=active_symbols,
                    metadata_by_symbol=metadata_active,
                    risk_aversion=dynamic_risk_aversion,
                    requested_max_weight=dynamic_max_weight,
                    policy=universe_policy,
                    nav=1.0,
                    optimizer_mode=str(constraints.optimizer_mode),
                    cvar_alpha=float(constraints.cvar_alpha),
                    cvar_lambda=float(constraints.cvar_lambda),
                    scenario_returns=scenario_frame.fillna(0.0).to_numpy(dtype=float),
                    current_weights=current_active,
                    cost_params=cost_params,
                    exposure_constraints=exposure_constraints,
                    beta_vector=beta_active,
                    target_vol=(
                        float(constraints.target_vol)
                        if getattr(constraints, "target_vol", None) is not None
                        else None
                    ),
                )
                optimized_active = opt_result.weights
                if regime_policy == "mixed" and risk_budget_scale < 0.999:
                    optimized_active = optimized_active * float(risk_budget_scale)
                    binding_constraints = list(opt_result.binding_constraints) + [
                        "dynamic_risk_budget"
                    ]
                else:
                    binding_constraints = list(opt_result.binding_constraints)
                for local_idx, global_idx in enumerate(active_indices):
                    optimized[global_idx] = float(optimized_active[local_idx])
                cash_weight = float(max(0.0, 1.0 - float(np.sum(optimized_active))))
                latest_cash_weight = cash_weight
                period_violations = [
                    {"date": rebalance_key, **violation}
                    for violation in opt_result.constraint_violations
                ]
                liquidity_clip_values.append(float(opt_result.liquidity_clip_ratio))
                risk_contribution_values.append(float(opt_result.risk_contribution_max))
                rebalance_reports.append(
                    {
                        "date": rebalance_key,
                        "position_sizing_log": [
                            {
                                "symbol": symbol,
                                "weight": float(weight),
                                "sector": str(metadata_active.get(symbol, {}).get("sector_l1", "other")),
                                "country": str(metadata_active.get(symbol, {}).get("country", "US")),
                            }
                            for symbol, weight in zip(active_symbols, optimized_active, strict=False)
                            if float(weight) > 0
                        ],
                        "liquidity_constraint_report": [
                            {
                                "symbol": symbol,
                                "adv20_usd": float(
                                    metadata_active.get(symbol, {}).get("adv20_usd", 0.0)
                                ),
                                "weight_cap_adv": float(
                                    0.05
                                    * float(metadata_active.get(symbol, {}).get("adv20_usd", 0.0))
                                ),
                            }
                            for symbol in active_symbols
                        ],
                        "risk_contribution_report": [
                            {
                                "symbol": symbol,
                                "risk_contribution": float(value),
                            }
                            for symbol, value in zip(
                                active_symbols,
                                (
                                    np.zeros(len(active_symbols))
                                    if len(active_symbols) == 0
                                    else (
                                        optimized_active
                                        * (cov_active @ optimized_active)
                                        / max(
                                            float(
                                                np.sqrt(
                                                    max(
                                                        float(
                                                            optimized_active
                                                            @ cov_active
                                                            @ optimized_active
                                                        ),
                                                        1e-9,
                                                    )
                                                )
                                            ),
                                            1e-9,
                                        )
                                    )
                                ),
                                strict=False,
                            )
                        ],
                        "sector_exposure_report": [
                            {"sector": sector, "weight": float(weight)}
                            for sector, weight in opt_result.sector_exposure.items()
                        ],
                        "country_exposure_report": [
                            {"country": country, "weight": float(weight)}
                            for country, weight in opt_result.country_exposure.items()
                        ],
                        "binding_constraints": binding_constraints,
                        "estimated_cost": float(opt_result.estimated_cost),
                        "gross_exposure": float(opt_result.gross_exposure),
                        "net_exposure": float(opt_result.net_exposure),
                        "portfolio_beta": float(opt_result.portfolio_beta),
                    }
                )

        constraint_violations.extend(period_violations)
        turnover = float(np.abs(optimized - current_weights).sum())
        turnover_values.append(turnover)
        regime_mode_rows.append(
            {"date": rebalance_date.date().isoformat(), "mode": mode_used}
        )

        prev_map = {
            symbol: float(weight)
            for symbol, weight in zip(symbols, current_weights, strict=False)
            if float(weight) > 0
        }
        prev_map[cash_symbol] = float(current_cash_weight)
        curr_map = {
            symbol: float(weight)
            for symbol, weight in zip(symbols, optimized, strict=False)
            if float(weight) > 0
        }
        curr_map[cash_symbol] = float(cash_weight)
        added = sorted(
            [symbol for symbol, weight in curr_map.items() if symbol != cash_symbol and weight > 0 and prev_map.get(symbol, 0.0) <= 0]
        )
        sold = sorted(
            [symbol for symbol, weight in prev_map.items() if symbol != cash_symbol and weight > 0 and curr_map.get(symbol, 0.0) <= 0]
        )
        deltas = {
            symbol: float(curr_map.get(symbol, 0.0) - prev_map.get(symbol, 0.0))
            for symbol in set(prev_map) | set(curr_map)
            if symbol != cash_symbol
        }
        increases = sorted(
            [item for item in deltas.items() if item[1] > 0],
            key=lambda item: item[1],
            reverse=True,
        )[:5]
        decreases = sorted(
            [item for item in deltas.items() if item[1] < 0],
            key=lambda item: item[1],
        )[:5]
        rebalance_history_rows.append(
            {
                "date": rebalance_key,
                "previous_date": weight_rows[-1]["date"] if weight_rows else None,
                "added": added,
                "sold": sold,
                "top_weight_increases": [
                    {"symbol": symbol, "delta": float(delta)} for symbol, delta in increases
                ],
                "top_weight_decreases": [
                    {"symbol": symbol, "delta": float(delta)} for symbol, delta in decreases
                ],
                "turnover": float(turnover),
                "risk_budget_scale": float(risk_budget_scale),
                "binding_constraints": binding_constraints,
            }
        )

        metric_rows_all = context.get("symbol_metrics", {})
        adv_full = np.array(
            [
                float(
                    (
                        metric_rows_all.get(symbol, {}).get("adv20_usd", 0.0)
                        if isinstance(metric_rows_all, dict)
                        else 0.0
                    )
                    or (
                        max(
                            float(
                                pd.to_numeric(
                                    close_panel.loc[:rebalance_date, symbol].tail(20),
                                    errors="coerce",
                                )
                                .replace([np.inf, -np.inf], np.nan)
                                .dropna()
                                .mean()
                            )
                            * 100_000.0,
                            10_000_000.0,
                        )
                        if symbol in close_panel.columns
                        else 10_000_000.0
                    )
                )
                for symbol in symbols
            ],
            dtype=float,
        )
        entry_cost_components = _estimate_trade_cost_components(
            delta_w=(optimized - current_weights),
            adv_usd=adv_full,
            commission_bps=commission_bps,
            half_spread_bps=half_spread_bps,
            impact_k=impact_k,
            nav=1.0,
        )

        next_date = (
            rebalance_dates[idx + 1]
            if idx + 1 < len(rebalance_dates)
            else pd.Timestamp(end_date)
        )
        period_mask = (returns.index > rebalance_date) & (returns.index <= next_date)
        period_dates = returns.index[period_mask]

        if len(period_dates) > 0:
            realized_first = returns.loc[period_dates[0], symbols].fillna(0.0).astype(float)
            mu_series = pd.Series(mu, index=symbols, dtype=float)
            valid_mask = np.isfinite(mu_series.values) & np.isfinite(realized_first.values)
            if int(valid_mask.sum()) >= 3:
                mu_valid = mu_series.values[valid_mask]
                ret_valid = realized_first.values[valid_mask]
                if np.std(mu_valid) > 1e-12 and np.std(ret_valid) > 1e-12:
                    ic_values.append(float(np.corrcoef(mu_valid, ret_valid)[0, 1]))
                rank_ic_stat = spearmanr(mu_valid, ret_valid, nan_policy="omit")
                if np.isfinite(rank_ic_stat.correlation):
                    rank_ic_values.append(float(rank_ic_stat.correlation))

        if len(period_dates) == 0:
            current_weights = optimized
            current_cash_weight = cash_weight
            continue

        holding_period_days = int(getattr(constraints, "holding_period_days", -1))
        if holding_period_days < 0:
            active_count = len(period_dates)
        elif holding_period_days == 0:
            active_count = min(1, len(period_dates))
        else:
            active_count = min(int(holding_period_days), len(period_dates))
        liquidate_early = bool(holding_period_days >= 0 and active_count < len(period_dates))
        exit_cost_components = (
            _estimate_trade_cost_components(
                delta_w=(-optimized),
                adv_usd=adv_full,
                commission_bps=commission_bps,
                half_spread_bps=half_spread_bps,
                impact_k=impact_k,
                nav=1.0,
            )
            if liquidate_early and active_count > 0
            else {"commission": 0.0, "spread": 0.0, "impact": 0.0, "total": 0.0}
        )

        for day_idx, trading_date in enumerate(period_dates):
            invested = bool(day_idx < active_count)
            weights_today = optimized if invested else np.zeros(len(symbols), dtype=float)
            ret_vec = returns.loc[trading_date, symbols].fillna(0.0).values.astype(float)
            gross_return = float(np.dot(weights_today, ret_vec))

            cost_commission = 0.0
            cost_spread = 0.0
            cost_impact = 0.0
            trading_cost = 0.0
            if day_idx == 0 and active_count > 0:
                cost_commission += float(entry_cost_components["commission"])
                cost_spread += float(entry_cost_components["spread"])
                cost_impact += float(entry_cost_components["impact"])
                trading_cost += float(entry_cost_components["total"])
            if liquidate_early and day_idx == active_count:
                cost_commission += float(exit_cost_components["commission"])
                cost_spread += float(exit_cost_components["spread"])
                cost_impact += float(exit_cost_components["impact"])
                trading_cost += float(exit_cost_components["total"])

            short_exposure = float(np.abs(np.minimum(weights_today, 0.0)).sum())
            borrow_cost = float(short_exposure * (borrow_bps / 1e4) / 252.0)
            net_return = gross_return - trading_cost - borrow_cost

            gross_exposure_series.append(float(np.abs(weights_today).sum()))
            long_exposure_series.append(float(np.maximum(weights_today, 0.0).sum()))
            short_exposure_series.append(short_exposure)
            net_exposure_series.append(float(np.sum(weights_today)))

            gross_returns.append(gross_return)
            trading_costs.append(trading_cost)
            commission_costs.append(cost_commission)
            spread_costs.append(cost_spread)
            impact_costs.append(cost_impact)
            borrow_costs.append(borrow_cost)
            strategy_returns.append(net_return)
            equity *= 1.0 + net_return
            daily_rows.append(
                {
                    "date": trading_date.date().isoformat(),
                    "daily_return": net_return,
                    "equity": equity,
                    "gross_return": gross_return,
                    "trading_cost": trading_cost,
                }
            )
            max_equity_seen = max(max_equity_seen, float(equity))
            cost_breakdown.append(
                {
                    "date": trading_date.date().isoformat(),
                    "gross_return": gross_return,
                    "trading_cost": trading_cost,
                    "commission_cost": cost_commission,
                    "spread_cost": cost_spread,
                    "impact_cost": cost_impact,
                    "borrow_cost": borrow_cost,
                    "net_return": net_return,
                }
            )

        weight_rows.append(
            {
                "date": rebalance_date.date().isoformat(),
                "weights": (
                    {
                        **{
                            symbol: float(weight)
                            for symbol, weight in zip(symbols, optimized, strict=False)
                        },
                        cash_symbol: float(cash_weight),
                    }
                    if mode_used == "long_only"
                    else {
                        symbol: float(weight)
                        for symbol, weight in zip(symbols, optimized, strict=False)
                    }
                ),
            }
        )
        if liquidate_early:
            current_weights = np.zeros(len(symbols), dtype=float)
            current_cash_weight = 1.0
            latest_cash_weight = 1.0
        else:
            current_weights = optimized
            current_cash_weight = cash_weight

    if not strategy_returns:
        raise ValueError("Backtest produced no return observations.")

    curve = pd.DataFrame(daily_rows)
    daily_returns = pd.Series(strategy_returns, dtype=float)
    equity_series = curve["equity"]
    metrics = _compute_metrics(daily_returns, equity_series)
    metrics["turnover"] = float(np.mean(turnover_values)) if turnover_values else 0.0
    metrics["monthly_turnover"] = float(np.mean(turnover_values)) if turnover_values else 0.0
    metrics["annual_turnover"] = float(metrics["monthly_turnover"] * 12.0)
    metrics["gross_return"] = (
        float(np.prod(1.0 + np.array(gross_returns)) - 1.0) if gross_returns else 0.0
    )
    metrics["total_cost"] = float(np.sum(trading_costs)) if trading_costs else 0.0
    metrics["total_commission"] = (
        float(np.sum(commission_costs)) if commission_costs else 0.0
    )
    metrics["total_spread_cost"] = float(np.sum(spread_costs)) if spread_costs else 0.0
    metrics["total_impact_cost"] = float(np.sum(impact_costs)) if impact_costs else 0.0
    metrics["total_borrow_cost"] = float(np.sum(borrow_costs)) if borrow_costs else 0.0
    metrics["net_return"] = float(equity_series.iloc[-1] / equity_series.iloc[0] - 1.0)
    tail = daily_returns.nsmallest(max(1, int(len(daily_returns) * 0.05)))
    metrics["cvar_95"] = float(tail.mean()) if not tail.empty else 0.0
    metrics["gross_exposure_avg"] = (
        float(np.mean(gross_exposure_series)) if gross_exposure_series else 0.0
    )
    metrics["net_exposure_avg"] = (
        float(np.mean(net_exposure_series)) if net_exposure_series else 0.0
    )
    metrics["long_exposure_avg"] = (
        float(np.mean(long_exposure_series)) if long_exposure_series else 0.0
    )
    metrics["short_exposure_avg"] = (
        float(np.mean(short_exposure_series)) if short_exposure_series else 0.0
    )
    metrics["ic_mean"] = float(np.mean(ic_values)) if ic_values else 0.0
    metrics["ic_ir"] = (
        float(np.mean(ic_values) / (np.std(ic_values, ddof=0) + 1e-12))
        if ic_values
        else 0.0
    )
    metrics["rank_ic_mean"] = float(np.mean(rank_ic_values)) if rank_ic_values else 0.0
    metrics["rank_ic_ir"] = (
        float(np.mean(rank_ic_values) / (np.std(rank_ic_values, ddof=0) + 1e-12))
        if rank_ic_values
        else 0.0
    )

    curve_dates = pd.to_datetime(curve["date"]).dt.tz_localize(None)
    benchmark_curve = _benchmark_curve(
        close_panel=close_panel,
        curve_dates=pd.DatetimeIndex(curve_dates),
        benchmark_symbol=benchmark_symbol,
        base_index=base_index,
    )

    return BacktestResult(
        metrics=metrics,
        equity_curve=curve.to_dict(orient="records"),
        period_weights=weight_rows,
        benchmark_symbol=benchmark_symbol,
        benchmark_curve=benchmark_curve,
        base_index=base_index,
        cost_breakdown=cost_breakdown,
        consistency_checks=_consistency_checks(weight_rows, turnover_values),
        regime_mode_by_period=regime_mode_rows,
        effective_constraints={
            "max_weight_requested": float(constraints.max_weight),
            "max_weight_applied": float(effective_max_weight),
            "max_weight": float(effective_max_weight),
            "long_only": bool(constraints.long_only),
            "risk_aversion": float(constraints.risk_aversion),
            "lookback_days": float(constraints.lookback_days),
            "optimizer_mode_cvar": bool(str(constraints.optimizer_mode) == "cvar"),
            "cvar_alpha": float(constraints.cvar_alpha),
            "cvar_lambda": float(constraints.cvar_lambda),
            "scenario_lookback_days": float(constraints.scenario_lookback_days),
            "cov_method": str(getattr(constraints, "cov_method", "sample")),
            "cov_ewma_halflife": float(getattr(constraints, "cov_ewma_halflife", 42)),
            "cov_shrinkage": float(getattr(constraints, "cov_shrinkage", 0.15)),
            "commission_bps": float(commission_bps),
            "half_spread_bps": float(half_spread_bps),
            "impact_k": float(impact_k),
            "borrow_bps": float(borrow_bps),
            "holding_period_days": float(getattr(constraints, "holding_period_days", -1)),
            "leakage_guard": bool(getattr(constraints, "leakage_guard", True)),
            "dynamic_risk_budget_mixed": bool(regime_policy == "mixed"),
            "risk_budget_scale_avg": float(np.mean(risk_budget_scales))
            if risk_budget_scales
            else 1.0,
            "risk_budget_scale_min": float(np.min(risk_budget_scales))
            if risk_budget_scales
            else 1.0,
            "sector_cap": float(
                universe_policy.get("portfolio_constraints", {}).get("sector_cap", 0.25)
            ),
            "country_cap": float(
                universe_policy.get("portfolio_constraints", {}).get("country_cap", 0.35)
            ),
        },
        cash_weight=float(latest_cash_weight),
        rebalance_history_summary=rebalance_history_rows,
        constraint_violations=constraint_violations,
        liquidity_clip_ratio=(
            float(np.mean(liquidity_clip_values)) if liquidity_clip_values else 0.0
        ),
        risk_contribution_max=(
            float(np.max(risk_contribution_values)) if risk_contribution_values else 0.0
        ),
        universe_stage_counts=universe_stage_counts_latest,
        rebalance_reports=rebalance_reports,
    )
