"""Operational HTML reporting helpers."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from html import escape
from typing import Any

from openbb_quant_ml.models import (
    ReportRunItemResponse,
    ReportsHistoryResponse,
    ReportsLatestResponse,
)
from openbb_quant_ml.service.constants import REPORTS_DIR
from openbb_quant_ml.service.registry.run_registry_db import (
    insert_report_run,
    list_report_runs,
)
from openbb_quant_ml.service.storage import load_json, save_json


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _safe_slug(value: str) -> str:
    cleaned = "".join(
        ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in str(value).strip()
    )
    return cleaned.strip("_") or "report"


def _render_html(
    *,
    title: str,
    metadata: dict[str, Any] | None = None,
    summary: dict[str, Any] | None = None,
    sections: list[dict[str, Any]] | None = None,
) -> str:
    meta = metadata or {}
    summary_payload = summary or {}
    section_rows = sections or []
    meta_html = "".join(
        f"<li><b>{escape(str(key))}</b>: {escape(str(value))}</li>"
        for key, value in meta.items()
    )
    summary_html = "".join(
        f"<li><b>{escape(str(key))}</b>: {escape(str(value))}</li>"
        for key, value in summary_payload.items()
    )
    sections_html = []
    for row in section_rows:
        heading = escape(str(row.get("heading", "Section")))
        body = row.get("body", "")
        if isinstance(body, (dict, list)):
            body_html = (
                "<pre>"
                + escape(json.dumps(body, ensure_ascii=False, indent=2))
                + "</pre>"
            )
        else:
            body_html = f"<p>{escape(str(body))}</p>"
        sections_html.append(f"<section><h2>{heading}</h2>{body_html}</section>")
    return (
        "<html><head><meta charset='utf-8'>"
        f"<title>{escape(title)}</title>"
        "<style>"
        "body{font-family:Segoe UI,Arial,sans-serif;margin:32px;line-height:1.5;color:#111827;}"
        "h1,h2{color:#111827;}section{margin-top:24px;padding-top:8px;border-top:1px solid #e5e7eb;}"
        "pre{background:#f3f4f6;padding:12px;border-radius:8px;overflow:auto;}"
        "ul{padding-left:20px;}"
        "</style></head><body>"
        f"<h1>{escape(title)}</h1>"
        f"<p>Generated at {_now_iso()}</p>"
        + (f"<h2>Metadata</h2><ul>{meta_html}</ul>" if meta_html else "")
        + (f"<h2>Summary</h2><ul>{summary_html}</ul>" if summary_html else "")
        + "".join(sections_html)
        + "</body></html>"
    )


def _update_report_index(item: dict[str, Any]) -> None:
    index_path = REPORTS_DIR / "_index.json"
    payload = load_json(index_path, default={"items": []})
    rows = payload.get("items", []) if isinstance(payload, dict) else []
    if not isinstance(rows, list):
        rows = []
    rows.insert(0, item)
    save_json(index_path, {"items": rows[:500]})


def write_report(
    *,
    run_id: str | None,
    report_type: str,
    title: str,
    metadata: dict[str, Any] | None = None,
    summary: dict[str, Any] | None = None,
    sections: list[dict[str, Any]] | None = None,
    status: str = "created",
) -> dict[str, Any]:
    """Write one HTML report and persist it in the registry."""
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_token = _safe_slug(run_id or "global")
    type_token = _safe_slug(report_type)
    report_dir = REPORTS_DIR / type_token
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{run_token}_{ts}.html"
    report_path.write_text(
        _render_html(
            title=title,
            metadata=metadata,
            summary=summary,
            sections=sections,
        ),
        encoding="utf-8",
    )
    created_at = _now_iso()
    summary_payload = summary or {}
    insert_report_run(
        run_id=run_id,
        report_type=report_type,
        report_path=str(report_path),
        status=status,
        summary_json=summary_payload,
        created_at_utc=created_at,
    )
    item = {
        "run_id": run_id,
        "report_type": report_type,
        "report_path": str(report_path),
        "status": status,
        "summary": summary_payload,
        "created_at": created_at,
    }
    _update_report_index(item)
    return item


def write_quality_report(
    *,
    run_id: str | None,
    gate_name: str,
    qc_status: str,
    as_of_date: str | None,
    checks: list[dict[str, Any]],
    summary: dict[str, Any],
) -> dict[str, Any]:
    """Write a standardized data quality report."""
    return write_report(
        run_id=run_id,
        report_type="data_quality",
        title=f"Data Quality Report: {gate_name}",
        metadata={
            "run_id": run_id,
            "gate_name": gate_name,
            "qc_status": qc_status,
            "as_of_date": as_of_date,
        },
        summary=summary,
        sections=[{"heading": "Checks", "body": checks}],
    )


def write_backtest_report(
    *,
    run_id: str,
    model_name: str,
    metrics: dict[str, Any],
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Write a standardized backtest performance report."""
    return write_report(
        run_id=run_id,
        report_type="backtest_performance",
        title=f"Backtest Performance Report: {model_name}",
        metadata={"run_id": run_id, "model_name": model_name},
        summary=metrics,
        sections=[
            {
                "heading": "Performance Metrics",
                "body": metrics,
            },
            {
                "heading": "Backtest Payload Excerpt",
                "body": {
                    "benchmark_symbol": payload.get("benchmark_symbol"),
                    "cost_bps": payload.get("cost_bps"),
                    "slippage_bps": payload.get("slippage_bps"),
                    "rebalance_history_summary": payload.get(
                        "rebalance_history_summary", []
                    )[:5],
                },
            },
        ],
    )


def _row_to_response(row: dict[str, Any]) -> ReportRunItemResponse:
    summary = (
        row.get("summary")
        if isinstance(row.get("summary"), dict)
        else json.loads(str(row.get("summary_json") or "{}"))
    )
    if not isinstance(summary, dict):
        summary = {}
    title = summary.get("title")
    if title is None:
        report_type = str(row.get("report_type", "")).strip().replace("_", " ")
        title = report_type.title() or "Report"
    symbols = summary.get("symbols", [])
    if not isinstance(symbols, list):
        symbols = []
    return ReportRunItemResponse(
        id=int(row.get("id")) if row.get("id") is not None else None,
        run_id=row.get("run_id"),
        report_type=str(row.get("report_type", "")),
        report_path=str(row.get("report_path", "")),
        status=str(row.get("status", "created") or "created"),
        created_at=(
            str(row.get("created_at"))
            if row.get("created_at") is not None
            else str(row.get("created_at_utc")) if row.get("created_at_utc") else None
        ),
        title=str(title) if title is not None else None,
        symbols=[str(item).upper() for item in symbols if str(item).strip()],
        summary=summary,
    )


def get_reports_latest_response(
    *,
    run_id: str | None = None,
    report_type: str | None = None,
) -> ReportsLatestResponse:
    """Return the latest stored report."""
    rows = list_report_runs(run_id=run_id, report_type=report_type, limit=1)
    if not rows:
        return ReportsLatestResponse(item=None)
    return ReportsLatestResponse(item=_row_to_response(rows[0]))


def get_reports_history_response(
    *,
    run_id: str | None = None,
    report_type: str | None = None,
    limit: int = 50,
) -> ReportsHistoryResponse:
    """Return historical reports."""
    rows = list_report_runs(run_id=run_id, report_type=report_type, limit=limit)
    return ReportsHistoryResponse(items=[_row_to_response(row) for row in rows])
