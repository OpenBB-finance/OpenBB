"""Additional coverage tests for macro catalog service."""

from __future__ import annotations

import types
from datetime import date

import pandas as pd
import pytest
from openbb_quant_ml.service import macro_catalog as mc
from openbb_quant_ml.service.macro_fred_client import FredApiKeyMissingError, FredClientError


class _DummyPayload:
    def __init__(self, frame: pd.DataFrame):
        self._frame = frame

    def to_df(self) -> pd.DataFrame:
        return self._frame


def test_domain_defaults_and_default_ids(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        mc,
        "load_macro_config",
        lambda: {
            "domains": {
                "inflation": {
                    "default_transform": "yoy",
                    "default_publish_lag": 35,
                    "default_series": ["cpiaucsl", " "],
                },
                "growth": {
                    "default_transform": "mom_3",
                    "default_publish_lag": 20,
                    "default_series": ["INDPRO", "CPIAUCSL"],
                },
            }
        },
    )
    rows = mc._domain_defaults()
    assert any(row["id"] == "FRED:CPIAUCSL" for row in rows)
    assert any(row["id"] == "FRED:INDPRO" for row in rows)
    ids = mc.all_default_series_ids()
    assert ids.count("CPIAUCSL") == 1


def test_extract_result_rows_supports_list_dict_and_dataframe() -> None:
    assert mc._extract_result_rows([{"series_id": "A"}]) == [{"series_id": "A"}]
    assert mc._extract_result_rows({"results": [{"series_id": "B"}]}) == [{"series_id": "B"}]
    payload = _DummyPayload(pd.DataFrame([{"series_id": "C"}]))
    assert mc._extract_result_rows(payload) == [{"series_id": "C"}]


def test_openbb_search_and_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    class _Economy:
        @staticmethod
        def fred_search(*, query=None, symbol=None, limit=25):  # noqa: ANN001
            token = query or symbol
            return {"results": [{"series_id": str(token).upper(), "title": "Title", "frequency": "Monthly"}]}

    dummy_openbb = types.SimpleNamespace(obb=types.SimpleNamespace(economy=_Economy()))
    monkeypatch.setitem(__import__("sys").modules, "openbb", dummy_openbb)

    rows = mc._openbb_fred_search("unrate", limit=10)
    assert rows and rows[0]["series_id"] == "UNRATE"
    meta = mc._openbb_fred_metadata("UNRATE")
    assert meta["series_id"] == "UNRATE"


def test_register_series_success_and_fallbacks(monkeypatch: pytest.MonkeyPatch) -> None:
    upserted: list[dict[str, object]] = []
    monkeypatch.setattr(mc, "upsert_catalog_item", lambda row: upserted.append(row))
    monkeypatch.setattr(mc, "default_publish_lag_days", lambda freq: 12)

    # OpenBB metadata success path.
    monkeypatch.setattr(
        mc,
        "_openbb_fred_metadata",
        lambda sid: {"series_id": sid, "title": "Unemployment", "frequency": "Monthly", "units": "Percent", "notes": "n"},
    )
    row = mc.register_series("unrate", domain="Labor")
    assert row["id"] == "FRED:UNRATE"
    assert row["publish_lag"] == 12
    assert upserted

    # OpenBB empty -> FredClient fallback path.
    monkeypatch.setattr(mc, "_openbb_fred_metadata", lambda sid: {})

    class _Client:
        def get_series_metadata(self, sid: str):  # noqa: ANN001
            return {"series_id": sid, "title": "CPI", "frequency": "Monthly", "units": "Index"}

    monkeypatch.setattr(mc, "FredClient", _Client)
    row2 = mc.register_series("cpiaucsl")
    assert row2["id"] == "FRED:CPIAUCSL"


def test_register_series_handles_missing_key_and_client_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mc, "_openbb_fred_metadata", lambda sid: {})
    monkeypatch.setattr(mc, "default_publish_lag_days", lambda freq: 30)

    class _MissingKeyClient:
        def get_series_metadata(self, sid: str):  # noqa: ANN001
            raise FredApiKeyMissingError("missing")

    monkeypatch.setattr(mc, "FredClient", _MissingKeyClient)
    monkeypatch.setattr(mc, "get_catalog_item", lambda key: None)
    monkeypatch.setattr(mc, "upsert_catalog_item", lambda row: None)
    row = mc.register_series("pce")
    assert row["id"] == "FRED:PCE"

    monkeypatch.setattr(mc, "get_catalog_item", lambda key: {"id": key})
    with pytest.raises(ValueError, match="FRED_API_KEY is not configured"):
        mc.register_series("pce")

    class _ErrorClient:
        def get_series_metadata(self, sid: str):  # noqa: ANN001
            raise FredClientError("fred failed")

    monkeypatch.setattr(mc, "FredClient", _ErrorClient)
    monkeypatch.setattr(mc, "get_catalog_item", lambda key: None)
    with pytest.raises(ValueError, match="fred failed"):
        mc.register_series("pce")


def test_search_catalog_and_resolve_create(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(mc, "_openbb_fred_search", lambda q, limit=25: [])

    class _SearchClient:
        def search_series(self, q: str, limit: int = 25):  # noqa: ANN001
            return [{"series_id": "DGS10", "title": "10Y", "frequency": "Daily", "units": "Percent"}]

    monkeypatch.setattr(mc, "FredClient", _SearchClient)
    rows = mc.search_catalog("10y")
    assert rows and rows[0]["id"] == "FRED:DGS10"

    calls: list[dict[str, object]] = []
    monkeypatch.setattr(mc, "upsert_catalog_item", lambda row: calls.append(row))
    monkeypatch.setattr(mc, "get_catalog_item", lambda key: None)
    resolved = mc.resolve_catalog_item("UNRATE", create_if_missing=True)
    assert resolved is not None
    assert resolved["id"] == "FRED:UNRATE"
    assert calls


def test_parse_date_input_variants() -> None:
    assert mc.parse_date_input(None) is None
    assert mc.parse_date_input("  ") is None
    assert mc.parse_date_input(date(2026, 2, 1)) == date(2026, 2, 1)
    assert mc.parse_date_input("2026-02-01") == date(2026, 2, 1)
    assert isinstance(mc.parse_date_input("today"), date)
