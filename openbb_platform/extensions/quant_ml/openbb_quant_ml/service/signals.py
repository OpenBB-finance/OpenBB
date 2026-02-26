"""Signal generation helpers."""

from __future__ import annotations

from datetime import date
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import norm

EPS = 1e-12
SECTOR_COLUMNS = ("sector", "sector_l1", "gics_sector", "industry")
SIZE_COLUMNS = ("log_mktcap", "market_cap", "mkt_cap", "market_cap_usd", "size")
BETA_COLUMNS = ("beta", "beta_spy", "beta_market")
PRICE_COLUMNS = ("close", "price", "last_price")


def _winsorize(series: pd.Series, pct: float) -> pd.Series:
    pct = float(np.clip(pct, 0.0, 0.49))
    if pct <= 0:
        return series
    lower = float(series.quantile(pct))
    upper = float(series.quantile(1.0 - pct))
    return series.clip(lower=lower, upper=upper)


def _standard_zscore(series: pd.Series) -> pd.Series:
    mean = float(series.mean())
    std = float(series.std(ddof=0))
    if not np.isfinite(std) or std <= EPS:
        std = 1.0
    return (series - mean) / (std + EPS)


def _robust_zscore(series: pd.Series) -> pd.Series:
    median = float(series.median())
    mad = float((series - median).abs().median())
    scale = 1.4826 * mad
    if not np.isfinite(scale) or scale <= EPS:
        return _standard_zscore(series)
    return (series - median) / (scale + EPS)


def _gaussianize_rank(series: pd.Series) -> pd.Series:
    n = len(series)
    if n <= 1:
        return pd.Series(np.zeros(n, dtype=float), index=series.index)
    rank = series.rank(method="average", pct=False)
    u = (rank - 0.5) / float(n)
    u = u.clip(1e-6, 1.0 - 1e-6)
    return pd.Series(norm.ppf(u), index=series.index)


def _build_neutralization_matrix(
    frame: pd.DataFrame,
    *,
    neutralize_sector: bool,
    neutralize_size: bool,
    neutralize_beta: bool,
) -> tuple[pd.DataFrame, list[str]]:
    matrices: list[pd.DataFrame] = []
    used_features: list[str] = []

    if neutralize_sector:
        sector_col = next((col for col in SECTOR_COLUMNS if col in frame.columns), None)
        if sector_col is not None:
            sector = frame[sector_col].astype(str).replace("", "other").fillna("other")
            dummies = pd.get_dummies(sector, prefix="sec", drop_first=True, dtype=float)
            if not dummies.empty:
                matrices.append(dummies)
                used_features.append("sector")

    if neutralize_size:
        size_col = next((col for col in SIZE_COLUMNS if col in frame.columns), None)
        if size_col is not None:
            size_raw = pd.to_numeric(frame[size_col], errors="coerce")
            if size_col == "log_mktcap":
                size = size_raw.replace([np.inf, -np.inf], np.nan)
            else:
                size = np.log1p(size_raw.clip(lower=0.0))
            if size.notna().any():
                matrices.append(size.fillna(size.median()).to_frame("size"))
                used_features.append("size")

    if neutralize_beta:
        beta_col = next((col for col in BETA_COLUMNS if col in frame.columns), None)
        if beta_col is not None:
            beta = pd.to_numeric(frame[beta_col], errors="coerce")
            if beta.notna().any():
                matrices.append(beta.fillna(beta.median()).to_frame("beta"))
                used_features.append("beta")

    if not matrices:
        return pd.DataFrame(index=frame.index), used_features

    design = pd.concat(matrices, axis=1)
    design = design.loc[:, ~design.columns.duplicated()].copy()
    design.insert(0, "intercept", 1.0)
    return design, used_features


def _neutralize_alpha(
    alpha: pd.Series,
    frame: pd.DataFrame,
    *,
    neutralize_sector: bool,
    neutralize_size: bool,
    neutralize_beta: bool,
) -> tuple[pd.Series, list[str]]:
    design, used_features = _build_neutralization_matrix(
        frame,
        neutralize_sector=neutralize_sector,
        neutralize_size=neutralize_size,
        neutralize_beta=neutralize_beta,
    )
    if design.empty:
        return alpha, used_features

    y = pd.to_numeric(alpha, errors="coerce").fillna(0.0).to_numpy(dtype=float)
    x = design.to_numpy(dtype=float)
    try:
        beta_hat, *_ = np.linalg.lstsq(x, y, rcond=None)
        fitted = x @ beta_hat
        residual = y - fitted
    except (np.linalg.LinAlgError, ValueError, FloatingPointError):
        return alpha, used_features
    return pd.Series(residual, index=alpha.index), used_features


