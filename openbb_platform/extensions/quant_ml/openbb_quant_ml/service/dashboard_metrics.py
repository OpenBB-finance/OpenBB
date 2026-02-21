"""Dashboard metrics and payload builders for Quant ML."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from openbb_quant_ml.models import (
    AlertItem,
    AlertsResponse,
    AssetClassWeightItem,
    DashboardHealthResponse,
    ICDecayResponse,
    ModelName,
    ModelShapResponse,
    PerformanceRegimeResponse,
    PortfolioExposureResponse,
    PortfolioRiskResponse,
    PredictionDistributionResponse,
    RegimeCurrentResponse,
    RegimeHistoryResponse,
    RollingPerformanceResponse,
)
from openbb_quant_ml.service.constants import RAW_STORE_DIR, RUNS_DIR
from openbb_quant_ml.service.run_index import (
    get_latest_run_id_from_index,
    upsert_run_index_entry,
)
from openbb_quant_ml.service.run_registry import append_log, update_run
from openbb_quant_ml.service.runtime_pointer import get_promoted_model
from openbb_quant_ml.service.stale_policy import (
    STALE_TIMEOUT_MINUTES,
    is_stale,
    latest_artifact_mtime,
)
from openbb_quant_ml.service.storage import (
    get_run_dir,
    load_json,
    read_registry,
    save_json,
)
from openbb_quant_ml.service.universe import (
    get_symbol_metadata_map,
    load_universe_config,
)

DEFAULT_MODEL: ModelName = "lgbm_ranker"
SUPPORTED_MODELS: tuple[ModelName, ...] = ("xgb_lstm", "lgbm_ranker")
ALERTS_FILENAME_PREFIX = "alerts"

BOND_DURATION_MAP: dict[str, float] = {
    "TLT": 17.2,
    "VGLT": 16.1,
    "IEF": 7.4,
    "VGIT": 5.6,
    "GOVT": 6.8,
    "SHY": 1.8,
    "VGSH": 1.9,
    "BIL": 0.1,
    "TIP": 6.7,
    "LQD": 8.6,
    "VCIT": 6.4,
    "VCLT": 12.5,
    "HYG": 3.7,
    "JNK": 4.0,
    "SJNK": 2.6,
    "BND": 6.2,
    "BNDX": 7.3,
    "EMB": 7.7,
    "BWX": 7.8,
    "MBB": 4.2,
}


def _normalize_model_name(model_name: str | None) -> ModelName:
    if model_name in SUPPORTED_MODELS:
        return model_name
    return DEFAULT_MODEL


def _parse_iso_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        normalized = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)
    except ValueError:
        return None


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        casted = float(value)
        if np.isnan(casted) or np.isinf(casted):
            return default
        return casted
    except (TypeError, ValueError):
        return default


def _json_sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_sanitize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_sanitize(item) for item in value]
    if isinstance(value, tuple):
        return [_json_sanitize(item) for item in value]
    if isinstance(value, (float, np.floating)):
        casted = float(value)
        if np.isnan(casted) or np.isinf(casted):
            return 0.0
        return casted
    return value


def _sanitize_model_response(model: Any) -> Any:
    payload = _json_sanitize(model.model_dump(mode="json"))
    return model.__class__.model_validate(payload)


def _has_run_dir(run_id: str | None) -> bool:
    if not run_id:
        return False
    return get_run_dir(run_id).exists()


def _list_run_dirs() -> list[Path]:
    if not RUNS_DIR.exists():
        return []
    return [path for path in RUNS_DIR.iterdir() if path.is_dir()]


def _latest_run_from_registry() -> str | None:
    payload = read_registry()
    runs = payload.get("runs", {})
    latest_run_id = None
    latest_ts: datetime | None = None
    for run_id, item in runs.items():
        parsed = _parse_iso_timestamp(item.get("updated_at"))
        if parsed is None:
            continue
        if latest_ts is None or parsed > latest_ts:
            latest_ts = parsed
            latest_run_id = str(run_id)
    return latest_run_id


def get_latest_run_id() -> str | None:
    """Return latest run id using registry first, then filesystem mtime."""
    indexed_latest = get_latest_run_id_from_index()
    if indexed_latest and _has_run_dir(indexed_latest):
        return indexed_latest

    registry_latest = _latest_run_from_registry()
    if registry_latest and _has_run_dir(registry_latest):
        upsert_run_index_entry(run_id=registry_latest)
        return registry_latest

    run_dirs = _list_run_dirs()
    if not run_dirs:
        return None
    run_dirs.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    upsert_run_index_entry(run_id=run_dirs[0].name)
    return run_dirs[0].name


def _resolve_run_id(run_id: str | None) -> str | None:
    if run_id and _has_run_dir(run_id):
        return run_id
    return get_latest_run_id()


def _artifact_candidates(
    run_dir: Path, prefix: str, model_name: ModelName, suffix: str
) -> list[Path]:
    return [
        run_dir / f"{prefix}_{model_name}.{suffix}",
        run_dir / f"{prefix}.{suffix}",
    ]


def _artifact_exists(
    run_dir: Path, prefix: str, model_name: ModelName, suffix: str
) -> bool:
    return any(
        path.exists()
        for path in _artifact_candidates(run_dir, prefix, model_name, suffix)
    )


def _registry_run_state(run_id: str) -> dict[str, Any]:
    payload = read_registry()
    runs = payload.get("runs", {})
    state = runs.get(run_id, {})
    return state if isinstance(state, dict) else {}


def _infer_run_state(run_dir: Path, model_name: ModelName) -> dict[str, Any]:
    has_backtest = _artifact_exists(run_dir, "backtest", model_name, "json")
    has_predictions = _artifact_exists(run_dir, "predictions", model_name, "parquet")
    has_metrics = _artifact_exists(run_dir, "metrics", model_name, "json")
    has_signals = _artifact_exists(run_dir, "signals", model_name, "parquet")
    has_market_data = (run_dir / "market_data.parquet").exists()
    has_config = (run_dir / "config.json").exists()

    if has_backtest:
        status = "completed"
        progress = 100
        stage = "backtest_completed"
    elif has_predictions or has_metrics:
        status = "completed"
        progress = 95
        stage = "training_completed"
    elif has_market_data:
        status = "running"
        progress = 60
        stage = "training_artifacts_detected"
    elif has_config:
        status = "queued"
        progress = 5
        stage = "configured"
    else:
        status = "unknown"
        progress = 0
        stage = "unknown"

    return {
        "status": status,
        "progress": progress,
        "stage": stage,
        "updated_at": datetime.fromtimestamp(run_dir.stat().st_mtime, tz=UTC)
        .replace(microsecond=0)
        .isoformat(),
        "artifacts_ready": {
            "predictions": bool(has_predictions),
            "signals": bool(has_signals),
            "backtest": bool(has_backtest),
            "portfolio_current": bool(has_backtest),
        },
    }


def _workflow_state_payload(
    run_id: str, run_dir: Path, model_name: ModelName
) -> tuple[dict[str, Any], bool]:
    inferred = _infer_run_state(run_dir, model_name)
    registry_state = _registry_run_state(run_id)
    artifact_flags = inferred["artifacts_ready"]

    run_status = str(registry_state.get("status", inferred["status"]))
    run_stage = str(registry_state.get("stage", inferred["stage"]))
    run_progress = int(registry_state.get("progress", inferred["progress"]))
    updated_at = str(registry_state.get("updated_at", inferred["updated_at"]))

    stale_running = False
    stale_reason: str | None = None
    if run_status == "running":
        stale_running, stale_reason, _ = is_stale(
            updated_at,
            registry_state.get("last_heartbeat_at"),
            latest_artifact_mtime(run_dir),
            timeout_minutes=STALE_TIMEOUT_MINUTES,
        )
        if stale_running and not any(artifact_flags.values()):
            update_run(
                run_id,
                status="failed",
                stage="stale_run_timeout",
                progress=100,
                error="stale_run_timeout",
                stale_reason=stale_reason or "idle_timeout",
            )
            append_log(
                run_id,
                f"Run failed automatically after {STALE_TIMEOUT_MINUTES} minutes without heartbeat/artifact progress.",
            )
            run_status = "failed"
            run_stage = "stale_run_timeout"
            run_progress = 100
            updated_at = datetime.now(UTC).replace(microsecond=0).isoformat()
            stale_running = False
            upsert_run_index_entry(
                run_id=run_id,
                status=run_status,
                stage=run_stage,
                updated_at=updated_at,
            )

    return (
        {
            "run_status": (
                run_status
                if run_status in {"queued", "running", "completed", "failed"}
                else "unknown"
            ),
            "run_stage": run_stage,
            "run_progress": max(0, min(100, run_progress)),
            "artifacts_ready": artifact_flags,
            "updated_at": updated_at,
        },
        stale_running,
    )


def _load_json_artifact(
    run_dir: Path, prefix: str, model_name: ModelName
) -> dict[str, Any]:
    for path in _artifact_candidates(run_dir, prefix, model_name, "json"):
        payload = load_json(path, default={})
        if isinstance(payload, dict) and payload:
            return payload
    return {}


def _load_predictions(run_dir: Path, model_name: ModelName) -> pd.DataFrame:
    for path in _artifact_candidates(run_dir, "predictions", model_name, "parquet"):
        if path.exists():
            frame = pd.read_parquet(path)
            if frame.empty:
                return frame
            frame = frame.copy()
            frame["date"] = pd.to_datetime(frame["date"]).dt.tz_localize(None)
            return frame
    return pd.DataFrame()


def _load_backtest(run_dir: Path, model_name: ModelName) -> dict[str, Any]:
    return _load_json_artifact(run_dir, "backtest", model_name)


def _load_metrics(run_dir: Path, model_name: ModelName) -> dict[str, Any]:
    return _load_json_artifact(run_dir, "metrics", model_name)


def _load_market_panel(run_dir: Path) -> pd.DataFrame:
    _, close_panel = _load_market_price_panels(run_dir)
    return close_panel


def _load_market_price_panels(run_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    market_path = run_dir / "market_data.parquet"
    if not market_path.exists():
        return pd.DataFrame(), pd.DataFrame()
    frame = pd.read_parquet(market_path)
    if frame.empty:
        return pd.DataFrame(), pd.DataFrame()
    base = frame.assign(date=pd.to_datetime(frame["date"]).dt.tz_localize(None))
    close_panel = base.pivot(
        index="date", columns="symbol", values="close"
    ).sort_index()
    if "open" in base.columns:
        open_panel = base.pivot(
            index="date", columns="symbol", values="open"
        ).sort_index()
    else:
        open_panel = close_panel.copy()
    open_panel = open_panel.reindex(
        index=close_panel.index, columns=close_panel.columns
    ).ffill()
    return open_panel, close_panel


def _series_points(
    series: pd.Series, *, key: str = "value"
) -> list[dict[str, float | str]]:
    if series.empty:
        return []
    series = series.dropna()
    points: list[dict[str, float | str]] = []
    for date_value, value in series.items():
        points.append(
            {
                "date": pd.Timestamp(date_value).date().isoformat(),
                key: _safe_float(value),
            }
        )
    return points


def _safe_spearman(x: pd.Series, y: pd.Series) -> float:
    aligned = pd.concat([x, y], axis=1).replace([np.inf, -np.inf], np.nan).dropna()
    if aligned.shape[0] < 3:
        return 0.0
    xv = aligned.iloc[:, 0]
    yv = aligned.iloc[:, 1]
    if xv.nunique(dropna=True) <= 1 or yv.nunique(dropna=True) <= 1:
        return 0.0
    corr = spearmanr(xv, yv, nan_policy="omit").correlation
    if corr is None or np.isnan(corr):
        return 0.0
    return float(corr)


def _ic_series(
    predictions: pd.DataFrame, score_col: str = "predicted_return"
) -> pd.Series:
    if predictions.empty or "target_return" not in predictions.columns:
        return pd.Series(dtype=float)
    with_target = predictions.dropna(subset=["target_return"]).copy()
    if with_target.empty:
        return pd.Series(dtype=float)
    rows: list[tuple[pd.Timestamp, float]] = []
    for date_value, group in with_target.groupby("date"):
        if len(group) < 3:
            continue
        ic = _safe_spearman(group[score_col], group["target_return"])
        rows.append((pd.Timestamp(date_value), ic))
    if not rows:
        return pd.Series(dtype=float)
    frame = pd.DataFrame(rows, columns=["date", "ic"]).set_index("date").sort_index()
    return frame["ic"]


def _strategy_returns(backtest_payload: dict[str, Any]) -> pd.Series:
    curve = pd.DataFrame(backtest_payload.get("equity_curve", []))
    if curve.empty:
        return pd.Series(dtype=float)
    curve["date"] = pd.to_datetime(curve["date"]).dt.tz_localize(None)
    curve["daily_return"] = pd.to_numeric(
        curve["daily_return"], errors="coerce"
    ).fillna(0.0)
    return curve.set_index("date")["daily_return"].sort_index()


def _equity_series(backtest_payload: dict[str, Any]) -> pd.Series:
    curve = pd.DataFrame(backtest_payload.get("equity_curve", []))
    if curve.empty:
        return pd.Series(dtype=float)
    curve["date"] = pd.to_datetime(curve["date"]).dt.tz_localize(None)
    curve["equity"] = (
        pd.to_numeric(curve["equity"], errors="coerce").ffill().fillna(100.0)
    )
    return curve.set_index("date")["equity"].sort_index()


def _weights_by_date(
    backtest_payload: dict[str, Any],
) -> list[tuple[pd.Timestamp, dict[str, float]]]:
    rows: list[tuple[pd.Timestamp, dict[str, float]]] = []
    for item in backtest_payload.get("period_weights", []) or []:
        date_value = item.get("date")
        weights = item.get("weights", {})
        if not date_value or not isinstance(weights, dict):
            continue
        parsed = pd.Timestamp(date_value)
        normalized: dict[str, float] = {}
        for symbol, weight in weights.items():
            normalized[str(symbol)] = _safe_float(weight)
        rows.append((parsed, normalized))
    rows.sort(key=lambda pair: pair[0])
    return rows


def _latest_weights(
    backtest_payload: dict[str, Any],
) -> tuple[pd.Timestamp | None, dict[str, float]]:
    rows = _weights_by_date(backtest_payload)
    if not rows:
        return None, {}
    return rows[-1][0], rows[-1][1]


def _exposure_from_weights(weights: dict[str, float]) -> tuple[float, float, float]:
    if not weights:
        return 1.0, 0.0, 0.0
    gross = float(sum(abs(weight) for weight in weights.values()))
    net = float(sum(weights.values()))
    cash = max(0.0, 1.0 - gross)
    return cash, gross, net


def _turnover_and_exposure_series(
    backtest_payload: dict[str, Any],
) -> tuple[pd.Series, pd.DataFrame]:
    rows = _weights_by_date(backtest_payload)
    if not rows:
        return pd.Series(dtype=float), pd.DataFrame(columns=["cash", "gross", "net"])

    prev: dict[str, float] = {}
    turnover_rows: list[tuple[pd.Timestamp, float]] = []
    exposure_rows: list[dict[str, Any]] = []
    for date_value, weights in rows:
        symbols = set(prev).union(weights)
        turnover = float(
            sum(abs(weights.get(sym, 0.0) - prev.get(sym, 0.0)) for sym in symbols)
        )
        cash, gross, net = _exposure_from_weights(weights)
        turnover_rows.append((date_value, turnover))
        exposure_rows.append(
            {
                "date": date_value,
                "cash": cash,
                "gross": gross,
                "net": net,
            }
        )
        prev = weights

    turnover_series = pd.DataFrame(
        turnover_rows, columns=["date", "turnover"]
    ).set_index("date")["turnover"]
    exposure_frame = pd.DataFrame(exposure_rows).set_index("date").sort_index()
    return turnover_series.sort_index(), exposure_frame


def _rolling_sharpe(returns: pd.Series, window: int) -> pd.Series:
    if returns.empty:
        return pd.Series(dtype=float)
    rolling_mean = returns.rolling(
        window=window, min_periods=max(10, window // 3)
    ).mean()
    rolling_std = returns.rolling(window=window, min_periods=max(10, window // 3)).std(
        ddof=0
    )
    sharpe = (rolling_mean / (rolling_std + 1e-12)) * np.sqrt(252)
    return sharpe.replace([np.inf, -np.inf], 0.0).fillna(0.0)


def _rolling_max_drawdown(equity: pd.Series) -> pd.Series:
    if equity.empty:
        return pd.Series(dtype=float)
    running_max = equity.cummax()
    drawdown = equity / (running_max + 1e-12) - 1.0
    return drawdown.fillna(0.0)


def _category_map() -> dict[str, str]:
    symbol_metadata = get_symbol_metadata_map()
    if symbol_metadata:
        return {
            str(symbol): str(meta.get("category_l2") or meta.get("category") or "other")
            for symbol, meta in symbol_metadata.items()
        }
    universe_payload = load_universe_config()
    assets = universe_payload.get("assets", [])
    return {
        str(item.get("symbol")): str(item.get("category", "other")) for item in assets
    }


def _sector_exposure(weights: dict[str, float]) -> list[AssetClassWeightItem]:
    if not weights:
        return []
    category_map = _category_map()
    bucket: dict[str, float] = {}
    total = float(sum(max(weight, 0.0) for weight in weights.values()))
    total = total if total > 0 else 1.0
    for symbol, weight in weights.items():
        if weight <= 0:
            continue
        category = category_map.get(symbol, "other")
        bucket[category] = bucket.get(category, 0.0) + (weight / total)
    return [
        AssetClassWeightItem(category=key, weight=value)
        for key, value in sorted(bucket.items(), key=lambda pair: pair[1], reverse=True)
    ]


def _returns_panel(close_panel: pd.DataFrame) -> pd.DataFrame:
    if close_panel.empty:
        return pd.DataFrame()
    return (
        close_panel.pct_change(fill_method=None)
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0.0)
    )


def _beta(y: pd.Series, x: pd.Series) -> float:
    aligned = pd.concat([y, x], axis=1).dropna()
    if aligned.shape[0] < 30:
        return 0.0
    yv = aligned.iloc[:, 0].to_numpy(dtype=float)
    xv = aligned.iloc[:, 1].to_numpy(dtype=float)
    var_x = float(np.var(xv))
    if var_x <= 1e-12:
        return 0.0
    cov_xy = float(np.cov(xv, yv)[0, 1])
    return cov_xy / var_x


def _rolling_beta(y: pd.Series, x: pd.Series, window: int = 126) -> pd.Series:
    aligned = pd.concat([y, x], axis=1).dropna()
    if aligned.shape[0] < max(window, 30):
        return pd.Series(dtype=float)
    values: list[tuple[pd.Timestamp, float]] = []
    for idx in range(window, len(aligned) + 1):
        window_frame = aligned.iloc[idx - window : idx]
        beta_value = _beta(window_frame.iloc[:, 0], window_frame.iloc[:, 1])
        values.append((window_frame.index[-1], beta_value))
    if not values:
        return pd.Series(dtype=float)
    return pd.DataFrame(values, columns=["date", "beta"]).set_index("date")["beta"]


def _factor_exposure(
    strategy_returns: pd.Series, close_panel: pd.DataFrame, lookback: int = 126
) -> dict[str, float]:
    returns = _returns_panel(close_panel)
    if returns.empty or strategy_returns.empty:
        return {
            "momentum": 0.0,
            "value": 0.0,
            "size": 0.0,
            "volatility": 0.0,
        }
    aligned = strategy_returns.dropna()
    if aligned.shape[0] > lookback:
        aligned = aligned.tail(lookback)

    proxies: dict[str, pd.Series] = {}
    if "MTUM" in returns.columns:
        proxies["momentum"] = returns["MTUM"]
    if "VLUE" in returns.columns:
        proxies["value"] = returns["VLUE"]
    elif "VTV" in returns.columns:
        proxies["value"] = returns["VTV"]
    if "IWM" in returns.columns and "SPY" in returns.columns:
        proxies["size"] = returns["IWM"] - returns["SPY"]
    if "USMV" in returns.columns:
        proxies["volatility"] = returns["USMV"]

    out = {"momentum": 0.0, "value": 0.0, "size": 0.0, "volatility": 0.0}
    for key, series in proxies.items():
        out[key] = _safe_float(_beta(aligned, series.reindex(aligned.index)), 0.0)
    return out


def _duration_estimate(weights: dict[str, float]) -> float:
    if not weights:
        return 0.0
    total = 0.0
    for symbol, weight in weights.items():
        duration = BOND_DURATION_MAP.get(symbol)
        if duration is None:
            continue
        total += abs(weight) * duration
    return float(total)


def _portfolio_cov(
    close_panel: pd.DataFrame, symbols: list[str], lookback: int
) -> tuple[pd.DataFrame, pd.Series]:
    if close_panel.empty or not symbols:
        return pd.DataFrame(), pd.Series(dtype=float)
    returns = _returns_panel(close_panel)[symbols].dropna(how="all")
    if returns.empty:
        return pd.DataFrame(), pd.Series(dtype=float)
    returns = returns.tail(max(lookback, 20)).fillna(0.0)
    cov = returns.cov()
    mean_ret = returns.mean() * 252.0
    return cov, mean_ret


def _risk_contributions(
    cov: pd.DataFrame, weights: dict[str, float]
) -> list[dict[str, float | str]]:
    if cov.empty or not weights:
        return []
    symbols = [symbol for symbol in cov.columns if symbol in weights]
    if not symbols:
        return []
    w = np.array([weights[symbol] for symbol in symbols], dtype=float)
    sigma = cov.loc[symbols, symbols].to_numpy(dtype=float)
    port_var = float(w @ sigma @ w)
    port_vol = np.sqrt(max(port_var, 1e-12))
    mrc = sigma @ w / (port_vol + 1e-12)
    rc = w * mrc
    rows = [
        {"symbol": symbol, "contribution": float(value)}
        for symbol, value in zip(symbols, rc, strict=False)
    ]
    rows.sort(key=lambda item: abs(float(item["contribution"])), reverse=True)
    return rows


def _regime_frame(close_panel: pd.DataFrame) -> pd.DataFrame:
    if close_panel.empty:
        return pd.DataFrame()
    spy_symbol = "SPY" if "SPY" in close_panel.columns else str(close_panel.columns[0])
    spy = close_panel[spy_symbol].dropna().astype(float)
    if spy.empty:
        return pd.DataFrame()

    spy_ret = spy.pct_change().fillna(0.0)
    ma200 = spy.rolling(200, min_periods=20).mean()
    distance = (spy / (ma200 + 1e-12) - 1.0).fillna(0.0)
    trend_regime = np.where(
        distance > 0.01, "bull", np.where(distance < -0.01, "bear", "sideways")
    )

    vol20 = (spy_ret.rolling(20, min_periods=5).std(ddof=0) * np.sqrt(252)).fillna(0.0)
    if (vol20 > 0).any():
        low_q = float(vol20.quantile(0.33))
        high_q = float(vol20.quantile(0.66))
        vol_regime = np.where(
            vol20 <= low_q, "low", np.where(vol20 >= high_q, "high", "mid")
        )
    else:
        vol_regime = np.repeat("mid", len(vol20))

    breadth_cols = [
        symbol
        for symbol in close_panel.columns
        if close_panel[symbol].notna().sum() > 220
    ]
    if not breadth_cols:
        breadth = pd.Series(0.0, index=spy.index)
    else:
        filtered = close_panel[breadth_cols].reindex(spy.index).ffill()
        above_ma = (
            filtered / (filtered.rolling(200, min_periods=20).mean() + 1e-12) - 1.0
        ) > 0
        breadth = above_ma.mean(axis=1).fillna(0.0)

    liquidity_proxy = (
        close_panel.reindex(spy.index)
        .notna()
        .sum(axis=1)
        .rolling(20, min_periods=5)
        .mean()
    )
    if liquidity_proxy.nunique(dropna=True) <= 1:
        liquidity_regime = np.repeat("mid", len(liquidity_proxy))
    else:
        low_q = float(liquidity_proxy.quantile(0.33))
        high_q = float(liquidity_proxy.quantile(0.66))
        liquidity_regime = np.where(
            liquidity_proxy <= low_q,
            "low",
            np.where(liquidity_proxy >= high_q, "high", "mid"),
        )

    vix_level = vol20 * 100.0
    if "^VIX" in close_panel.columns:
        vix_level = close_panel["^VIX"].reindex(spy.index).ffill().bfill()

    out = pd.DataFrame(
        {
            "trend_regime": trend_regime,
            "vol_regime": vol_regime,
            "liquidity_regime": liquidity_regime,
            "vix_level": vix_level,
            "breadth": breadth,
            "spx_distance_200ma": distance,
        },
        index=spy.index,
    )
    out.index.name = "date"
    return out.sort_index()


def _performance_stats(series: pd.Series) -> dict[str, float | int]:
    if series.empty:
        return {"count": 0, "mean_return": 0.0, "sharpe": 0.0}
    vol = _safe_float(series.std(ddof=0))
    sharpe = _safe_float((series.mean() / (vol + 1e-12)) * np.sqrt(252))
    return {
        "count": int(series.shape[0]),
        "mean_return": _safe_float(series.mean()),
        "sharpe": sharpe,
    }


def _build_regime_performance(
    regime_frame: pd.DataFrame,
    strategy_returns: pd.Series,
    ic_series: pd.Series,
    turnover_series: pd.Series,
) -> tuple[
    dict[str, dict[str, float | int]],
    dict[str, dict[str, float | int]],
    dict[str, dict[str, float | int]],
    list[dict[str, float | str | int]],
]:
    if regime_frame.empty or strategy_returns.empty:
        return {}, {}, {}, []

    aligned = regime_frame.join(strategy_returns.rename("strategy_return"), how="inner")
    if aligned.empty:
        return {}, {}, {}, []

    aligned["ic"] = ic_series.reindex(aligned.index).ffill().fillna(0.0)
    aligned["turnover"] = turnover_series.reindex(aligned.index).ffill().fillna(0.0)

    def _collect(column: str) -> dict[str, dict[str, float | int]]:
        payload: dict[str, dict[str, float | int]] = {}
        for key, group in aligned.groupby(column):
            stats = _performance_stats(group["strategy_return"])
            stats["ic"] = _safe_float(group["ic"].mean())
            stats["turnover"] = _safe_float(group["turnover"].mean())
            payload[str(key)] = stats
        return payload

    trend_perf = _collect("trend_regime")
    vol_perf = _collect("vol_regime")
    liq_perf = _collect("liquidity_regime")

    matrix_rows: list[dict[str, float | str | int]] = []
    for (trend_key, vol_key), group in aligned.groupby(["trend_regime", "vol_regime"]):
        stats = _performance_stats(group["strategy_return"])
        matrix_rows.append(
            {
                "trend_regime": str(trend_key),
                "vol_regime": str(vol_key),
                "count": int(stats["count"]),
                "sharpe": _safe_float(stats["sharpe"]),
                "mean_return": _safe_float(stats["mean_return"]),
                "ic": _safe_float(group["ic"].mean()),
            }
        )
    return trend_perf, vol_perf, liq_perf, matrix_rows


def _latest_prediction_frame(predictions: pd.DataFrame) -> pd.DataFrame:
    if predictions.empty:
        return pd.DataFrame()
    latest_date = predictions["date"].max()
    latest = predictions[predictions["date"] == latest_date].copy()
    if latest.empty:
        return latest
    score = latest["predicted_return"].astype(float)
    std = float(score.std(ddof=0))
    if std <= 0:
        latest["z_score"] = 0.0
    else:
        latest["z_score"] = (score - float(score.mean())) / (std + 1e-12)
    return latest


def _safe_symbol(symbol: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", str(symbol))


def _cache_warm_ratio(
    config_payload: dict[str, Any],
    predictions: pd.DataFrame,
) -> float:
    symbols: list[str] = []
    req = config_payload.get("request", {}) if isinstance(config_payload, dict) else {}
    req_symbols = req.get("symbols", []) if isinstance(req, dict) else []
    if isinstance(req_symbols, list):
        symbols = [
            str(item).strip().upper() for item in req_symbols if str(item).strip()
        ]
    if not symbols and not predictions.empty:
        symbols = sorted(
            {
                str(item).strip().upper()
                for item in predictions["symbol"].tolist()
                if str(item).strip()
            }
        )
    if not symbols:
        return 0.0
    warmed = 0
    for symbol in symbols:
        path = RAW_STORE_DIR / f"{_safe_symbol(symbol)}.parquet"
        if path.exists():
            warmed += 1
    return float(warmed) / float(max(len(symbols), 1))


def _prediction_confidence(latest_predictions: pd.DataFrame) -> float:
    if latest_predictions.empty:
        return 0.0
    z_abs = latest_predictions.get("z_score", pd.Series(dtype=float)).abs()
    dispersion = _safe_float(z_abs.mean())

    agreement = 1.0
    if {"predicted_xgb", "predicted_lstm"}.issubset(set(latest_predictions.columns)):
        diff = (
            latest_predictions["predicted_xgb"] - latest_predictions["predicted_lstm"]
        ).abs()
        denom = latest_predictions["predicted_return"].abs().mean() + 1e-12
        agreement = float(max(0.0, min(1.0, 1.0 - float(diff.mean()) / float(denom))))

    confidence = 0.6 * min(1.0, dispersion / 2.5) + 0.4 * agreement
    return float(max(0.0, min(1.0, confidence)))


def _strategy_health(
    latest_predictions: pd.DataFrame,
    latest_weights: dict[str, float],
    strategy_returns: pd.Series,
    benchmark_returns: pd.Series,
    regime_perf: dict[str, dict[str, float | int]],
    current_regime: str | None,
) -> dict[str, float]:
    if latest_predictions.empty:
        return {
            "signal_dispersion": 0.0,
            "crowding_risk_proxy": 0.0,
            "market_correlation": 0.0,
            "regime_mismatch_risk": 0.0,
            "prediction_confidence": 0.0,
        }

    signal_dispersion = _safe_float(latest_predictions["z_score"].std(ddof=0))

    weights = np.array([abs(weight) for weight in latest_weights.values()], dtype=float)
    if weights.size == 0:
        crowding = 0.0
    else:
        normalized = weights / (weights.sum() + 1e-12)
        hhi = float(np.sum(normalized**2))
        top10 = float(np.sort(normalized)[::-1][:10].sum())
        crowding = 0.5 * hhi + 0.5 * top10

    market_corr = 0.0
    aligned = pd.concat([strategy_returns, benchmark_returns], axis=1).dropna()
    if aligned.shape[0] >= 30:
        market_corr = _safe_float(aligned.iloc[:, 0].corr(aligned.iloc[:, 1]))

    mismatch = 0.0
    sharpe_values = [float(item.get("sharpe", 0.0)) for item in regime_perf.values()]
    if sharpe_values and current_regime in regime_perf:
        current = float(regime_perf[current_regime].get("sharpe", 0.0))
        mean_sharpe = float(np.mean(sharpe_values))
        std_sharpe = float(np.std(sharpe_values))
        z = (current - mean_sharpe) / (std_sharpe + 1e-12)
        mismatch = float(max(0.0, -z))

    return {
        "signal_dispersion": signal_dispersion,
        "crowding_risk_proxy": crowding,
        "market_correlation": market_corr,
        "regime_mismatch_risk": mismatch,
        "prediction_confidence": _prediction_confidence(latest_predictions),
    }


def _recommended_portfolio_mode(
    trend_regime: str | None, vol_regime: str | None
) -> str:
    trend = (trend_regime or "sideways").lower()
    vol = (vol_regime or "mid").lower()
    if trend == "bull" and vol in {"low", "mid"}:
        return "long_short"
    return "long_only"


def get_dashboard_health(
    run_id: str | None = None, model_name: str | None = None
) -> DashboardHealthResponse:
    """Build dashboard health payload."""
    normalized_model = _normalize_model_name(model_name)
    latest_run_id = get_latest_run_id()
    resolved_run_id = _resolve_run_id(run_id)
    promoted_payload = get_promoted_model(model_name=normalized_model)
    promoted_run_id = (
        str(promoted_payload.get("run_id")) if promoted_payload.get("run_id") else None
    )
    pretrain_ready = bool(promoted_payload.get("ready", False))

    if run_id and not _has_run_dir(run_id):
        return _sanitize_model_response(
            DashboardHealthResponse(
                run_id=run_id,
                model_name=normalized_model,
                status="not_found",
                message="Run not found",
                latest_run_id=latest_run_id,
                resolved_run_id=resolved_run_id,
                promoted_run_id=promoted_run_id,
                pretrain_ready=pretrain_ready,
                backend_connected=True,
                backend_source="quant_ml_api",
                backend_detail="quant_ml_api_connected",
            )
        )

    if not resolved_run_id:
        return _sanitize_model_response(
            DashboardHealthResponse(
                run_id=run_id,
                model_name=normalized_model,
                status="insufficient_data",
                message="No available runs",
                latest_run_id=latest_run_id,
                resolved_run_id=resolved_run_id,
                promoted_run_id=promoted_run_id,
                pretrain_ready=pretrain_ready,
            )
        )

    run_dir = get_run_dir(resolved_run_id)
    workflow_state, stale_running = _workflow_state_payload(
        resolved_run_id, run_dir, normalized_model
    )
    backtest_payload = _load_backtest(run_dir, normalized_model)
    predictions = _load_predictions(run_dir, normalized_model)
    metrics_payload = _load_metrics(run_dir, normalized_model)
    config_payload = load_json(run_dir / "config.json", default={})
    cache_warm_ratio = _cache_warm_ratio(config_payload, predictions)

    latest_weight_date, latest_weights = _latest_weights(backtest_payload)
    cash_exp, gross_exp, net_exp = _exposure_from_weights(latest_weights)

    universe_size = 0
    symbols = config_payload.get("request", {}).get("symbols")
    if isinstance(symbols, list):
        universe_size = len(symbols)
    elif not predictions.empty:
        universe_size = int(predictions["symbol"].nunique())

    data_timestamp: str | None = None
    if latest_weight_date is not None:
        data_timestamp = latest_weight_date.date().isoformat()
    elif not predictions.empty:
        data_timestamp = pd.Timestamp(predictions["date"].max()).date().isoformat()

    strategy_returns = _strategy_returns(backtest_payload)
    close_panel = _load_market_panel(run_dir)
    benchmark_returns = pd.Series(dtype=float)
    if not close_panel.empty:
        benchmark_symbol = (
            "SPY" if "SPY" in close_panel.columns else str(close_panel.columns[0])
        )
        benchmark_returns = _returns_panel(close_panel)[benchmark_symbol]
        benchmark_returns = benchmark_returns.reindex(strategy_returns.index).fillna(
            0.0
        )

    ic_series = _ic_series(predictions)
    turnover_series, _ = _turnover_and_exposure_series(backtest_payload)
    regime_frame = _regime_frame(close_panel)
    trend_perf, _, _, _ = _build_regime_performance(
        regime_frame, strategy_returns, ic_series, turnover_series
    )
    current_regime = None
    current_vol_regime = None
    if not regime_frame.empty:
        current_regime = str(regime_frame.iloc[-1]["trend_regime"])
        current_vol_regime = str(regime_frame.iloc[-1]["vol_regime"])

    strategy_health = _strategy_health(
        latest_predictions=_latest_prediction_frame(predictions),
        latest_weights=latest_weights,
        strategy_returns=strategy_returns,
        benchmark_returns=benchmark_returns,
        regime_perf=trend_perf,
        current_regime=current_regime,
    )

    has_predictions = bool(
        workflow_state.get("artifacts_ready", {}).get("predictions", False)
    )
    has_backtest = bool(
        workflow_state.get("artifacts_ready", {}).get("backtest", False)
    )
    has_metrics = bool(metrics_payload)
    latest_market_date = None
    if not close_panel.empty:
        latest_market_date = pd.Timestamp(close_panel.index.max()).date().isoformat()
    elif not predictions.empty:
        latest_market_date = pd.Timestamp(predictions["date"].max()).date().isoformat()

    staleness_days = 0
    if data_timestamp and latest_market_date:
        try:
            staleness_days = max(
                0,
                (
                    pd.Timestamp(latest_market_date).date()
                    - pd.Timestamp(data_timestamp).date()
                ).days,
            )
        except Exception:  # noqa: BLE001
            staleness_days = 0

    recommended_mode = _recommended_portfolio_mode(current_regime, current_vol_regime)
    status = "ok"
    message: str | None = None
    if not has_predictions or not has_metrics:
        status = "insufficient_data"
        message = "Run exists but predictions/metrics are not ready."
    elif not has_backtest:
        message = "Run backtest first to populate portfolio and risk panels."
    if stale_running and status != "not_found":
        stall_message = f"Run appears stalled: no heartbeat/artifact progress for >= {STALE_TIMEOUT_MINUTES} minutes."
        message = f"{message} {stall_message}".strip() if message else stall_message
    if (
        workflow_state.get("run_status") == "running"
        and not has_predictions
        and not has_metrics
    ):
        status = "insufficient_data"
        if not message:
            message = "Run is still in progress. Predictions are not ready yet."

    return _sanitize_model_response(
        DashboardHealthResponse(
            run_id=run_id,
            model_name=normalized_model,
            status=status,
            latest_run_id=latest_run_id,
            resolved_run_id=resolved_run_id,
            promoted_run_id=promoted_run_id,
            pretrain_ready=pretrain_ready,
            cache_warm_ratio=cache_warm_ratio,
            data_timestamp=data_timestamp,
            latest_market_date=latest_market_date,
            staleness_days=staleness_days,
            recommended_portfolio_mode=recommended_mode,
            universe_size=universe_size,
            cost_bps=_safe_float(backtest_payload.get("cost_bps", 10.0), 10.0),
            cash_exposure=cash_exp,
            gross_exposure=gross_exp,
            net_exposure=net_exp,
            strategy_health=strategy_health,
            message=message,
            workflow_state=workflow_state,
            backend_connected=True,
            backend_source="quant_ml_api",
            backend_detail="quant_ml_api_connected",
        )
    )


def get_performance_rolling(
    run_id: str,
    model_name: str | None = None,
    window_short: int = 63,
    window_long: int = 126,
) -> RollingPerformanceResponse:
    """Return rolling performance payload."""
    if not _has_run_dir(run_id):
        raise ValueError(f"Run not found: {run_id}")
    normalized_model = _normalize_model_name(model_name)
    run_dir = get_run_dir(run_id)
    backtest_payload = _load_backtest(run_dir, normalized_model)
    predictions = _load_predictions(run_dir, normalized_model)

    strategy_returns = _strategy_returns(backtest_payload)
    equity = _equity_series(backtest_payload)
    if strategy_returns.empty or equity.empty:
        return _sanitize_model_response(
            RollingPerformanceResponse(
                run_id=run_id,
                model_name=normalized_model,
                status="insufficient_data",
                message="Run backtest first",
                window_short=window_short,
                window_long=window_long,
            )
        )

    cumulative = equity / (float(equity.iloc[0]) + 1e-12) - 1.0
    rolling_sharpe_short = _rolling_sharpe(strategy_returns, max(int(window_short), 10))
    rolling_sharpe_long = _rolling_sharpe(strategy_returns, max(int(window_long), 20))

    ic_series = _ic_series(predictions)
    rolling_ic_short = ic_series.rolling(
        max(int(window_short), 5), min_periods=1
    ).mean()
    rolling_ic_long = ic_series.rolling(max(int(window_long), 5), min_periods=1).mean()

    maxdd = _rolling_max_drawdown(equity)
    turnover_series, exposure_frame = _turnover_and_exposure_series(backtest_payload)
    exposure_rows: list[dict[str, float | str]] = []
    for date_value, row in exposure_frame.iterrows():
        exposure_rows.append(
            {
                "date": pd.Timestamp(date_value).date().isoformat(),
                "cash": _safe_float(row.get("cash")),
                "gross": _safe_float(row.get("gross")),
                "net": _safe_float(row.get("net")),
            }
        )

    return _sanitize_model_response(
        RollingPerformanceResponse(
            run_id=run_id,
            model_name=normalized_model,
            status="ok",
            window_short=window_short,
            window_long=window_long,
            cumulative_return=_series_points(cumulative),
            rolling_sharpe_3m=_series_points(rolling_sharpe_short),
            rolling_sharpe_6m=_series_points(rolling_sharpe_long),
            rolling_ic_3m=_series_points(rolling_ic_short),
            rolling_ic_6m=_series_points(rolling_ic_long),
            rolling_maxdd=_series_points(maxdd),
            turnover_ts=_series_points(turnover_series, key="value"),
            exposure_ts=exposure_rows,
        )
    )


def get_performance_regime(
    run_id: str, model_name: str | None = None
) -> PerformanceRegimeResponse:
    """Return regime performance payload."""
    if not _has_run_dir(run_id):
        raise ValueError(f"Run not found: {run_id}")
    normalized_model = _normalize_model_name(model_name)
    run_dir = get_run_dir(run_id)
    backtest_payload = _load_backtest(run_dir, normalized_model)
    predictions = _load_predictions(run_dir, normalized_model)
    close_panel = _load_market_panel(run_dir)

    strategy_returns = _strategy_returns(backtest_payload)
    if strategy_returns.empty or close_panel.empty:
        return _sanitize_model_response(
            PerformanceRegimeResponse(
                run_id=run_id,
                model_name=normalized_model,
                status="insufficient_data",
                message="Run backtest first",
            )
        )

    ic_series = _ic_series(predictions)
    turnover_series, _ = _turnover_and_exposure_series(backtest_payload)
    regime_frame = _regime_frame(close_panel)
    trend_perf, vol_perf, liquidity_perf, matrix = _build_regime_performance(
        regime_frame=regime_frame,
        strategy_returns=strategy_returns,
        ic_series=ic_series,
        turnover_series=turnover_series,
    )

    return _sanitize_model_response(
        PerformanceRegimeResponse(
            run_id=run_id,
            model_name=normalized_model,
            trend_regime_perf=trend_perf,
            vol_regime_perf=vol_perf,
            liquidity_regime_perf=liquidity_perf,
            matrix_2d=matrix,
        )
    )


def get_portfolio_exposure(
    run_id: str, model_name: str | None = None
) -> PortfolioExposureResponse:
    """Return portfolio exposure payload."""
    if not _has_run_dir(run_id):
        raise ValueError(f"Run not found: {run_id}")
    normalized_model = _normalize_model_name(model_name)
    run_dir = get_run_dir(run_id)
    backtest_payload = _load_backtest(run_dir, normalized_model)
    close_panel = _load_market_panel(run_dir)

    _, latest_weights = _latest_weights(backtest_payload)
    if not latest_weights:
        return _sanitize_model_response(
            PortfolioExposureResponse(
                run_id=run_id,
                model_name=normalized_model,
                status="insufficient_data",
                message="Run backtest first",
            )
        )

    sector_exposure = _sector_exposure(latest_weights)
    strategy_returns = _strategy_returns(backtest_payload)
    factor_exposure = _factor_exposure(strategy_returns, close_panel, lookback=126)

    returns = _returns_panel(close_panel)
    spy_series = returns["SPY"] if "SPY" in returns.columns else pd.Series(dtype=float)
    qqq_series = returns["QQQ"] if "QQQ" in returns.columns else pd.Series(dtype=float)
    beta_spy = _beta(
        strategy_returns.tail(126), spy_series.reindex(strategy_returns.tail(126).index)
    )
    beta_qqq = _beta(
        strategy_returns.tail(126), qqq_series.reindex(strategy_returns.tail(126).index)
    )

    top_long = sorted(
        ((symbol, weight) for symbol, weight in latest_weights.items() if weight > 0),
        key=lambda pair: pair[1],
        reverse=True,
    )[:10]
    top_short = sorted(
        ((symbol, weight) for symbol, weight in latest_weights.items() if weight < 0),
        key=lambda pair: pair[1],
    )[:10]

    top10_long = [
        {"symbol": symbol, "weight": _safe_float(weight)} for symbol, weight in top_long
    ]
    top10_short = [
        {"symbol": symbol, "weight": _safe_float(weight)}
        for symbol, weight in top_short
    ]

    return _sanitize_model_response(
        PortfolioExposureResponse(
            run_id=run_id,
            model_name=normalized_model,
            sector_exposure=sector_exposure,
            factor_exposure=factor_exposure,
            beta_spy=_safe_float(beta_spy),
            beta_qqq=_safe_float(beta_qqq),
            duration_estimate=_duration_estimate(latest_weights),
            top10_long=top10_long,
            top10_short=top10_short,
        )
    )


def get_portfolio_risk(
    run_id: str, model_name: str | None = None, lookback: int = 126
) -> PortfolioRiskResponse:
    """Return portfolio risk payload."""
    if not _has_run_dir(run_id):
        raise ValueError(f"Run not found: {run_id}")
    normalized_model = _normalize_model_name(model_name)
    run_dir = get_run_dir(run_id)
    backtest_payload = _load_backtest(run_dir, normalized_model)
    close_panel = _load_market_panel(run_dir)
    strategy_returns = _strategy_returns(backtest_payload)
    _, latest_weights = _latest_weights(backtest_payload)

    if not latest_weights:
        return _sanitize_model_response(
            PortfolioRiskResponse(
                run_id=run_id,
                model_name=normalized_model,
                status="insufficient_data",
                message="Run backtest first",
            )
        )

    symbols = [symbol for symbol in latest_weights if symbol in close_panel.columns]
    cov, mean_ret = _portfolio_cov(close_panel, symbols, max(int(lookback), 20))

    w = np.array([latest_weights[symbol] for symbol in symbols], dtype=float)
    sigma = cov.to_numpy(dtype=float) if not cov.empty else np.zeros((0, 0))
    port_var = float(w @ sigma @ w) if sigma.size else 0.0
    vol_ex_ante = float(np.sqrt(max(port_var, 0.0)) * np.sqrt(252))

    cvar_95 = 0.0
    if not strategy_returns.empty:
        tail = strategy_returns.nsmallest(max(1, int(strategy_returns.shape[0] * 0.05)))
        cvar_95 = _safe_float(tail.mean())

    risk_contrib = _risk_contributions(cov, latest_weights)
    return_contrib_rows: list[dict[str, float | str]] = []
    for symbol in symbols:
        value = latest_weights[symbol] * _safe_float(mean_ret.get(symbol, 0.0))
        return_contrib_rows.append({"symbol": symbol, "contribution": value})
    return_contrib_rows.sort(
        key=lambda item: abs(float(item["contribution"])), reverse=True
    )

    worst_rows: list[dict[str, float | str]] = []
    if symbols:
        returns = _returns_panel(close_panel)[symbols].tail(max(int(lookback), 20))
        cumulative = (1 + returns).prod() - 1.0
        for symbol in symbols:
            contribution = latest_weights[symbol] * _safe_float(
                cumulative.get(symbol, 0.0)
            )
            worst_rows.append({"symbol": symbol, "contribution": contribution})
        worst_rows.sort(key=lambda item: float(item["contribution"]))

    return _sanitize_model_response(
        PortfolioRiskResponse(
            run_id=run_id,
            model_name=normalized_model,
            vol_ex_ante=vol_ex_ante,
            cvar_95=cvar_95,
            position_risk_contrib_top5=risk_contrib[:5],
            position_return_contrib_top5=return_contrib_rows[:5],
            worst5_positions=worst_rows[:5],
        )
    )


def get_model_ic_decay(
    run_id: str, model_name: str | None = None, max_horizon: int = 20
) -> ICDecayResponse:
    """Return IC decay payload."""
    if not _has_run_dir(run_id):
        raise ValueError(f"Run not found: {run_id}")
    normalized_model = _normalize_model_name(model_name)
    run_dir = get_run_dir(run_id)
    predictions = _load_predictions(run_dir, normalized_model)
    open_panel, close_panel = _load_market_price_panels(run_dir)
    config_payload = load_json(run_dir / "config.json", default={})
    request_payload = (
        config_payload.get("request", {}) if isinstance(config_payload, dict) else {}
    )
    target_mode = str(request_payload.get("target_mode", "close_to_close"))
    close_to_next_open_policy = str(
        request_payload.get("close_to_next_open_horizon_policy", "fixed_1")
    )

    if predictions.empty or close_panel.empty or open_panel.empty:
        return _sanitize_model_response(
            ICDecayResponse(
                run_id=run_id,
                model_name=normalized_model,
                status="insufficient_data",
                message="Insufficient predictions or market data",
                max_horizon=max_horizon,
            )
        )

    max_h = max(1, int(max_horizon))
    ic_rows: list[dict[str, float | int]] = []
    horizon_values: list[float] = []

    for horizon in range(1, max_h + 1):
        if target_mode == "close_to_next_open":
            open_h = 1 if close_to_next_open_policy == "fixed_1" else horizon
            fwd = open_panel.shift(-open_h) / (close_panel + 1e-12) - 1.0
        elif target_mode == "next_open_to_close":
            fwd = close_panel.shift(-horizon) / (open_panel.shift(-1) + 1e-12) - 1.0
        else:
            fwd = close_panel.shift(-horizon) / (close_panel + 1e-12) - 1.0
        fwd_long = (
            fwd.reset_index()
            .melt(id_vars=["date"], var_name="symbol", value_name="fwd_return")
            .dropna(subset=["fwd_return"])
        )
        merged = predictions.merge(fwd_long, on=["date", "symbol"], how="inner")
        if merged.empty:
            ic_value = 0.0
        else:
            per_date: list[float] = []
            for _, group in merged.groupby("date"):
                if len(group) < 3:
                    continue
                per_date.append(
                    _safe_spearman(group["predicted_return"], group["fwd_return"])
                )
            ic_value = float(np.mean(per_date)) if per_date else 0.0
        ic_rows.append({"horizon": horizon, "ic": _safe_float(ic_value)})
        horizon_values.append(_safe_float(ic_value))

    arr = np.array(horizon_values, dtype=float)
    ic_t_stat = 0.0
    if arr.size >= 2 and float(np.std(arr, ddof=1)) > 0:
        ic_t_stat = float(arr.mean() / (arr.std(ddof=1) / np.sqrt(arr.size)))

    return _sanitize_model_response(
        ICDecayResponse(
            run_id=run_id,
            model_name=normalized_model,
            max_horizon=max_h,
            ic_decay=ic_rows,
            ic_t_stat=ic_t_stat,
        )
    )


def get_prediction_distribution(
    run_id: str, model_name: str | None = None, bins: int = 30
) -> PredictionDistributionResponse:
    """Return prediction distribution payload."""
    if not _has_run_dir(run_id):
        raise ValueError(f"Run not found: {run_id}")
    normalized_model = _normalize_model_name(model_name)
    run_dir = get_run_dir(run_id)
    predictions = _load_predictions(run_dir, normalized_model)
    if predictions.empty:
        return _sanitize_model_response(
            PredictionDistributionResponse(
                run_id=run_id,
                model_name=normalized_model,
                status="insufficient_data",
                message="No predictions available",
                bins=bins,
            )
        )

    latest = _latest_prediction_frame(predictions)
    scores = (
        latest["predicted_return"].astype(float).to_numpy()
        if not latest.empty
        else np.array([])
    )
    hist_rows: list[dict[str, float | int]] = []
    if scores.size >= 1:
        counts, edges = np.histogram(scores, bins=max(5, int(bins)))
        for idx, count in enumerate(counts):
            hist_rows.append(
                {
                    "bin_left": _safe_float(edges[idx]),
                    "bin_right": _safe_float(edges[idx + 1]),
                    "count": int(count),
                }
            )

    top_decile_mean = 0.0
    bottom_decile_mean = 0.0
    if not latest.empty:
        ranked = latest.sort_values("predicted_return", ascending=False)
        k = max(1, int(np.ceil(len(ranked) * 0.1)))
        top_decile_mean = _safe_float(ranked.head(k)["predicted_return"].mean())
        bottom_decile_mean = _safe_float(ranked.tail(k)["predicted_return"].mean())

    spread_rows: list[dict[str, float | str]] = []
    for date_value, group in predictions.groupby("date"):
        ranked = group.sort_values("predicted_return", ascending=False)
        if ranked.empty:
            continue
        k = max(1, int(np.ceil(len(ranked) * 0.1)))
        top_mean = _safe_float(ranked.head(k)["predicted_return"].mean())
        bottom_mean = _safe_float(ranked.tail(k)["predicted_return"].mean())
        spread_rows.append(
            {
                "date": pd.Timestamp(date_value).date().isoformat(),
                "spread": top_mean - bottom_mean,
            }
        )

    return _sanitize_model_response(
        PredictionDistributionResponse(
            run_id=run_id,
            model_name=normalized_model,
            bins=max(5, int(bins)),
            histogram=hist_rows,
            top_decile_mean=top_decile_mean,
            bottom_decile_mean=bottom_decile_mean,
            decile_spread_ts=spread_rows,
        )
    )


def get_regime_history(
    run_id: str, model_name: str | None = None
) -> RegimeHistoryResponse:
    """Return regime history payload."""
    if not _has_run_dir(run_id):
        raise ValueError(f"Run not found: {run_id}")
    normalized_model = _normalize_model_name(model_name)
    run_dir = get_run_dir(run_id)
    regime_frame = _regime_frame(_load_market_panel(run_dir))
    if regime_frame.empty:
        return _sanitize_model_response(
            RegimeHistoryResponse(
                run_id=run_id,
                model_name=normalized_model,
                status="insufficient_data",
                message="No market data available",
            )
        )

    history: list[dict[str, float | str | int]] = []
    for date_value, row in regime_frame.iterrows():
        history.append(
            {
                "date": pd.Timestamp(date_value).date().isoformat(),
                "trend_regime": str(row["trend_regime"]),
                "vol_regime": str(row["vol_regime"]),
                "liquidity_regime": str(row["liquidity_regime"]),
                "vix_level": _safe_float(row["vix_level"]),
                "breadth": _safe_float(row["breadth"]),
                "spx_distance_200ma": _safe_float(row["spx_distance_200ma"]),
            }
        )

    transitions = 0
    prev_state = None
    for row in history:
        state = f"{row['trend_regime']}|{row['vol_regime']}|{row['liquidity_regime']}"
        if prev_state is not None and state != prev_state:
            transitions += 1
        prev_state = state

    transition_stats = {
        "total_points": len(history),
        "transitions": transitions,
        "transition_rate": _safe_float(transitions / max(1, len(history) - 1)),
    }

    return _sanitize_model_response(
        RegimeHistoryResponse(
            run_id=run_id,
            model_name=normalized_model,
            history=history,
            regime_transition_stats=transition_stats,
        )
    )


def get_regime_current(
    run_id: str, model_name: str | None = None
) -> RegimeCurrentResponse:
    """Return current regime payload."""
    history_payload = get_regime_history(run_id=run_id, model_name=model_name)
    if history_payload.status != "ok" or not history_payload.history:
        return _sanitize_model_response(
            RegimeCurrentResponse(
                run_id=history_payload.run_id,
                model_name=history_payload.model_name,
                status=history_payload.status,
                message=history_payload.message,
            )
        )

    latest = history_payload.history[-1]
    return _sanitize_model_response(
        RegimeCurrentResponse(
            run_id=history_payload.run_id,
            model_name=history_payload.model_name,
            trend_regime=str(latest.get("trend_regime", "sideways")),
            vol_regime=str(latest.get("vol_regime", "mid")),
            liquidity_regime=str(latest.get("liquidity_regime", "mid")),
            vix_level=_safe_float(latest.get("vix_level", 0.0)),
            breadth=_safe_float(latest.get("breadth", 0.0)),
            spx_distance_200ma=_safe_float(latest.get("spx_distance_200ma", 0.0)),
        )
    )


def _alerts_path(run_dir: Path, model_name: ModelName) -> Path:
    return run_dir / f"{ALERTS_FILENAME_PREFIX}_{model_name}.json"


def _upsert_alert_history(
    run_dir: Path, model_name: ModelName, alerts: list[dict[str, Any]]
) -> dict[str, Any]:
    path = _alerts_path(run_dir, model_name)
    payload = load_json(path, default={"alerts": [], "alerts_history": []})
    history = payload.get("alerts_history", [])
    seen = {
        (item.get("rule_id"), item.get("triggered_at"))
        for item in history
        if isinstance(item, dict)
    }
    for alert in alerts:
        key = (alert.get("rule_id"), alert.get("triggered_at"))
        if key not in seen:
            history.append(alert)
            seen.add(key)
    payload["alerts"] = alerts
    payload["alerts_history"] = history[-1000:]
    payload["updated_at"] = datetime.now(UTC).replace(microsecond=0).isoformat()
    save_json(path, payload)
    return payload


def _compute_alerts(run_id: str, model_name: ModelName) -> list[dict[str, Any]]:
    run_dir = get_run_dir(run_id)
    backtest_payload = _load_backtest(run_dir, model_name)
    predictions = _load_predictions(run_dir, model_name)
    close_panel = _load_market_panel(run_dir)

    strategy_returns = _strategy_returns(backtest_payload)
    if strategy_returns.empty:
        return []

    alerts: list[dict[str, Any]] = []
    now_iso = datetime.now(UTC).replace(microsecond=0).isoformat()

    ic = _ic_series(predictions)
    if ic.shape[0] >= 3 and (ic.tail(3) <= 0).all():
        alerts.append(
            {
                "rule_id": "ic_non_positive_3m",
                "severity": "warning",
                "triggered_at": now_iso,
                "message": "IC is non-positive for the latest 3 observations.",
                "value": _safe_float(ic.tail(3).mean()),
            }
        )

    maxdd = _safe_float(backtest_payload.get("metrics", {}).get("max_drawdown", 0.0))
    if maxdd <= -0.15:
        alerts.append(
            {
                "rule_id": "maxdd_over_15pct",
                "severity": "critical",
                "triggered_at": now_iso,
                "message": "Max drawdown exceeded 15%.",
                "value": maxdd,
            }
        )

    turnover_series, _ = _turnover_and_exposure_series(backtest_payload)
    if turnover_series.shape[0] >= 6:
        latest = _safe_float(turnover_series.iloc[-1])
        mean_12 = _safe_float(turnover_series.mean())
        std_12 = _safe_float(turnover_series.std(ddof=0))
        recent_3 = _safe_float(turnover_series.tail(3).mean())
        if latest > (mean_12 + 2 * std_12) or latest > (1.5 * recent_3):
            alerts.append(
                {
                    "rule_id": "turnover_spike",
                    "severity": "warning",
                    "triggered_at": now_iso,
                    "message": "Turnover spiked above historical threshold.",
                    "value": latest,
                }
            )

    if not close_panel.empty:
        returns = _returns_panel(close_panel)
        benchmark = (
            returns["SPY"] if "SPY" in returns.columns else pd.Series(dtype=float)
        )
        benchmark = benchmark.reindex(strategy_returns.index).fillna(0.0)
        beta_series = _rolling_beta(strategy_returns, benchmark, window=126)
        if beta_series.shape[0] >= 22:
            latest_beta = _safe_float(beta_series.iloc[-1])
            prev_beta = _safe_float(beta_series.iloc[-22])
            if latest_beta > 1.2 and (latest_beta - prev_beta) > 0.3:
                alerts.append(
                    {
                        "rule_id": "beta_spike",
                        "severity": "warning",
                        "triggered_at": now_iso,
                        "message": "SPY beta spiked above threshold.",
                        "value": latest_beta,
                    }
                )

    return alerts


def refresh_alerts_for_run(
    run_id: str, model_name: str | None = None
) -> AlertsResponse:
    """Compute and persist current alerts."""
    if not _has_run_dir(run_id):
        raise ValueError(f"Run not found: {run_id}")
    normalized_model = _normalize_model_name(model_name)
    run_dir = get_run_dir(run_id)
    alerts = _compute_alerts(run_id, normalized_model)
    payload = _upsert_alert_history(run_dir, normalized_model, alerts)
    return _sanitize_model_response(
        AlertsResponse(
            run_id=run_id,
            model_name=normalized_model,
            alerts=[AlertItem(**item) for item in payload.get("alerts", [])],
        )
    )


def get_alerts_current(run_id: str, model_name: str | None = None) -> AlertsResponse:
    """Return current alerts and refresh rules."""
    return refresh_alerts_for_run(run_id=run_id, model_name=model_name)


def get_alerts_history(
    run_id: str, model_name: str | None = None, limit: int = 200
) -> AlertsResponse:
    """Return stored alerts history."""
    if not _has_run_dir(run_id):
        raise ValueError(f"Run not found: {run_id}")
    normalized_model = _normalize_model_name(model_name)
    run_dir = get_run_dir(run_id)
    payload = load_json(
        _alerts_path(run_dir, normalized_model), default={"alerts_history": []}
    )
    rows = payload.get("alerts_history", [])
    if not isinstance(rows, list):
        rows = []
    clipped = rows[-max(1, int(limit)) :]
    return _sanitize_model_response(
        AlertsResponse(
            run_id=run_id,
            model_name=normalized_model,
            alerts=[AlertItem(**item) for item in clipped if isinstance(item, dict)],
        )
    )


def get_model_shap(run_id: str, model_name: str | None = None) -> ModelShapResponse:
    """Return explainability payload with surrogate fallback when SHAP is unavailable."""
    if not _has_run_dir(run_id):
        raise ValueError(f"Run not found: {run_id}")
    normalized_model = _normalize_model_name(model_name)
    run_dir = get_run_dir(run_id)
    metrics_payload = _load_metrics(run_dir, normalized_model)

    feature_rows = metrics_payload.get("feature_importance", [])
    if not isinstance(feature_rows, list):
        feature_rows = []

    normalized: list[dict[str, float | str]] = []
    for row in feature_rows:
        if not isinstance(row, dict):
            continue
        feature = str(row.get("feature", "")).strip()
        importance = _safe_float(row.get("importance", 0.0))
        if not feature:
            continue
        normalized.append({"feature": feature, "importance": importance})
    normalized.sort(
        key=lambda item: abs(float(item.get("importance", 0.0))), reverse=True
    )

    if not normalized:
        return _sanitize_model_response(
            ModelShapResponse(
                run_id=run_id,
                model_name=normalized_model,
                status="insufficient_data",
                message="Explainability data is unavailable. Train run with feature importance artifacts first.",
            )
        )

    top20 = normalized[:20]
    top3 = normalized[:3]
    run_state = _registry_run_state(run_id)
    updated_at = str(
        run_state.get("updated_at")
        or datetime.now(UTC).replace(microsecond=0).isoformat()
    )
    feature_stability_ts = [
        {
            "date": updated_at[:10],
            "feature": str(item.get("feature", "")),
            "importance": float(item.get("importance", 0.0)),
        }
        for item in top3
    ]

    return _sanitize_model_response(
        ModelShapResponse(
            run_id=run_id,
            model_name=normalized_model,
            status="ok",
            message="Explainability(beta): surrogate importance summary (SHAP optional dependency not required).",
            summary_points=top20,
            dependence_top3=top3,
            feature_stability_ts=feature_stability_ts,
        )
    )
