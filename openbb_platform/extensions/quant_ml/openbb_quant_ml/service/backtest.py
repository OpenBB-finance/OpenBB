"""Portfolio construction and backtest helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

import numpy as np
import pandas as pd
from scipy.optimize import minimize
import yfinance as yf

from openbb_quant_ml.models import BacktestConstraints


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


def _monthly_rebalance_dates(dates: pd.DatetimeIndex) -> list[pd.Timestamp]:
    if len(dates) == 0:
        return []
    grouped = pd.Series(dates, index=dates).groupby(dates.to_period("M")).first()
    return [pd.Timestamp(value) for value in grouped.values]


def _safe_initial_weights(asset_count: int, max_weight: float) -> np.ndarray:
    equal = np.repeat(1.0 / asset_count, asset_count)
    clipped = np.minimum(equal, max_weight)
    clipped_sum = clipped.sum()
    if clipped_sum <= 0:
        return equal
    if np.isclose(clipped_sum, 1.0):
        return clipped
    return clipped / clipped_sum


def _optimize_weights(
    mu: np.ndarray,
    cov: np.ndarray,
    constraints: BacktestConstraints,
    *,
    allow_short: bool,
) -> np.ndarray:
    asset_count = len(mu)
    if asset_count == 0:
        return np.array([])

    feasible_max = max(constraints.max_weight, 1.0 / asset_count)
    bounds = [(-feasible_max, feasible_max) if allow_short else (0.0, feasible_max) for _ in range(asset_count)]
    initial = _safe_initial_weights(asset_count, feasible_max)

    def objective(weights: np.ndarray) -> float:
        mean_term = float(np.dot(mu, weights))
        risk_term = float(weights @ cov @ weights)
        return -(mean_term - constraints.risk_aversion * risk_term)

    optimizer_constraints = [{"type": "eq", "fun": lambda w: float(np.sum(w) - 1.0)}]
    if allow_short:
        gross_cap = 1.5
        optimizer_constraints.append({"type": "ineq", "fun": lambda w: float(gross_cap - np.sum(np.abs(w)))})

    result = minimize(
        objective,
        initial,
        method="SLSQP",
        bounds=bounds,
        constraints=optimizer_constraints,
    )
    if result.success:
        clipped = np.clip(result.x, -feasible_max if allow_short else 0.0, feasible_max)
        if allow_short:
            gross = float(np.sum(np.abs(clipped)))
            if gross > 1.5 and gross > 0:
                clipped = clipped * (1.5 / gross)
            clipped = clipped + ((1.0 - float(np.sum(clipped))) / max(asset_count, 1))
            clipped = np.clip(clipped, -feasible_max, feasible_max)
        return clipped

    positive = np.maximum(mu, 0.0)
    if allow_short:
        centered = mu - float(np.mean(mu))
        positive = np.maximum(centered, 0.0)
        negative = np.maximum(-centered, 0.0)
        if positive.sum() > 0 and negative.sum() > 0:
            short_budget = min(0.35, float(negative.sum() / (positive.sum() + negative.sum() + 1e-12)))
            long_w = positive / positive.sum()
            short_w = negative / negative.sum()
            fallback = long_w * (1.0 + short_budget) - short_w * short_budget
            fallback = np.clip(fallback, -feasible_max, feasible_max)
            fallback = fallback + ((1.0 - float(np.sum(fallback))) / max(asset_count, 1))
            return np.clip(fallback, -feasible_max, feasible_max)
    if positive.sum() > 0:
        fallback = positive / positive.sum()
        return np.clip(fallback, -feasible_max if allow_short else 0.0, feasible_max)
    return initial


def _compute_regime_series(
    close_panel: pd.DataFrame,
    dates: pd.DatetimeIndex,
    benchmark_symbol: str,
) -> pd.DataFrame:
    if len(dates) == 0:
        return pd.DataFrame(columns=["trend_regime", "vol_regime"])
    symbol = benchmark_symbol if benchmark_symbol in close_panel.columns else str(close_panel.columns[0])
    benchmark = close_panel[symbol].astype(float).reindex(dates).ffill().bfill()
    if benchmark.empty:
        return pd.DataFrame(index=dates, data={"trend_regime": "sideways", "vol_regime": "mid"})
    ret = benchmark.pct_change(fill_method=None).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    ma200 = benchmark.rolling(200, min_periods=20).mean()
    trend = np.where(
        benchmark > ma200 * 1.01,
        "bull",
        np.where(benchmark < ma200 * 0.99, "bear", "sideways"),
    )
    vol20 = ret.rolling(20, min_periods=5).std(ddof=0) * np.sqrt(252)
    low_q = float(vol20.quantile(0.33))
    high_q = float(vol20.quantile(0.66))
    vol_regime = np.where(vol20 <= low_q, "low", np.where(vol20 >= high_q, "high", "mid"))
    return pd.DataFrame(
        index=dates,
        data={
            "trend_regime": trend,
            "vol_regime": vol_regime,
        },
    )


def _mixed_policy_allows_short(trend_regime: str, vol_regime: str) -> bool:
    return trend_regime == "bull" and vol_regime in {"low", "mid"}


def _consistency_checks(period_weights: list[dict[str, Any]], turnover_values: list[float]) -> dict[str, float | bool]:
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


def _compute_metrics(daily_returns: pd.Series, equity_curve: pd.Series) -> dict[str, float]:
    if daily_returns.empty:
        return {
            "cagr": 0.0,
            "sharpe": 0.0,
            "max_drawdown": 0.0,
            "volatility": 0.0,
            "turnover": 0.0,
        }

    trading_days = max(len(daily_returns), 1)
    total_return = float(equity_curve.iloc[-1] / equity_curve.iloc[0] - 1.0)
    cagr = float((1 + total_return) ** (252 / trading_days) - 1) if trading_days > 0 else 0.0

    vol = float(daily_returns.std(ddof=0) * np.sqrt(252))
    sharpe = float((daily_returns.mean() / (daily_returns.std(ddof=0) + 1e-12)) * np.sqrt(252))

    running_max = equity_curve.cummax()
    drawdown = equity_curve / (running_max + 1e-12) - 1.0
    max_drawdown = float(drawdown.min())
    return {
        "cagr": cagr,
        "sharpe": sharpe,
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
        return [{"date": d.date().isoformat(), "benchmark": float(base_index)} for d in curve_dates]

    first_price = float(aligned.iloc[0]) if float(aligned.iloc[0]) != 0 else 1.0
    index_values = (aligned / first_price) * base_index
    return [
        {"date": dt.date().isoformat(), "benchmark": float(value)}
        for dt, value in index_values.items()
    ]


def run_backtest(
    predictions: pd.DataFrame,
    close_panel: pd.DataFrame,
    start_date: date,
    end_date: date,
    constraints: BacktestConstraints,
    cost_bps: float,
    benchmark_symbol: str = "SPY",
    portfolio_mode: str = "long_only",
    regime_policy: str = "fixed",
) -> BacktestResult:
    """Run monthly-rebalance mean-variance backtest with SPY benchmark."""
    if predictions.empty:
        raise ValueError("No predictions are available for backtest.")
    if close_panel.empty:
        raise ValueError("No price data is available for backtest.")

    pred = predictions.copy()
    pred["date"] = pd.to_datetime(pred["date"]).dt.tz_localize(None)
    pred_wide = pred.pivot(index="date", columns="symbol", values="predicted_return").sort_index()

    price_panel = close_panel.copy()
    price_panel.index = pd.to_datetime(price_panel.index).tz_localize(None)
    returns = price_panel.pct_change(fill_method=None).fillna(0.0)

    window_mask = (returns.index.date >= start_date) & (returns.index.date <= end_date)
    trade_dates = returns.index[window_mask]
    if len(trade_dates) == 0:
        raise ValueError("No trading days found in the selected date range.")

    rebalance_dates = [d for d in _monthly_rebalance_dates(trade_dates) if d in pred_wide.index]
    if not rebalance_dates:
        candidates = [d for d in pred_wide.index if d in trade_dates]
        if not candidates:
            raise ValueError("Prediction dates and price dates do not overlap.")
        rebalance_dates = [candidates[0]]

    symbols = sorted(list(set(pred_wide.columns).intersection(set(returns.columns))))
    if not symbols:
        raise ValueError("No overlapping symbols between predictions and prices.")

    daily_rows: list[dict[str, Any]] = []
    weight_rows: list[dict[str, Any]] = []
    current_weights = np.zeros(len(symbols))
    turnover_values: list[float] = []
    strategy_returns: list[float] = []
    gross_returns: list[float] = []
    trading_costs: list[float] = []
    cost_breakdown: list[dict[str, Any]] = []
    regime_mode_rows: list[dict[str, str]] = []
    regime_frame = _compute_regime_series(price_panel, returns.index, benchmark_symbol)

    base_index = 100.0
    equity = base_index
    first_trade_date = pd.Timestamp(trade_dates[0])
    daily_rows.append(
        {
            "date": first_trade_date.date().isoformat(),
            "daily_return": 0.0,
            "equity": equity,
        }
    )

    for idx, rebalance_date in enumerate(rebalance_dates):
        mu = pred_wide.loc[rebalance_date, symbols].fillna(0.0).values.astype(float)
        hist = returns.loc[:rebalance_date, symbols].tail(constraints.lookback_days)
        cov = hist.cov().fillna(0.0).values
        allow_short = bool(portfolio_mode == "long_short" and not constraints.long_only)
        mode_used = "long_short" if allow_short else "long_only"
        if allow_short and regime_policy == "mixed" and not regime_frame.empty:
            regime_row = regime_frame.reindex([rebalance_date], method="ffill").iloc[0]
            allow_short = _mixed_policy_allows_short(
                str(regime_row.get("trend_regime", "sideways")),
                str(regime_row.get("vol_regime", "mid")),
            )
            mode_used = "long_short" if allow_short else "long_only"

        optimized = _optimize_weights(mu, cov, constraints, allow_short=allow_short)

        turnover = float(np.abs(optimized - current_weights).sum())
        turnover_values.append(turnover)
        regime_mode_rows.append({"date": rebalance_date.date().isoformat(), "mode": mode_used})

        next_date = rebalance_dates[idx + 1] if idx + 1 < len(rebalance_dates) else pd.Timestamp(end_date)
        period_mask = (returns.index > rebalance_date) & (returns.index <= next_date)
        period_dates = returns.index[period_mask]
        if len(period_dates) == 0:
            current_weights = optimized
            continue

        for day_idx, trading_date in enumerate(period_dates):
            ret_vec = returns.loc[trading_date, symbols].fillna(0.0).values
            gross_return = float(np.dot(optimized, ret_vec))
            trading_cost = (cost_bps / 10000.0) * turnover if day_idx == 0 else 0.0
            net_return = gross_return - trading_cost
            gross_returns.append(gross_return)
            trading_costs.append(trading_cost)
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
            cost_breakdown.append(
                {
                    "date": trading_date.date().isoformat(),
                    "gross_return": gross_return,
                    "trading_cost": trading_cost,
                    "net_return": net_return,
                }
            )

        weight_rows.append(
            {
                "date": rebalance_date.date().isoformat(),
                "weights": {
                    symbol: float(weight) for symbol, weight in zip(symbols, optimized, strict=False)
                },
            }
        )
        current_weights = optimized

    if not strategy_returns:
        raise ValueError("Backtest produced no return observations.")

    curve = pd.DataFrame(daily_rows)
    daily_returns = pd.Series(strategy_returns, dtype=float)
    equity_series = curve["equity"]
    metrics = _compute_metrics(daily_returns, equity_series)
    metrics["turnover"] = float(np.mean(turnover_values)) if turnover_values else 0.0
    gross_curve = float(np.prod(1.0 + np.array(gross_returns)) - 1.0) if gross_returns else 0.0
    metrics["gross_return"] = gross_curve
    metrics["total_cost"] = float(np.sum(trading_costs)) if trading_costs else 0.0
    metrics["net_return"] = float(equity_series.iloc[-1] / equity_series.iloc[0] - 1.0)

    curve_dates = pd.to_datetime(curve["date"]).dt.tz_localize(None)
    benchmark_curve = _benchmark_curve(
        close_panel=price_panel,
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
    )
