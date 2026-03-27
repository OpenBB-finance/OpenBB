"""Aggregated workspace brief helpers."""

from __future__ import annotations

from openbb_quant_ml.models import (
    RiskPretradeRequest,
    WorkspaceActionItemResponse,
    WorkspaceBriefResponse,
    WorkspaceLatestReportResponse,
    WorkspaceMacroStudyCardResponse,
    WorkspacePortfolioContributorResponse,
    WorkspacePortfolioSnapshotResponse,
    WorkspaceStrategyCandidateResponse,
)
from openbb_quant_ml.service.dashboard_metrics import get_portfolio_risk
from openbb_quant_ml.service.execution import risk_check_pretrade
from openbb_quant_ml.service.experiment_tracking import (
    get_experiment_detail_response,
    get_experiment_list_response,
)
from openbb_quant_ml.service.macro_constants import MACRO_ROOT
from openbb_quant_ml.service.macro_db import list_macro_studies
from openbb_quant_ml.service.ops_issues import get_ops_issue_queue_response
from openbb_quant_ml.service.reporting import get_reports_latest_response
from openbb_quant_ml.service.runtime_pointer import get_promoted_model_response
from openbb_quant_ml.service.storage import utc_now_iso


def _latest_feature_export_path(study_id: str | None) -> str | None:
    if not study_id:
        return None
    path = MACRO_ROOT / "feature_exports" / f"{study_id}.json"
    return str(path) if path.exists() else None


def _build_active_macro_study() -> WorkspaceMacroStudyCardResponse:
    studies = list_macro_studies()
    if not studies:
        return WorkspaceMacroStudyCardResponse()
    study = studies[0]
    linked_reports = study.get("linked_reports", [])
    latest_report = linked_reports[0]["report_path"] if linked_reports else None
    conclusion = study.get("conclusion", {})
    summary = conclusion.get("summary") if isinstance(conclusion, dict) else None
    return WorkspaceMacroStudyCardResponse(
        study_id=str(study.get("id")) if study.get("id") else None,
        name=str(study.get("name")) if study.get("name") else None,
        objective=str(study.get("objective")) if study.get("objective") else None,
        conclusion_summary=str(summary) if summary else None,
        linked_assets=[
            str(item).upper()
            for item in (study.get("linked_assets") or [])
            if str(item).strip()
        ],
        latest_feature_export=_latest_feature_export_path(study.get("id")),
        latest_attached_report=str(latest_report) if latest_report else None,
    )


def _build_strategy_candidate() -> WorkspaceStrategyCandidateResponse:
    promoted = get_promoted_model_response()
    if promoted.run_id:
        item = get_experiment_detail_response(str(promoted.run_id))
        feature_lineage = item.macro_study_links or (
            [item.feature_set_version] if item.feature_set_version else []
        )
        readiness = "ready" if promoted.ready else (item.promotion_state or "not_ready")
        return WorkspaceStrategyCandidateResponse(
            run_id=str(promoted.run_id),
            model_name=str(promoted.model_name),
            as_of_date=promoted.as_of_date,
            feature_lineage=[str(row) for row in feature_lineage if str(row).strip()],
            promotion_readiness=readiness,
            training_window=item.training_window,
            macro_study_links=item.macro_study_links,
        )
    recent = get_experiment_list_response(limit=1).items
    if not recent:
        return WorkspaceStrategyCandidateResponse()
    item = recent[0]
    return WorkspaceStrategyCandidateResponse(
        run_id=item.run_id,
        model_name=item.model_type,
        feature_lineage=item.macro_study_links
        or ([item.feature_set_version] if item.feature_set_version else []),
        promotion_readiness=item.promotion_state or "candidate",
        training_window=item.training_window,
        macro_study_links=item.macro_study_links,
    )


