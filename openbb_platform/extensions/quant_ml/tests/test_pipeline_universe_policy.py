"""Pipeline universe resolution policy tests."""

from __future__ import annotations

import pytest

from openbb_quant_ml.models import TrainRequest
from openbb_quant_ml.service import pipeline


def _build_request(**overrides) -> TrainRequest:
    payload = {
        "date_range": {"start": "2024-01-01", "end": "2024-02-01"},
        "horizon_days": 1,
    }
    payload.update(overrides)
    return TrainRequest(**payload)


def test_unknown_universe_id_raises_value_error(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(pipeline, "get_symbols_for_universe", lambda universe_id: [])
    monkeypatch.setattr(pipeline, "list_universe_ids", lambda: ["default", "sp500"])

    request = _build_request(universe_id="does_not_exist")
    with pytest.raises(ValueError, match="invalid_or_empty_universe_id"):
        pipeline._resolve_symbols_for_training_request(request)


def test_empty_universe_id_raises_value_error(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(pipeline, "list_universe_ids", lambda: ["default", "sp500"])

    request = _build_request(universe_id="   ")
    with pytest.raises(ValueError, match="invalid_or_empty_universe_id"):
        pipeline._resolve_symbols_for_training_request(request)


def test_symbols_override_universe_id_policy():
    request = _build_request(symbols=["AAPL", "MSFT"], universe_id="   ")
    symbols = pipeline._resolve_symbols_for_training_request(request)
    assert symbols == ["AAPL", "MSFT"]


def test_undersized_universe_id_raises_value_error(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(pipeline, "get_symbols_for_universe", lambda universe_id: ["AAPL", "MSFT"])
    monkeypatch.setattr(pipeline, "list_universe_ids", lambda: ["default", "sp500"])
    monkeypatch.setattr(pipeline, "get_universe_size_status", lambda universe_id, symbols: (2, 450, False))

    request = _build_request(universe_id="sp500")
    with pytest.raises(ValueError, match="invalid_or_undersized_universe_id"):
        pipeline._resolve_symbols_for_training_request(request)
