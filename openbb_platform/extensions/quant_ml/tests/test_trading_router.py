"""Trading router endpoint coverage."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.testclient import TestClient
from openbb_core.app.router import Router
from openbb_quant_ml import quant_ml_router as qmr


def test_trading_endpoints_passthrough(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(qmr, "get_trading_status_payload", lambda: {"mode": "paper", "runtime_status": "running"})
    monkeypatch.setattr(qmr, "get_trading_settings_payload", lambda: {"version": "v1", "built_in_strategies": [], "custom_algorithm_records": []})
    monkeypatch.setattr(qmr, "update_trading_settings_payload", lambda payload: {**payload, "version": "v1", "built_in_strategies": [], "custom_algorithm_records": []})
    monkeypatch.setattr(qmr, "run_trading_cycle", lambda auto_execute=None: {"cycle_id": "c1", "status": "completed"})
    monkeypatch.setattr(qmr, "get_trading_latest_scan_payload", lambda limit=200: {"items": [], "signal_count": 0})
    monkeypatch.setattr(qmr, "get_trading_scan_history_payload", lambda limit=250: {"items": []})
    monkeypatch.setattr(qmr, "get_trading_symbol_detail_payload", lambda ticker: {"ticker": ticker, "series": [], "signals": [], "orders": [], "position": None})
    monkeypatch.setattr(qmr, "get_trading_orders_payload", lambda limit=250: {"items": []})
    monkeypatch.setattr(qmr, "get_trading_fills_payload", lambda limit=250: {"items": []})
    monkeypatch.setattr(qmr, "get_trading_positions_payload", lambda: {"items": [], "mode": "paper"})
    monkeypatch.setattr(qmr, "get_trading_performance_payload", lambda: {"equity": 100.0})
    monkeypatch.setattr(qmr, "get_trading_risk_payload", lambda: {"limits": {}, "events": []})
    monkeypatch.setattr(qmr, "get_trading_events_payload", lambda limit=250: {"items": []})
    monkeypatch.setattr(qmr, "get_trading_algorithms_payload", lambda: {"items": []})
    monkeypatch.setattr(qmr, "toggle_trading_algorithm_payload", lambda **kwargs: {"items": [{"name": kwargs["name"], "version": "0.1.0"}]})
    monkeypatch.setattr(qmr, "validate_trading_algorithm_payload", lambda name, version=None: {"name": name, "version": version or "0.1.0", "status": "passed", "passed": True})
    monkeypatch.setattr(qmr, "get_trading_execution_mode_payload", lambda: {"mode": "paper"})
    monkeypatch.setattr(qmr, "set_trading_execution_mode_payload", lambda mode: {"mode": mode})
    monkeypatch.setattr(qmr, "approve_trading_order_payload", lambda order_id: {"order_id": order_id, "ticker": "AAA", "strategy_name": "ema_cross", "side": "buy"})
    monkeypatch.setattr(qmr, "cancel_trading_order_payload", lambda order_id: {"order_id": order_id, "ticker": "AAA", "strategy_name": "ema_cross", "side": "buy"})
    monkeypatch.setattr(qmr, "close_trading_position_payload", lambda ticker: {"order_id": "ord-1", "ticker": ticker, "strategy_name": "ema_cross", "side": "sell"})

    assert qmr.trading_status().mode == "paper"
    assert qmr.trading_settings().version == "v1"
    assert qmr.trading_settings_update(SimpleNamespace(model_dump=lambda exclude_none=True: {})).version == "v1"
    assert qmr.trading_cycle_run(SimpleNamespace(auto_execute=False)).status == "completed"
    assert qmr.trading_scan_latest().signal_count == 0
    assert qmr.trading_scan_history().items == []
    assert qmr.trading_symbol_detail("AAA").ticker == "AAA"
    assert qmr.trading_orders().items == []
    assert qmr.trading_fills().items == []
    assert qmr.trading_positions().mode == "paper"
    assert qmr.trading_performance().equity == 100.0
    assert qmr.trading_risk().events == []
    assert qmr.trading_events().items == []
    assert qmr.trading_algorithms().items == []
    assert qmr.trading_algorithms_toggle(SimpleNamespace(name="algo", version=None, active=True, sandbox_mode=None, signal_only=None, status=None)).items[0].name == "algo"
    assert qmr.trading_algorithms_validate(SimpleNamespace(name="algo", version=None)).passed is True
    assert qmr.trading_execution_mode().mode == "paper"
    assert qmr.trading_execution_mode_update(SimpleNamespace(mode="shadow_live")).mode == "shadow_live"
    assert qmr.trading_order_approve("ord-1").order_id == "ord-1"
    assert qmr.trading_order_cancel("ord-1").order_id == "ord-1"
    assert qmr.trading_position_close("AAA").ticker == "AAA"


def test_trading_router_maps_value_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(qmr, "get_trading_symbol_detail_payload", lambda ticker: (_ for _ in ()).throw(ValueError("missing")))
    monkeypatch.setattr(qmr, "approve_trading_order_payload", lambda order_id: (_ for _ in ()).throw(ValueError("missing")))
    monkeypatch.setattr(qmr, "cancel_trading_order_payload", lambda order_id: (_ for _ in ()).throw(ValueError("missing")))
    monkeypatch.setattr(qmr, "close_trading_position_payload", lambda ticker: (_ for _ in ()).throw(ValueError("missing")))
    monkeypatch.setattr(qmr, "validate_trading_algorithm_payload", lambda name, version=None: (_ for _ in ()).throw(ValueError("missing")))
    monkeypatch.setattr(qmr, "run_trading_cycle", lambda auto_execute=None: (_ for _ in ()).throw(ValueError("bad")))

    with pytest.raises(HTTPException):
        qmr.trading_symbol_detail("AAA")
    with pytest.raises(HTTPException):
        qmr.trading_order_approve("ord-1")
    with pytest.raises(HTTPException):
        qmr.trading_order_cancel("ord-1")
    with pytest.raises(HTTPException):
        qmr.trading_position_close("AAA")
    with pytest.raises(HTTPException):
        qmr.trading_algorithms_validate(SimpleNamespace(name="algo", version=None))
    with pytest.raises(HTTPException):
        qmr.trading_cycle_run(SimpleNamespace(auto_execute=True))


def test_trading_http_routes_separate_get_and_post_paths(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        qmr,
        "get_trading_settings_payload",
        lambda: {
            "version": "v1",
            "tab_name": "Trading",
            "mode": "paper",
            "runtime_status": "running",
            "universe_id": "default",
            "schedule": {},
            "scan": {},
            "execution": {"mode": "paper"},
            "account": {},
            "risk": {},
            "strategies": {},
            "custom_algorithms": {},
            "ui": {},
            "built_in_strategies": [],
            "custom_algorithm_records": [],
        },
    )
    monkeypatch.setattr(
        qmr,
        "update_trading_settings_payload",
        lambda payload: {
            "version": "v1",
            "tab_name": "Trading",
            "mode": "paper",
            "runtime_status": "running",
            "universe_id": "default",
            "schedule": {},
            "scan": payload.get("scan", {}),
            "execution": payload.get("execution", {"mode": "paper"}),
            "account": {},
            "risk": {},
            "strategies": {},
            "custom_algorithms": {},
            "ui": {},
            "built_in_strategies": [],
            "custom_algorithm_records": [],
        },
    )
    monkeypatch.setattr(
        qmr,
        "get_trading_execution_mode_payload",
        lambda: {
            "mode": "paper",
            "live_adapter_enabled": False,
            "broker_ready": False,
            "kill_switch": False,
        },
    )
    monkeypatch.setattr(
        qmr,
        "set_trading_execution_mode_payload",
        lambda mode: {
            "mode": mode,
            "live_adapter_enabled": False,
            "broker_ready": False,
            "kill_switch": False,
        },
    )

    api_router = Router(prefix="/api/v1/quant_ml")
    api_router.include_router(qmr.router)
    app = FastAPI()
    app.include_router(api_router._api_router)
    client = TestClient(app)

    settings_get = client.get("/api/v1/quant_ml/trading/settings")
    assert settings_get.status_code == 200
    assert settings_get.json()["tab_name"] == "Trading"

    settings_post = client.post(
        "/api/v1/quant_ml/trading/settings/update",
        json={"scan": {"lookback_days": 252}},
    )
    assert settings_post.status_code == 200
    assert settings_post.json()["scan"]["lookback_days"] == 252

    mode_get = client.get("/api/v1/quant_ml/trading/execution/mode")
    assert mode_get.status_code == 200
    assert mode_get.json()["mode"] == "paper"

    mode_post = client.post(
        "/api/v1/quant_ml/trading/execution/mode/update",
        json={"mode": "shadow_live"},
    )
    assert mode_post.status_code == 200
    assert mode_post.json()["mode"] == "shadow_live"
