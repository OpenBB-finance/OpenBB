"""Unit tests for ``openbb_ecb.utils.query_builder`` (mocked HTTP)."""

import asyncio

import openbb_core.provider.utils.helpers as core_helpers
import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_ecb.utils import query_builder

_MSG = {
    "dataSets": [{"series": {"0": {"observations": {"0": [1.5]}}}}],
    "structure": {
        "dimensions": {
            "series": [{"id": "FREQ", "values": [{"id": "D", "name": "Daily"}]}],
            "observation": [{"id": "TIME_PERIOD", "values": [{"id": "2024-01-01"}]}],
        }
    },
}


class _FakeResp:
    def __init__(self, status=200, json_data=None, text=""):
        self.status = status
        self._json = json_data
        self._text = text

    async def json(self):
        return self._json

    async def text(self):
        return self._text


def _patch(monkeypatch, status=200, json_data=None, text=""):
    async def fake(url, headers=None, response_callback=None, **kwargs):
        return await response_callback(_FakeResp(status, json_data, text), None)

    monkeypatch.setattr(core_helpers, "amake_request", fake)


def test_build_data_url_all_params():
    """Every query parameter is appended to the URL."""
    url = query_builder.build_data_url(
        "EXR",
        "D.USD.EUR.SP00.A",
        start_date="2024-01-01",
        end_date="2024-02-01",
        detail="dataonly",
        first_n=5,
        last_n=3,
        include_history=True,
    )
    assert "/data/EXR/D.USD.EUR.SP00.A?" in url
    for fragment in (
        "format=jsondata",
        "detail=dataonly",
        "startPeriod=2024-01-01",
        "endPeriod=2024-02-01",
        "firstNObservations=5",
        "lastNObservations=3",
        "includeHistory=true",
    ):
        assert fragment in url


def test_build_data_url_minimal():
    """With no optional params only format/detail are present."""
    url = query_builder.build_data_url("EXR", "D.USD.EUR.SP00.A")
    assert url.endswith("?format=jsondata&detail=full")


def test_fetch_sdmx_data_success(monkeypatch):
    """A 200 SDMX-JSON response parses to records."""
    _patch(monkeypatch, 200, _MSG)
    records = asyncio.run(query_builder.fetch_sdmx_data("EXR", "D.USD.EUR.SP00.A"))
    assert records[0]["OBS_VALUE"] == 1.5


def test_fetch_sdmx_data_404_raises(monkeypatch):
    """A 404 raises by default."""
    _patch(monkeypatch, 404, None, "No results")
    with pytest.raises(OpenBBError):
        asyncio.run(query_builder.fetch_sdmx_data("EXR", "BAD"))


def test_fetch_sdmx_data_404_no_raise(monkeypatch):
    """A 404 returns [] when raise_empty is False."""
    _patch(monkeypatch, 404, None, "No results")
    assert (
        asyncio.run(query_builder.fetch_sdmx_data("EXR", "BAD", raise_empty=False))
        == []
    )


def test_fetch_sdmx_data_error_status(monkeypatch):
    """A non-404 error status raises."""
    _patch(monkeypatch, 500, None, "boom")
    with pytest.raises(OpenBBError):
        asyncio.run(query_builder.fetch_sdmx_data("EXR", "X"))


def test_fetch_sdmx_data_empty(monkeypatch):
    """A 200 with no series raises, or returns [] when raise_empty is False."""
    _patch(monkeypatch, 200, {"dataSets": []})
    with pytest.raises(OpenBBError):
        asyncio.run(query_builder.fetch_sdmx_data("EXR", "X"))
    _patch(monkeypatch, 200, {"dataSets": []})
    assert (
        asyncio.run(query_builder.fetch_sdmx_data("EXR", "X", raise_empty=False)) == []
    )


_KEYS_MSG = {
    "dataSets": [{"series": {"0:0": {}}}],
    "structure": {
        "dimensions": {
            "series": [
                {"id": "FREQ", "values": [{"id": "D", "name": "Daily"}]},
                {"id": "CURRENCY", "values": [{"id": "USD", "name": "US dollar"}]},
            ]
        }
    },
}


def test_fetch_series_keys_success(monkeypatch):
    """``serieskeysonly`` parses to one record per series with a composed name."""
    _patch(monkeypatch, 200, _KEYS_MSG)
    rows = asyncio.run(query_builder.fetch_series_keys("EXR"))
    assert rows[0]["series_key"] == "D.USD"
    assert rows[0]["name"] == "Daily — US dollar"
    # The URL requests the serieskeysonly detail.
    assert "detail=serieskeysonly" in query_builder.build_data_url(
        "EXR", "", detail="serieskeysonly"
    )


def test_fetch_series_keys_404_no_raise(monkeypatch):
    """A 404 returns [] by default (raise_empty is False)."""
    _patch(monkeypatch, 404, None, "No results")
    assert asyncio.run(query_builder.fetch_series_keys("EXR", "BAD")) == []


def test_fetch_series_keys_404_raise(monkeypatch):
    """A 404 raises when raise_empty is True."""
    _patch(monkeypatch, 404, None, "No results")
    with pytest.raises(OpenBBError):
        asyncio.run(query_builder.fetch_series_keys("EXR", "BAD", raise_empty=True))


def test_fetch_series_keys_empty_raise(monkeypatch):
    """A 200 with no series raises when raise_empty is True."""
    _patch(monkeypatch, 200, {"dataSets": []})
    with pytest.raises(OpenBBError):
        asyncio.run(query_builder.fetch_series_keys("EXR", raise_empty=True))


def test_request_sdmx_non_dict_body(monkeypatch):
    """A non-dict 200 body resolves to no records (not an error)."""
    _patch(monkeypatch, 200, ["not", "a", "dict"])
    assert asyncio.run(query_builder.fetch_series_keys("EXR")) == []
