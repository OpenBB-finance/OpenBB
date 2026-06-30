"""Unit tests for the ECB available indicators model (series enumeration)."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_ecb.models.available_indicators import (
    ECBAvailableIndicatorsFetcher as Fetcher,
)

_SERIES = [
    {
        "series_key": "M.U2.N.000000.4.ANR",
        "name": "Monthly — Euro area — HICP — Annual rate of change",
        "FREQ__label": "Monthly",
        "REF_AREA__label": "Euro area",
    },
    {
        "series_key": "M.U2.N.000000.4.INX",
        "name": "Monthly — Euro area — HICP — Index",
        "FREQ__label": "Monthly",
        "REF_AREA__label": "Euro area",
    },
]


def _patch_keys(monkeypatch, series=_SERIES):
    from openbb_ecb.utils import query_builder

    async def _keys(flow_ref, key="", **kwargs):
        return [dict(s) for s in series]

    monkeypatch.setattr(query_builder, "fetch_series_keys", _keys)


def test_requires_valid_dataflow():
    """Missing or unknown dataflow raises — there is no series index to scan."""
    with pytest.raises(OpenBBError):
        asyncio.run(Fetcher.aextract_data(Fetcher.transform_query({}), None))
    with pytest.raises(OpenBBError):
        asyncio.run(
            Fetcher.aextract_data(Fetcher.transform_query({"dataflow": "ZZZ"}), None)
        )


def test_enumerate_and_transform(monkeypatch):
    """Series enumerate into FLOW::KEY indicator rows with decoded metadata."""
    _patch_keys(monkeypatch)
    query = Fetcher.transform_query(
        {"dataflow": "ICP", "frequency": "M", "reference_area": "U2"}
    )
    raw = asyncio.run(Fetcher.aextract_data(query, None))
    out = Fetcher.transform_data(query, raw)
    assert {d.symbol for d in out} == {
        "ICP::M.U2.N.000000.4.ANR",
        "ICP::M.U2.N.000000.4.INX",
    }
    first = out[0]
    assert first.symbol_root == "ICP"
    assert first.dataflow_id == "ICP"
    assert first.series_key == "M.U2.N.000000.4.ANR"
    assert first.frequency == "Monthly"
    assert first.country == "Euro area"
    assert first.description


def test_query_filter_and_empty(monkeypatch):
    """A text query filters by name; an empty result raises (no freq/area set)."""
    _patch_keys(monkeypatch)
    query = Fetcher.transform_query(
        {"dataflow": "ICP", "query": "annual rate of change"}
    )
    raw = asyncio.run(Fetcher.aextract_data(query, None))
    assert [r["series_key"] for r in raw] == ["M.U2.N.000000.4.ANR"]

    with pytest.raises(OpenBBError):
        asyncio.run(
            Fetcher.aextract_data(
                Fetcher.transform_query({"dataflow": "ICP", "query": "no_such_term"}),
                None,
            )
        )


def test_frequency_and_area_narrow_the_key(monkeypatch):
    """``frequency`` -> FREQ and ``reference_area`` -> the geography dimension."""
    from openbb_ecb.utils import query_builder
    from openbb_ecb.utils.metadata import EcbMetadata

    captured = {}

    async def _keys(flow_ref, key="", **kwargs):
        captured["key"] = key
        return [dict(_SERIES[0])]

    monkeypatch.setattr(query_builder, "fetch_series_keys", _keys)

    # EXR geography dim is CURRENCY: FREQ.CURRENCY.CURRENCY_DENOM.EXR_TYPE.EXR_SUFFIX
    asyncio.run(
        Fetcher.aextract_data(
            Fetcher.transform_query(
                {"dataflow": "EXR", "frequency": "A", "reference_area": "USD"}
            ),
            None,
        )
    )
    assert captured["key"] == "A.USD..."

    # A dataflow with no geography dim -> reference_area is ignored.
    monkeypatch.setattr(
        EcbMetadata,
        "get_dataflow_dimensions",
        lambda self, flow: [{"id": "FREQ"}, {"id": "OTHER"}],
    )
    asyncio.run(
        Fetcher.aextract_data(
            Fetcher.transform_query(
                {"dataflow": "EXR", "frequency": "M", "reference_area": "U2"}
            ),
            None,
        )
    )
    assert captured["key"] == "M."


def test_dimension_values_narrow_the_key(monkeypatch):
    """Extra 'DIM:VALUE' filters parse from a string, a list, or a comma-joined item."""
    from openbb_ecb.utils import query_builder

    captured = {}

    async def _keys(flow_ref, key="", **kwargs):
        captured["key"] = key
        return [dict(_SERIES[0])]

    monkeypatch.setattr(query_builder, "fetch_series_keys", _keys)

    # EXR dims: FREQ.CURRENCY.CURRENCY_DENOM.EXR_TYPE.EXR_SUFFIX
    for dim_values in (
        "EXR_TYPE:SP00,EXR_SUFFIX:A",
        ["EXR_TYPE:SP00", "EXR_SUFFIX:A", "junk"],  # 'junk' has no ':' -> skipped
        ["EXR_TYPE:SP00,EXR_SUFFIX:A"],  # the Workspace marshals as one joined value
    ):
        asyncio.run(
            Fetcher.aextract_data(
                Fetcher.transform_query(
                    {
                        "dataflow": "EXR",
                        "frequency": "M",
                        "dimension_values": dim_values,
                    }
                ),
                None,
            )
        )
        assert captured["key"] == "M...SP00.A"


def test_limit(monkeypatch):
    """A positive limit caps the result; <=0 returns all."""
    _patch_keys(monkeypatch)
    capped = asyncio.run(
        Fetcher.aextract_data(
            Fetcher.transform_query({"dataflow": "ICP", "limit": 1}), None
        )
    )
    assert len(capped) == 1
    every = asyncio.run(
        Fetcher.aextract_data(
            Fetcher.transform_query({"dataflow": "ICP", "limit": 0}), None
        )
    )
    assert len(every) == 2
