"""Constraint log builders."""

from __future__ import annotations

from collections import Counter
from typing import Any

import pandas as pd


def build_constraints_log(
    *,
    rebalance_reports: list[dict[str, Any]],
    constraint_violations: list[dict[str, Any]],
) -> pd.DataFrame:
    """Build standardized constraints_log.parquet rows."""
    rows: list[dict[str, Any]] = []
    for report in rebalance_reports:
        if not isinstance(report, dict):
            continue
        as_of = str(report.get("date", ""))
        binding = report.get("binding_constraints", [])
        if isinstance(binding, list):
            for item in binding:
                rows.append(
                    {
                        "date": as_of,
                        "ticker": None,
                        "constraint_type": str(item),
                        "before_weight": None,
                        "after_weight": None,
                        "threshold": None,
                        "binding": True,
                        "violation_bp": 0.0,
                        "reason_code": "binding",
                    }
                )
        for liq in report.get("liquidity_constraint_report", []) or []:
            if not isinstance(liq, dict):
                continue
            cap = float(liq.get("weight_cap_adv", 0.0) or 0.0)
            rows.append(
                {
                    "date": as_of,
                    "ticker": str(liq.get("symbol", "")).strip().upper() or None,
                    "constraint_type": "liquidity_adv20",
                    "before_weight": None,
                    "after_weight": None,
                    "threshold": cap,
                    "binding": cap <= 0.0,
                    "violation_bp": 0.0,
                    "reason_code": "adv_cap",
                }
            )
    for item in constraint_violations:
        if not isinstance(item, dict):
            continue
        value = float(item.get("value", 0.0) or 0.0)
        threshold = float(item.get("threshold", 0.0) or 0.0)
        violation_bp = max(0.0, (value - threshold) * 10_000.0)
        rows.append(
            {
                "date": str(item.get("date", "")),
                "ticker": str(item.get("symbol", "")).strip().upper() or None,
                "constraint_type": str(item.get("type", "unknown")),
                "before_weight": item.get("before_weight"),
                "after_weight": item.get("after_weight"),
                "threshold": threshold if threshold else None,
                "binding": True,
                "violation_bp": violation_bp,
                "reason_code": "violation",
            }
        )
    if not rows:
        return pd.DataFrame(
            columns=[
                "date",
                "ticker",
                "constraint_type",
                "before_weight",
                "after_weight",
                "threshold",
                "binding",
                "violation_bp",
                "reason_code",
            ]
        )
    return pd.DataFrame(rows)


def summarize_constraint_bindings(
    constraints_log: pd.DataFrame,
) -> list[dict[str, Any]]:
    """Summarize binding frequency by constraint type."""
    if constraints_log.empty or "constraint_type" not in constraints_log.columns:
        return []
    filtered = constraints_log[constraints_log["binding"] == True]  # noqa: E712
    counter = Counter(str(item) for item in filtered["constraint_type"].tolist())
    total = max(1, int(sum(counter.values())))
    rows = []
    for key, count in sorted(counter.items(), key=lambda item: item[1], reverse=True):
        rows.append(
            {
                "constraint_type": key,
                "binding_count": int(count),
                "binding_ratio": float(count) / float(total),
            }
        )
    return rows

