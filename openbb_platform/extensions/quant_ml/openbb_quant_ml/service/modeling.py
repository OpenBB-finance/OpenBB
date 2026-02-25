"""Hybrid XGBoost + PyTorch LSTM training and inference."""

from __future__ import annotations

import copy
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from openbb_quant_ml.models import ModelConfig


class _LSTMRegressor:  # pragma: no cover - wrapper for deferred torch import
    """LSTM regressor with deferred torch import."""

    def __init__(self, input_size: int, hidden_size: int, num_layers: int, dropout: float):
        from torch import nn

        self.model = nn.Sequential()  # placeholder for type checker
        self._nn = nn
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.dropout = dropout
        self.model = self._build()

    def _build(self):
        nn = self._nn

        class LSTMNet(nn.Module):
            def __init__(self, input_size: int, hidden_size: int, num_layers: int, dropout: float):
                super().__init__()
                self.lstm = nn.LSTM(
                    input_size=input_size,
                    hidden_size=hidden_size,
                    num_layers=num_layers,
                    dropout=dropout if num_layers > 1 else 0.0,
                    batch_first=True,
                )
                self.fc = nn.Linear(hidden_size, 1)

            def forward(self, x):  # noqa: ANN001
                output, _ = self.lstm(x)
                last_hidden = output[:, -1, :]
                return self.fc(last_hidden).squeeze(-1)

        return LSTMNet(
            input_size=self.input_size,
            hidden_size=self.hidden_size,
            num_layers=self.num_layers,
            dropout=self.dropout,
        )


@dataclass
class LSTMBundle:
    """Serialized LSTM model bundle."""

    state_dict: dict[str, Any]
    scaler_mean: list[float]
    scaler_scale: list[float]
    feature_columns: list[str]
    seq_len: int
    hidden_size: int
    num_layers: int
    dropout: float
    validation_mse: float


@dataclass
class TrainingOutput:
    """Combined training output for downstream services."""

    predictions: pd.DataFrame
    metrics: dict[str, Any]
    feature_importance: list[dict[str, float]]
    model_meta: dict[str, Any]
    xgb_model: XGBRegressor
    lstm_bundle: LSTMBundle | None


