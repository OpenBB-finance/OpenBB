"""Custom algorithm interfaces and safe adapter."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any

import numpy as np
import pandas as pd

VALID_ALGORITHM_STATUSES = {
    "draft",
    "dev",
    "sandbox",
    "validated",
    "active",
    "paused",
    "deprecated",
}


class BaseCustomAlgorithm(ABC):
    """Contract for user-supplied trading algorithms."""

    name: str = "custom_algorithm"
    version: str = "0.1.0"
    description: str = ""
    required_columns: tuple[str, ...] = ("date", "open", "high", "low", "close", "volume")
    parameters: dict[str, Any] = {}
    warmup_period: int = 60

    def generate_features(self, data: pd.DataFrame) -> pd.DataFrame:
        return data

    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> pd.DataFrame | list[dict[str, Any]] | dict[str, Any] | None:
        """Return one or more signal rows."""

    def validate_output(self, output: pd.DataFrame) -> bool:
        return not output.empty

    def explain_signal(self, output_row: dict[str, Any]) -> str:
        return str(output_row.get("reason", "") or self.description or self.name)


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def normalize_algorithm_output(
    *,
    algorithm: BaseCustomAlgorithm,
    output: pd.DataFrame | list[dict[str, Any]] | dict[str, Any] | None,
    symbol: str | None = None,
) -> pd.DataFrame:
    """Convert custom algorithm output into the canonical signal schema."""
    if output is None:
        return pd.DataFrame()
    if isinstance(output, dict):
        frame = pd.DataFrame([output])
    elif isinstance(output, list):
        frame = pd.DataFrame(output)
    elif isinstance(output, pd.DataFrame):
        frame = output.copy()
    else:
        return pd.DataFrame()
    if frame.empty:
        return pd.DataFrame()
    if "timestamp" not in frame.columns and "date" in frame.columns:
        frame["timestamp"] = pd.to_datetime(frame["date"]).dt.tz_localize(None).astype(str)
    if "timestamp" not in frame.columns:
        frame["timestamp"] = _now_iso()
    if "ticker" not in frame.columns and symbol:
        frame["ticker"] = symbol
    if "signal" not in frame.columns:
        frame["signal"] = frame.get("signal_type", "entry")
    if "signal_type" not in frame.columns:
        frame["signal_type"] = frame["signal"]
    if "side" not in frame.columns:
        frame["side"] = np.where(frame["signal_type"].astype(str).str.lower().eq("exit"), "sell", "buy")
    if "strength" not in frame.columns:
        frame["strength"] = 0.5
    if "confidence" not in frame.columns:
        frame["confidence"] = 0.5
    if "strategy_name" not in frame.columns:
        frame["strategy_name"] = algorithm.name
    if "algorithm_version" not in frame.columns:
        frame["algorithm_version"] = algorithm.version
    if "reason" not in frame.columns:
        frame["reason"] = algorithm.description or algorithm.name
    if "metadata" not in frame.columns:
        frame["metadata"] = [{} for _ in range(len(frame))]
    if "entry_price_hint" not in frame.columns:
        frame["entry_price_hint"] = frame.get("close", np.nan)
    if "stop_loss_hint" not in frame.columns:
        frame["stop_loss_hint"] = np.nan
    if "take_profit_hint" not in frame.columns:
        frame["take_profit_hint"] = np.nan
    keep_cols = [
        "timestamp",
        "ticker",
        "signal",
        "signal_type",
        "side",
        "strength",
        "confidence",
        "strategy_name",
        "algorithm_version",
        "entry_price_hint",
        "stop_loss_hint",
        "take_profit_hint",
        "reason",
        "metadata",
    ]
    for column in keep_cols:
        if column not in frame.columns:
            frame[column] = np.nan
    return frame[keep_cols].copy()


class CustomAlgorithmAdapter:
    """Safely execute custom algorithms and normalize output."""

    def __init__(self, algorithm: BaseCustomAlgorithm):
        self.algorithm = algorithm

    def validate_data(self, data: pd.DataFrame) -> list[str]:
        issues: list[str] = []
        for column in self.algorithm.required_columns:
            if column not in data.columns:
                issues.append(f"missing_required_column:{column}")
        if data.empty:
            issues.append("empty_input")
        return issues

    def execute(self, data: pd.DataFrame, *, symbol: str | None = None) -> tuple[pd.DataFrame, list[str], str | None]:
        issues = self.validate_data(data)
        if issues:
            return pd.DataFrame(), issues, "validation_failed"
        try:
            features = self.algorithm.generate_features(data.copy())
            output = self.algorithm.generate_signal(features.copy())
            normalized = normalize_algorithm_output(
                algorithm=self.algorithm,
                output=output,
                symbol=symbol,
            )
        except Exception as exc:  # noqa: BLE001
            return pd.DataFrame(), ["execution_error"], str(exc)
        if normalized.empty:
            return normalized, issues, None
        if normalized.replace([np.inf, -np.inf], np.nan).isna().all(axis=None):
            issues.append("all_nan_output")
        if not self.algorithm.validate_output(normalized):
            issues.append("validate_output_failed")
        return normalized, issues, None