def _historical_symbol_vol(
    pred: pd.DataFrame,
    as_of: pd.DataFrame,
    target_date: pd.Timestamp,
    *,
    lookback: int,
    method: str,
) -> pd.Series:
    lookback = max(int(lookback), 5)
    halflife = max(2.0, float(lookback) / 3.0)
    history = pred[pred["date"] < target_date].copy()
    if history.empty:
        return pd.Series(1.0, index=as_of.index, dtype=float)

    out = pd.Series(1.0, index=as_of.index, dtype=float)
    for idx, row in as_of.iterrows():
        symbol = row["symbol"]
        symbol_hist = (
            history[history["symbol"] == symbol]
            .sort_values("date")
            .tail(lookback)["predicted_return"]
        )
        values = pd.to_numeric(symbol_hist, errors="coerce").dropna()
        vol = np.nan
        if len(values) >= 2:
            if method == "ewma":
                vol = float(values.ewm(halflife=halflife, adjust=False).std(bias=False).iloc[-1])
            else:
                vol = float(values.std(ddof=0))
        if not np.isfinite(vol) or vol <= EPS:
            vol = float(abs(as_of.loc[idx, "predicted_return"]))
        if not np.isfinite(vol) or vol <= EPS:
            vol = 1.0
        out.loc[idx] = vol
    return out


def _infer_prev_side(value: Any) -> str:
    if isinstance(value, str):
        normed = value.strip().lower()
        if normed in {"buy", "sell", "hold"}:
            return normed
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "hold"
    if numeric > EPS:
        return "buy"
    if numeric < -EPS:
        return "sell"
    return "hold"


def _apply_liquidity_filter(
    frame: pd.DataFrame,
    *,
    enabled: bool,
    min_adv_usd: float,
    min_price: float,
) -> tuple[pd.Series, pd.Series]:
    reasons = pd.Series([[] for _ in range(len(frame))], index=frame.index, dtype=object)
    if not enabled:
        return pd.Series(True, index=frame.index), reasons

    tradable = pd.Series(True, index=frame.index)
    checks_available = 0

    if "adv20_usd" in frame.columns:
        checks_available += 1
        adv = pd.to_numeric(frame["adv20_usd"], errors="coerce")
        fail_adv = adv.fillna(0.0) < float(min_adv_usd)
        tradable &= ~fail_adv
        for idx in frame.index[fail_adv]:
            reasons.at[idx] = [*reasons.at[idx], "adv_below_min"]

    price_col = next((col for col in PRICE_COLUMNS if col in frame.columns), None)
    if price_col is not None:
        checks_available += 1
        px = pd.to_numeric(frame[price_col], errors="coerce")
        fail_px = px.fillna(0.0) < float(min_price)
        tradable &= ~fail_px
        for idx in frame.index[fail_px]:
            reasons.at[idx] = [*reasons.at[idx], "price_below_min"]

    if "is_tradable" in frame.columns:
        checks_available += 1
        td = frame["is_tradable"].astype(bool)
        fail_td = ~td
        tradable &= td
        for idx in frame.index[fail_td]:
            reasons.at[idx] = [*reasons.at[idx], "not_tradable"]

    if checks_available == 0:
        for idx in frame.index:
            reasons.at[idx] = [*reasons.at[idx], "liquidity_filter_skipped"]
        return pd.Series(True, index=frame.index), reasons

    return tradable, reasons


