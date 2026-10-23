"""Unit tests for ``openbb_sec.models.cik_map``."""

import asyncio
from unittest.mock import patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_sec.models.cik_map import SecCikMapFetcher, SecCikMapQueryParams


def test_cik_map_aextract_symbol_not_found():
    """cik_map.py:54 -> raise OpenBBError when symbol_map returns nothing."""

    async def _empty(symbol, use_cache):  # noqa: ARG001
        return ""

    query = SecCikMapQueryParams(symbol="DOESNOTEXIST")
    with patch("openbb_sec.utils.helpers.symbol_map", _empty):
        with pytest.raises(OpenBBError) as exc:
            asyncio.run(SecCikMapFetcher.aextract_data(query, None))
    assert "not found in SEC database" in str(exc.value)


def test_cik_map_aextract_success():
    """cik_map.py happy path returns the resolved CIK dict."""

    async def _cik(symbol, use_cache):  # noqa: ARG001
        return "0000320193"

    query = SecCikMapQueryParams(symbol="AAPL")
    with patch("openbb_sec.utils.helpers.symbol_map", _cik):
        result = asyncio.run(SecCikMapFetcher.aextract_data(query, None))
    assert result == {"cik": "0000320193"}
