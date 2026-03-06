"""Additional coverage tests for macro service orchestration."""

from __future__ import annotations

import pandas as pd
import pytest
from openbb_quant_ml.macro_models import MacroExpressionRequest, MacroUpdateRequest
from openbb_quant_ml.service import macro_service as ms


def test_catalog_search_register_and_multi(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ms, "search_catalog", lambda **kwargs: [{"id": "FRED:UNRATE", "series_id": "UNRATE", "source": "FRED", "default_transform": "level", "publish_lag": 30, "active": True}])
    payload = ms.search_catalog_response("unemployment")
    assert payload.status == "ok"
    assert payload.items[0].id == "FRED:UNRATE"

    monkeypatch.setattr(ms, "search_catalog", lambda **kwargs: (_ for _ in ()).throw(RuntimeError("search failed")))
    payload2 = ms.search_catalog_response("x")
    assert payload2.status == "insufficient_data"

    monkeypatch.setattr(ms, "register_series", lambda **kwargs: {"id": "FRED:CPIAUCSL", "series_id": "CPIAUCSL", "source": "FRED", "default_transform": "level", "publish_lag": 30, "active": True})
    reg = ms.register_catalog_response("cpiaucsl")
    assert reg.status == "ok"
    monkeypatch.setattr(ms, "register_series", lambda **kwargs: (_ for _ in ()).throw(ValueError("register failed")))
    reg2 = ms.register_catalog_response("cpiaucsl")
    assert reg2.status == "insufficient_data"

    ok_series = ms.MacroSeriesResponse(
        meta={"key": "A", "source": "stub", "transform": "level"},
        data=[],
        stats={},
        status="ok",
    )
    bad_series = ms.MacroSeriesResponse(
        meta={"key": "B", "source": "stub", "transform": "level"},
        data=[],
        stats={},
        status="insufficient_data",
        message="bad",
    )
    monkeypatch.setattr(ms, "get_series_response", lambda q: ok_series if q.key == "A" else bad_series)
    multi = ms.get_series_multi_response(["A", "B"])
    assert multi.status == "insufficient_data"
    assert "B: bad" in str(multi.message)


def test_expression_error_and_generic_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ms, "evaluate_expression", lambda expr, resolver: (_ for _ in ()).throw(ms.MacroExpressionError("bad expr")))
    out = ms.evaluate_expression_response(MacroExpressionRequest(expr="x", transform="level", freq="D", fill="ffill"))
    assert out.status == "error"

    monkeypatch.setattr(ms, "evaluate_expression", lambda expr, resolver: (_ for _ in ()).throw(RuntimeError("boom")))
    out2 = ms.evaluate_expression_response(MacroExpressionRequest(expr="x", transform="level", freq="D", fill="ffill"))
    assert out2.status == "insufficient_data"


def test_regime_and_alert_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    idx = pd.date_range("2026-01-01", periods=4, freq="W")
    frame = pd.DataFrame(
        {
            "risk_on_score": [70, 65, 60, 55],
            "inflation_score": [40, 45, 50, 55],
            "growth_score": [65, 60, 55, 50],
            "liquidity_score": [60, 60, 55, 50],
            "credit_stress_score": [30, 35, 40, 45],
        },
        index=idx,
    )

    monkeypatch.setattr(ms, "compute_regime_scores", lambda **kwargs: frame)
    reg = ms.get_regime_response(freq="W")
    assert reg.status == "ok"
    assert reg.latest is not None

    monkeypatch.setattr(ms, "compute_regime_scores", lambda **kwargs: pd.DataFrame())
    reg_empty = ms.get_regime_response(freq="W")
    assert reg_empty.status == "insufficient_data"

    monkeypatch.setattr(ms, "get_regime_response", lambda **kwargs: reg)
    state = ms.get_regime_state_response()
    assert state.status == "ok"

    monkeypatch.setattr(ms, "_resolver_factory", lambda *args, **kwargs: (lambda key: pd.Series(dtype=float)))
    monkeypatch.setattr(ms, "evaluate_alerts", lambda frame, resolver: [{"rule_id": "r1", "severity": "warning", "message": "m", "triggered_at": "2026-01-01T00:00:00Z", "value": 1.0, "threshold": 0.5}])
    monkeypatch.setattr(ms, "persist_and_get_alerts", lambda current, history_limit=200: (current, current))
    alerts = ms.get_alerts_response()
    assert alerts.status == "ok"
    assert alerts.current

    monkeypatch.setattr(ms, "get_regime_response", lambda **kwargs: ms.MacroRegimeResponse(status="insufficient_data", message="none", data=[], latest=None))
    monkeypatch.setattr(ms, "list_alert_events", lambda limit=200: [])
    alerts_empty = ms.get_alerts_response()
    assert alerts_empty.status == "insufficient_data"