def _assign_sides_quantile(
    frame: pd.DataFrame,
    *,
    q_long: float,
    q_short: float,
    use_hysteresis: bool,
    entry_q_long: float,
    exit_q_long: float,
    entry_q_short: float,
    exit_q_short: float,
    min_hold_periods: int,
    prev_side: pd.Series,
    prev_hold: pd.Series,
    long_only: bool,
) -> pd.Series:
    alpha = frame["alpha_final"]
    n = len(alpha)
    if n == 0:
        return pd.Series(dtype=object)

    def quantile_top(series: pd.Series, q: float) -> float:
        return float(series.quantile(1.0 - float(np.clip(q, 0.0, 1.0))))

    def quantile_bottom(series: pd.Series, q: float) -> float:
        return float(series.quantile(float(np.clip(q, 0.0, 1.0))))

    long_entry_cut = quantile_top(alpha, q_long if not use_hysteresis else entry_q_long)
    short_entry_cut = quantile_bottom(alpha, q_short if not use_hysteresis else entry_q_short)
    long_exit_cut = quantile_top(alpha, exit_q_long)
    short_exit_cut = quantile_bottom(alpha, exit_q_short)

    out = pd.Series("hold", index=frame.index, dtype=object)
    for idx, value in alpha.items():
        prev = prev_side.get(idx, "hold")
        hold_age = int(prev_hold.get(idx, 0))

        if hold_age < int(min_hold_periods) and prev in {"buy", "sell"}:
            if prev == "sell" and long_only:
                out.at[idx] = "hold"
            else:
                out.at[idx] = prev
            continue

        if use_hysteresis and prev == "buy":
            if value >= long_exit_cut:
                out.at[idx] = "buy"
            elif long_only:
                out.at[idx] = "sell"
            elif value <= short_entry_cut:
                out.at[idx] = "sell"
            else:
                out.at[idx] = "hold"
            continue

        if use_hysteresis and prev == "sell" and not long_only:
            if value <= short_exit_cut:
                out.at[idx] = "sell"
            elif value >= long_entry_cut:
                out.at[idx] = "buy"
            else:
                out.at[idx] = "hold"
            continue

        if value >= long_entry_cut:
            out.at[idx] = "buy"
        elif value <= short_entry_cut:
            out.at[idx] = "hold" if long_only and prev != "buy" else "sell"
        else:
            out.at[idx] = "sell" if long_only and prev == "buy" else "hold"
    return out


def _assign_sides_z_threshold(
    frame: pd.DataFrame,
    *,
    score_threshold: float,
    prev_side: pd.Series,
    prev_hold: pd.Series,
    min_hold_periods: int,
    long_only: bool,
) -> pd.Series:
    threshold = max(float(score_threshold), 0.0)
    out = pd.Series("hold", index=frame.index, dtype=object)
    for idx, z_score in frame["z_score"].items():
        prev = prev_side.get(idx, "hold")
        hold_age = int(prev_hold.get(idx, 0))
        if hold_age < int(min_hold_periods) and prev in {"buy", "sell"}:
            if prev == "sell" and long_only:
                out.at[idx] = "hold"
            else:
                out.at[idx] = prev
            continue
        if z_score >= threshold:
            out.at[idx] = "buy"
        elif z_score <= -threshold:
            out.at[idx] = "hold" if long_only and prev != "buy" else "sell"
        else:
            out.at[idx] = "sell" if long_only and prev == "buy" else "hold"
    return out


