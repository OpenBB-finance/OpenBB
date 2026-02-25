"""Learning-to-rank modeling with walk-forward validation."""

from __future__ import annotations

import copy
import warnings
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
import pandas as pd
from scipy.stats import ConstantInputWarning, spearmanr

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
    inference_model: Any
    inference_backend: str
    label_return_map: dict[int, float]
    label_return_fallback: float


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
    horizon_days: int,
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
        val_start = pd.Timestamp(val_df["date"].min()).tz_localize(None)
        if str(config.purging_mode) == "strict_label_overlap":
            label_end = train_df["date"] + pd.to_timedelta(max(1, int(horizon_days)), unit="D")
            train_df = train_df[label_end < val_start]
        else:
            purge_months = max(1, int(np.ceil(max(1, int(horizon_days)) / 21)))
            purge_cutoff = val_start - pd.DateOffset(months=purge_months)
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


def _group_ic(
    frame: pd.DataFrame,
    score_col: str,
    target_col: str,
    *,
    return_stats: bool = False,
) -> float | tuple[float, dict[str, int]]:
    values: list[float] = []
    skipped_constant = 0
    valid_groups = 0
    for _, group in frame.groupby("date"):
        if len(group) < 3:
            continue
        if (
            group[score_col].nunique(dropna=True) < 2
            or group[target_col].nunique(dropna=True) < 2
        ):
            skipped_constant += 1
            continue
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConstantInputWarning)
            corr = spearmanr(
                group[score_col], group[target_col], nan_policy="omit"
            ).correlation
        if corr is None or np.isnan(corr):
            continue
        valid_groups += 1
        values.append(float(corr))
    ic_value = float(np.mean(values)) if values else 0.0
    if return_stats:
        return ic_value, {
            "ic_skipped_constant_groups": int(skipped_constant),
            "ic_valid_groups": int(valid_groups),
        }
    return ic_value


def _fit_catboost_ranker(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    feature_columns: list[str],
    config: RankerConfig,
):
    """Fit CatBoost ranker; fallback to LightGBM if CatBoost unavailable."""
    x_train = train_df[feature_columns].to_numpy(dtype=float)
    y_train = train_df["label"].to_numpy(dtype=float)
    group_train = train_df.groupby("date").size().to_numpy(dtype=int)
    group_id_train = np.repeat(np.arange(len(group_train)), group_train)

    x_val = val_df[feature_columns].to_numpy(dtype=float)
    y_val = val_df["label"].to_numpy(dtype=float)
    group_val = val_df.groupby("date").size().to_numpy(dtype=int)
    group_id_val = np.repeat(np.arange(len(group_val)), group_val)

    try:
        from catboost import CatBoostRanker, Pool

        model = CatBoostRanker(
            iterations=min(config.n_estimators, 10000),
            learning_rate=config.learning_rate,
            depth=6,
            l2_leaf_reg=config.reg_lambda,
            random_seed=config.random_state,
            verbose=False,
            early_stopping_rounds=config.early_stopping_rounds,
        )
        train_pool = Pool(
            data=x_train,
            label=y_train,
            group_id=group_id_train,
        )
        eval_pool = Pool(
            data=x_val,
            label=y_val,
            group_id=group_id_val,
        )
        model.fit(train_pool, eval_set=eval_pool)
        feature_importance = np.array(model.get_feature_importance(), dtype=float)
        return model, feature_importance, "catboost"
    except Exception:
        return _fit_ranker_model(train_df, val_df, feature_columns, config)


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
        mapped.loc[group.index] = labels.map(
            lambda item: float(label_means.get(int(item), fallback))
        )
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


def _top_k_mean_return(frame: pd.DataFrame, k: int) -> float:
    period_returns: list[float] = []
    for _, group in frame.groupby("date"):
        if group.empty:
            continue
        top = group.sort_values("score", ascending=False).head(max(1, int(k)))
        period_returns.append(float(top["target_return"].mean()))
    return float(np.mean(period_returns)) if period_returns else 0.0


def _decile_spread(frame: pd.DataFrame) -> float:
    spreads: list[float] = []
    for _, group in frame.groupby("date"):
        if len(group) < 10:
            continue
        ranked = group.sort_values("score", ascending=False)
        bucket = max(1, int(np.ceil(len(ranked) * 0.1)))
        top = float(ranked.head(bucket)["target_return"].mean())
        bottom = float(ranked.tail(bucket)["target_return"].mean())
        spreads.append(top - bottom)
    return float(np.mean(spreads)) if spreads else 0.0


