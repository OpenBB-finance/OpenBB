"""Workspace brief, symbol context, ops queue, and run compare service tests."""

from __future__ import annotations

from openbb_quant_ml.models import (
    ExperimentListResponse,
    ExperimentRunItemResponse,
    NotificationItemResponse,
    NotificationsHistoryResponse,
    OpsIssueItemResponse,
    OpsIssueQueueResponse,
    OpsJobStateResponse,
    OpsStatusResponse,
    PromotedModelResponse,
    ReportRunItemResponse,
    ReportsHistoryResponse,
    ReportsLatestResponse,
    RiskPretradeResponse,
    WorkspaceBriefResponse,
)
from openbb_quant_ml.service import ops_issues, run_compare, symbol_context, workspace_brief


def test_workspace_brief_response_builds_cards(monkeypatch) -> None:
    monkeypatch.setattr(
        workspace_brief,
        "list_macro_studies",
        lambda: [
            {
                "id": "study-1",
                "name": "Growth Monitor",
                "objective": "Track growth slowdown.",
                "conclusion": {"summary": "Growth is slowing."},
                "linked_assets": ["SPY", "TLT"],
                "linked_reports": [
                    {
                        "report_id": "report-1",
                        "report_path": "/tmp/macro-report.html",
                        "created_at": "2026-03-25T00:00:00Z",
                        "title": "Macro report",
                        "symbols": ["SPY"],
                    }
                ],
            }
        ],
    )
    monkeypatch.setattr(
        workspace_brief,
        "get_promoted_model_response",
        lambda: PromotedModelResponse(
            run_id="run-1",
            model_name="lgbm_ranker",
            as_of_date="2026-03-25",
            ready=True,
        ),
    )
    monkeypatch.setattr(
        workspace_brief,
        "get_experiment_detail_response",
        lambda run_id: ExperimentRunItemResponse(
            run_id=run_id,
            model_type="lgbm_ranker",
            feature_set_version="fs-v1",
            performance={"sharpe": 1.2},
            macro_study_links=["study-1"],
            training_window="2021-01-01 -> 2026-03-25",
            promotion_state="ready",
        ),
    )
    monkeypatch.setattr(
        workspace_brief,
        "get_portfolio_risk",
        lambda run_id, model_name: type(
            "RiskPayload",
            (),
            {
                "run_id": run_id,
                "model_name": model_name,
                "vol_ex_ante": 0.12,
                "cvar_95": 0.08,
                "position_risk_contrib_top5": [{"symbol": "SPY", "contribution": 0.31}],
            },
        )(),
    )
    monkeypatch.setattr(
        workspace_brief,
        "risk_check_pretrade",
        lambda request: RiskPretradeResponse(
            run_id=request.run_id,
            model_name=request.model_name,
            passed=False,
            kill_switch=False,
            violations=[
                {
                    "rule_id": "turnover",
                    "severity": "warning",
                    "value": 0.62,
                    "limit": 0.5,
                    "message": "Turnover constraint is blocking execution.",
                }
            ],
            blocking_summary="Turnover constraint is blocking execution.",
        ),
    )
    monkeypatch.setattr(
        workspace_brief,
        "get_ops_issue_queue_response",
        lambda limit=5: OpsIssueQueueResponse(
            items=[
                OpsIssueItemResponse(
                    id="issue-1",
                    severity="warning",
                    title="Execution blocked",
                    impact="Orders are blocked.",
                    suggested_action="Review execution blockers.",
                    target_route="/execution",
                    target_search={"runId": "run-1"},
                    source="execution",
                    status="open",
                )
            ]
        ),
    )
    monkeypatch.setattr(
        workspace_brief,
        "get_reports_latest_response",
        lambda: ReportsLatestResponse(
            item=ReportRunItemResponse(
                id=1,
                run_id="run-1",
                report_type="macro",
                report_path="/tmp/report.html",
                title="Macro report",
            )
        ),
    )

    payload = workspace_brief.get_workspace_brief_response()

    assert isinstance(payload, WorkspaceBriefResponse)
    assert payload.active_macro_study.study_id == "study-1"
    assert payload.current_strategy_candidate.run_id == "run-1"
    assert payload.portfolio_snapshot.blocked_constraints == [
        "Turnover constraint is blocking execution."
    ]
    assert payload.latest_report.report_path == "/tmp/report.html"
    assert any(item.target_route == "/macro" for item in payload.pending_actions)


