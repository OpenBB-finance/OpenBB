"""Unit tests for ``openbb_bls.utils.helpers.get_bls_timeseries``."""

from __future__ import annotations

import asyncio
import json
from typing import Any
from unittest.mock import AsyncMock

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_bls.utils import helpers as helpers_mod


def _run(coro):
    """Run an async helper synchronously."""
    return asyncio.run(coro)


def _install_fake_amake(monkeypatch, payload: dict | list[dict], captured: dict):
    """Patch ``amake_request`` inside helpers to return a canned payload."""

    async def _fake(url: str, **kwargs: Any) -> Any:
        captured["url"] = url
        captured["kwargs"] = kwargs
        return payload

    monkeypatch.setattr(
        "openbb_core.provider.utils.helpers.amake_request",
        AsyncMock(side_effect=_fake),
    )
    return captured


def test_monthly_series_with_full_calc_and_catalog(monkeypatch):
    """Single monthly series with calculations + catalog hits every numeric branch."""
    payload = {
        "Results": {
            "series": [
                {
                    "seriesID": "CUUR0000SA0",
                    "catalog": {"series_title": "All items"},
                    "data": [
                        {
                            "year": "2026",
                            "period": "M04",
                            "value": "311.2",
                            "latest": "true",
                            "footnotes": [{"text": "Preliminary"}, {}, None],
                            "calculations": {
                                "net_changes": {
                                    "1": "0.5",
                                    "3": "1.0",
                                    "6": "1.8",
                                    "12": "3.6",
                                },
                                "pct_changes": {
                                    "1": "0.2",
                                    "3": "0.5",
                                    "6": "0.9",
                                    "12": "1.8",
                                },
                            },
                        }
                    ],
                }
            ]
        }
    }
    captured: dict = {}
    _install_fake_amake(monkeypatch, payload, captured)
    result = _run(
        helpers_mod.get_bls_timeseries(
            api_key="KEY", series_ids="CUUR0000SA0", start_year=2024, end_year=2026
        )
    )
    assert isinstance(result, dict)
    assert result["metadata"]["CUUR0000SA0"] == {"series_title": "All items"}
    row = result["data"][0]
    assert row["symbol"] == "CUUR0000SA0"
    assert row["title"] == "All items"
    assert row["date"] == "2026-04-01"
    assert row["value"] == pytest.approx(311.2)
    assert row["latest"] is True
    assert row["footnotes"] == "Preliminary"
    assert row["change_1M"] == pytest.approx(0.5)
    assert row["change_3M"] == pytest.approx(1.0)
    assert row["change_6M"] == pytest.approx(1.8)
    assert row["change_12M"] == pytest.approx(3.6)
    assert row["change_percent_1M"] == pytest.approx(0.002)
    assert row["change_percent_3M"] == pytest.approx(0.005)
    assert row["change_percent_6M"] == pytest.approx(0.009)
    assert row["change_percent_12M"] == pytest.approx(0.018)
    sent = json.loads(captured["kwargs"]["data"])
    assert sent["seriesid"] == ["CUUR0000SA0"]
    assert sent["startyear"] == 2024
    assert sent["registrationkey"] == "KEY"


def test_truncates_more_than_50_symbols(monkeypatch):
    """When passed >50 series IDs, helpers warns and truncates to the first 50."""
    payload = {"Results": {"series": []}}
    captured: dict = {}
    _install_fake_amake(monkeypatch, payload, captured)
    ids = [f"S{i:03d}" for i in range(60)]
    with pytest.warns(UserWarning, match="Max 50 symbols"):
        result = _run(helpers_mod.get_bls_timeseries(api_key="KEY", series_ids=ids))
    sent = json.loads(captured["kwargs"]["data"])
    assert len(sent["seriesid"]) == 50
    assert isinstance(result, EmptyDataError)


