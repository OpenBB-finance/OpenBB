"""Unit tests for ``openbb_sec.models.equity_search``."""

import asyncio
from unittest.mock import patch

from openbb_sec.models.equity_search import (
    SecEquitySearchFetcher,
    SecEquitySearchQueryParams,
)


def test_equity_search_aextract_is_fund_branch():
    """equity_search.py:68-69 -> the is_fund=True branch filters the fund map."""
    from pandas import DataFrame

    funds = DataFrame(
        {
            "cik": ["0000111", "0000222"],
            "seriesId": ["S001", "S002"],
            "classId": ["C001", "C002"],
            "symbol": ["SPY", "DIA"],
        }
    )

    async def _fund_map(use_cache=True):  # noqa: ARG001
        return funds

    query = SecEquitySearchQueryParams(query="SPY", is_fund=True, use_cache=False)
    with patch("openbb_sec.utils.helpers.get_mf_and_etf_map", _fund_map):
        result = asyncio.run(SecEquitySearchFetcher.aextract_data(query, None))
    assert len(result) == 1
    assert result[0]["symbol"] == "SPY"
