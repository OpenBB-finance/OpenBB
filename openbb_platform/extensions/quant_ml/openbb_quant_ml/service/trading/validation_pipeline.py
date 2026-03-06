"""Validation helpers for custom algorithm runtime."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import numpy as np
import pandas as pd

from openbb_quant_ml.service.reporting import write_report
from openbb_quant_ml.service.trading.custom_algorithm_adapter import (
    BaseCustomAlgorithm,
    CustomAlgorithmAdapter,
)
from openbb_quant_ml.service.trading.registry import insert_validation_run
from openbb_quant_ml.service.trading.storage import latest_validation_path, save_runtime_json


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def validate_custom_algorithm(
    *,
    algorithm: BaseCustomAlgorithm,
    data: pd.DataFrame,
    symbol: str | None = None,
) -> dict[str, Any]:
    """Validate one custom algorithm against a sample input frame."""
    adapter = CustomAlgorithmAdapter(algorithm)
    normalized, issues, error = adapter.execute(data, symbol=symbol)
    checks: list[dict[str, Any]] = []
    passed = True

    required_missing = [item for item in issues if item.startswith("missing_required_column:")]
    checks.append({"name": "required_columns", "passed": not required_missing, "value": required_missing})
    passed &= not required_missing

    nan_or_inf = False
    if not normalized.empty:
        numeric = normalized.select_dtypes(include=["number"]).replace([np.inf, -np.inf], np.nan)
        nan_or_inf = bool(numeric.isna().any().any())
    checks.append({"name": "nan_or_inf", "passed": not nan_or_inf, "value": nan_or_inf})
    passed &= not nan_or_inf

    invalid_side = False
    if not normalized.empty and "side" in normalized.columns:
        invalid_side = bool(~normalized["side"].astype(str).isin(["buy", "sell"]).all())
    checks.append({"name": "signal_side", "passed": not invalid_side, "value": invalid_side})
    passed &= not invalid_side

    timestamp_issue = False
    if not normalized.empty and "timestamp" in normalized.columns and "date" in data.columns:
        max_input = pd.to_datetime(data["date"]).max()
        max_output = pd.to_datetime(normalized["timestamp"]).max()
        timestamp_issue = bool(max_output > max_input)
    checks.append({"name": "future_reference", "passed": not timestamp_issue, "value": timestamp_issue})
    passed &= not timestamp_issue

    signal_density = 0.0
    if len(data) > 0:
        signal_density = float(len(normalized)) / float(len(data))
    density_fail = signal_density > 0.5
    checks.append({"name": "signal_density", "passed": not density_fail, "value": signal_density})
    passed &= not density_fail

    execution_error = error is not None
    checks.append({"name": "execution_error", "passed": not execution_error, "value": error})
    passed &= not execution_error

    status = "passed" if passed else "failed"
    summary = {
        "algorithm_name": algorithm.name,
        "algorithm_version": algorithm.version,
        "passed": passed,
        "issue_count": len([item for item in checks if not item["passed"]]),
        "signal_rows": int(len(normalized)),
    }
    report = write_report(
        run_id=None,
        report_type="trading_algorithm_validation",
        title=f"Trading Algorithm Validation: {algorithm.name}",
        metadata={
            "algorithm_name": algorithm.name,
            "algorithm_version": algorithm.version,
            "validated_at": _now_iso(),
        },
        summary=summary,
        sections=[
            {"heading": "Checks", "body": checks},
            {"heading": "Sample Output", "body": normalized.head(10).to_dict(orient="records")},
        ],
        status=status,
    )
    payload = {
        "name": algorithm.name,
        "version": algorithm.version,
        "status": status,
        "passed": passed,
        "summary": summary,
        "checks": checks,
        "report_path": report["report_path"],
        "created_at": _now_iso(),
    }
    insert_validation_run(payload)
    save_runtime_json(latest_validation_path(), payload)
    return payload
