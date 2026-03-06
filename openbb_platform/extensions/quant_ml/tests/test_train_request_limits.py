"""Tests for training request guardrails."""

from __future__ import annotations

from datetime import date

import pytest
from openbb_quant_ml.models import DateRange, TrainRequest


def _base_request(symbols: list[str]) -> TrainRequest:
    return TrainRequest(
        symbols=symbols,
        date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 12, 31)),
        horizon_days=1,
    )


def test_train_request_accepts_symbol_limit_boundary() -> None:
    payload = _base_request([f"S{i}" for i in range(5000)])
    assert payload.symbols is not None
    assert len(payload.symbols) == 5000


def test_train_request_rejects_symbol_limit_overflow() -> None:
    with pytest.raises(ValueError, match="Maximum 5000 symbols"):
        _base_request([f"S{i}" for i in range(5001)])


def test_train_request_maps_legacy_hpo_fields() -> None:
    payload = TrainRequest(
        symbols=["AAPL", "MSFT"],
        date_range=DateRange(start=date(2024, 1, 1), end=date(2024, 12, 31)),
        horizon_days=1,
        enable_hpo=True,
        hpo_n_trials=33,
    )
    assert payload.hpo_config.enabled is True
    assert payload.hpo_config.n_trials == 33
