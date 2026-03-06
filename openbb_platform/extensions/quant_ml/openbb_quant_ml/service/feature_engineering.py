"""Feature engineering for Quant ML training/inference."""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from openbb_quant_ml.models import (
    CloseToNextOpenHorizonPolicy,
    FeatureConfig,
    TargetMode,
)
from openbb_quant_ml.service.cache_registry import (
    compute_params_hash,
    get_feature_version,
    is_cache_stale,
    update_feature_version,
)
from openbb_quant_ml.service.constants import FEATURE_STORE_DIR
from openbb_quant_ml.service.data_loader import build_close_panel
from openbb_quant_ml.service.macro_feature_engineering import load_macro_feature_wide
from openbb_quant_ml.service.storage import save_parquet_atomic

LOGGER = logging.getLogger(__name__)


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    avg_gain = gains.rolling(period).mean()
    avg_loss = losses.rolling(period).mean()
    rs = avg_gain / (avg_loss + 1e-12)
    return 100 - (100 / (1 + rs))


def _macd_hist(series: pd.Series) -> pd.Series:
    ema_fast = series.ewm(span=12, adjust=False).mean()
    ema_slow = series.ewm(span=26, adjust=False).mean()
    macd = ema_fast - ema_slow
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd - signal


def _bollinger_percent_b(
    series: pd.Series, window: int = 20, n_std: float = 2.0
) -> pd.Series:
    ma = series.rolling(window).mean()
    std = series.rolling(window).std(ddof=0)
    upper = ma + n_std * std
    lower = ma - n_std * std
    return (series - lower) / ((upper - lower) + 1e-12)


