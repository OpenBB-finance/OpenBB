"""Additional coverage tests for macro update workflow."""

from __future__ import annotations

import types
from datetime import date

import pandas as pd
import pytest
from openbb_quant_ml.service import macro_update as mu
from openbb_quant_ml.service.macro_fred_client import FredApiKeyMissingError, FredClientError


def test_normalize_series_ids_and_effective_window(monkeypatch: pytest.MonkeyPatch) -> None:
    out = mu._normalize_series_ids([" fred:unrate ", "UNRATE", "", "cpiaucsl"])
    assert out == ["UNRATE", "CPIAUCSL"]

    monkeypatch.setattr(mu, "get_obs_date_bounds", lambda source, sid: (None, "2026-01-31"))
    start, end = mu._effective_window("UNRATE", None, date(2026, 2, 15), stale_refresh_days=30)
    assert start == date(2026, 1, 1)
    assert end == date(2026, 2, 15)

    monkeypatch.setattr(mu, "get_obs_date_bounds", lambda source, sid: (None, "invalid"))
    start2, end2 = mu._effective_window("UNRATE", date(2026, 1, 1), None, stale_refresh_days=20)
    assert start2 == date(2026, 1, 1)
    assert end2 == date.today()


def test_extract_and_normalize_openbb_rows() -> None:
    frame = pd.DataFrame(
        [
            {"date": "2026-01-01", "close": "10.0"},
            {"date": "2026-01-02", "close": "10.5"},
        ]
    )
    rows = mu._normalize_openbb_fred_rows(frame)
    assert len(rows) == 2
    assert rows[0]["date"] == "2026-01-01"
    assert rows[0]["value"] == 10.0

    class _Dummy:
        def to_df(self):
            return frame

    extracted = mu._extract_result_frame(_Dummy())
    assert isinstance(extracted, pd.DataFrame)
    assert len(extracted) == 2


def test_fetch_openbb_fred_observations(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Economy:
        @staticmethod
        def fred_series(**kwargs):  # noqa: ANN003
            return pd.DataFrame(
                [{"date": "2026-01-01", "value": 1.0}, {"date": "2026-01-02", "value": 1.1}]
            )

    monkeypatch.setitem(
        __import__("sys").modules,
        "openbb",
        types.SimpleNamespace(obb=types.SimpleNamespace(economy=_Economy())),
    )
    rows = mu._fetch_openbb_fred_observations("UNRATE")
    assert len(rows) == 2


def test_update_series_ids_with_openbb_and_fred_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mu, "load_macro_config", lambda: {"defaults": {"stale_refresh_days": 30}})
    monkeypatch.setattr(mu, "resolve_catalog_item", lambda sid, create_if_missing=True: {"id": sid})
    monkeypatch.setattr(mu, "_effective_window", lambda sid, start, end, stale: (start, end))

    # OpenBB path for first series, FredClient fallback for second series.
    def _fetch_openbb(series_id: str, start=None, end=None):  # noqa: ANN001
        if series_id == "UNRATE":
            return [{"date": "2026-01-01", "value": 4.1}]
        return []

    monkeypatch.setattr(mu, "_fetch_openbb_fred_observations", _fetch_openbb)
    upserts: list[tuple[str, list[dict[str, object]]]] = []
    monkeypatch.setattr(mu, "upsert_observations", lambda source, sid, rows: upserts.append((sid, rows)))

    class _Client:
        def get_series_observations(self, sid: str, start=None, end=None):  # noqa: ANN001
            return [{"date": "2026-01-02", "value": 2.0}]

    monkeypatch.setattr(mu, "FredClient", _Client)
    feature_calls: list[dict[str, object]] = []
    monkeypatch.setattr(
        mu,
        "update_macro_features_for_series",
        lambda ids, start=None, end=None: feature_calls.append({"ids": ids, "start": start, "end": end}),
    )

    updated = mu.update_series_ids(
        ["UNRATE", "CPIAUCSL"],
        start=date(2026, 1, 1),
        end=date(2026, 1, 31),
        compute_features=True,
        features_lookback_days=45,
    )
    assert updated == ["UNRATE", "CPIAUCSL"]
    assert len(upserts) == 2
    assert feature_calls


def test_update_series_ids_handles_client_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mu, "load_macro_config", lambda: {"defaults": {"stale_refresh_days": 30}})
    monkeypatch.setattr(mu, "resolve_catalog_item", lambda sid, create_if_missing=True: {"id": sid})
    monkeypatch.setattr(mu, "_effective_window", lambda sid, start, end, stale: (start, end))
    monkeypatch.setattr(mu, "_fetch_openbb_fred_observations", lambda *args, **kwargs: [])
    monkeypatch.setattr(mu, "upsert_observations", lambda *args, **kwargs: None)

    class _MissingClient:
        def get_series_observations(self, sid: str, start=None, end=None):  # noqa: ANN001
            raise FredApiKeyMissingError("missing key")

    monkeypatch.setattr(mu, "FredClient", _MissingClient)
    updated = mu.update_series_ids(["UNRATE"], compute_features=False)
    assert updated == []

    class _ErrorClient:
        def get_series_observations(self, sid: str, start=None, end=None):  # noqa: ANN001
            raise FredClientError("fail")

    monkeypatch.setattr(mu, "FredClient", _ErrorClient)
    updated2 = mu.update_series_ids(["UNRATE"], compute_features=False)
    assert updated2 == []


def test_update_market_symbols_and_public_helpers(monkeypatch: pytest.MonkeyPatch) -> None:
    idx = pd.date_range("2026-01-01", periods=3, freq="D")
    series = pd.Series([100.0, 101.0, 102.0], index=idx, dtype=float)
    monkeypatch.setattr(
        mu,
        "get_market_series",
        lambda key, start=None, end=None: (series if key == "SPY" else pd.Series(dtype=float), "mock", None),
    )
    calls: list[str] = []
    monkeypatch.setattr(mu, "upsert_observations", lambda source, sid, rows: calls.append(sid))

    updated = mu.update_market_symbols(["spy", "", "qqq"])
    assert updated == ["SPY"]
    assert calls == ["SPY"]

    monkeypatch.setattr(mu, "update_series_ids", lambda ids, **kwargs: ids)
    assert mu.update_macro_series("UNRATE", provider="fred") == ["UNRATE"]
    assert mu.update_macro_series("UNRATE", provider="other") == []
    assert mu.update_macro_all(series_list=["UNRATE"], lookback_years=2) == ["UNRATE"]


def test_main_routes_arguments(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    args_all = types.SimpleNamespace(
        start="2026-01-01",
        end="2026-01-31",
        also_features=False,
        skip_features=False,
        all_default=True,
        series=[],
        features_lookback_days=30,
    )
    monkeypatch.setattr(mu, "_parse_args", lambda: args_all)
    monkeypatch.setattr(mu, "update_all_defaults", lambda **kwargs: ["UNRATE", "CPIAUCSL"])
    rc = mu.main()
    assert rc == 0
    assert "Updated 2 series." in capsys.readouterr().out

    args_ids = types.SimpleNamespace(
        start=None,
        end="today",
        also_features=True,
        skip_features=False,
        all_default=False,
        series=["UNRATE"],
        features_lookback_days=None,
    )
    monkeypatch.setattr(mu, "_parse_args", lambda: args_ids)
    monkeypatch.setattr(mu, "update_series_ids", lambda ids, **kwargs: ids)
    rc2 = mu.main()
    assert rc2 == 0