def tune_ranker_hyperparameters(
    feature_data: pd.DataFrame,
    feature_columns: list[str],
    walk_forward: WalkForwardConfig,
    ranker_config: RankerConfig,
    *,
    horizon_days: int = 1,
    n_trials: int = 25,
    timeout_sec: int = 1800,
    random_state: int = 42,
    objective_metric: str = "val_ic",
    backend: Literal["lightgbm", "catboost"] = "lightgbm",
) -> tuple[RankerConfig, dict[str, Any]]:
    """Tune ranker hyperparameters with Optuna using walk-forward splits."""
    data = feature_data.dropna(subset=["target_return"]).copy()
    if data.empty:
        return ranker_config, {
            "status": "skipped",
            "reason": "empty_target_rows",
            "objective_metric": objective_metric,
        }

    data["date"] = pd.to_datetime(data["date"]).dt.tz_localize(None)
    data["month_id"] = _monthly_index(data["date"])
    data["label"] = _build_rank_labels(data).astype(int)
    data = data.sort_values(["date", "symbol"]).reset_index(drop=True)
    splits = _build_splits(data, walk_forward, horizon_days)
    if not splits:
        return ranker_config, {
            "status": "skipped",
            "reason": "no_walkforward_splits",
            "objective_metric": objective_metric,
        }
    splits = splits[: min(3, len(splits))]

    try:
        import optuna
    except Exception as exc:  # noqa: BLE001
        return ranker_config, {
            "status": "skipped",
            "reason": f"optuna_unavailable:{exc}",
            "objective_metric": objective_metric,
        }

    sampler = optuna.samplers.TPESampler(seed=int(random_state))

    def objective(trial) -> float:  # noqa: ANN001
        tuned = copy.deepcopy(ranker_config)
        tuned.learning_rate = trial.suggest_float("learning_rate", 1e-4, 0.3, log=True)
        tuned.n_estimators = trial.suggest_int("n_estimators", 300, 8000)
        tuned.num_leaves = trial.suggest_int("num_leaves", 16, 256)
        tuned.min_data_in_leaf = trial.suggest_int("min_data_in_leaf", 50, 1500)
        tuned.subsample = trial.suggest_float("subsample", 0.5, 1.0)
        tuned.colsample_bytree = trial.suggest_float("colsample_bytree", 0.5, 1.0)
        tuned.reg_lambda = trial.suggest_float("reg_lambda", 1e-3, 100.0, log=True)
        tuned.random_state = int(random_state)

        fold_scores: list[float] = []
        for train_df, val_df in splits:
            if backend == "catboost":
                model, _, _ = _fit_catboost_ranker(
                    train_df=train_df,
                    val_df=val_df,
                    feature_columns=feature_columns,
                    config=tuned,
                )
            else:
                model, _, _ = _fit_ranker_model(
                    train_df=train_df,
                    val_df=val_df,
                    feature_columns=feature_columns,
                    config=tuned,
                )
            scored = val_df.copy()
            scored["score"] = model.predict(
                scored[feature_columns].to_numpy(dtype=float)
            ).astype(float)
            fold_scores.append(float(_group_ic(scored, "score", "target_return")))
        return float(np.mean(fold_scores)) if fold_scores else 0.0

    try:
        study = optuna.create_study(direction="maximize", sampler=sampler)
        study.optimize(objective, n_trials=int(n_trials), timeout=int(timeout_sec))
    except Exception as exc:  # noqa: BLE001
        return ranker_config, {
            "status": "failed",
            "reason": str(exc),
            "objective_metric": objective_metric,
        }

    params = study.best_params or {}
    tuned = copy.deepcopy(ranker_config)
    tuned.learning_rate = float(params.get("learning_rate", ranker_config.learning_rate))
    tuned.n_estimators = int(params.get("n_estimators", ranker_config.n_estimators))
    tuned.num_leaves = int(params.get("num_leaves", ranker_config.num_leaves))
    tuned.min_data_in_leaf = int(
        params.get("min_data_in_leaf", ranker_config.min_data_in_leaf)
    )
    tuned.subsample = float(params.get("subsample", ranker_config.subsample))
    tuned.colsample_bytree = float(
        params.get("colsample_bytree", ranker_config.colsample_bytree)
    )
    tuned.reg_lambda = float(params.get("reg_lambda", ranker_config.reg_lambda))
    tuned.random_state = int(random_state)
    return tuned, {
        "status": "ok",
        "objective_metric": str(objective_metric or "val_ic").strip().lower(),
        "direction": "maximize",
        "n_trials_requested": int(n_trials),
        "n_trials_completed": int(len(study.trials)),
        "best_value": float(study.best_value),
        "best_params": {
            "learning_rate": tuned.learning_rate,
            "n_estimators": tuned.n_estimators,
            "num_leaves": tuned.num_leaves,
            "min_data_in_leaf": tuned.min_data_in_leaf,
            "subsample": tuned.subsample,
            "colsample_bytree": tuned.colsample_bytree,
            "reg_lambda": tuned.reg_lambda,
        },
    }