def _final_top_k_selection(
    frame: pd.DataFrame,
    *,
    top_k: int,
    balanced_long_short: bool,
) -> pd.DataFrame:
    top_k = max(int(top_k), 1)
    non_hold = frame[frame["side"] != "hold"].copy()
    if non_hold.empty:
        return frame.sort_values("z_score", ascending=False).head(top_k).copy()

    if balanced_long_short and top_k > 1:
        long_count = max(1, top_k // 2)
        short_count = max(1, top_k - long_count)
        longs = non_hold[non_hold["side"] == "buy"].sort_values("z_score", ascending=False).head(long_count)
        shorts = non_hold[non_hold["side"] == "sell"].sort_values("z_score", ascending=True).head(short_count)
        selected = pd.concat([longs, shorts], axis=0)
    else:
        selected = non_hold.sort_values("z_score", ascending=False).head(top_k)

    if len(selected) < top_k:
        remaining = (
            frame.loc[~frame.index.isin(selected.index)]
            .reindex(columns=frame.columns)
            .sort_values("z_score", ascending=False)
            .head(top_k - len(selected))
        )
        selected = pd.concat([selected, remaining], axis=0)
    return selected.sort_values("z_score", ascending=False).head(top_k).copy()


def generate_signals(
    predictions: pd.DataFrame,
    as_of_date: date | None,
    top_k: int,
    score_threshold: float,
    balanced_long_short: bool = False,
    *,
    selection_mode: str = "z_threshold",
    q_long: float = 0.10,
    q_short: float = 0.10,
    use_hysteresis: bool = True,
    entry_q_long: float = 0.10,
    exit_q_long: float = 0.30,
    entry_q_short: float = 0.10,
    exit_q_short: float = 0.30,
    min_hold_periods: int = 1,
    liquidity_filter_enabled: bool = True,
    min_adv_usd: float = 5_000_000.0,
    min_price: float = 2.0,
    winsorize_pct: float = 0.01,
    use_robust_zscore: bool = True,
    use_rank_gaussianization: bool = True,
    neutralize_sector: bool = True,
    neutralize_size: bool = True,
    neutralize_beta: bool = False,
    risk_scale_enabled: bool = True,
    risk_vol_lookback: int = 60,
    risk_vol_method: str = "ewma",
    confidence_sizing_enabled: bool = True,
    confidence_disagreement_scale: float = 1.0,
    prev_positions: dict[str, Any] | None = None,
    prev_holding_periods: dict[str, int] | None = None,
    long_only: bool = False,
) -> tuple[str, pd.DataFrame]:
    """Generate cross-sectional signals from predictions."""
    if predictions.empty:
        raise ValueError("Prediction table is empty.")

    pred = predictions.copy()
    if "predicted_return" not in pred.columns:
        if "score" in pred.columns:
            pred["predicted_return"] = pd.to_numeric(pred["score"], errors="coerce").fillna(0.0)
        else:
            raise ValueError("predicted_return column is missing.")
    if "predicted_xgb" not in pred.columns:
        pred["predicted_xgb"] = pred["predicted_return"]
    if "predicted_lstm" not in pred.columns:
        pred["predicted_lstm"] = pred["predicted_return"]

    pred["date"] = pd.to_datetime(pred["date"]).dt.tz_localize(None)
    pred["predicted_return"] = pd.to_numeric(pred["predicted_return"], errors="coerce").fillna(0.0)
    pred["predicted_xgb"] = pd.to_numeric(pred["predicted_xgb"], errors="coerce").fillna(pred["predicted_return"])
    pred["predicted_lstm"] = pd.to_numeric(pred["predicted_lstm"], errors="coerce").fillna(pred["predicted_return"])

    target_date = pd.Timestamp(as_of_date) if as_of_date else pred["date"].max()
    as_of = pred[pred["date"] == target_date].copy()
    if as_of.empty:
        raise ValueError(f"No prediction rows found for selected date: {target_date.date()}")

    as_of = as_of.dropna(subset=["symbol"]).copy()
    as_of["symbol"] = as_of["symbol"].astype(str)
    as_of["alpha_raw"] = as_of["predicted_return"].astype(float)
    as_of["alpha_post"] = _winsorize(as_of["alpha_raw"], winsorize_pct)
    as_of["alpha_post"] = (
        _robust_zscore(as_of["alpha_post"]) if use_robust_zscore else _standard_zscore(as_of["alpha_post"])
    )
    if use_rank_gaussianization:
        as_of["alpha_post"] = _gaussianize_rank(as_of["alpha_post"])

    alpha_neutral, neutral_features = _neutralize_alpha(
        as_of["alpha_post"],
        as_of,
        neutralize_sector=neutralize_sector,
        neutralize_size=neutralize_size,
        neutralize_beta=neutralize_beta,
    )
    as_of["alpha_neutral"] = alpha_neutral

    if risk_scale_enabled:
        symbol_vol = _historical_symbol_vol(
            pred,
            as_of,
            target_date=target_date,
            lookback=risk_vol_lookback,
            method=str(risk_vol_method).strip().lower(),
        )
        as_of["risk_vol"] = symbol_vol.clip(lower=EPS)
        as_of["alpha_scaled"] = as_of["alpha_neutral"] / (as_of["risk_vol"] + EPS)
    else:
        as_of["risk_vol"] = 1.0
        as_of["alpha_scaled"] = as_of["alpha_neutral"]

    disagreement = (as_of["predicted_xgb"] - as_of["predicted_lstm"]).abs()
    if confidence_sizing_enabled:
        scale = max(float(confidence_disagreement_scale), EPS)
        as_of["confidence"] = 1.0 / (1.0 + disagreement / scale)
    else:
        agreement = np.sign(as_of["predicted_xgb"]) == np.sign(as_of["predicted_lstm"])
        abs_norm = as_of["predicted_return"].abs()
        abs_scale = float(abs_norm.max()) if float(abs_norm.max()) > 0 else 1.0
        as_of["confidence"] = (0.6 * agreement.astype(float) + 0.4 * (abs_norm / abs_scale)).clip(0.0, 1.0)
    as_of["confidence"] = as_of["confidence"].clip(0.0, 1.0)
    as_of["alpha_final"] = as_of["alpha_scaled"] * as_of["confidence"]
    as_of["z_score"] = _standard_zscore(as_of["alpha_final"])

    prev_positions = prev_positions or {}
    prev_holding_periods = prev_holding_periods or {}
    as_of["prev_side"] = as_of["symbol"].map(lambda s: _infer_prev_side(prev_positions.get(str(s), "hold")))
    as_of["prev_hold"] = (
        as_of["symbol"]
        .map(lambda s: int(prev_holding_periods.get(str(s), 0)))
        .fillna(0)
        .astype(int)
    )

    if str(selection_mode).strip().lower() == "quantile":
        as_of["side"] = _assign_sides_quantile(
            as_of,
            q_long=q_long,
            q_short=q_short,
            use_hysteresis=bool(use_hysteresis),
            entry_q_long=entry_q_long,
            exit_q_long=exit_q_long,
            entry_q_short=entry_q_short,
            exit_q_short=exit_q_short,
            min_hold_periods=min_hold_periods,
            prev_side=as_of["prev_side"],
            prev_hold=as_of["prev_hold"],
            long_only=bool(long_only),
        )
    else:
        as_of["side"] = _assign_sides_z_threshold(
            as_of,
            score_threshold=score_threshold,
            prev_side=as_of["prev_side"],
            prev_hold=as_of["prev_hold"],
            min_hold_periods=min_hold_periods,
            long_only=bool(long_only),
        )

    tradable_mask, liq_reasons = _apply_liquidity_filter(
        as_of,
        enabled=bool(liquidity_filter_enabled),
        min_adv_usd=float(min_adv_usd),
        min_price=float(min_price),
    )
    as_of["is_tradable_signal"] = tradable_mask
    as_of["liq_reasons"] = liq_reasons
    as_of.loc[~tradable_mask & (as_of["side"] != "hold"), "side"] = "hold"

    def reason_codes(row: pd.Series) -> list[str]:
        reasons: list[str] = []
        if row["z_score"] >= score_threshold:
            reasons.append("zscore_high")
        elif row["z_score"] <= -score_threshold:
            reasons.append("zscore_low")
        else:
            reasons.append("zscore_neutral")

        if abs(float(row["predicted_xgb"])) > EPS and abs(float(row["predicted_lstm"])) > EPS:
            if np.sign(float(row["predicted_xgb"])) == np.sign(float(row["predicted_lstm"])):
                reasons.append("models_agree")
            else:
                reasons.append("models_diverge")

        if abs(float(row["predicted_return"])) >= 0.002:
            reasons.append("magnitude_strong")

        if bool(row.get("side") == "hold") and str(row.get("prev_side")) in {"buy", "sell"}:
            reasons.append("position_exit_or_hold")

        if bool(row.get("prev_hold", 0) < min_hold_periods) and str(row.get("prev_side")) in {"buy", "sell"}:
            reasons.append("min_hold_lock")

        if neutral_features:
            reasons.append("neutralized_" + "_".join(sorted(set(neutral_features))))
        if bool(risk_scale_enabled):
            reasons.append("risk_scaled")
        if bool(use_rank_gaussianization):
            reasons.append("gaussianized")
        if bool(use_robust_zscore):
            reasons.append("robust_zscore")
        if bool(confidence_sizing_enabled):
            reasons.append("confidence_sized")

        liq_codes = row.get("liq_reasons", [])
        if isinstance(liq_codes, list):
            reasons.extend([str(code) for code in liq_codes if code])

        if not bool(row.get("is_tradable_signal", True)):
            reasons.append("liquidity_filtered")

        return sorted(set(reasons))

    as_of["reason_codes"] = as_of.apply(reason_codes, axis=1)
    filtered = _final_top_k_selection(
        as_of,
        top_k=top_k,
        balanced_long_short=bool(balanced_long_short),
    )

    result = filtered[
        [
            "symbol",
            "side",
            "predicted_return",
            "confidence",
            "reason_codes",
            "z_score",
            "predicted_xgb",
            "predicted_lstm",
        ]
    ].copy()
    return target_date.date().isoformat(), result.reset_index(drop=True)