def test_invalid_api_key_message_is_rewritten(monkeypatch):
    """The BLS 'key provided by the User is invalid' messages are rephrased."""
    payload = {
        "Results": {"series": []},
        "message": [
            "The key: ABC provided by the User is invalid. Bad key.",
            "",
            "Other message",
        ],
    }
    captured: dict = {}
    _install_fake_amake(monkeypatch, payload, captured)
    result = _run(helpers_mod.get_bls_timeseries(api_key="ABC", series_ids=["X"]))
    assert isinstance(result, EmptyDataError)
    text = str(result)
    assert "The key provided by the User is invalid." in text
    assert "Other message" in text


def test_string_series_ids_split_on_comma(monkeypatch):
    """A comma-separated ``series_ids`` string is split into a list before posting."""
    payload = {"Results": {"series": []}}
    captured: dict = {}
    _install_fake_amake(monkeypatch, payload, captured)
    _run(helpers_mod.get_bls_timeseries(api_key="K", series_ids="A,B,C"))
    sent = json.loads(captured["kwargs"]["data"])
    assert sent["seriesid"] == ["A", "B", "C"]


def test_skips_results_with_missing_seriesid(monkeypatch):
    """Results entries without a ``seriesID`` field are silently skipped."""
    payload = {
        "Results": {
            "series": [
                {
                    "seriesID": None,
                    "data": [{"year": "2025", "period": "M01", "value": "100"}],
                },
                {
                    "seriesID": "GOOD",
                    "data": [{"year": "2025", "period": "M02", "value": "101"}],
                },
            ]
        }
    }
    captured: dict = {}
    _install_fake_amake(monkeypatch, payload, captured)
    result = _run(helpers_mod.get_bls_timeseries(api_key="K", series_ids=["A"]))
    assert isinstance(result, dict)
    assert all(r["symbol"] == "GOOD" for r in result["data"])


def test_period_annual_marker_yields_jan_first(monkeypatch):
    """An ``A`` period (annual average) maps to YYYY-01-01."""
    payload = {
        "Results": {
            "series": [
                {
                    "seriesID": "X",
                    "catalog": {"series_title": "X title"},
                    "data": [
                        {
                            "year": "2025",
                            "period": "A01",
                            "value": "10",
                            "latest": "false",
                        }
                    ],
                }
            ]
        }
    }
    captured: dict = {}
    _install_fake_amake(monkeypatch, payload, captured)
    result = _run(helpers_mod.get_bls_timeseries(api_key="K", series_ids=["X"]))
    assert result["data"][0]["date"] == "2025-01-01"


def test_semiannual_and_quarterly_period_dates(monkeypatch):
    """Semiannual + quarterly tokens (S01/S02/S03 + Q01..Q05) map to canonical dates."""
    rows = [
        ("S01", "2025-01-01"),
        ("S02", "2025-07-01"),
        ("S03", "2025-12-31"),
        ("Q01", "2025-01-01"),
        ("Q02", "2025-04-01"),
        ("Q03", "2025-07-01"),
        ("Q04", "2025-10-01"),
        ("Q05", "2025-12-31"),
    ]
    payload = {
        "Results": {
            "series": [
                {
                    "seriesID": "X",
                    "data": [
                        {"year": "2025", "period": p, "value": "1"} for p, _ in rows
                    ],
                }
            ]
        }
    }
    captured: dict = {}
    _install_fake_amake(monkeypatch, payload, captured)
    result = _run(helpers_mod.get_bls_timeseries(api_key="K", series_ids=["X"]))
    dates = [r["date"] for r in result["data"]]
    assert dates == [d for _, d in rows]


def test_period_13_yields_year_dec_and_annual_average_title(monkeypatch):
    """``M13`` (annual average) maps to YYYY-12-31 and decorates the catalog title."""
    payload = {
        "Results": {
            "series": [
                {
                    "seriesID": "X",
                    "catalog": {"series_title": "All items"},
                    "data": [
                        {
                            "year": "2024",
                            "period": "M13",
                            "value": "299.0",
                            "latest": "true",
                        }
                    ],
                }
            ]
        }
    }
    captured: dict = {}
    _install_fake_amake(monkeypatch, payload, captured)
    result = _run(helpers_mod.get_bls_timeseries(api_key="K", series_ids=["X"]))
    row = result["data"][0]
    assert row["date"] == "2024-12-31"
    assert row["title"].endswith("(Annual Average)")


