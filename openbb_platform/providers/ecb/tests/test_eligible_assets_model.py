"""Unit tests for the ECB eligible assets (collateral) model."""

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
    """Extract returns the raw list tagged with the snapshot date."""
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
    """Each filter narrows the snapshot."""
    query = Fetcher.transform_query(params)
    out = Fetcher.transform_data(query, [dict(r) for r in _ROWS])
    assert [r.isin for r in out] == expected


def test_transform_empty_raises():
    """A filter matching nothing raises."""
    query = Fetcher.transform_query({"currency": "GBP"})
    with pytest.raises(EmptyDataError):
        Fetcher.transform_data(query, [dict(r) for r in _ROWS])
