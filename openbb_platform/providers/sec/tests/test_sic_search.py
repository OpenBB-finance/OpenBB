"""Unit tests for ``openbb_sec.models.sic_search``."""

import asyncio
from unittest.mock import patch

from openbb_sec.models.sic_search import SecSicSearchFetcher, SecSicSearchQueryParams


def test_sic_search_aextract_empty_table():
    """sic_search.py:88 -> early return [] when the parsed table is empty."""
    # A table with a header row but no data rows -> read_html yields 0 rows.
    empty_table = (
        "<html><body><table>"
        "<tr><th>SIC Code</th><th>Office</th><th>Industry Title</th></tr>"
        "</table></body></html>"
    )

    async def _cached_request(*args, **kwargs):  # noqa: ARG001
        return empty_table

    query = SecSicSearchQueryParams(query="bank", use_cache=False)
    with patch("openbb_sec.utils.cache.cached_request", _cached_request):
        result = asyncio.run(SecSicSearchFetcher.aextract_data(query, None))
    assert result == []