def test_transition_hmm_scheduler_update_and_health(monkeypatch: pytest.MonkeyPatch) -> None:
    regime = ms.MacroRegimeResponse(
        status="ok",
        data=[
            ms.MacroRegimePoint(
                date="2026-01-01",
                risk_on_score=70,
                inflation_score=40,
                growth_score=65,
                liquidity_score=55,
                credit_stress_score=30,
            ),
            ms.MacroRegimePoint(
                date="2026-01-08",
                risk_on_score=45,
                inflation_score=75,
                growth_score=35,
                liquidity_score=35,
                credit_stress_score=65,
            ),
        ],
        latest=None,
    )
    monkeypatch.setattr(ms, "get_regime_response", lambda **kwargs: regime)
    monkeypatch.setattr(
        ms,
        "detect_regime_transitions",
        lambda frame, threshold=10.0: pd.DataFrame(
            [
                {
                    "date": "2026-01-08",
                    "axis": "risk_on_score",
                    "from_score": 70.0,
                    "to_score": 45.0,
                    "delta": -25.0,
                    "direction": "falling",
                    "severity": "major",
                }
            ]
        ),
    )
    monkeypatch.setattr(ms, "classify_regime_label", lambda row: "Transitional")
    transitions = ms.get_regime_transitions_response()
    assert transitions.status == "ok"
    assert transitions.transitions

    monkeypatch.setattr(
        ms,
        "fit_hmm_regime",
        lambda score_frame, n_states=4: {
            "index": pd.to_datetime(["2026-01-01", "2026-01-08"]),
            "states": [0, 1],
            "probabilities": [[0.8, 0.2], [0.1, 0.9]],
            "state_meta": {0: {"label": "Risk-On / Bull", "means": {"risk_on_score": 70.0}}, 1: {"label": "Risk-Off / Crisis", "means": {"risk_on_score": 30.0}}},
        },
    )
    hmm = ms.get_hmm_regime_response()
    assert hmm.status == "ok"
    assert len(hmm.states) == 2

    monkeypatch.setattr(ms, "fit_hmm_regime", lambda score_frame, n_states=4: None)
    hmm_empty = ms.get_hmm_regime_response()
    assert hmm_empty.status == "insufficient_data"

    monkeypatch.setattr(ms, "ensure_scheduler_started", lambda: None)
    monkeypatch.setattr(
        ms,
        "get_scheduler_status",
        lambda: {
            "running": True,
            "last_market_refresh": "2026-02-28T00:00:00Z",
            "last_fred_update": None,
            "next_market_refresh": None,
            "next_fred_update": None,
        },
    )
    sch = ms.get_regime_scheduler_status_response()
    assert sch.running is True
    monkeypatch.setattr(ms, "trigger_regime_refresh", lambda: {"status": "ok"})
    assert ms.trigger_regime_refresh_response()["status"] == "ok"

    monkeypatch.setattr(ms, "update_all_defaults", lambda **kwargs: ["UNRATE"])
    ok_update = ms.trigger_update_response(MacroUpdateRequest(all_default=True))
    assert ok_update.status == "ok"
    monkeypatch.setattr(ms, "update_all_defaults", lambda **kwargs: [])
    empty_update = ms.trigger_update_response(MacroUpdateRequest(all_default=True))
    assert empty_update.status == "insufficient_data"
    monkeypatch.setattr(ms, "update_all_defaults", lambda **kwargs: (_ for _ in ()).throw(RuntimeError("update failed")))
    err_update = ms.trigger_update_response(MacroUpdateRequest(all_default=True))
    assert err_update.status == "error"

    monkeypatch.setattr(ms, "FredClient", lambda: type("C", (), {"has_api_key": False})())
    monkeypatch.setattr(ms, "get_macro_obs_health_stats", lambda: {"total_series_with_obs": 0, "last_obs_date_global": None})
    monkeypatch.setattr(ms, "get_macro_feature_health_stats", lambda top_n=12: {"total_feature_rows": 0, "last_feature_date": None, "top_coverage": []})
    health = ms.get_health_response()
    assert health.status == "insufficient_data"


def test_market_expression_wrappers_and_bootstrap_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        ms,
        "evaluate_expression_response",
        lambda request: ms.MacroExpressionResponse(
            meta={"key": request.expr, "source": "expression", "transform": request.transform},
            data=[],
            stats={},
            status="ok",
            dependencies=[],
        ),
    )
    ratio = ms.get_market_ratio_response("SPY", "QQQ")
    corr = ms.get_market_rolling_corr_response("SPY", "QQQ", window=90)
    assert ratio.meta.title == "SPY/QQQ"
    assert "rolling_corr" in str(corr.meta.title)

    ms._DERIVED_BOOTSTRAPPED = False
    monkeypatch.setattr(
        ms,
        "load_macro_config",
        lambda: {
            "derived_defaults": [
                {"derived_id": "cg", "expression": "HG/GC", "default_transform": "level"},
                {"derived_id": "", "expression": ""},
            ]
        },
    )
    monkeypatch.setattr(ms, "_resolver_factory", lambda *args, **kwargs: (lambda key: pd.Series(dtype=float)))
    monkeypatch.setattr(ms, "evaluate_expression", lambda expr, resolver: type("Eval", (), {"dependencies": ["HG", "GC"]})())
    saved: list[dict[str, object]] = []
    monkeypatch.setattr(
        ms,
        "save_derived_expression",
        lambda **kwargs: saved.append(kwargs),
    )
    ms.bootstrap_default_derived_expressions()
    assert saved
    # second call should be no-op due bootstrap guard
    ms.bootstrap_default_derived_expressions()
    assert len(saved) == 1