def _split_train_validation(data: pd.DataFrame, train_val_split: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    unique_dates = sorted(data["date"].unique())
    if not unique_dates:
        return pd.DataFrame(), pd.DataFrame()
    cut_idx = max(1, min(len(unique_dates) - 1, int(len(unique_dates) * train_val_split)))
    cut_date = unique_dates[cut_idx - 1]
    train_df = data[data["date"] <= cut_date].copy()
    val_df = data[data["date"] > cut_date].copy()
    return train_df, val_df


def _fit_xgb(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    feature_columns: list[str],
    config: ModelConfig,
) -> tuple[XGBRegressor, float]:
    xgb_model = XGBRegressor(
        n_estimators=config.xgb_n_estimators,
        max_depth=config.xgb_max_depth,
        learning_rate=config.xgb_learning_rate,
        subsample=config.xgb_subsample,
        colsample_bytree=config.xgb_colsample_bytree,
        objective="reg:squarederror",
        random_state=42,
        n_jobs=1,
    )
    xgb_model.fit(
        train_df[feature_columns].values,
        train_df["target_return"].values,
        eval_set=[(val_df[feature_columns].values, val_df["target_return"].values)] if not val_df.empty else None,
        verbose=False,
    )
    if val_df.empty:
        return xgb_model, float("nan")
    val_pred = xgb_model.predict(val_df[feature_columns].values)
    val_mse = float(mean_squared_error(val_df["target_return"].values, val_pred))
    return xgb_model, val_mse


def _validation_ic(val_df: pd.DataFrame, y_pred: np.ndarray) -> float:
    if val_df.empty:
        return 0.0
    scored = val_df[["date", "target_return"]].copy()
    scored["pred"] = y_pred
    values: list[float] = []
    for _, group in scored.groupby("date"):
        if len(group) < 3:
            continue
        if (
            group["pred"].nunique(dropna=True) < 2
            or group["target_return"].nunique(dropna=True) < 2
        ):
            continue
        corr = spearmanr(group["pred"], group["target_return"], nan_policy="omit").correlation
        if corr is None or np.isnan(corr):
            continue
        values.append(float(corr))
    return float(np.mean(values)) if values else 0.0


def tune_xgb_hyperparameters(
    feature_data: pd.DataFrame,
    feature_columns: list[str],
    config: ModelConfig,
    *,
    n_trials: int = 25,
    timeout_sec: int = 1800,
    random_state: int = 42,
    objective_metric: str = "validation_mse",
) -> tuple[ModelConfig, dict[str, Any]]:
    """Tune XGBoost hyperparameters with Optuna on a fixed train/validation split."""
    model_input = feature_data.dropna(subset=["target_return"]).copy()
    if model_input.empty:
        return config, {
            "status": "skipped",
            "reason": "empty_target_rows",
            "objective_metric": objective_metric,
        }

    train_df, val_df = _split_train_validation(model_input, config.train_val_split)
    if train_df.empty or val_df.empty:
        return config, {
            "status": "skipped",
            "reason": "insufficient_validation_rows",
            "objective_metric": objective_metric,
        }

    try:
        import optuna
    except Exception as exc:  # noqa: BLE001
        return config, {
            "status": "skipped",
            "reason": f"optuna_unavailable:{exc}",
            "objective_metric": objective_metric,
        }

    metric = str(objective_metric or "validation_mse").strip().lower()
    maximize_metric = metric == "val_ic"
    direction = "maximize" if maximize_metric else "minimize"
    sampler = optuna.samplers.TPESampler(seed=int(random_state))

    def objective(trial) -> float:  # noqa: ANN001
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 2000),
            "max_depth": trial.suggest_int("max_depth", 2, 10),
            "learning_rate": trial.suggest_float("learning_rate", 1e-4, 0.3, log=True),
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        }
        model = XGBRegressor(
            **params,
            objective="reg:squarederror",
            random_state=int(random_state),
            n_jobs=1,
        )
        model.fit(
            train_df[feature_columns].values,
            train_df["target_return"].values,
            eval_set=[(val_df[feature_columns].values, val_df["target_return"].values)],
            verbose=False,
        )
        pred = model.predict(val_df[feature_columns].values)
        if maximize_metric:
            return float(_validation_ic(val_df, pred))
        return float(mean_squared_error(val_df["target_return"].values, pred))

    try:
        study = optuna.create_study(direction=direction, sampler=sampler)
        study.optimize(objective, n_trials=int(n_trials), timeout=int(timeout_sec))
    except Exception as exc:  # noqa: BLE001
        return config, {
            "status": "failed",
            "reason": str(exc),
            "objective_metric": metric,
        }

    best_params = study.best_params or {}
    tuned = copy.deepcopy(config)
    tuned.xgb_n_estimators = int(best_params.get("n_estimators", config.xgb_n_estimators))
    tuned.xgb_max_depth = int(best_params.get("max_depth", config.xgb_max_depth))
    tuned.xgb_learning_rate = float(best_params.get("learning_rate", config.xgb_learning_rate))
    tuned.xgb_subsample = float(best_params.get("subsample", config.xgb_subsample))
    tuned.xgb_colsample_bytree = float(
        best_params.get("colsample_bytree", config.xgb_colsample_bytree)
    )
    return tuned, {
        "status": "ok",
        "objective_metric": metric,
        "direction": direction,
        "n_trials_requested": int(n_trials),
        "n_trials_completed": int(len(study.trials)),
        "best_value": float(study.best_value),
        "best_params": {
            "xgb_n_estimators": tuned.xgb_n_estimators,
            "xgb_max_depth": tuned.xgb_max_depth,
            "xgb_learning_rate": tuned.xgb_learning_rate,
            "xgb_subsample": tuned.xgb_subsample,
            "xgb_colsample_bytree": tuned.xgb_colsample_bytree,
        },
    }


def _build_lstm_sequences(
    data: pd.DataFrame,
    feature_columns: list[str],
    seq_len: int,
) -> tuple[np.ndarray, np.ndarray]:
    x_values: list[np.ndarray] = []
    y_values: list[float] = []
    for _, group in data.groupby("symbol"):
        group = group.sort_values("date").reset_index(drop=True)
        feature_matrix = group[feature_columns].values
        targets = group["target_return"].values
        if len(group) < seq_len:
            continue
        for index in range(seq_len - 1, len(group)):
            target = targets[index]
            if np.isnan(target):
                continue
            window = feature_matrix[index - seq_len + 1 : index + 1]
            x_values.append(window)
            y_values.append(float(target))
    if not x_values:
        return np.empty((0, seq_len, len(feature_columns))), np.empty((0,))
    return np.array(x_values, dtype=np.float32), np.array(y_values, dtype=np.float32)