def _build_portfolio_snapshot(
    candidate: WorkspaceStrategyCandidateResponse,
) -> WorkspacePortfolioSnapshotResponse:
    if not candidate.run_id:
        return WorkspacePortfolioSnapshotResponse()
    try:
        risk = get_portfolio_risk(
            run_id=candidate.run_id,
            model_name=candidate.model_name,
        )
    except Exception:  # noqa: BLE001
        return WorkspacePortfolioSnapshotResponse(
            run_id=candidate.run_id,
            model_name=candidate.model_name,
        )
    blocked: list[str] = []
    try:
        pretrade = risk_check_pretrade(
            RiskPretradeRequest(
                run_id=candidate.run_id,
                model_name=candidate.model_name or "lgbm_ranker",
            )
        )
        blocked = [item.message for item in pretrade.violations]
    except Exception:  # noqa: BLE001
        blocked = []
    return WorkspacePortfolioSnapshotResponse(
        run_id=risk.run_id,
        model_name=risk.model_name,
        vol_ex_ante=risk.vol_ex_ante,
        cvar_95=risk.cvar_95,
        top_risk_contributors=[
            WorkspacePortfolioContributorResponse(
                symbol=str(item.get("symbol", "")),
                contribution=float(item.get("contribution", 0.0) or 0.0),
            )
            for item in risk.position_risk_contrib_top5
            if str(item.get("symbol", "")).strip()
        ],
        blocked_constraints=blocked,
    )


def _build_latest_report() -> WorkspaceLatestReportResponse:
    report = get_reports_latest_response().item
    if report is None:
        return WorkspaceLatestReportResponse()
    return WorkspaceLatestReportResponse(
        report_id=report.id,
        title=report.title,
        report_type=report.report_type,
        report_path=report.report_path,
        created_at=report.created_at,
    )


def _build_actions(
    macro_card: WorkspaceMacroStudyCardResponse,
    strategy_card: WorkspaceStrategyCandidateResponse,
    portfolio_card: WorkspacePortfolioSnapshotResponse,
    latest_report: WorkspaceLatestReportResponse,
    ops_count: int,
) -> list[WorkspaceActionItemResponse]:
    items: list[WorkspaceActionItemResponse] = []
    if macro_card.study_id:
        items.append(
            WorkspaceActionItemResponse(
                id="action:macro",
                title="Open Macro Lab",
                detail="Continue the active macro study and update the conclusion if needed.",
                target_route="/macro",
                target_search={"studyId": macro_card.study_id},
            )
        )
    else:
        items.append(
            WorkspaceActionItemResponse(
                id="action:macro:new",
                title="Start a macro study",
                detail="Create a new macro study to define the current thesis and linked assets.",
                target_route="/macro",
            )
        )
    if strategy_card.run_id:
        items.append(
            WorkspaceActionItemResponse(
                id="action:strategy",
                title="Open Strategy Lab",
                detail="Review the latest strategy candidate and its feature lineage.",
                target_route="/quant",
                target_search={"runId": strategy_card.run_id},
            )
        )
    if portfolio_card.blocked_constraints:
        items.append(
            WorkspaceActionItemResponse(
                id="action:execution",
                title="Resolve execution blockers",
                detail=portfolio_card.blocked_constraints[0],
                target_route="/execution",
                target_search={"runId": strategy_card.run_id or ""},
            )
        )
    if latest_report.report_path:
        items.append(
            WorkspaceActionItemResponse(
                id="action:report",
                title="Open latest report",
                detail="Jump to the newest report artifact from the workspace brief.",
                target_route="/ops",
                target_search={"reportPath": latest_report.report_path},
            )
        )
    if ops_count:
        items.append(
            WorkspaceActionItemResponse(
                id="action:ops",
                title="Review Ops queue",
                detail=f"{ops_count} active issue(s) require attention.",
                target_route="/ops",
            )
        )
    return items[:6]


def get_workspace_brief_response() -> WorkspaceBriefResponse:
    """Return the aggregated workspace brief payload."""
    macro_card = _build_active_macro_study()
    strategy_card = _build_strategy_candidate()
    portfolio_card = _build_portfolio_snapshot(strategy_card)
    ops_queue = get_ops_issue_queue_response(limit=5).items
    latest_report = _build_latest_report()
    return WorkspaceBriefResponse(
        status="ok",
        generated_at=utc_now_iso(),
        active_macro_study=macro_card,
        current_strategy_candidate=strategy_card,
        portfolio_snapshot=portfolio_card,
        ops_issue_queue=ops_queue,
        latest_report=latest_report,
        pending_actions=_build_actions(
            macro_card,
            strategy_card,
            portfolio_card,
            latest_report,
            len(ops_queue),
        ),
    )
