"""Router error handling and rate-limit tests."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from openbb_quant_ml import quant_ml_router as qmr


def _dummy_request(ip: str = "127.0.0.1"):
    return SimpleNamespace(client=SimpleNamespace(host=ip))


def test_run_latest_meta_maps_value_error_to_404(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise(*args, **kwargs):  # noqa: ANN002, ANN003
        raise ValueError("not found")

    monkeypatch.setattr(qmr, "get_run_latest_meta", _raise)
    with pytest.raises(HTTPException) as exc_info:
        qmr.run_latest_meta(run_id="unknown", model_name="lgbm_ranker")
    assert exc_info.value.status_code == 404


def test_run_backtest_result_maps_value_error_to_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _raise(*args, **kwargs):  # noqa: ANN002, ANN003
        raise ValueError("not found")

    monkeypatch.setattr(qmr, "get_backtest_result", _raise)
    with pytest.raises(HTTPException) as exc_info:
        qmr.run_backtest_result(run_id="unknown", model_name="lgbm_ranker")
    assert exc_info.value.status_code == 404


def test_train_rate_limit_is_enforced(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(qmr, "_SLOWAPI_LIMITER", None)
    monkeypatch.setattr(qmr, "_TRAIN_RATE_LIMIT_ITEM", None)
    monkeypatch.setattr(qmr, "_TRAIN_RATE_BUCKETS", {})
    monkeypatch.setattr(qmr, "_TRAIN_RATE_LIMIT_MAX_REQUESTS", 2)
    monkeypatch.setattr(qmr, "_TRAIN_RATE_LIMIT_WINDOW_SEC", 60.0)
    ticks = iter([0.0, 1.0, 2.0])
    monkeypatch.setattr(qmr, "_now_monotonic", lambda: next(ticks))

    req = _dummy_request()
    qmr._enforce_train_rate_limit(req)
    qmr._enforce_train_rate_limit(req)
    with pytest.raises(HTTPException) as exc_info:
        qmr._enforce_train_rate_limit(req)
    assert exc_info.value.status_code == 429