def train_ranker_models(
    feature_data: pd.DataFrame,
    feature_columns: list[str],
    walk_forward: WalkForwardConfig,
    ranker_config: RankerConfig,
    theta_grid: list[float],
    horizon_days: int = 1,
    progress_callback: Callable[[float, str], None] | None = None,
    backend: Literal["lightgbm", "catboost"] = "lightgbm",
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

    splits = _build_splits(data, walk_forward, horizon_days)
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
    ic_skipped_constant_groups = 0
    ic_valid_groups = 0

    for fold_idx, (train_df, val_df) in enumerate(splits, start=1):
        emit_progress(
            0.2 + 0.6 * (float(fold_idx - 1) / max(float(len(splits)), 1.0)),
            f"Ranker fold {fold_idx}/{len(splits)}",
        )
        if backend == "catboost":
            model, feature_importance, backend_name = _fit_catboost_ranker(
                train_df=train_df,
                val_df=val_df,
                feature_columns=feature_columns,
                config=ranker_config,
            )
        else:
            model, feature_importance, backend_name = _fit_ranker_model(
                train_df=train_df,
                val_df=val_df,
                feature_columns=feature_columns,
                config=ranker_config,
            )
        importance_accumulator += feature_importance

        train_scored = train_df.copy()
        train_scored["score"] = model.predict(
            train_scored[feature_columns].to_numpy(dtype=float)
        ).astype(float)

        scored = val_df.copy()
        scored["score"] = model.predict(
            scored[feature_columns].to_numpy(dtype=float)
        ).astype(float)
        scored["predicted_return"] = _map_score_to_mu(train_df, scored).astype(float)
        scored["predicted_xgb"] = scored["score"]
        scored["predicted_lstm"] = scored["score"]
        fold_frames.append(scored)

        train_ic_value, train_ic_stats = _group_ic(
            train_scored,
            "score",
            "target_return",
            return_stats=True,
        )
        val_ic_value, val_ic_stats = _group_ic(
            scored,
            "score",
            "target_return",
            return_stats=True,
        )
        ic_skipped_constant_groups += int(
            train_ic_stats.get("ic_skipped_constant_groups", 0)
        ) + int(val_ic_stats.get("ic_skipped_constant_groups", 0))
        ic_valid_groups += int(train_ic_stats.get("ic_valid_groups", 0)) + int(
            val_ic_stats.get("ic_valid_groups", 0)
        )

        fold_metrics.append(
            {
                "fold": float(fold_idx),
                "train_ic": float(train_ic_value),
                "val_ic": float(val_ic_value),
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
    best_theta = float(
        max(theta_candidates, key=lambda item: theta_scores.get(str(item), -1e9))
    )

    # Fit an inference model on the full sample for daily infer-only refresh jobs.
    emit_progress(0.92, "Fitting final ranker inference model")
    final_train_df = data.copy()
    months = sorted(final_train_df["month_id"].unique())
    if len(months) >= 2:
        final_val_df = final_train_df[final_train_df["month_id"] == months[-1]].copy()
    else:
        final_val_df = final_train_df.tail(min(300, len(final_train_df))).copy()
    if final_val_df.empty:
        final_val_df = final_train_df.tail(min(300, len(final_train_df))).copy()
    if backend == "catboost":
        final_model, _, final_backend = _fit_catboost_ranker(
            train_df=final_train_df,
            val_df=final_val_df,
            feature_columns=feature_columns,
            config=ranker_config,
        )
    else:
        final_model, _, final_backend = _fit_ranker_model(
            train_df=final_train_df,
            val_df=final_val_df,
            feature_columns=feature_columns,
            config=ranker_config,
        )

    label_return_map: dict[int, float] = {}
    grouped = final_train_df.groupby("label")["target_return"].mean()
    for label, value in grouped.items():
        casted = float(value)
        if np.isnan(casted) or np.isinf(casted):
            continue
        label_return_map[int(label)] = casted
    label_return_fallback = (
        float(final_train_df["target_return"].mean())
        if not final_train_df.empty
        else 0.0
    )
    if np.isnan(label_return_fallback) or np.isinf(label_return_fallback):
        label_return_fallback = 0.0

    train_ic = 0.0
    val_ic = 0.0
    if fold_metrics:
        train_ic = float(np.mean([item["train_ic"] for item in fold_metrics]))
        val_ic = float(np.mean([item["val_ic"] for item in fold_metrics]))
    ndcg_5 = (
        float(np.mean([item["ndcg_5"] for item in fold_metrics]))
        if fold_metrics
        else 0.0
    )
    ndcg_10 = (
        float(np.mean([item["ndcg_10"] for item in fold_metrics]))
        if fold_metrics
        else 0.0
    )
    ndcg_20 = (
        float(np.mean([item["ndcg_20"] for item in fold_metrics]))
        if fold_metrics
        else 0.0
    )
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
        "top_k_mean_return": {
            "k5": _top_k_mean_return(combined, 5),
            "k10": _top_k_mean_return(combined, 10),
            "k20": _top_k_mean_return(combined, 20),
        },
        "decile_spread": _decile_spread(combined),
        "fold_count": len(splits),
        "model_backend": final_backend,
        "ic_skipped_constant_groups": int(ic_skipped_constant_groups),
        "ic_valid_groups": int(ic_valid_groups),
    }

    model_meta: dict[str, Any] = {
        "model": "LGBMRanker",
        "backend": final_backend,
        "feature_count": len(feature_columns),
        "walk_forward": walk_forward.model_dump(mode="json"),
        "purging_mode": str(walk_forward.purging_mode),
        "horizon_days": int(horizon_days),
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
        inference_model=final_model,
        inference_backend=final_backend,
        label_return_map=label_return_map,
        label_return_fallback=label_return_fallback,
    )
