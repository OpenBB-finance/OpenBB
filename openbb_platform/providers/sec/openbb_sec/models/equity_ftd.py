"""SEC Equity FTD Model."""

import concurrent.futures
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_ftd import (
    EquityFtdData,
    EquityFtdQueryParams,
)
from openbb_sec.utils.helpers import download_zip_file, get_ftd_urls
from pydantic import Field


class SecEquityFtdQueryParams(EquityFtdQueryParams):
    """SEC Equity FTD Query.

    Source: https://sec.gov/
    """

    limit: Optional[int] = Field(
        description="""
        Limit the number of reports to parse, from most recent.
        Approximately 24 reports per year, going back to 2009.
        """,
        default=24,
    )
    skip_reports: Optional[int] = Field(
        description="""
        Skip N number of reports from current. A value of 1 will skip the most recent report.
        """,
        default=0,
    )


class SecEquityFtdData(EquityFtdData):
    """SEC Equity FTD Data."""


class SecEquityFtdFetcher(
    Fetcher[
        SecEquityFtdQueryParams,
        List[SecEquityFtdData],
    ]
):
    """Transform the query, extract and transform the data from the SEC endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> SecEquityFtdQueryParams:
        """Transform query params."""
        return SecEquityFtdQueryParams(**params)

    @staticmethod
    def extract_data(
        query: SecEquityFtdQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extracts the data from the SEC website."""
        results = []
        limit = query.limit if query.limit is not None and query.limit > 0 else 0
        symbol = query.symbol.upper()

        urls_data = get_ftd_urls()
        urls = list(urls_data.values())
        if limit > 0:
            urls = (
                urls[:limit]
                if not query.skip_reports
                else urls[query.skip_reports : limit + query.skip_reports]  # noqa: E203
            )

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(
                lambda url: results.extend(download_zip_file(url, symbol)), urls
            )

        results = sorted(results, key=lambda d: d["date"], reverse=True)

        return results

    @staticmethod
    def transform_data(
        query: SecEquityFtdQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[SecEquityFtdData]:
        """Transforms the data to the standard format."""
        return [SecEquityFtdData.model_validate(d) for d in data]