def _fit_lstm(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    feature_columns: list[str],
    config: ModelConfig,
    epoch_callback: Callable[[int, int], None] | None = None,
) -> LSTMBundle | None:
    if len(train_df) < config.seq_len * 5:
        return None

    import torch
    from torch.utils.data import DataLoader, TensorDataset

    scaler = StandardScaler()
    train_df_scaled = train_df.copy()
    val_df_scaled = val_df.copy()
    train_df_scaled[feature_columns] = scaler.fit_transform(train_df[feature_columns].values)
    if not val_df.empty:
        val_df_scaled[feature_columns] = scaler.transform(val_df[feature_columns].values)

    x_train, y_train = _build_lstm_sequences(train_df_scaled, feature_columns, config.seq_len)
    x_val, y_val = _build_lstm_sequences(val_df_scaled, feature_columns, config.seq_len)
    if len(x_train) == 0:
        return None

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    wrapper = _LSTMRegressor(
        input_size=len(feature_columns),
        hidden_size=config.lstm_hidden_size,
        num_layers=config.lstm_num_layers,
        dropout=config.lstm_dropout,
    )
    model = wrapper.model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=config.lstm_learning_rate)
    criterion = torch.nn.MSELoss()

    dataset = TensorDataset(torch.from_numpy(x_train), torch.from_numpy(y_train))
    loader = DataLoader(dataset, batch_size=config.lstm_batch_size, shuffle=True)

    model.train()
    for epoch in range(config.lstm_epochs):
        for batch_x, batch_y in loader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)
            optimizer.zero_grad()
            pred = model(batch_x)
            loss = criterion(pred, batch_y)
            loss.backward()
            optimizer.step()
        if epoch_callback is not None:
            epoch_callback(epoch + 1, config.lstm_epochs)

    val_mse = float("nan")
    if len(x_val) > 0:
        model.eval()
        with torch.no_grad():
            x_val_t = torch.from_numpy(x_val).to(device)
            y_val_t = torch.from_numpy(y_val).to(device)
            val_pred = model(x_val_t)
            val_mse = float(criterion(val_pred, y_val_t).item())

    return LSTMBundle(
        state_dict=model.state_dict(),
        scaler_mean=scaler.mean_.tolist(),
        scaler_scale=scaler.scale_.tolist(),
        feature_columns=feature_columns,
        seq_len=config.seq_len,
        hidden_size=config.lstm_hidden_size,
        num_layers=config.lstm_num_layers,
        dropout=config.lstm_dropout,
        validation_mse=val_mse,
    )


def _lstm_predict_dataset(
    full_df: pd.DataFrame,
    bundle: LSTMBundle,
) -> pd.DataFrame:
    import torch

    if full_df.empty:
        return pd.DataFrame(columns=["date", "symbol", "predicted_lstm"])

    scaler_mean = np.array(bundle.scaler_mean)
    scaler_scale = np.array(bundle.scaler_scale)

    wrapper = _LSTMRegressor(
        input_size=len(bundle.feature_columns),
        hidden_size=bundle.hidden_size,
        num_layers=bundle.num_layers,
        dropout=bundle.dropout,
    )
    model = wrapper.model
    model.load_state_dict(bundle.state_dict)
    model.eval()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    rows: list[dict[str, Any]] = []
    for symbol, group in full_df.groupby("symbol"):
        group = group.sort_values("date").reset_index(drop=True)
        if len(group) < bundle.seq_len:
            continue
        raw = group[bundle.feature_columns].values.astype(np.float32)
        scaled = (raw - scaler_mean) / (scaler_scale + 1e-12)
        for index in range(bundle.seq_len - 1, len(group)):
            window = scaled[index - bundle.seq_len + 1 : index + 1]
            window_tensor = torch.from_numpy(window[None, :, :]).float().to(device)
            with torch.no_grad():
                pred = model(window_tensor).cpu().numpy().item()
            rows.append(
                {
                    "date": group.loc[index, "date"],
                    "symbol": symbol,
                    "predicted_lstm": float(pred),
                }
            )
    return pd.DataFrame(rows)