def test_symbol_context_response_links_studies_reports_and_backlinks(monkeypatch) -> None:
    monkeypatch.setattr(
        symbol_context,
        "list_macro_studies",
        lambda: [
            {
                "id": "study-1",
                "name": "Growth Monitor",
                "objective": "Track growth slowdown.",
                "linked_assets": ["AAPL"],
                "linked_reports": [
                        {
                        "report_id": 1,
                        "report_path": "/tmp/report.html",
                        "title": "Attached report",
                        "created_at": "2026-03-25T00:00:00Z",
                        "source_run_id": "run-1",
                        "symbols": ["AAPL"],
                    }
                ],
            }
        ],
    )
    monkeypatch.setattr(
        symbol_context,
        "get_reports_history_response",
        lambda limit=100: ReportsHistoryResponse(items=[]),
    )
    monkeypatch.setattr(
        symbol_context,
        "get_experiment_detail_response",
        lambda run_id: ExperimentRunItemResponse(
            run_id=run_id,
            model_type="lgbm_ranker",
            feature_set_version="fs-v1",
            performance={"sharpe": 1.0},
            promotion_state="ready",
        ),
    )
    monkeypatch.setattr(
        symbol_context,
        "get_trading_symbol_detail_payload",
        lambda ticker: {
            "signals": [{"signal_id": "sig-1", "signal_type": "buy"}],
            "orders": [{"order_id": "ord-1", "status": "submitted"}],
            "position": {"ticker": ticker, "quantity": 10},
        },
    )

    payload = symbol_context.get_symbol_context_response(
        symbol="AAPL",
        source="execution",
        run_id="run-1",
        signal_id="sig-1",
    )

    assert payload.symbol == "AAPL"
    assert payload.linked_studies[0]["study_id"] == "study-1"
    assert payload.related_runs[0]["run_id"] == "run-1"
    assert payload.latest_signal["signal_type"] == "buy"
    assert payload.attached_reports[0].report_path == "/tmp/report.html"
    assert payload.back_links[0].target_route == "/execution"


def test_ops_issue_queue_response_surfaces_execution_blockers(monkeypatch) -> None:
    monkeypatch.setattr(
        ops_issues,
        "get_ops_status_response",
        lambda: OpsStatusResponse(
            jobs=[
                OpsJobStateResponse(
                    job="daily",
                    last_status="failed",
                    steps={},
                )
            ],
            macro_health={"status": "warning"},
            data_quality={"qc_status": "WARNING"},
        ),
    )
    monkeypatch.setattr(
        ops_issues,
        "get_notifications_history_response",
        lambda limit=20: NotificationsHistoryResponse(
            items=[
                NotificationItemResponse(
                    id=1,
                    channel="email",
                    status="failed",
                    event_type="report",
                    fingerprint="report:email",
                )
            ]
        ),
    )
    monkeypatch.setattr(
        ops_issues,
        "get_promoted_model_response",
        lambda: PromotedModelResponse(run_id="run-1", model_name="lgbm_ranker"),
    )
    monkeypatch.setattr(
        ops_issues,
        "risk_check_pretrade",
        lambda request: RiskPretradeResponse(
            run_id=request.run_id,
            model_name=request.model_name,
            passed=False,
            kill_switch=True,
            violations=[],
            blocking_summary="Kill switch is active.",
        ),
    )
    monkeypatch.setattr(ops_issues, "get_reports_latest_response", lambda: ReportsLatestResponse(item=None))

    payload = ops_issues.get_ops_issue_queue_response(limit=6)

    assert payload.items
    assert payload.items[0].severity == "critical"
    assert any(item.id == "execution:blocked" for item in payload.items)
    assert any(item.id == "reports:missing" for item in payload.items)


def test_run_compare_response_summarizes_recent_runs(monkeypatch) -> None:
    monkeypatch.setattr(
        run_compare,
        "get_experiment_list_response",
        lambda limit=5: ExperimentListResponse(
            items=[
                ExperimentRunItemResponse(
                    run_id="run-1",
                    model_type="lgbm_ranker",
                    performance={"sharpe": 1.1},
                ),
                ExperimentRunItemResponse(
                    run_id="run-2",
                    model_type="xgb_lstm",
                    performance={"cagr": 0.12},
                ),
            ]
        ),
    )
    monkeypatch.setattr(
        run_compare,
        "get_experiment_detail_response",
        lambda run_id: ExperimentRunItemResponse(
            run_id=run_id,
            model_type="lgbm_ranker" if run_id == "run-1" else "xgb_lstm",
            feature_set_version="fs-v1",
            performance={"sharpe": 1.1} if run_id == "run-1" else {"cagr": 0.12},
            macro_study_links=["study-1"],
            training_window="2021-01-01 -> 2026-03-25",
            constraints_summary={"turnover": 0.35},
            promotion_state="candidate",
        ),
    )

    payload = run_compare.get_run_compare_response(limit=2)

    assert len(payload.items) == 2
    assert payload.items[0].run_id == "run-1"
    assert payload.items[0].metrics["sharpe"] == 1.1
    assert payload.items[1].metrics["cagr"] == 0.12