def test_value_dash_maps_to_none(monkeypatch):
    """A literal '-' in ``value`` resolves to ``None`` not 0."""
    payload = {
        "Results": {
            "series": [
                {
                    "seriesID": "X",
                    "data": [
                        {
                            "year": "2025",
                            "period": "M05",
                            "value": "-",
                            "latest": "false",
                        }
                    ],
                }
            ]
        }
    }
    captured: dict = {}
    _install_fake_amake(monkeypatch, payload, captured)
    result = _run(helpers_mod.get_bls_timeseries(api_key="K", series_ids=["X"]))
    assert result["data"][0]["value"] is None


def test_footnotes_string_fallback(monkeypatch):
    """Non-dict footnote entries are coerced via ``str()``."""
    payload = {
        "Results": {
            "series": [
                {
                    "seriesID": "X",
                    "data": [
                        {
                            "year": "2025",
                            "period": "M05",
                            "value": "1",
                            "footnotes": ["plain string note"],
                        }
                    ],
                }
            ]
        }
    }
    captured: dict = {}
    _install_fake_amake(monkeypatch, payload, captured)
    result = _run(helpers_mod.get_bls_timeseries(api_key="K", series_ids=["X"]))
    assert result["data"][0]["footnotes"] == "plain string note"


def test_footnotes_all_empty_strips_field(monkeypatch):
    """Footnotes list with only None values yields no ``footnotes`` key on output."""
    payload = {
        "Results": {
            "series": [
                {
                    "seriesID": "X",
                    "data": [
                        {
                            "year": "2025",
                            "period": "M05",
                            "value": "1",
                            "footnotes": [{"text": ""}],
                        }
                    ],
                }
            ]
        }
    }
    captured: dict = {}
    _install_fake_amake(monkeypatch, payload, captured)
    result = _run(helpers_mod.get_bls_timeseries(api_key="K", series_ids=["X"]))
    assert "footnotes" not in result["data"][0]


def test_aspects_appended_when_requested(monkeypatch):
    """``aspects=True`` lifts aspect rows into the metadata block."""
    payload = {
        "Results": {
            "series": [
                {
                    "seriesID": "X",
                    "catalog": {"series_title": "x"},
                    "data": [
                        {
                            "year": "2025",
                            "period": "M05",
                            "value": "1",
                            "footnotes": [{"text": "fn"}],
                            "aspects": [
                                {"name": "Standard Error", "value": "0.1"},
                                {"name": "Skip", "value": "-"},
                            ],
                        }
                    ],
                }
            ]
        }
    }
    captured: dict = {}
    _install_fake_amake(monkeypatch, payload, captured)
    result = _run(
        helpers_mod.get_bls_timeseries(api_key="K", series_ids=["X"], aspects=True)
    )
    assert result["metadata"]["X"]["aspects"][0]["name"] == "Standard Error"
    assert all(a["value"] != "-" for a in result["metadata"]["X"]["aspects"])


def test_aspects_empty_appends_message(monkeypatch):
    """When all aspect values are non-numeric the messages list is annotated."""
    payload = {
        "Results": {
            "series": [
                {
                    "seriesID": "X",
                    "catalog": {"series_title": "x"},
                    "data": [
                        {
                            "year": "2025",
                            "period": "M05",
                            "value": "1",
                            "footnotes": [{"text": "fn"}],
                            "aspects": [{"name": "skip", "value": "-"}],
                        }
                    ],
                }
            ]
        }
    }
    captured: dict = {}
    _install_fake_amake(monkeypatch, payload, captured)
    result = _run(
        helpers_mod.get_bls_timeseries(api_key="K", series_ids=["X"], aspects=True)
    )
    assert any("No Aspect Available" in m for m in result["messages"])


def test_returns_empty_data_error_when_no_rows(monkeypatch):
    """An empty payload returns an EmptyDataError without raising."""
    payload = {"Results": {"series": []}}
    captured: dict = {}
    _install_fake_amake(monkeypatch, payload, captured)
    out = _run(helpers_mod.get_bls_timeseries(api_key="K", series_ids=["X"]))
    assert isinstance(out, EmptyDataError)