def _atr(
    high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.rolling(period).mean()


def _adx(
    high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
) -> pd.Series:
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    plus_dm = pd.Series(plus_dm, index=high.index)
    minus_dm = pd.Series(minus_dm, index=high.index)

    atr = _atr(high, low, close, period=period)
    plus_di = 100.0 * (plus_dm.rolling(period).sum() / (atr + 1e-12))
    minus_di = 100.0 * (minus_dm.rolling(period).sum() / (atr + 1e-12))
    dx = 100.0 * (plus_di - minus_di).abs() / ((plus_di + minus_di) + 1e-12)
    return dx.rolling(period).mean()


def _obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    direction = np.sign(close.diff().fillna(0.0))
    return (direction * volume.fillna(0.0)).cumsum()


def _stochastic(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    k_period: int = 14,
    d_period: int = 3,
) -> tuple[pd.Series, pd.Series]:
    lowest_low = low.rolling(k_period).min()
    highest_high = high.rolling(k_period).max()
    k = 100.0 * (close - lowest_low) / ((highest_high - lowest_low) + 1e-12)
    d = k.rolling(d_period).mean()
    return k, d


def _williams_r(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> pd.Series:
    lowest_low = low.rolling(period).min()
    highest_high = high.rolling(period).max()
    return -100.0 * (highest_high - close) / ((highest_high - lowest_low) + 1e-12)


def _cci(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 20,
) -> pd.Series:
    typical_price = (high + low + close) / 3.0
    ma = typical_price.rolling(period).mean()
    mad = (typical_price - ma).abs().rolling(period).mean()
    return (typical_price - ma) / ((0.015 * mad) + 1e-12)


def _vwap_ratio(
    close: pd.Series,
    volume: pd.Series,
    window: int = 20,
) -> pd.Series:
    vol = volume.fillna(0.0)
    vwap = (close * vol).rolling(window).sum() / (vol.rolling(window).sum() + 1e-12)
    return close / (vwap + 1e-12)


def _ichimoku_signal(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
) -> pd.Series:
    tenkan = (high.rolling(9).max() + low.rolling(9).min()) / 2.0
    kijun = (high.rolling(26).max() + low.rolling(26).min()) / 2.0
    span_a = ((tenkan + kijun) / 2.0).shift(26)
    span_b = ((high.rolling(52).max() + low.rolling(52).min()) / 2.0).shift(26)
    cloud_top = np.maximum(span_a, span_b)
    cloud_bottom = np.minimum(span_a, span_b)
    bullish = (close > cloud_top) & (tenkan > kijun)
    bearish = (close < cloud_bottom) & (tenkan < kijun)
    return np.where(bullish, 1.0, np.where(bearish, -1.0, 0.0))


def _safe_symbol(symbol: str) -> str:
    return "".join(
        ch if ch.isalnum() or ch in {"_", "-", "."} else "_" for ch in str(symbol)
    )


def _feature_cache_path(feature_set_id: str, params_hash: str, symbol: str) -> Path:
    return (
        FEATURE_STORE_DIR
        / feature_set_id
        / params_hash
        / f"{_safe_symbol(symbol)}.parquet"
    )


def _feature_overlap_days(feature_config: FeatureConfig, horizon_days: int) -> int:
    lookbacks = [
        max(feature_config.lags or [1]),
        max(feature_config.vol_windows or [5]),
        max(feature_config.momentum_windows or [5]),
        max(feature_config.bollinger_windows or [20]),
        max(feature_config.atr_windows or [14]),
        max(feature_config.adx_windows or [14]),
        int(feature_config.stochastic_k_period),
        int(feature_config.williams_r_period),
        int(feature_config.cci_period),
        int(feature_config.vwap_window),
        60,
        26,
        52,
        14,
    ]
    return max(30, int(max(lookbacks)) + int(max(1, horizon_days)) + 10)


def _compute_target_return(
    frame: pd.DataFrame,
    target_mode: TargetMode,
    horizon_days: int,
    close_to_next_open_horizon_policy: CloseToNextOpenHorizonPolicy = "fixed_1",
) -> pd.Series:
    close = frame["close"].astype(float)
    open_ = frame["open"].astype(float)
    h = max(1, int(horizon_days))

    if target_mode == "close_to_close":
        return close.shift(-h) / (close + 1e-12) - 1.0

    if target_mode == "close_to_next_open":
        open_h = 1 if close_to_next_open_horizon_policy == "fixed_1" else h
        return open_.shift(-open_h) / (close + 1e-12) - 1.0

    # next_open_to_close
    return close.shift(-h) / (open_.shift(-1) + 1e-12) - 1.0


def _attach_residual_momentum(
    merged: pd.DataFrame,
    data_by_symbol: dict[str, pd.DataFrame],
    windows: list[int],
) -> pd.DataFrame:
    """Add residual momentum features: ret - beta*market_ret over rolling windows."""
    close_panel = build_close_panel(data_by_symbol)
    if close_panel.empty or len(close_panel.columns) < 2:
        return merged

    market_ret = close_panel.pct_change(fill_method=None).mean(axis=1)
    market_ret = market_ret.reindex(merged["date"].unique()).fillna(0.0)

    merged = merged.copy()
    merged["_market_ret"] = merged["date"].map(market_ret)

    for window in windows or [20]:
        if window < 5:
            continue
        col = f"residual_momentum_{window}"
        min_periods = max(5, window // 2)
        values_list: list[pd.Series] = []

        for symbol, group in merged.groupby("symbol", sort=False):
            g = group.sort_values("date").reset_index(drop=True)
            ret = g["daily_return"].astype(float)
            mkt = g["_market_ret"].astype(float)
            cov = ret.rolling(window, min_periods=min_periods).cov(mkt)
            var_mkt = mkt.rolling(window, min_periods=min_periods).var()
            beta = np.where(var_mkt > 1e-12, cov / (var_mkt + 1e-12), 0.0)
            beta = np.where(np.isfinite(beta), beta, 0.0)
            residual = ret - beta * mkt
            res_mom = residual.rolling(window, min_periods=min_periods).sum()
            values_list.append(res_mom)

        merged[col] = pd.concat(values_list, axis=0)

    merged = merged.drop(columns=["_market_ret"], errors="ignore")
    return merged


def _build_regime_features(data_by_symbol: dict[str, pd.DataFrame]) -> pd.DataFrame:
    close_panel = build_close_panel(data_by_symbol)
    if close_panel.empty:
        return pd.DataFrame(
            columns=["date", "regime_rate_change_1d", "regime_commodity_change_1d"]
        )

    rate_candidates = ["^TNX", "IEF", "TLT", "BIL"]
    commodity_candidates = ["DBC", "GLD", "USO", "SLV"]

    available = set(close_panel.columns)
    rate_symbol = next((s for s in rate_candidates if s in available), None)
    commodity_symbol = next((s for s in commodity_candidates if s in available), None)

    regime = pd.DataFrame(index=close_panel.index)
    regime["regime_rate_change_1d"] = (
        close_panel[rate_symbol].pct_change()
        if rate_symbol
        else pd.Series(0.0, index=close_panel.index)
    )
    regime["regime_commodity_change_1d"] = (
        close_panel[commodity_symbol].pct_change()
        if commodity_symbol
        else pd.Series(0.0, index=close_panel.index)
    )
    return regime.fillna(0.0).reset_index(names="date")


def _build_single_symbol_features(
    symbol_df: pd.DataFrame,
    feature_config: FeatureConfig,
    horizon_days: int,
    target_mode: TargetMode,
    close_to_next_open_horizon_policy: CloseToNextOpenHorizonPolicy,
) -> pd.DataFrame:
    df = symbol_df.copy().sort_values("date").reset_index(drop=True)
    if "open" not in df.columns:
        df["open"] = df["close"]
    if "high" not in df.columns:
        df["high"] = np.maximum(df["open"], df["close"])
    if "low" not in df.columns:
        df["low"] = np.minimum(df["open"], df["close"])
    if "volume" not in df.columns:
        df["volume"] = 0.0

    close = df["close"].astype(float)
    open_ = df["open"].astype(float)
    high = df["high"].astype(float)
    low = df["low"].astype(float)
    volume = df["volume"].astype(float)
    daily_return = close.pct_change(fill_method=None)

    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(df["date"]).dt.tz_localize(None),
            "symbol": df["symbol"],
            "open": open_,
            "close": close,
            "daily_return": daily_return,
        }
    )

    for lag in feature_config.lags:
        frame[f"ret_lag_{lag}"] = daily_return.shift(lag)

    for window in feature_config.vol_windows:
        frame[f"vol_{window}"] = daily_return.rolling(window).std()

    for window in feature_config.momentum_windows:
        frame[f"mom_{window}"] = close / (close.shift(window) + 1e-12) - 1.0

    frame["trend_ratio_20"] = close / (close.rolling(20).mean() + 1e-12)
    frame["trend_ratio_60"] = close / (close.rolling(60).mean() + 1e-12)

    if feature_config.include_rsi:
        frame["rsi_14"] = _rsi(close, period=14)
    if feature_config.include_macd:
        frame["macd_hist"] = _macd_hist(close)
    if feature_config.include_bollinger:
        for window in feature_config.bollinger_windows or [20]:
            frame[f"bollinger_pb_{int(window)}"] = _bollinger_percent_b(
                close, window=int(window)
            )
    if feature_config.include_atr:
        for window in feature_config.atr_windows or [14]:
            frame[f"atr_{int(window)}"] = _atr(
                high, low, close, period=int(window)
            )
    if feature_config.include_adx:
        for window in feature_config.adx_windows or [14]:
            frame[f"adx_{int(window)}"] = _adx(
                high, low, close, period=int(window)
            )
    if feature_config.include_obv:
        frame["obv"] = _obv(close, volume)
    if feature_config.include_stochastic:
        k, d = _stochastic(
            high,
            low,
            close,
            k_period=int(feature_config.stochastic_k_period),
            d_period=int(feature_config.stochastic_d_period),
        )
        frame[
            f"stoch_k_{int(feature_config.stochastic_k_period)}_{int(feature_config.stochastic_d_period)}"
        ] = k
        frame[
            f"stoch_d_{int(feature_config.stochastic_k_period)}_{int(feature_config.stochastic_d_period)}"
        ] = d
    if feature_config.include_williams_r:
        frame[f"williams_r_{int(feature_config.williams_r_period)}"] = _williams_r(
            high,
            low,
            close,
            period=int(feature_config.williams_r_period),
        )
    if feature_config.include_cci:
        frame[f"cci_{int(feature_config.cci_period)}"] = _cci(
            high,
            low,
            close,
            period=int(feature_config.cci_period),
        )
    if feature_config.include_vwap_ratio:
        frame[f"vwap_ratio_{int(feature_config.vwap_window)}"] = _vwap_ratio(
            close,
            volume,
            window=int(feature_config.vwap_window),
        )
    if feature_config.include_ichimoku_signal:
        frame["ichimoku_signal"] = _ichimoku_signal(high, low, close)

    frame["target_return"] = _compute_target_return(
        frame=frame,
        target_mode=target_mode,
        horizon_days=horizon_days,
        close_to_next_open_horizon_policy=close_to_next_open_horizon_policy,
    )
    return frame


def attach_macro_features(
    panel_df: pd.DataFrame,
    include_macro_features: bool = True,
    subset: list[str] | None = None,
    publication_lag_mode: str = "none",
) -> pd.DataFrame:
    """Attach macro feature panel by backward as-of join on date."""
    if not include_macro_features or panel_df.empty:
        return panel_df

    macro_wide = load_macro_feature_wide(feature_names=subset or [])
    if macro_wide.empty:
        return panel_df

    macro_wide = macro_wide.copy()
    macro_wide["macro_date"] = (
        pd.to_datetime(macro_wide["date"]).dt.tz_localize(None).astype("datetime64[ns]")
    )
    if publication_lag_mode == "one_day":
        macro_wide["macro_date"] = macro_wide["macro_date"] + timedelta(days=1)
    macro_wide = macro_wide.drop(columns=["date"]).sort_values("macro_date")

    left_dates = (
        panel_df[["date"]]
        .drop_duplicates()
        .rename(columns={"date": "sample_date"})
        .assign(
            sample_date=lambda x: pd.to_datetime(x["sample_date"])
            .dt.tz_localize(None)
            .astype("datetime64[ns]")
        )
        .sort_values("sample_date")
    )

    aligned = pd.merge_asof(
        left_dates,
        macro_wide,
        left_on="sample_date",
        right_on="macro_date",
        direction="backward",
    )
    if "macro_date" in aligned.columns:
        invalid = aligned["macro_date"].notna() & (
            aligned["macro_date"] > aligned["sample_date"]
        )
        if bool(invalid.any()):
            raise ValueError("Macro asof join leakage detected.")
    aligned = aligned.rename(columns={"sample_date": "date"}).drop(
        columns=["macro_date"], errors="ignore"
    )
    return panel_df.merge(aligned, on="date", how="left")


def _result_to_frame(result: Any) -> pd.DataFrame:
    if isinstance(result, pd.DataFrame):
        return result
    for method_name in ("to_df", "to_dataframe"):
        method = getattr(result, method_name, None)
        if callable(method):
            candidate = method()
            if isinstance(candidate, pd.DataFrame):
                return candidate
    return pd.DataFrame()


def _normalize_fundamental_frame(frame: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()
    normalized = frame.copy()
    normalized.columns = [str(col).lower() for col in normalized.columns]

    date_col = next(
        (
            col
            for col in (
                "date",
                "as_of_date",
                "reported_date",
                "filing_date",
                "fiscal_date",
                "calendar_date",
                "period_ending",
                "period_end_date",
            )
            if col in normalized.columns
        ),
        None,
    )
    if date_col is None:
        return pd.DataFrame()

    keep_candidates = [
        "pe_ratio",
        "pb_ratio",
        "ps_ratio",
        "ev_to_ebitda",
        "roe",
        "roa",
        "gross_margin",
        "operating_margin",
        "net_margin",
        "debt_to_equity",
        "current_ratio",
        "quick_ratio",
        "free_cash_flow",
        "fcf_yield",
        "eps",
        "eps_diluted",
        "revenue_growth",
        "ebitda_margin",
        "return_on_equity",
    ]
    available_features = [col for col in keep_candidates if col in normalized.columns]
    if not available_features:
        numeric_columns = [
            col
            for col in normalized.columns
            if col != date_col and pd.api.types.is_numeric_dtype(normalized[col])
        ]
        available_features = numeric_columns[:20]
    if not available_features:
        return pd.DataFrame()

    out = normalized[[date_col, *available_features]].copy()
    out = out.rename(columns={date_col: "date"})
    out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.tz_localize(None)
    out = out.dropna(subset=["date"])
    out = out.sort_values("date").drop_duplicates(subset=["date"], keep="last")
    out["symbol"] = symbol
    prefixed = {
        column: f"fund_{column}"
        for column in out.columns
        if column not in {"date", "symbol"}
    }
    return out.rename(columns=prefixed).reset_index(drop=True)


def _fetch_symbol_fundamentals(
    symbol: str,
    provider: str | None = None,
) -> pd.DataFrame:
    provider_norm = str(provider or "").strip().lower() or None
    try:
        from openbb import obb  # type: ignore[import-not-found]
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("OpenBB import failed for fundamentals %s: %s", symbol, exc)
        return pd.DataFrame()

    for endpoint_name in ("metrics", "income"):
        endpoint = getattr(getattr(obb, "equity", object()), "fundamental", None)
        if endpoint is None:
            break
        method = getattr(endpoint, endpoint_name, None)
        if not callable(method):
            continue
        try:
            result = method(symbol=symbol, provider=provider_norm)
        except TypeError:
            try:
                result = method(symbol=symbol)
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning(
                    "Fundamental endpoint %s failed for %s: %s",
                    endpoint_name,
                    symbol,
                    exc,
                )
                continue
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning(
                "Fundamental endpoint %s failed for %s: %s",
                endpoint_name,
                symbol,
                exc,
            )
            continue

        normalized = _normalize_fundamental_frame(_result_to_frame(result), symbol)
        if not normalized.empty:
            return normalized
    return pd.DataFrame()


def attach_fundamental_features(
    panel_df: pd.DataFrame,
    symbols: list[str],
    provider: str | None = None,
    lag_days: int = 60,
) -> pd.DataFrame:
    if panel_df.empty or not symbols:
        return panel_df

    merged = panel_df.copy().sort_values(["symbol", "date"]).reset_index(drop=True)
    all_frames: list[pd.DataFrame] = []
    for symbol in symbols:
        symbol_frame = _fetch_symbol_fundamentals(symbol, provider=provider)
        if symbol_frame.empty:
            continue
        symbol_frame = symbol_frame.copy()
        symbol_frame["date"] = pd.to_datetime(symbol_frame["date"]).dt.tz_localize(None)
        symbol_frame["date"] = symbol_frame["date"] + timedelta(days=max(0, int(lag_days)))
        all_frames.append(symbol_frame)

    if not all_frames:
        return merged

    fundamentals = pd.concat(all_frames, ignore_index=True)
    fundamentals = fundamentals.sort_values(["symbol", "date"]).reset_index(drop=True)
    out_chunks: list[pd.DataFrame] = []
    for symbol, chunk in merged.groupby("symbol", sort=False):
        right = fundamentals[fundamentals["symbol"] == symbol].copy()
        if right.empty:
            out_chunks.append(chunk.copy())
            continue
        left = chunk.sort_values("date").copy()
        right = right.drop(columns=["symbol"], errors="ignore").sort_values("date")
        aligned = pd.merge_asof(
            left,
            right,
            on="date",
            direction="backward",
        )
        out_chunks.append(aligned)
    if not out_chunks:
        return merged
    return pd.concat(out_chunks, ignore_index=True)


def _validate_feature_columns(feature_columns: list[str]) -> None:
    forbidden_prefixes = ("target_", "future_", "label_")
    leaked = [col for col in feature_columns if col.startswith(forbidden_prefixes)]
    if leaked:
        raise ValueError(f"Feature leakage columns detected: {', '.join(leaked[:5])}")


def _build_or_load_symbol_features(
    symbol: str,
    symbol_df: pd.DataFrame,
    feature_config: FeatureConfig,
    horizon_days: int,
    target_mode: TargetMode,
    close_to_next_open_horizon_policy: CloseToNextOpenHorizonPolicy,
    feature_set_id: str,
    params_hash: str,
) -> pd.DataFrame:
    cache_path = _feature_cache_path(feature_set_id, params_hash, symbol)
    symbol_working = symbol_df.copy()
    symbol_working["date"] = pd.to_datetime(symbol_working["date"]).dt.tz_localize(None)
    last_date = pd.Timestamp(symbol_working["date"].max()).date().isoformat()
    version_row = get_feature_version(symbol=symbol, feature_set_id=feature_set_id)
    cached_frame = pd.DataFrame()
    cache_is_valid = (
        cache_path.exists()
        and version_row
        and str(version_row.get("params_hash")) == params_hash
        and not is_cache_stale(feature_set_id=feature_set_id, symbol=symbol)
    )
    if cache_is_valid:
        try:
            cached_frame = pd.read_parquet(cache_path)
            if not cached_frame.empty:
                cached_frame["date"] = pd.to_datetime(
                    cached_frame["date"]
                ).dt.tz_localize(None)
        except Exception as exc:  # noqa: BLE001
            LOGGER.warning(
                "Feature cache load failed for symbol %s (%s): %s",
                symbol,
                cache_path,
                exc,
                exc_info=True,
            )
            cached_frame = pd.DataFrame()

    if (
        cache_is_valid
        and not cached_frame.empty
        and str(version_row.get("last_date")) == last_date
    ):
        return cached_frame

    if cache_is_valid and not cached_frame.empty:
        cached_last = pd.Timestamp(cached_frame["date"].max())
        source_last = pd.Timestamp(symbol_working["date"].max())
        if source_last <= cached_last:
            return cached_frame

        # OBV is cumulative; incremental slices can break continuity.
        # Rebuild full series when OBV is enabled to preserve cumulative state.
        if feature_config.include_obv:
            features = _build_single_symbol_features(
                symbol_df=symbol_working,
                feature_config=feature_config,
                horizon_days=horizon_days,
                target_mode=target_mode,
                close_to_next_open_horizon_policy=close_to_next_open_horizon_policy,
            )
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            save_parquet_atomic(cache_path, features, index=False)
            update_feature_version(
                symbol=symbol,
                feature_set_id=feature_set_id,
                params_hash=params_hash,
                frame=features,
            )
            return features

        overlap_days = _feature_overlap_days(feature_config, horizon_days)
        recalc_start = cached_last - pd.Timedelta(days=overlap_days)
        recalc_source = symbol_working[symbol_working["date"] >= recalc_start].copy()
        if not recalc_source.empty:
            recalculated = _build_single_symbol_features(
                symbol_df=recalc_source,
                feature_config=feature_config,
                horizon_days=horizon_days,
                target_mode=target_mode,
                close_to_next_open_horizon_policy=close_to_next_open_horizon_policy,
            )
            if not recalculated.empty:
                recalculated["date"] = pd.to_datetime(
                    recalculated["date"]
                ).dt.tz_localize(None)
                keep_until = pd.Timestamp(recalculated["date"].min())
                preserved = cached_frame[cached_frame["date"] < keep_until].copy()
                merged = pd.concat([preserved, recalculated], ignore_index=True)
                merged = merged.sort_values(["date", "symbol"]).drop_duplicates(
                    subset=["date", "symbol"], keep="last"
                )
                save_parquet_atomic(cache_path, merged, index=False)
                update_feature_version(
                    symbol=symbol,
                    feature_set_id=feature_set_id,
                    params_hash=params_hash,
                    frame=merged,
                )
                return merged

    features = _build_single_symbol_features(
        symbol_df=symbol_working,
        feature_config=feature_config,
        horizon_days=horizon_days,
        target_mode=target_mode,
        close_to_next_open_horizon_policy=close_to_next_open_horizon_policy,
    )
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    save_parquet_atomic(cache_path, features, index=False)
    update_feature_version(
        symbol=symbol,
        feature_set_id=feature_set_id,
        params_hash=params_hash,
        frame=features,
    )
    return features


def build_feature_dataset(
    data_by_symbol: dict[str, pd.DataFrame],
    feature_config: FeatureConfig,
    horizon_days: int,
    target_mode: TargetMode = "next_open_to_close",
    close_to_next_open_horizon_policy: CloseToNextOpenHorizonPolicy = "fixed_1",
    include_macro_features: bool = True,
    macro_feature_subset: list[str] | None = None,
    include_fundamentals: bool = False,
    fundamental_provider: str | None = None,
    include_sentiment: bool = False,
    fundamentals_lag_days: int = 60,
    feature_set_id: str = "default",
    max_workers: int | None = None,
) -> tuple[pd.DataFrame, list[str], list[str]]:
    """Create panel feature dataset from symbol-wise OHLCV series."""
    if not data_by_symbol:
        return pd.DataFrame(), [], []

    params_hash = compute_params_hash(
        {
            "feature_config": feature_config.model_dump(mode="json"),
            "horizon_days": int(horizon_days),
            "target_mode": target_mode,
            "close_to_next_open_horizon_policy": close_to_next_open_horizon_policy,
        }
    )

    all_frames: list[pd.DataFrame] = []
    skipped_symbols: list[str] = []
    workers = max(1, int(max_workers or min(8, len(data_by_symbol))))

    with ThreadPoolExecutor(
        max_workers=workers, thread_name_prefix="feature-build"
    ) as executor:
        futures = {
            executor.submit(
                _build_or_load_symbol_features,
                symbol,
                symbol_df,
                feature_config,
                horizon_days,
                target_mode,
                close_to_next_open_horizon_policy,
                feature_set_id,
                params_hash,
            ): symbol
            for symbol, symbol_df in data_by_symbol.items()
        }
        for future in as_completed(futures):
            symbol = futures[future]
            try:
                features = future.result()
            except Exception as exc:
                LOGGER.warning(
                    "Feature build failed for symbol %s: %s",
                    symbol,
                    exc,
                    exc_info=True,
                )
                skipped_symbols.append(symbol)
                continue
            if features.empty:
                skipped_symbols.append(symbol)
                continue
            all_frames.append(features)

    if not all_frames:
        return pd.DataFrame(), [], sorted(list(data_by_symbol.keys()))

    merged = pd.concat(all_frames, ignore_index=True)
    merged["date"] = pd.to_datetime(merged["date"]).dt.tz_localize(None)

    if feature_config.include_regime_features:
        regime = _build_regime_features(data_by_symbol)
        merged = merged.merge(regime, on="date", how="left")

    if feature_config.include_residual_momentum:
        merged = _attach_residual_momentum(
            merged, data_by_symbol, feature_config.residual_momentum_windows
        )

    merged = attach_macro_features(
        panel_df=merged,
        include_macro_features=include_macro_features,
        subset=macro_feature_subset,
        publication_lag_mode="none",
    )
    if include_fundamentals or bool(getattr(feature_config, "include_fundamentals", False)):
        merged = attach_fundamental_features(
            panel_df=merged,
            symbols=sorted(data_by_symbol.keys()),
            provider=fundamental_provider,
            lag_days=fundamentals_lag_days,
        )
    if include_sentiment:
        LOGGER.warning(
            "Sentiment feature toggle is enabled but sentiment backend is not configured. Skipping sentiment features."
        )

    merged = merged.sort_values(["date", "symbol"]).reset_index(drop=True)
    merged = merged.replace([np.inf, -np.inf], np.nan)

    ignore_columns = {
        "date",
        "symbol",
        "target_return",
        "close",
        "open",
        "daily_return",
    }
    feature_columns = [col for col in merged.columns if col not in ignore_columns]
    _validate_feature_columns(feature_columns)

    merged[feature_columns] = merged[feature_columns].fillna(0.0)
    return merged, feature_columns, sorted(set(skipped_symbols))
