"""Learning-to-rank modeling with walk-forward validation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from openbb_quant_ml.models import RankerConfig, WalkForwardConfig


@dataclass
class RankerTrainingOutput:
    """Ranker training artifacts."""

    predictions: pd.DataFrame
    metrics: dict[str, Any]
    feature_importance: list[dict[str, float]]
    model_meta: dict[str, Any]
    best_theta: float
    feature_names: list[str]


def _monthly_index(values: pd.Series) -> pd.Series:
    dt = pd.to_datetime(values).dt.tz_localize(None)
    return dt.dt.to_period("M").astype(str)


def _rank_labels_for_date(frame: pd.DataFrame) -> pd.Series:
    if frame.empty:
        return pd.Series(dtype=int)
    pct = frame["target_return"].rank(method="first", pct=True)
    labels = np.floor(np.clip((pct - 1e-12) * 5, 0.0, 4.999)).astype(int)
    return pd.Series(labels, index=frame.index)


def _build_rank_labels(frame: pd.DataFrame) -> pd.Series:
    return frame.groupby("date", group_keys=False).apply(_rank_labels_for_date)


def _build_splits(
    data: pd.DataFrame,
    config: WalkForwardConfig,
    horizon_months: int,
) -> list[tuple[pd.DataFrame, pd.DataFrame]]:
    month_values = sorted(data["month_id"].unique())
    min_needed = config.train_months + config.embargo_months + config.val_months
    if len(month_values) < min_needed:
        return []

    splits: list[tuple[pd.DataFrame, pd.DataFrame]] = []
    cursor = config.train_months
    while cursor + config.embargo_months + config.val_months <= len(month_values):
        train_months = month_values[cursor - config.train_months : cursor]
        val_start_idx = cursor + config.embargo_months
        val_months = month_values[val_start_idx : val_start_idx + config.val_months]
        if not val_months:
            break

        train_df = data[data["month_id"].isin(train_months)].copy()
        val_df = data[data["month_id"].isin(val_months)].copy()
        if train_df.empty or val_df.empty:
            cursor += max(config.step_months, 1)
            continue

        # Purge labels whose forward horizon overlaps with validation period.
        val_start = pd.Period(val_months[0], freq="M").start_time
        purge_cutoff = val_start - pd.DateOffset(months=horizon_months)
        train_df = train_df[train_df["date"] < purge_cutoff]
        if train_df.empty:
            cursor += max(config.step_months, 1)
            continue

        splits.append((train_df, val_df))
        cursor += max(config.step_months, 1)

    return splits


def _ndcg_at_k(relevance: np.ndarray, score: np.ndarray, k: int) -> float:
    if relevance.size == 0:
        return 0.0
    order = np.argsort(score)[::-1][:k]
    ideal = np.argsort(relevance)[::-1][:k]
    gains = (2 ** relevance[order] - 1) / np.log2(np.arange(order.size) + 2)
    ideal_gains = (2 ** relevance[ideal] - 1) / np.log2(np.arange(ideal.size) + 2)
    denom = float(ideal_gains.sum())
    if denom <= 0:
        return 0.0
    return float(gains.sum() / denom)


def _group_ndcg(frame: pd.DataFrame, k: int) -> float:
    values: list[float] = []
    for _, group in frame.groupby("date"):
        if len(group) < 2:
            continue
        rel = group["label"].to_numpy(dtype=float)
        scr = group["score"].to_numpy(dtype=float)
        values.append(_ndcg_at_k(rel, scr, k))
    return float(np.mean(values)) if values else 0.0


def _group_ic(frame: pd.DataFrame, score_col: str, target_col: str) -> float:
    values: list[float] = []
    for _, group in frame.groupby("date"):
        if len(group) < 3:
            continue
        corr = spearmanr(group[score_col], group[target_col], nan_policy="omit").correlation
        if corr is None or np.isnan(corr):
            continue
        values.append(float(corr))
    return float(np.mean(values)) if values else 0.0


def _fit_ranker_model(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    feature_columns: list[str],
    config: RankerConfig,
):
    params = {
        "objective": config.objective,
        "metric": config.metric,
        "ndcg_eval_at": config.ndcg_eval_at,
        "learning_rate": config.learning_rate,
        "n_estimators": config.n_estimators,
        "num_leaves": config.num_leaves,
        "min_data_in_leaf": config.min_data_in_leaf,
        "subsample": config.subsample,
        "colsample_bytree": config.colsample_bytree,
        "reg_lambda": config.reg_lambda,
        "random_state": config.random_state,
    }

    x_train = train_df[feature_columns].to_numpy(dtype=float)
    y_train = train_df["label"].to_numpy(dtype=float)
    group_train = train_df.groupby("date").size().to_numpy(dtype=int)

    x_val = val_df[feature_columns].to_numpy(dtype=float)
    y_val = val_df["label"].to_numpy(dtype=float)
    group_val = val_df.groupby("date").size().to_numpy(dtype=int)

    try:
        import lightgbm as lgb

        model = lgb.LGBMRanker(**params)
        callbacks = [lgb.early_stopping(config.early_stopping_rounds, verbose=False)]
        model.fit(
            x_train,
            y_train,
            group=group_train,
            eval_set=[(x_val, y_val)],
            eval_group=[group_val],
            eval_at=config.ndcg_eval_at,
            callbacks=callbacks,
        )
        feature_importance = model.feature_importances_.astype(float)
        return model, feature_importance, "lightgbm"
    except Exception:
        # Keep local runs functional even when lightgbm binary is not available.
        from xgboost import XGBRegressor

        model = XGBRegressor(
            n_estimators=max(300, min(3000, config.n_estimators)),
            max_depth=6,
            learning_rate=config.learning_rate,
            subsample=config.subsample,
            colsample_bytree=config.colsample_bytree,
            reg_lambda=config.reg_lambda,
            objective="reg:squarederror",
            random_state=config.random_state,
            n_jobs=1,
        )
        model.fit(x_train, y_train, eval_set=[(x_val, y_val)], verbose=False)
        feature_importance = model.feature_importances_.astype(float)
        return model, feature_importance, "xgb-fallback"


def _map_score_to_mu(
    train_df: pd.DataFrame,
    scored_df: pd.DataFrame,
) -> pd.Series:
    label_means = train_df.groupby("label")["target_return"].mean().to_dict()
    fallback = float(train_df["target_return"].mean()) if not train_df.empty else 0.0

    mapped = pd.Series(index=scored_df.index, dtype=float)
    for _, group in scored_df.groupby("date"):
        if group.empty:
            continue
        pct = group["score"].rank(method="first", pct=True)
        labels = np.floor(np.clip((pct - 1e-12) * 5, 0.0, 4.999)).astype(int)
        mapped.loc[group.index] = labels.map(lambda item: float(label_means.get(int(item), fallback)))
    return mapped.fillna(fallback)


def _validation_sharpe_for_theta(frame: pd.DataFrame, theta: float) -> float:
    period_returns: list[float] = []
    for _, group in frame.groupby("date"):
        score = group["score"]
        std = float(score.std(ddof=0))
        if std <= 0 or np.isnan(std):
            continue
        z = (score - float(score.mean())) / (std + 1e-12)
        chosen = group[z >= theta]
        if chosen.empty:
            continue
        period_returns.append(float(chosen["target_return"].mean()))

    if len(period_returns) < 2:
        return 0.0
    values = np.array(period_returns, dtype=float)
    vol = float(values.std(ddof=0))
    if vol <= 0:
        return 0.0
    return float((values.mean() / vol) * np.sqrt(12))


def train_ranker_models(
    feature_data: pd.DataFrame,
    feature_columns: list[str],
    walk_forward: WalkForwardConfig,
    ranker_config: RankerConfig,
    theta_grid: list[float],
    horizon_months: int = 1,
    progress_callback: Callable[[float, str], None] | None = None,
) -> RankerTrainingOutput:
    """Train ranker model with walk-forward splits and return OOS predictions."""
    def emit_progress(ratio: float, message: str) -> None:
        if progress_callback is None:
            return
        clipped = float(max(0.0, min(1.0, ratio)))
        progress_callback(clipped, message)

    data = feature_data.dropna(subset=["target_return"]).copy()
    if data.empty:
        raise ValueError("No valid target rows for ranker training.")

    data["date"] = pd.to_datetime(data["date"]).dt.tz_localize(None)
    data["month_id"] = _monthly_index(data["date"])
    data["label"] = _build_rank_labels(data).astype(int)
    data = data.sort_values(["date", "symbol"]).reset_index(drop=True)
    emit_progress(0.1, "Prepared ranker labels")

    splits = _build_splits(data, walk_forward, horizon_months)
    if not splits:
        # Fallback to a single last-month validation split.
        months = sorted(data["month_id"].unique())
        if len(months) < 2:
            raise ValueError("Not enough monthly groups for ranker validation.")
        train_df = data[data["month_id"].isin(months[:-1])].copy()
        val_df = data[data["month_id"] == months[-1]].copy()
        splits = [(train_df, val_df)]
    emit_progress(0.2, f"Walk-forward splits ready: {len(splits)}")

    fold_frames: list[pd.DataFrame] = []
    fold_metrics: list[dict[str, float]] = []
    importance_accumulator = np.zeros(len(feature_columns), dtype=float)
    backend_name = "lightgbm"

    for fold_idx, (train_df, val_df) in enumerate(splits, start=1):
        emit_progress(
            0.2 + 0.6 * (float(fold_idx - 1) / max(float(len(splits)), 1.0)),
            f"Ranker fold {fold_idx}/{len(splits)}",
        )
        model, feature_importance, backend_name = _fit_ranker_model(
            train_df=train_df,
            val_df=val_df,
            feature_columns=feature_columns,
            config=ranker_config,
        )
        importance_accumulator += feature_importance

        train_scored = train_df.copy()
        train_scored["score"] = model.predict(train_scored[feature_columns].to_numpy(dtype=float)).astype(float)

        scored = val_df.copy()
        scored["score"] = model.predict(scored[feature_columns].to_numpy(dtype=float)).astype(float)
        scored["predicted_return"] = _map_score_to_mu(train_df, scored).astype(float)
        scored["predicted_xgb"] = scored["score"]
        scored["predicted_lstm"] = scored["score"]
        fold_frames.append(scored)

        fold_metrics.append(
            {
                "fold": float(fold_idx),
                "train_ic": _group_ic(train_scored, "score", "target_return"),
                "val_ic": _group_ic(scored, "score", "target_return"),
                "ndcg_5": _group_ndcg(scored, 5),
                "ndcg_10": _group_ndcg(scored, 10),
                "ndcg_20": _group_ndcg(scored, 20),
            }
        )
        emit_progress(
            0.2 + 0.6 * (float(fold_idx) / max(float(len(splits)), 1.0)),
            f"Finished ranker fold {fold_idx}/{len(splits)}",
        )

    emit_progress(0.9, "Aggregating ranker outputs")
    combined = pd.concat(fold_frames, ignore_index=True)
    combined = combined.sort_values(["date", "symbol"]).reset_index(drop=True)
    combined = combined[
        [
            "date",
            "symbol",
            "close",
            "daily_return",
            "target_return",
            "predicted_return",
            "predicted_xgb",
            "predicted_lstm",
            "score",
            "label",
        ]
    ]

    theta_candidates = theta_grid or [0.8, 1.0, 1.2, 1.5]
    theta_scores = {
        str(theta): _validation_sharpe_for_theta(combined, float(theta))
        for theta in theta_candidates
    }
    best_theta = float(max(theta_candidates, key=lambda item: theta_scores.get(str(item), -1e9)))

    train_ic = float(np.mean([item["train_ic"] for item in fold_metrics])) if fold_metrics else 0.0
    val_ic = float(np.mean([item["val_ic"] for item in fold_metrics])) if fold_metrics else 0.0
    ndcg_5 = float(np.mean([item["ndcg_5"] for item in fold_metrics])) if fold_metrics else 0.0
    ndcg_10 = float(np.mean([item["ndcg_10"] for item in fold_metrics])) if fold_metrics else 0.0
    ndcg_20 = float(np.mean([item["ndcg_20"] for item in fold_metrics])) if fold_metrics else 0.0
    hit_rate = float(
        (
            np.sign(combined["predicted_return"].to_numpy(dtype=float))
            == np.sign(combined["target_return"].to_numpy(dtype=float))
        ).mean()
    )

    avg_importance = importance_accumulator / max(len(splits), 1)
    feature_importance = [
        {"feature": feature_name, "importance": float(importance)}
        for feature_name, importance in sorted(
            zip(feature_columns, avg_importance, strict=False),
            key=lambda pair: pair[1],
            reverse=True,
        )[:20]
    ]

    metrics: dict[str, Any] = {
        "train_ic": train_ic,
        "val_ic": float(val_ic),
        "ndcg": {
            "ndcg_5": ndcg_5,
            "ndcg_10": ndcg_10,
            "ndcg_20": ndcg_20,
        },
        "best_theta": best_theta,
        "theta_validation_sharpe": theta_scores,
        "hit_rate": hit_rate,
        "fold_count": len(splits),
        "model_backend": backend_name,
    }

    model_meta: dict[str, Any] = {
        "model": "LGBMRanker",
        "backend": backend_name,
        "feature_count": len(feature_columns),
        "walk_forward": walk_forward.model_dump(mode="json"),
        "ranker_config": ranker_config.model_dump(mode="json"),
    }

    emit_progress(1.0, "Ranker training finished")
    return RankerTrainingOutput(
        predictions=combined,
        metrics=metrics,
        feature_importance=feature_importance,
        model_meta=model_meta,
        best_theta=best_theta,
        feature_names=feature_columns,
    )