def train_hybrid_models(
    feature_data: pd.DataFrame,
    feature_columns: list[str],
    config: ModelConfig,
    progress_callback: Callable[[float, str], None] | None = None,
) -> TrainingOutput:
    """Train XGBoost + LSTM and produce full prediction table."""
    def emit_progress(ratio: float, message: str) -> None:
        if progress_callback is None:
            return
        clipped = float(max(0.0, min(1.0, ratio)))
        progress_callback(clipped, message)

    model_input = feature_data.dropna(subset=["target_return"]).copy()
    if model_input.empty:
        raise ValueError("No target rows are available for training.")

    emit_progress(0.05, "Preparing train/validation split")
    train_df, val_df = _split_train_validation(model_input, config.train_val_split)
    if train_df.empty:
        raise ValueError("Training split is empty; not enough training samples.")

    emit_progress(0.2, "Training XGBoost")
    xgb_model, xgb_val_mse = _fit_xgb(train_df, val_df, feature_columns, config)
    emit_progress(0.42, "Training LSTM")
    lstm_bundle = _fit_lstm(
        train_df,
        val_df,
        feature_columns,
        config,
        epoch_callback=lambda epoch, total: emit_progress(
            0.42 + 0.35 * (float(epoch) / max(float(total), 1.0)),
            f"LSTM epoch {epoch}/{total}",
        ),
    )

    emit_progress(0.8, "Building prediction frame")
    xgb_pred_all = xgb_model.predict(feature_data[feature_columns].values)
    pred_frame = feature_data[["date", "symbol", "close", "daily_return", "target_return"]].copy()
    pred_frame["predicted_xgb"] = xgb_pred_all.astype(float)

    if lstm_bundle:
        lstm_pred = _lstm_predict_dataset(feature_data, lstm_bundle)
        pred_frame = pred_frame.merge(lstm_pred, on=["date", "symbol"], how="left")
    else:
        pred_frame["predicted_lstm"] = np.nan

    xgb_score = 1.0 / (xgb_val_mse + 1e-12) if np.isfinite(xgb_val_mse) else 1.0
    if lstm_bundle and np.isfinite(lstm_bundle.validation_mse):
        lstm_score = 1.0 / (lstm_bundle.validation_mse + 1e-12)
    else:
        lstm_score = 0.0
    total = xgb_score + lstm_score
    xgb_weight = xgb_score / total if total > 0 else 1.0
    lstm_weight = lstm_score / total if total > 0 else 0.0

    pred_frame["predicted_lstm"] = pred_frame["predicted_lstm"].fillna(pred_frame["predicted_xgb"])
    pred_frame["predicted_return"] = (
        pred_frame["predicted_xgb"] * xgb_weight + pred_frame["predicted_lstm"] * lstm_weight
    )

    feature_importance = []
    for name, importance in sorted(
        zip(feature_columns, xgb_model.feature_importances_, strict=False),
        key=lambda item: item[1],
        reverse=True,
    )[:20]:
        feature_importance.append({"feature": str(name), "importance": float(importance)})

    latest_val_error = float(xgb_val_mse) if np.isfinite(xgb_val_mse) else None
    if lstm_bundle and np.isfinite(lstm_bundle.validation_mse):
        lstm_err = float(lstm_bundle.validation_mse)
        latest_val_error = (latest_val_error + lstm_err) / 2 if latest_val_error is not None else lstm_err

    metrics: dict[str, Any] = {
        "validation_mse_xgb": float(xgb_val_mse) if np.isfinite(xgb_val_mse) else None,
        "validation_mse_lstm": (
            float(lstm_bundle.validation_mse)
            if lstm_bundle and np.isfinite(lstm_bundle.validation_mse)
            else None
        ),
        "ensemble_weights": {"xgb": float(xgb_weight), "lstm": float(lstm_weight)},
        "latest_validation_error": latest_val_error,
    }

    model_meta = {
        "models": {
            "xgboost": "XGBRegressor",
            "lstm": "PyTorch LSTM" if lstm_bundle else "disabled",
        },
        "feature_count": len(feature_columns),
        "seq_len": config.seq_len,
        "train_rows": int(len(train_df)),
        "validation_rows": int(len(val_df)),
    }

    emit_progress(1.0, "Hybrid model training finished")
    return TrainingOutput(
        predictions=pred_frame.sort_values(["date", "symbol"]).reset_index(drop=True),
        metrics=metrics,
        feature_importance=feature_importance,
        model_meta=model_meta,
        xgb_model=xgb_model,
        lstm_bundle=lstm_bundle,
    )
