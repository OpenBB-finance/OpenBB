"""Run-level universe exclusion aggregation."""

from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

from openbb_quant_ml.service.storage import get_run_dir, save_parquet_atomic


def exclusions_path(run_id: str):
    """Return run-level exclusion parquet path."""
    return get_run_dir(run_id) / "exclusions.parquet"


def _normalize_rows(
    run_id: str, rebalance_date: date, rows: list[dict[str, Any]]
) -> pd.DataFrame:
    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        reasons = row.get("reasons", [])
        if isinstance(reasons, list):
            reason_code = "|".join(
                sorted(
                    {
                        str(item).strip()
                        for item in reasons
                        if str(item).strip()
                    }
                )
            )
        else:
            reason_code = str(reasons or "").strip()
        out.append(
            {
                "run_id": run_id,
                "rebalance_date": rebalance_date.isoformat(),
                "ticker": str(row.get("symbol", "")).strip().upper(),
                "stage": str(row.get("stage", "u0")).strip().lower(),
                "reason_code": reason_code,
                "company_id": str(row.get("company_id", "")).strip() or None,
                "raw_value": str(row),
            }
        )
    return pd.DataFrame(out)


def append_exclusions(
    run_id: str, rebalance_date: date, rows: list[dict[str, Any]]
) -> None:
    """Append exclusion rows to run-level exclusions.parquet."""
    new_rows = _normalize_rows(run_id, rebalance_date, rows)
    if new_rows.empty:
        return
    path = exclusions_path(run_id)
    if path.exists():
        old = pd.read_parquet(path)
        merged = pd.concat([old, new_rows], ignore_index=True)
    else:
        merged = new_rows
    merged = merged.drop_duplicates(
        subset=["run_id", "rebalance_date", "ticker", "stage", "reason_code"],
        keep="last",
    ).reset_index(drop=True)
    save_parquet_atomic(path, merged, index=False)

