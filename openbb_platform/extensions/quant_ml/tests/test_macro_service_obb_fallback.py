"""Macro service FRED cache fallback tests."""

from __future__ import annotations

from datetime import date

import pytest
from openbb_quant_ml.service import macro_service as ms


def test_load_fred_series_uses_cache_when_update_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ms, "resolve_catalog_item", lambda *args, **kwargs: {"series_id": "UNRATE", "frequency": "M"})
    monkeypatch.setattr(ms, "update_series_ids", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        ms,
        "load_observations",
        lambda *args, **kwargs: [
            {"date": "2024-01-31", "value": 3.9},
            {"date": "2024-02-29", "value": 4.0},
        ],
    )

    series, meta, warning = ms._load_fred_series("UNRATE", start=date(2024, 1, 1), end=date(2024, 2, 29))
    assert not series.empty
    assert meta["source"] == "FRED"
    assert warning == "fred_cache_fallback"


def test_load_fred_series_raises_when_no_observations(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(ms, "resolve_catalog_item", lambda *args, **kwargs: {"series_id": "UNRATE", "frequency": "M"})
    monkeypatch.setattr(ms, "update_series_ids", lambda *args, **kwargs: [])
    monkeypatch.setattr(ms, "load_observations", lambda *args, **kwargs: [])

    with pytest.raises(ValueError):
        ms._load_fred_series("UNRATE", start=None, end=None)
