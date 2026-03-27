"""Cross-workflow Symbol Lab context helpers."""

from __future__ import annotations

from typing import Any

from openbb_quant_ml.models import (
    ReportRunItemResponse,
    SymbolContextLinkResponse,
    SymbolContextResponse,
)
from openbb_quant_ml.service.experiment_tracking import get_experiment_detail_response
from openbb_quant_ml.service.macro_db import list_macro_studies
from openbb_quant_ml.service.reporting import get_reports_history_response
from openbb_quant_ml.service.trading import get_trading_symbol_detail_payload


def _study_matches_symbol(study: dict[str, Any], symbol: str) -> bool:
    assets = {
        str(item).upper()
        for item in (study.get("linked_assets") or [])
        if str(item).strip()
    }
    if symbol in assets:
        return True
    for report in study.get("linked_reports") or []:
        symbols = {
            str(item).upper()
            for item in (report.get("symbols") or [])
            if str(item).strip()
        }
        if symbol in symbols:
            return True
    return False


def _build_back_links(
    *,
    source: str | None,
    study_id: str | None,
    run_id: str | None,
    signal_id: str | None,
    report_path: str | None,
) -> list[SymbolContextLinkResponse]:
    if not source:
        return []
    source_key = str(source).strip().lower()
    if source_key == "macro":
        return [
            SymbolContextLinkResponse(
                label="Back to Macro Lab",
                target_route="/macro",
                target_search={"studyId": str(study_id)} if study_id else {},
            )
        ]
    if source_key in {"strategy", "quant"}:
        return [
            SymbolContextLinkResponse(
                label="Back to Strategy Lab",
                target_route="/quant",
                target_search={"runId": str(run_id)} if run_id else {},
            )
        ]
    if source_key in {"execution", "trading"}:
        search = {}
        if run_id:
            search["runId"] = str(run_id)
        if signal_id:
            search["signalId"] = str(signal_id)
        return [
            SymbolContextLinkResponse(
                label="Back to Portfolio & Execution",
                target_route="/execution",
                target_search=search,
            )
        ]
    if source_key == "ops":
        return [
            SymbolContextLinkResponse(
                label="Back to Ops",
                target_route="/ops",
                target_search={"reportPath": str(report_path)} if report_path else {},
            )
        ]
    if source_key == "workspace":
        return [SymbolContextLinkResponse(label="Back to Workspace", target_route="/workspace")]
    return []


def get_symbol_context_response(
    *,
    symbol: str,
    source: str | None = None,
    study_id: str | None = None,
    run_id: str | None = None,
    signal_id: str | None = None,
    report_path: str | None = None,
) -> SymbolContextResponse:
    """Return the shared Symbol Lab context payload."""
    ticker = str(symbol or "").strip().upper()
    studies = [row for row in list_macro_studies() if _study_matches_symbol(row, ticker)]
    linked_studies = [
        {
            "study_id": str(row.get("id", "")),
            "name": str(row.get("name", "")),
            "objective": str(row.get("objective", "")),
        }
        for row in studies
    ]

    attached_reports_map: dict[str, ReportRunItemResponse] = {}
    for study in studies:
        for attachment in study.get("linked_reports") or []:
            symbols = {
                str(item).upper()
                for item in (attachment.get("symbols") or [])
                if str(item).strip()
            }
            if symbols and ticker not in symbols:
                continue
            report_key = str(attachment.get("report_path", "")).strip()
            if not report_key:
                continue
            attached_reports_map[report_key] = ReportRunItemResponse(
                id=attachment.get("report_id"),
                run_id=attachment.get("source_run_id"),
                report_type="study_attachment",
                report_path=report_key,
                status="attached",
                created_at=attachment.get("created_at"),
                title=attachment.get("title"),
                symbols=[str(item).upper() for item in (attachment.get("symbols") or [])],
                summary={},
            )

    if report_path:
        for report in get_reports_history_response(limit=100).items:
            if str(report.report_path).strip() == str(report_path).strip():
                attached_reports_map[str(report.report_path)] = report
                break

    related_runs_map: dict[str, dict[str, Any]] = {}
    candidate_run_ids = {
        str(run_id).strip()
        for run_id in [
            run_id,
            *[item.run_id for item in attached_reports_map.values() if item.run_id],
        ]
        if str(run_id or "").strip()
    }
    for candidate_run_id in candidate_run_ids:
        detail = get_experiment_detail_response(candidate_run_id)
        if not detail.run_id:
            continue
        related_runs_map[candidate_run_id] = {
            "run_id": detail.run_id,
            "model_name": detail.model_type,
            "feature_set_version": detail.feature_set_version,
            "promotion_state": detail.promotion_state,
        }

    trading_detail = get_trading_symbol_detail_payload(ticker)
    signals = trading_detail.get("signals", []) if isinstance(trading_detail, dict) else []
    orders = trading_detail.get("orders", []) if isinstance(trading_detail, dict) else []

    return SymbolContextResponse(
        symbol=ticker,
        source=str(source) if source else None,
        linked_studies=linked_studies,
        related_runs=list(related_runs_map.values()),
        latest_signal=signals[0] if signals else None,
        latest_order=orders[-1] if orders else None,
        latest_position=trading_detail.get("position") if isinstance(trading_detail, dict) else None,
        attached_reports=list(attached_reports_map.values()),
        back_links=_build_back_links(
            source=source,
            study_id=study_id,
            run_id=run_id,
            signal_id=signal_id,
            report_path=report_path,
        ),
    )
