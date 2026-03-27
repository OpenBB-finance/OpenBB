"""Human-readable ops issue queue helpers."""

from __future__ import annotations

from typing import Any

from openbb_quant_ml.models import OpsIssueItemResponse, OpsIssueQueueResponse, RiskPretradeRequest
from openbb_quant_ml.service.execution import risk_check_pretrade
from openbb_quant_ml.service.notification_center import get_notifications_history_response
from openbb_quant_ml.service.ops_status import get_ops_status_response
from openbb_quant_ml.service.reporting import get_reports_latest_response
from openbb_quant_ml.service.runtime_pointer import get_promoted_model_response

_SEVERITY_ORDER = {"critical": 0, "warning": 1, "info": 2}


def _append_issue(
    items: list[OpsIssueItemResponse],
    *,
    issue_id: str,
    severity: str,
    title: str,
    impact: str,
    suggested_action: str,
    target_route: str,
    target_search: dict[str, str] | None = None,
    source: str | None = None,
    status: str = "open",
) -> None:
    items.append(
        OpsIssueItemResponse(
            id=issue_id,
            severity=severity,  # type: ignore[arg-type]
            title=title,
            impact=impact,
            suggested_action=suggested_action,
            target_route=target_route,
            target_search=target_search or {},
            source=source,
            status=status,
        )
    )


def get_ops_issue_queue_response(*, limit: int = 10) -> OpsIssueQueueResponse:
    """Return the current issue queue for the Ops workspace."""
    status_payload = get_ops_status_response()
    items: list[OpsIssueItemResponse] = []

    for job in status_payload.jobs:
        last_status = str(job.last_status or "unknown").lower()
        if last_status == "failed":
            _append_issue(
                items,
                issue_id=f"job:{job.job}",
                severity="critical",
                title=f"{job.job.title()} scheduler job failed",
                impact="Scheduled data refreshes and downstream artifacts may be stale.",
                suggested_action="Open Ops, inspect the failing step, and rerun the job after fixing the root cause.",
                target_route="/ops",
                source="scheduler",
            )

    macro_health = status_payload.macro_health if isinstance(status_payload.macro_health, dict) else {}
    macro_status = str(macro_health.get("status", "ok")).lower()
    if macro_status != "ok":
        _append_issue(
            items,
            issue_id="macro:health",
            severity="warning",
            title="Macro data health requires attention",
            impact="Macro studies and feature exports may rely on stale or incomplete FRED data.",
            suggested_action="Open Macro Lab, review health diagnostics, and refresh the affected series.",
            target_route="/macro",
            source="macro",
        )

    data_quality = status_payload.data_quality if isinstance(status_payload.data_quality, dict) else {}
    qc_status = str(data_quality.get("qc_status", "NORMAL")).upper()
    if qc_status in {"WARNING", "CRITICAL"}:
        _append_issue(
            items,
            issue_id="quality:latest",
            severity="critical" if qc_status == "CRITICAL" else "warning",
            title=f"Latest data quality gate is {qc_status}",
            impact="Strategy evaluation and execution confidence are degraded until the gate is cleared.",
            suggested_action="Review the latest data quality report and rerun the affected pipeline.",
            target_route="/ops",
            source="data_quality",
        )

    notification_failures = get_notifications_history_response(limit=20).items
    for item in notification_failures:
        if item.status not in {"failed", "duplicate"}:
            continue
        _append_issue(
            items,
            issue_id=f"notification:{item.id}",
            severity="warning",
            title=f"Notification delivery {item.status}",
            impact="Important alerts may not be reaching downstream channels.",
            suggested_action="Review the notification payload and fix the failing delivery channel.",
            target_route="/ops",
            source="notifications",
        )
        if len(items) >= max(1, int(limit)):
            break

    promoted = get_promoted_model_response()
    if promoted.run_id:
        risk = risk_check_pretrade(
            RiskPretradeRequest(
                run_id=str(promoted.run_id),
                model_name=promoted.model_name,
            )
        )
        if not risk.passed:
            _append_issue(
                items,
                issue_id="execution:blocked",
                severity="critical" if risk.kill_switch else "warning",
                title="Execution handoff is blocked by pre-trade checks",
                impact="The current promoted strategy cannot be submitted as-is.",
                suggested_action=risk.blocking_summary
                or "Open Portfolio & Execution and resolve the blocking constraints before submitting orders.",
                target_route="/execution",
                target_search={
                    "runId": str(promoted.run_id),
                    "modelName": str(promoted.model_name),
                },
                source="execution",
            )

    if get_reports_latest_response().item is None:
        _append_issue(
            items,
            issue_id="reports:missing",
            severity="info",
            title="No recent HTML report is available",
            impact="Workspace summaries do not yet have a current report artifact to reference.",
            suggested_action="Generate a report from Macro Lab or Strategy Lab after the next successful run.",
            target_route="/ops",
            source="reports",
        )

    items.sort(key=lambda row: (_SEVERITY_ORDER.get(row.severity, 9), row.title))
    return OpsIssueQueueResponse(items=items[: max(1, int(limit))])
