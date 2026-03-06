"""Market-data update step window selection tests."""

from __future__ import annotations

from datetime import date

import pytest
from openbb_quant_ml.jobs.steps import update_market_data as step


class _FrozenDate(date):
    @classmethod
    def today(cls) -> _FrozenDate:
        return cls(2026, 2, 22)


def test_update_market_data_uses_delta_window_for_infer_only(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(step, "date", _FrozenDate)
    monkeypatch.setattr(
        step,
        "get_symbols_for_universe",
        lambda universe_id: ["AAPL", "MSFT"],
    )
    captured: dict[str, object] = {}

    def _load_market_data(
        symbols,  # noqa: ANN001
        start_date,  # noqa: ANN001
        end_date,  # noqa: ANN001
        progress_callback=None,  # noqa: ANN001
        timeout_sec=20,  # noqa: ANN001
        retry=2,  # noqa: ANN001
        backoff_base=2.0,  # noqa: ANN001
        max_workers=6,  # noqa: ANN001
    ):
        captured["start_date"] = start_date
        captured["end_date"] = end_date
        captured["workers"] = max_workers
        return {symbol: object() for symbol in symbols}, []

    monkeypatch.setattr(step, "load_market_data", _load_market_data)

    payload = step.run(
        {
            "universe_id": "all_in_one",
            "predict_mode": "infer_only",
            "market_update_delta_days": 60,
            "market_data_workers": 10,
        }
    )

    assert payload["symbols_requested"] == 2
    assert payload["market_data_workers"] == 10
    assert payload["market_update_delta_days"] == 60
    assert captured["workers"] == 10
    assert captured["end_date"] == _FrozenDate(2026, 2, 22)
    assert (captured["end_date"] - captured["start_date"]).days == 60


def test_update_market_data_uses_lookback_when_delta_not_set(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(step, "date", _FrozenDate)
    monkeypatch.setattr(step, "get_symbols_for_universe", lambda universe_id: ["AAPL"])
    captured: dict[str, object] = {}

    def _load_market_data(
        symbols,  # noqa: ANN001
        start_date,  # noqa: ANN001
        end_date,  # noqa: ANN001
        progress_callback=None,  # noqa: ANN001
        timeout_sec=20,  # noqa: ANN001
        retry=2,  # noqa: ANN001
        backoff_base=2.0,  # noqa: ANN001
        max_workers=6,  # noqa: ANN001
    ):
        captured["start_date"] = start_date
        captured["end_date"] = end_date
        return {"AAPL": object()}, []

    monkeypatch.setattr(step, "load_market_data", _load_market_data)

    payload = step.run(
        {
            "universe_id": "all_in_one",
            "lookback_years": 5,
            "market_data_workers": 10,
        }
    )

    assert payload["market_update_delta_days"] is None
    assert payload["lookback_years"] == 5
    assert (captured["end_date"] - captured["start_date"]).days == 365 * 5
