"""Strategy run comparison helpers."""

from __future__ import annotations

from typing import Any

from openbb_quant_ml.models import RunCompareItemResponse, RunCompareResponse
from openbb_quant_ml.service.experiment_tracking import (
    get_experiment_detail_response,
    get_experiment_list_response,
)

_METRIC_KEYS = (
    "sharpe",
    "sortino",
    "cagr",
    "annual_return",
    "max_drawdown",
    "turnover",
    "hit_rate",
    "ic_mean",
)


def _metrics_summary(performance: dict[str, Any]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for key in _METRIC_KEYS:
        if key in performance:
            summary[key] = performance.get(key)
    if summary:
        return summary
    for key, value in performance.items():
        if isinstance(value, (int, float, str, bool)):
            summary[str(key)] = value
        if len(summary) >= 8:
            break
    return summary


def get_run_compare_response(
    *, run_ids: list[str] | None = None, limit: int = 5
) -> RunCompareResponse:
    """Return a compact comparison payload for recent strategy runs."""
    selected_ids = [str(item).strip() for item in (run_ids or []) if str(item).strip()]
    if not selected_ids:
        selected_ids = [
            item.run_id
            for item in get_experiment_list_response(limit=max(2, int(limit))).items
            if item.run_id
        ][: max(2, int(limit))]

    rows: list[RunCompareItemResponse] = []
    for run_id in selected_ids:
        item = get_experiment_detail_response(run_id)
        if not item.run_id:
            continue
        rows.append(
            RunCompareItemResponse(
                run_id=item.run_id,
                model_name=item.model_type,
                training_window=item.training_window,
                feature_set_version=item.feature_set_version,
                macro_study_links=item.macro_study_links,
                metrics=_metrics_summary(item.performance),
                constraints_summary=item.constraints_summary,
                promotion_state=item.promotion_state,
            )
        )
    return RunCompareResponse(items=rows)
