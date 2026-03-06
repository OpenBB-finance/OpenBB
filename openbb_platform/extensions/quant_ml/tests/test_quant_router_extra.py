"""Additional coverage tests for quant router wrappers."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.testclient import TestClient
from openbb_core.app.router import Router
from openbb_quant_ml import quant_ml_router as qmr
from openbb_quant_ml.models import DashboardSnapshotV2


def _dummy_request(ip: str = "127.0.0.1"):
    return SimpleNamespace(client=SimpleNamespace(host=ip))


@pytest.mark.parametrize(
    ("attr", "func", "kwargs", "status"),
    [
        ("get_run", qmr.run_status, {"run_id": "x"}, 404),
        ("get_run_snapshot", qmr.run_snapshot, {"run_id": "x", "model_name": "lgbm_ranker"}, 404),
        ("get_run_risk", qmr.run_risk, {"run_id": "x", "model_name": "lgbm_ranker", "lookback": 10}, 404),
        ("get_run_exposures", qmr.run_exposures, {"run_id": "x", "model_name": "lgbm_ranker"}, 404),
        ("get_run_constraints", qmr.run_constraints, {"run_id": "x", "model_name": "lgbm_ranker"}, 404),
        ("build_signals", qmr.signals, {"request": SimpleNamespace()}, 400),
        (
            "run_backtest_for_run",
            qmr.backtest,
            {"request": SimpleNamespace()},
            400,
        ),
        ("submit_walkforward_backtest", qmr.backtest_walkforward, {"request": SimpleNamespace()}, 400),
        ("get_summary", qmr.artifacts_summary, {"run_id": "x", "model_name": "lgbm_ranker"}, 404),
        ("get_model_performance", qmr.model_performance, {"run_id": "x"}, 404),
        ("get_model_ic", qmr.model_ic, {"run_id": "x", "model_name": "lgbm_ranker", "window": 6}, 400),
        ("get_model_regime", qmr.model_regime, {"run_id": "x", "model_name": "lgbm_ranker"}, 400),
        ("get_rebalance_history", qmr.portfolio_rebalance_history, {"run_id": "x", "model_name": "lgbm_ranker"}, 404),
        ("get_feature_importance", qmr.feature_importance, {"run_id": "x", "model_name": "lgbm_ranker"}, 404),
        ("get_predictions_latest", qmr.predictions_latest, {"run_id": "x", "model_name": "lgbm_ranker", "top_k": 10}, 404),
        ("get_performance_rolling", qmr.performance_rolling, {"run_id": "x", "model_name": "lgbm_ranker", "window_short": 63, "window_long": 126}, 404),
        ("get_performance_regime", qmr.performance_regime, {"run_id": "x", "model_name": "lgbm_ranker"}, 404),
        ("get_portfolio_exposure", qmr.portfolio_exposure, {"run_id": "x", "model_name": "lgbm_ranker"}, 404),
        ("get_portfolio_risk", qmr.portfolio_risk, {"run_id": "x", "model_name": "lgbm_ranker", "lookback": 10}, 404),
        ("get_model_ic_decay", qmr.model_ic_decay, {"run_id": "x", "model_name": "lgbm_ranker", "max_horizon": 10}, 404),
        ("get_model_shap", qmr.model_shap, {"run_id": "x", "model_name": "lgbm_ranker"}, 404),
        ("get_prediction_distribution", qmr.prediction_distribution, {"run_id": "x", "model_name": "lgbm_ranker", "bins": 10}, 404),
        ("get_regime_current", qmr.regime_current, {"run_id": "x", "model_name": "lgbm_ranker"}, 404),
        ("get_regime_history", qmr.regime_history, {"run_id": "x", "model_name": "lgbm_ranker"}, 404),
        ("get_alerts_current", qmr.alerts_current, {"run_id": "x", "model_name": "lgbm_ranker"}, 404),
        ("get_alerts_history", qmr.alerts_history, {"run_id": "x", "model_name": "lgbm_ranker", "limit": 10}, 404),
        ("preview_execution_orders", qmr.execution_orders_preview, {"request": SimpleNamespace()}, 400),
        ("submit_execution_orders", qmr.execution_orders_submit, {"request": SimpleNamespace()}, 400),
        ("risk_check_pretrade", qmr.risk_check_pretrade_route, {"request": SimpleNamespace()}, 400),
        ("get_market_ratio_response", qmr.market_ratio, {"lhs": "SPY", "rhs": "QQQ"}, 400),
        ("get_market_rolling_corr_response", qmr.market_rolling_corr, {"x": "SPY", "y": "QQQ", "window": 60}, 400),
    ],
)
def test_router_wrappers_map_value_error(
    monkeypatch: pytest.MonkeyPatch,
    attr: str,
    func,
    kwargs: dict[str, object],
    status: int,
) -> None:
    def _raise(*args, **kwargs):  # noqa: ANN002, ANN003
        raise ValueError("boom")

    monkeypatch.setattr(qmr, attr, _raise)
    with pytest.raises(HTTPException) as exc:
        func(**kwargs)
    assert exc.value.status_code == status


def test_portfolio_current_maps_backtest_conflict(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(qmr, "get_portfolio_current", lambda **kwargs: (_ for _ in ()).throw(ValueError("Run backtest first")))
    with pytest.raises(HTTPException) as exc:
        qmr.portfolio_current(run_id="x", model_name="lgbm_ranker")
    assert exc.value.status_code == 409


def test_universe_list_and_resolve_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(qmr, "list_universe_ids", lambda: ["sp500"])
    monkeypatch.setattr(qmr, "get_universe_file_path", lambda uid: f"/tmp/{uid}.csv")
    monkeypatch.setattr(qmr, "universe_file_exists", lambda uid: True)
    monkeypatch.setattr(qmr, "get_universe_count_hint", lambda uid: 500)
    monkeypatch.setattr(qmr, "get_universe_minimum_required", lambda uid: 100)
    payload = qmr.universe_list()
    assert payload.universes[0].id == "sp500"

    monkeypatch.setattr(qmr, "get_symbols_for_universe", lambda uid: ["AAPL", "MSFT"])
    monkeypatch.setattr(qmr, "get_universe_size_status", lambda uid, symbols: (2, 1, True))
    resolved = qmr.universe_resolve(universe_id="sp500", mode="train", include_symbols=True)
    assert resolved.universe_id == "sp500"
    assert resolved.symbols == ["AAPL", "MSFT"]

    with pytest.raises(HTTPException):
        qmr.universe_resolve(universe_id=" ", mode="train", include_symbols=False)


def test_run_snapshot_profile_passthrough(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[str] = []

    def _snapshot(**kwargs):
        captured.append(str(kwargs.get("profile", "")))
        return DashboardSnapshotV2(
            run_id="run-1",
            model_name="lgbm_ranker",
            snapshot_profile=str(kwargs.get("profile", "full")),
            as_of_utc="2026-02-01T00:00:00+00:00",
        )

    monkeypatch.setattr(qmr, "get_run_snapshot", _snapshot)
    out = qmr.run_snapshot(run_id="run-1", model_name="lgbm_ranker", profile="core")
    assert out.snapshot_profile == "core"
    assert captured == ["core"]


def test_train_health_and_alias_endpoints_passthrough(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(qmr, "_SLOWAPI_LIMITER", None)
    monkeypatch.setattr(qmr, "_TRAIN_RATE_LIMIT_ITEM", None)
    monkeypatch.setattr(qmr, "_TRAIN_RATE_BUCKETS", {})
    monkeypatch.setattr(qmr, "submit_training", lambda request: {"status": "queued"})
    out = qmr.train(
        request=SimpleNamespace(),
        http_request=_dummy_request("1.1.1.1"),
    )
    assert out["status"] == "queued"

    monkeypatch.setattr(qmr, "get_dashboard_health", lambda **kwargs: {"status": "ok"})
    monkeypatch.setattr(qmr, "get_ops_status_response", lambda: {"status": "ok"})
    monkeypatch.setattr(qmr, "get_promoted_model_response", lambda **kwargs: {"model_name": "lgbm_ranker"})
    monkeypatch.setattr(qmr, "get_run_latest_risk", lambda **kwargs: {"status": "ok"})
    monkeypatch.setattr(qmr, "get_run_latest_exposures", lambda **kwargs: {"status": "ok"})
    monkeypatch.setattr(qmr, "get_run_latest_constraints", lambda **kwargs: {"status": "ok"})
    monkeypatch.setattr(qmr, "get_run_snapshot", lambda **kwargs: None)
    assert qmr.health()["status"] == "ok"
    bootstrap = qmr.dashboard_bootstrap()
    assert bootstrap.health.status == "ok"
    assert bootstrap.snapshot is None
    assert qmr.ops_status()["status"] == "ok"
    assert qmr.model_promoted()["model_name"] == "lgbm_ranker"
    assert qmr.run_latest_risk()["status"] == "ok"
    assert qmr.run_latest_exposures()["status"] == "ok"
    assert qmr.run_latest_constraints()["status"] == "ok"


def test_dashboard_bootstrap_profile_and_health_only_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        qmr,
        "get_dashboard_health",
        lambda **kwargs: {"status": "ok", "resolved_run_id": "run-1"},
    )
    qmr._DASHBOARD_BOOTSTRAP_CACHE.clear()
    captured_profiles: list[str] = []

    def _snapshot_ok(**kwargs):
        captured_profiles.append(str(kwargs.get("profile", "")))
        return DashboardSnapshotV2(
            run_id="run-1",
            model_name="lgbm_ranker",
            snapshot_profile=str(kwargs.get("profile", "full")),
            as_of_utc="2026-02-01T00:00:00+00:00",
        )

    monkeypatch.setattr(qmr, "run_snapshot", _snapshot_ok)
    payload = qmr.dashboard_bootstrap(
        run_id="run-1",
        model_name="lgbm_ranker",
        snapshot_profile="core",
    )
    assert payload.snapshot_profile == "core"
    assert payload.snapshot is not None
    assert payload.snapshot.snapshot_profile == "core"
    assert captured_profiles == ["core"]

    qmr._DASHBOARD_BOOTSTRAP_CACHE.clear()
    captured_profiles.clear()
    default_payload = qmr.dashboard_bootstrap(
        run_id="run-1",
        model_name="lgbm_ranker",
    )
    assert default_payload.snapshot_profile == "core"
    assert captured_profiles == ["core"]

    def _snapshot_not_found(**_kwargs):
        raise HTTPException(status_code=404, detail="not found")

    monkeypatch.setattr(qmr, "run_snapshot", _snapshot_not_found)
    qmr._DASHBOARD_BOOTSTRAP_CACHE.clear()
    fallback_payload = qmr.dashboard_bootstrap(
        run_id="run-1",
        model_name="lgbm_ranker",
        snapshot_profile="full",
    )
    assert fallback_payload.snapshot_profile == "full"
    assert fallback_payload.snapshot is None


def test_walkforward_status_and_stream_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(qmr, "get_walkforward_backtest_status", lambda job_id: SimpleNamespace(status="not_found", message="x"))
    with pytest.raises(HTTPException) as exc:
        qmr.backtest_walkforward_status("job-1")
    assert exc.value.status_code == 404

    monkeypatch.setattr(qmr, "get_run", lambda run_id: (_ for _ in ()).throw(ValueError("no run")))
    with pytest.raises(HTTPException) as exc2:
        asyncio.run(qmr.run_log_stream("run-1"))
    assert exc2.value.status_code == 404


def test_operational_endpoints_passthrough(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        qmr,
        "get_latest_data_quality_response",
        lambda **kwargs: {"run_id": kwargs.get("run_id"), "qc_status": "NORMAL"},
    )
    monkeypatch.setattr(
        qmr,
        "get_data_quality_history_response",
        lambda **kwargs: {"items": [{"qc_status": "WARNING"}], "limit": kwargs.get("limit")},
    )
    monkeypatch.setattr(
        qmr,
        "get_experiment_list_response",
        lambda **kwargs: {"items": [{"run_id": "run-1"}], "limit": kwargs.get("limit")},
    )
    monkeypatch.setattr(
        qmr,
        "get_experiment_detail_response",
        lambda run_id: {"run_id": run_id, "status": "completed"},
    )
    monkeypatch.setattr(
        qmr,
        "get_model_registry_entry_response",
        lambda alias, **kwargs: {"alias": alias, "run_id": kwargs.get("model_name") or "run-1"},
    )
    monkeypatch.setattr(
        qmr,
        "get_model_registry_history_response",
        lambda **kwargs: {"items": [{"alias": "champion"}], "limit": kwargs.get("limit")},
    )
    monkeypatch.setattr(
        qmr,
        "get_reports_latest_response",
        lambda **kwargs: {"item": {"report_type": kwargs.get("report_type") or "data_quality"}},
    )
    monkeypatch.setattr(
        qmr,
        "get_reports_history_response",
        lambda **kwargs: {"items": [{"report_type": "data_quality"}], "limit": kwargs.get("limit")},
    )
    monkeypatch.setattr(
        qmr,
        "get_notifications_history_response",
        lambda **kwargs: {"items": [{"status": "sent"}], "limit": kwargs.get("limit")},
    )
    monkeypatch.setattr(
        qmr,
        "get_scheduler_status_response",
        lambda: {"enabled": True, "run_phase": "post_close"},
    )
    invalidated: list[bool] = []
    monkeypatch.setattr(
        qmr,
        "get_execution_mode_response",
        lambda run_id, model_name: {"run_id": run_id, "mode": "paper", "model_name": model_name},
    )
    monkeypatch.setattr(
        qmr,
        "set_execution_mode",
        lambda request: {"run_id": request.run_id, "mode": request.mode},
    )
    monkeypatch.setattr(qmr, "_invalidate_read_caches", lambda: invalidated.append(True))

    assert qmr.data_quality_latest(run_id="run-1")["qc_status"] == "NORMAL"
    assert qmr.data_quality_history(run_id="run-1", limit=5)["items"][0]["qc_status"] == "WARNING"
    assert qmr.experiments_list(limit=5)["items"][0]["run_id"] == "run-1"
    assert qmr.experiment_get("run-1")["status"] == "completed"
    assert qmr.model_registry_champion(model_name="lgbm_ranker")["alias"] == "champion"
    assert qmr.model_registry_challenger(model_name="lgbm_ranker")["alias"] == "challenger"
    assert qmr.model_registry_history(model_name="lgbm_ranker", limit=5)["items"][0]["alias"] == "champion"
    assert qmr.reports_latest(run_id="run-1", report_type="data_quality")["item"]["report_type"] == "data_quality"
    assert qmr.reports_history(run_id="run-1", report_type="data_quality", limit=5)["items"][0]["report_type"] == "data_quality"
    assert qmr.notifications_history(limit=5)["items"][0]["status"] == "sent"
    assert qmr.scheduler_status()["enabled"] is True
    assert qmr.execution_mode(run_id="run-1", model_name="lgbm_ranker")["mode"] == "paper"

    update_response = qmr.execution_mode_update(
        SimpleNamespace(run_id="run-1", model_name="lgbm_ranker", mode="shadow_live")
    )
    assert update_response["mode"] == "shadow_live"
    assert invalidated == [True]


def test_execution_mode_http_routes_use_distinct_update_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        qmr,
        "get_execution_mode_response",
        lambda run_id, model_name: {
            "run_id": run_id,
            "model_name": model_name,
            "mode": "paper",
            "live_adapter_enabled": False,
            "broker_ready": False,
            "kill_switch": False,
        },
    )
    monkeypatch.setattr(
        qmr,
        "set_execution_mode",
        lambda request: {
            "run_id": request.run_id,
            "model_name": request.model_name,
            "mode": request.mode,
            "live_adapter_enabled": False,
            "broker_ready": False,
            "kill_switch": False,
        },
    )
    monkeypatch.setattr(qmr, "_invalidate_read_caches", lambda: None)

    api_router = Router(prefix="/api/v1/quant_ml")
    api_router.include_router(qmr.router)
    app = FastAPI()
    app.include_router(api_router._api_router)
    client = TestClient(app)

    get_response = client.get(
        "/api/v1/quant_ml/execution/mode",
        params={"run_id": "run-1", "model_name": "lgbm_ranker"},
    )
    assert get_response.status_code == 200
    assert get_response.json()["mode"] == "paper"

    post_response = client.post(
        "/api/v1/quant_ml/execution/mode/update",
        json={
            "run_id": "run-1",
            "model_name": "lgbm_ranker",
            "mode": "shadow_live",
        },
    )
    assert post_response.status_code == 200
    assert post_response.json()["mode"] == "shadow_live"
