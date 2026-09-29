import asyncio

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_ecb.models.eligible_assets import ECBEligibleAssetsFetcher as Fetcher
from openbb_ecb.utils import non_sdmx

_ROWS = [
    {
        "isin": "XS1",
        "asset_type": "AT01",
        "haircut_category": "L1A",
        "currency": "EUR",
        "issuer_group": "IG1",
    },
    {
        "isin": "XS2",
        "asset_type": "AT02",
        "haircut_category": "L1B",
        "currency": "USD",
        "issuer_group": "IG2",
    },
]


def _patch(monkeypatch):
    async def _ea(snapshot_date):
        return "2026-06-24", [dict(r) for r in _ROWS]

    monkeypatch.setattr(non_sdmx, "fetch_eligible_assets", _ea)


def test_aextract_tags_snapshot(monkeypatch):
    _patch(monkeypatch)
    raw = asyncio.run(Fetcher.aextract_data(Fetcher.transform_query({}), None))
    assert all(r["snapshot_date"] == "2026-06-24" for r in raw)


@pytest.mark.parametrize(
    "params, expected",
    [
        ({"currency": "EUR"}, ["XS1"]),
        ({"isin": "XS2", "limit": 5}, ["XS2"]),
        ({"asset_type": "AT01"}, ["XS1"]),
        ({"haircut_category": "L1B"}, ["XS2"]),
        ({"issuer_group": "IG2"}, ["XS2"]),
    ],
)
def test_transform_filters(params, expected):
    query = Fetcher.transform_query(params)
    out = Fetcher.transform_data(query, [dict(r) for r in _ROWS])
    assert [r.isin for r in out] == expected


def test_transform_empty_raises():
    query = Fetcher.transform_query({"currency": "GBP"})
    with pytest.raises(EmptyDataError):
        Fetcher.transform_data(query, [dict(r) for r in _ROWS])


def test_filter_by_label():
    out = Fetcher.transform_data(
        Fetcher.transform_query({"asset_type": "Bond"}), [dict(r) for r in _ROWS]
    )
    assert [r.isin for r in out] == ["XS1"]


def test_decode_labels():
    row = {
        "isin": "X",
        "asset_type": "AT11",
        "issuer_group": "IG8",
        "haircut_category": "L1E",
        "coupon_definition": "CD4",
        "issuer_residence": "IRDE",
        "guarantor_residence": "IRFR",
        "reference_market": "RMDE11",
    }
    out = Fetcher.transform_data(Fetcher.transform_query({}), [row])[0].model_dump()
    assert out["asset_type"] == "Asset-backed security (ABS)"
    assert out["issuer_group"] == "Agency – credit institution"
    assert out["haircut_category"].startswith("Category V")
    assert out["coupon_definition"] == "Fixed"
    assert out["issuer_residence"] == "Germany"
    assert out["guarantor_residence"] == "France"
    assert out["reference_market"] == "Germany (11)"


def test_decode_fallbacks():
    rows = [
        {
            "isin": "a",
            "asset_type": "ATZZ",
            "issuer_residence": "IR",
            "reference_market": "RMDE11",
        },
        {"isin": "b", "issuer_residence": "XX", "reference_market": "RMDE"},
        {"isin": "c", "reference_market": "FOO"},
        {"isin": "d", "reference_market": "RM"},
    ]
    out = [
        d.model_dump()
        for d in Fetcher.transform_data(Fetcher.transform_query({}), rows)
    ]
    assert out[0]["asset_type"] == "ATZZ" and out[0]["issuer_residence"] == "IR"
    assert out[0]["reference_market"] == "Germany (11)"
    assert (
        out[1]["issuer_residence"] == "XX" and out[1]["reference_market"] == "Germany"
    )
    assert out[2]["reference_market"] == "FOO"
    assert out[3]["reference_market"] == "RM"
