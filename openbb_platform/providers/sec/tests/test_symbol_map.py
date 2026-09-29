"""Unit tests for ``openbb_sec.models.symbol_map``."""

import asyncio

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_sec.models.symbol_map import SecSymbolMapFetcher, SecSymbolMapQueryParams


def test_symbol_map_aextract_invalid_cik():
    """symbol_map.py:57 -> raise OpenBBError when query is not a digit."""
    query = SecSymbolMapQueryParams(query="NOTACIK")
    with pytest.raises(OpenBBError) as exc:
        asyncio.run(SecSymbolMapFetcher.aextract_data(query, None))
    assert "must be a valid CIK" in str(exc.value)
