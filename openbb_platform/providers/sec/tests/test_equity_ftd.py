"""Unit tests for ``openbb_sec.models.equity_ftd``."""

import asyncio
from unittest.mock import patch

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_sec.models.equity_ftd import SecEquityFtdFetcher, SecEquityFtdQueryParams


def test_equity_ftd_aextract_no_results():
    """equity_ftd.py:93 -> raise EmptyDataError when no records collected."""

    async def _urls():
        return {"2024-01": "https://example.com/a.zip"}

    async def _download(url, symbol, use_cache):  # noqa: ARG001
        return []

    query = SecEquityFtdQueryParams(symbol="AAPL", limit=1, use_cache=False)
    with (
        patch("openbb_sec.utils.helpers.get_ftd_urls", _urls),
        patch("openbb_sec.utils.helpers.download_zip_file", _download),
    ):
        with pytest.raises(EmptyDataError) as exc:
            asyncio.run(SecEquityFtdFetcher.aextract_data(query, None))
    assert "no results were returned" in str(exc.value)
