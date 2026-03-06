"""Automated data quality checks and gate evaluation."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import numpy as np
import pandas as pd

from openbb_quant_ml.models import (
    DataQualityCheckResult,
    DataQualityHistoryResponse,
    DataQualityLatestResponse,
)
from openbb_quant_ml.service.data_lake import load_previous_lake_meta
from openbb_quant_ml.service.ops_policy import get_ops_policy
from openbb_quant_ml.service.registry.run_registry_db import (
    insert_quality_run,
    list_quality_runs,
    upsert_dataset_snapshot,
)
from openbb_quant_ml.service.reporting import write_quality_report

_SEVERITY_ORDER = {"NORMAL": 0, "WARNING": 1, "CRITICAL": 2}


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _threshold(name: str, default: float) -> float:
    policy = get_ops_policy()
    gate = policy.get("quality_gate", {}) if isinstance(policy, dict) else {}
    thresholds = gate.get("thresholds", {}) if isinstance(gate, dict) else {}
    try:
        return float(thresholds.get(name, default))
    except (TypeError, ValueError):
        return default


def _is_feature_layer(layer: str) -> bool:
    return str(layer).strip().lower() == "gold"


def _metric_severity(
    value: float,
    *,
    warning: float,
    critical: float,
    lower_is_bad: bool = False,
) -> str:
    if lower_is_bad:
        if value <= critical:
            return "CRITICAL"
        if value <= warning:
            return "WARNING"
        return "NORMAL"
    if value >= critical:
        return "CRITICAL"
    if value >= warning:
        return "WARNING"
    return "NORMAL"


def _pick_worst(left: str, right: str) -> str:
    return left if _SEVERITY_ORDER[left] >= _SEVERITY_ORDER[right] else right


def _numeric_outlier_ratio(frame: pd.DataFrame) -> float:
    numeric = frame.select_dtypes(include=["number"])
    if numeric.empty:
        return 0.0
    cleaned = numeric.apply(pd.to_numeric, errors="coerce")
    zscore = (cleaned - cleaned.mean()) / cleaned.std(ddof=0).replace(0.0, np.nan)
    outliers = zscore.abs() >= 5.0
    return float(np.nanmean(outliers.to_numpy(dtype=float)))


def _schema_drift(
    frame: pd.DataFrame, previous_meta: dict[str, Any]
) -> tuple[list[str], list[str]]:
    current = {str(col) for col in frame.columns}
    previous = set(
        str(col)
        for col in (
            previous_meta.get("profile", {}).get("columns", [])
            if isinstance(previous_meta, dict)
            else []
        )
    )
    return sorted(current - previous), sorted(previous - current)


def _distribution_shift(
    frame: pd.DataFrame, previous_meta: dict[str, Any]
) -> tuple[float, dict[str, float]]:
    prev_summary = previous_meta.get("profile", {}).get("numeric_summary", {})
    if not isinstance(prev_summary, dict):
        return 0.0, {}
    numeric = frame.select_dtypes(include=["number"])
    shifts: dict[str, float] = {}
    for column in numeric.columns:
        current = pd.to_numeric(numeric[column], errors="coerce")
        prev = prev_summary.get(str(column))
        if not isinstance(prev, dict):
            continue
        prev_mean = prev.get("mean")
        prev_std = prev.get("std")
        if prev_mean is None or prev_std in {None, 0, 0.0}:
            continue
        try:
            shift = abs(float(current.mean()) - float(prev_mean)) / max(
                abs(float(prev_std)), 1e-9
            )
        except (TypeError, ValueError):
            continue
        if not np.isnan(shift) and not np.isinf(shift):
            shifts[str(column)] = float(shift)
    return (max(shifts.values()) if shifts else 0.0), shifts


def _symbol_delta(
    frame: pd.DataFrame, previous_meta: dict[str, Any], snapshot_meta: dict[str, Any]
) -> tuple[float, list[str], list[str], float]:
    if "symbol" not in frame.columns:
        return 0.0, [], [], 1.0
    current_symbols = sorted(
        {str(symbol).strip().upper() for symbol in frame["symbol"].dropna().tolist()}
    )
    current_set = set(current_symbols)
    prev_symbols = set(
        str(symbol).strip().upper()
        for symbol in (
            previous_meta.get("metadata", {}).get("symbols", [])
            if isinstance(previous_meta, dict)
            else []
        )
    )
    added = sorted(current_set - prev_symbols)
    removed = sorted(prev_symbols - current_set)
    expected_symbols = (
        snapshot_meta.get("metadata", {}).get("expected_symbols", [])
        if isinstance(snapshot_meta, dict)
        else []
    )
    expected_count = max(len(expected_symbols), len(current_symbols), 1)
    coverage = float(len(current_set) / expected_count)
    return float(len(added) + len(removed)), added, removed, coverage


def _corporate_action_gaps(frame: pd.DataFrame) -> int:
    required = {"symbol", "date", "close"}
    if not required.issubset(frame.columns):
        return 0
    work = frame.loc[:, ["symbol", "date", "close"]].copy()
    work["date"] = pd.to_datetime(work["date"], errors="coerce")
    work["close"] = pd.to_numeric(work["close"], errors="coerce")
    work = work.dropna(subset=["date", "close"])
    if work.empty:
        return 0
    work = work.sort_values(["symbol", "date"])
    returns = work.groupby("symbol")["close"].pct_change(fill_method=None).abs()
    suspicious = returns >= 0.4
    return int(suspicious.sum())


def register_dataset_snapshot(snapshot_meta: dict[str, Any]) -> None:
    """Persist one lake snapshot entry in the registry DB."""
    if not isinstance(snapshot_meta, dict) or not snapshot_meta:
        return
    profile = snapshot_meta.get("profile", {})
    row_count = profile.get("rows") if isinstance(profile, dict) else None
    upsert_dataset_snapshot(
        run_id=(
            str(snapshot_meta.get("run_id")) if snapshot_meta.get("run_id") else None
        ),
        dataset_name=str(snapshot_meta.get("dataset", "unknown")),
        layer=str(snapshot_meta.get("layer", "unknown")),
        as_of_date=str(snapshot_meta.get("as_of_date", "")),
        version=str(snapshot_meta.get("version", "unknown")),
        uri=str(snapshot_meta.get("path", "")),
        row_count=int(row_count) if row_count is not None else None,
        checksum=str(snapshot_meta.get("version", "unknown")),
        profile_json=profile if isinstance(profile, dict) else {},
        metadata_json=(
            snapshot_meta.get("metadata", {})
            if isinstance(snapshot_meta.get("metadata"), dict)
            else {}
        ),
        created_at_utc=str(snapshot_meta.get("created_at_utc") or _now_iso()),
    )


def run_quality_gate(
    *,
    run_id: str | None,
    gate_name: str,
    dataset_name: str,
    layer: str,
    frame: pd.DataFrame,
    as_of_date: str,
    snapshot_meta: dict[str, Any],
) -> DataQualityLatestResponse:
    """Evaluate quality checks for one dataset and persist the result."""
    current_meta = snapshot_meta if isinstance(snapshot_meta, dict) else {}
    current_version = str(current_meta.get("version", "")).strip() or None
    previous_meta = load_previous_lake_meta(
        layer, dataset_name, exclude_version=current_version
    )
    checks: list[DataQualityCheckResult] = []
    worst = "NORMAL"

    layer_prefix = "feature" if _is_feature_layer(layer) else "market"
    missing_ratio = float(frame.isna().mean().mean()) if not frame.empty else 0.0
    severity = _metric_severity(
        missing_ratio,
        warning=_threshold(f"{layer_prefix}_missing_ratio_warning", 0.05),
        critical=_threshold(f"{layer_prefix}_missing_ratio_critical", 0.2),
    )
    worst = _pick_worst(worst, severity)
    checks.append(
        DataQualityCheckResult(
            check="missing_ratio",
            severity=severity,
            value=missing_ratio,
            threshold=_threshold(f"{layer_prefix}_missing_ratio_warning", 0.05),
            message="Overall missing-value ratio across the dataset.",
        )
    )

    outlier_ratio = _numeric_outlier_ratio(frame)
    severity = _metric_severity(
        outlier_ratio,
        warning=_threshold(f"{layer_prefix}_outlier_ratio_warning", 0.01),
        critical=_threshold(f"{layer_prefix}_outlier_ratio_critical", 0.03),
    )
    worst = _pick_worst(worst, severity)
    checks.append(
        DataQualityCheckResult(
            check="outlier_ratio",
            severity=severity,
            value=outlier_ratio,
            threshold=_threshold(f"{layer_prefix}_outlier_ratio_warning", 0.01),
            message="Share of numeric cells with |z-score| >= 5.",
        )
    )

    added_columns, removed_columns = _schema_drift(frame, previous_meta)
    schema_severity = "NORMAL"
    if len(removed_columns) >= int(
        _threshold("schema_drift_missing_columns_critical", 1)
    ):
        schema_severity = "CRITICAL"
    elif len(added_columns) >= int(
        _threshold("schema_drift_new_columns_warning", 3)
    ):
        schema_severity = "WARNING"
    worst = _pick_worst(worst, schema_severity)
    checks.append(
        DataQualityCheckResult(
            check="schema_drift",
            severity=schema_severity,
            value=len(added_columns) + len(removed_columns),
            threshold=_threshold("schema_drift_new_columns_warning", 3),
            message="Column-level schema change relative to the previous lake snapshot.",
            details={
                "added_columns": added_columns,
                "removed_columns": removed_columns,
            },
        )
    )

    distribution_shift, shift_details = _distribution_shift(frame, previous_meta)
    severity = _metric_severity(
        distribution_shift,
        warning=_threshold("distribution_shift_warning", 1.5),
        critical=_threshold("distribution_shift_critical", 2.5),
    )
    worst = _pick_worst(worst, severity)
    checks.append(
        DataQualityCheckResult(
            check="distribution_shift",
            severity=severity,
            value=distribution_shift,
            threshold=_threshold("distribution_shift_warning", 1.5),
            message="Max standardized mean shift versus the previous snapshot.",
            details={"columns": shift_details},
        )
    )

    ticker_change_count, added_symbols, removed_symbols, coverage = _symbol_delta(
        frame, previous_meta, current_meta
    )
    severity = _metric_severity(
        ticker_change_count,
        warning=_threshold("ticker_change_warning", 1),
        critical=max(_threshold("ticker_change_warning", 1) * 5.0, 5.0),
    )
    worst = _pick_worst(worst, severity)
    checks.append(
        DataQualityCheckResult(
            check="ticker_changes",
            severity=severity,
            value=ticker_change_count,
            threshold=_threshold("ticker_change_warning", 1),
            message="Symbol additions/removals relative to the previous snapshot.",
            details={
                "added_symbols": added_symbols[:25],
                "removed_symbols": removed_symbols[:25],
            },
        )
    )

    severity = _metric_severity(
        coverage,
        warning=_threshold("symbol_coverage_warning", 0.9),
        critical=_threshold("symbol_coverage_critical", 0.75),
        lower_is_bad=True,
    )
    worst = _pick_worst(worst, severity)
    checks.append(
        DataQualityCheckResult(
            check="symbol_coverage",
            severity=severity,
            value=coverage,
            threshold=_threshold("symbol_coverage_warning", 0.9),
            message="Observed symbol coverage versus expected universe size.",
        )
    )

    delisting_count = len(removed_symbols)
    severity = _metric_severity(
        float(delisting_count),
        warning=_threshold("delisting_warning", 1),
        critical=max(_threshold("delisting_warning", 1) * 5.0, 5.0),
    )
    worst = _pick_worst(worst, severity)
    checks.append(
        DataQualityCheckResult(
            check="delisting_detected",
            severity=severity,
            value=delisting_count,
            threshold=_threshold("delisting_warning", 1),
            message="Potential delistings or permanent symbol removals were detected.",
            details={"removed_symbols": removed_symbols[:25]},
        )
    )

    corporate_action_count = _corporate_action_gaps(frame)
    severity = _metric_severity(
        float(corporate_action_count),
        warning=_threshold("corporate_action_warning", 1),
        critical=max(_threshold("corporate_action_warning", 1) * 5.0, 5.0),
    )
    worst = _pick_worst(worst, severity)
    checks.append(
        DataQualityCheckResult(
            check="corporate_actions",
            severity=severity,
            value=corporate_action_count,
            threshold=_threshold("corporate_action_warning", 1),
            message="Large price jumps likely requiring corporate-action review.",
        )
    )

    summary = {
        "dataset_name": dataset_name,
        "layer": layer,
        "rows": int(len(frame)),
        "columns": int(len(frame.columns)),
        "version": current_meta.get("version"),
        "checks": [item.model_dump(mode="json") for item in checks],
    }
    report_item = write_quality_report(
        run_id=run_id,
        gate_name=gate_name,
        qc_status=worst,
        as_of_date=as_of_date,
        checks=summary["checks"],
        summary={
            "dataset_name": dataset_name,
            "layer": layer,
            "qc_status": worst,
            "rows": int(len(frame)),
            "columns": int(len(frame.columns)),
        },
    )
    insert_quality_run(
        run_id=run_id,
        gate_name=gate_name,
        qc_status=worst,
        as_of_date=as_of_date,
        summary_json=summary,
        report_path=str(report_item.get("report_path", "")),
        created_at_utc=_now_iso(),
    )
    return DataQualityLatestResponse(
        run_id=run_id,
        gate_name=gate_name,
        qc_status=worst,
        as_of_date=as_of_date,
        created_at=_now_iso(),
        checks=checks,
        summary=summary,
        report_path=str(report_item.get("report_path", "")),
    )


def _parse_quality_row(row: dict[str, Any]) -> DataQualityLatestResponse:
    summary_raw = row.get("summary", row.get("summary_json", {}))
    if isinstance(summary_raw, str):
        try:
            summary = json.loads(summary_raw)
        except json.JSONDecodeError:
            summary = {}
    else:
        summary = summary_raw if isinstance(summary_raw, dict) else {}
    checks_raw = summary.get("checks", []) if isinstance(summary, dict) else []
    checks: list[DataQualityCheckResult] = []
    if isinstance(checks_raw, list):
        for item in checks_raw:
            if isinstance(item, dict):
                checks.append(DataQualityCheckResult(**item))
    return DataQualityLatestResponse(
        run_id=row.get("run_id"),
        gate_name=str(row.get("gate_name", "")) or None,
        qc_status=str(row.get("qc_status", "NORMAL")),  # type: ignore[arg-type]
        as_of_date=row.get("as_of_date"),
        created_at=(
            str(row.get("created_at"))
            if row.get("created_at") is not None
            else str(row.get("created_at_utc")) if row.get("created_at_utc") else None
        ),
        checks=checks,
        summary=summary,
        report_path=(
            str(row.get("report_path")) if row.get("report_path") is not None else None
        ),
    )


def get_latest_data_quality_response(
    *, run_id: str | None = None
) -> DataQualityLatestResponse:
    """Return the latest data-quality result."""
    rows = list_quality_runs(run_id=run_id, limit=1)
    if not rows:
        return DataQualityLatestResponse()
    return _parse_quality_row(rows[0])


def get_data_quality_history_response(
    *, run_id: str | None = None, limit: int = 50
) -> DataQualityHistoryResponse:
    """Return historical data-quality results."""
    rows = list_quality_runs(run_id=run_id, limit=limit)
    return DataQualityHistoryResponse(
        items=[_parse_quality_row(row) for row in rows]
    )


def should_block_on_quality(qc_status: str) -> bool:
    """Return whether the execution gate must block the run."""
    policy = get_ops_policy()
    gate = policy.get("quality_gate", {}) if isinstance(policy, dict) else {}
    return bool(gate.get("block_on_critical", True)) and str(qc_status) == "CRITICAL"
