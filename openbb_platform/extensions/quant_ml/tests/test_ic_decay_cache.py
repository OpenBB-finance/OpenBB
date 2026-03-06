"""Tests for /model/ic_decay router-level cache behavior."""

from __future__ import annotations

from openbb_quant_ml import quant_ml_router as qmr


def test_model_ic_decay_endpoint_uses_ttl_cache(monkeypatch) -> None:
    qmr._MODEL_IC_DECAY_CACHE.clear()
    call_count = {"value": 0}

    def _stub(**kwargs):
        call_count["value"] += 1
        return {
            "run_id": kwargs.get("run_id"),
            "model_name": kwargs.get("model_name", "lgbm_ranker"),
            "status": "ok",
            "max_horizon": kwargs.get("max_horizon", 20),
            "ic_decay": [{"horizon": 1, "ic": 0.1}],
            "ic_t_stat": 1.0,
        }

    monkeypatch.setattr(qmr, "get_model_ic_decay", _stub)

    first = qmr.model_ic_decay(run_id="run-1", model_name="lgbm_ranker", max_horizon=20)
    second = qmr.model_ic_decay(run_id="run-1", model_name="lgbm_ranker", max_horizon=20)
    assert first["status"] == "ok"
    assert second["status"] == "ok"
    assert call_count["value"] == 1
