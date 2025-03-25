"""FMP Company Filings Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_filings import (
    CompanyFilingsData,
    CompanyFilingsQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
)
from pydantic import Field


class FMPCompanyFilingsQueryParams(CompanyFilingsQueryParams):
    """FMP Copmany Filings Query.

    Source: https://site.financialmodelingprep.com/developer/docs/sec-filings-api/
    """

    __alias_dict__ = {"form_type": "type"}

    form_type: Optional[str] = Field(
        default=None, description="SEC form type to filter by."
    )
    limit: int = Field(
        default=1000,
        description="Number of results to return.",
    )


class FMPCompanyFilingsData(CompanyFilingsData):
    """FMP Company Filings Data."""

    __alias_dict__ = {
        "filing_date": "fillingDate",  # FMP spells 'filing' wrong everywhere.
        "accepted_date": "acceptedDate",
        "report_type": "type",
        "filing_url": "link",
        "report_url": "finalLink",
    }
    filing_url: Optional[str] = Field(
        default=None, description="URL to the filing page."
    )
    symbol: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    cik: Optional[str] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("cik", "")
    )
    accepted_date: Optional[datetime] = Field(
        default=None, description="Accepted date of the filing."
    )


class FMPCompanyFilingsFetcher(
    Fetcher[
        FMPCompanyFilingsQueryParams,
        List[FMPCompanyFilingsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPCompanyFilingsQueryParams:
        """Transform the query params."""
        return FMPCompanyFilingsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPCompanyFilingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        import math
        from openbb_core.provider.utils.errors import EmptyDataError
        from openbb_core.provider.utils.helpers import amake_request, get_querystring
        from openbb_fmp.utils.helpers import response_callback

        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3/sec_filings"
        query_str = get_querystring(query.model_dump(by_alias=True), ["symbol"])

        # FMP only allows 1000 results per page
        pages = math.ceil(query.limit / 1000)

        urls = [
            f"{base_url}/{query.symbol}?{query_str}&page={page}&apikey={api_key}"
            for page in range(pages)
        ]

        results: list = []

        async def get_one(url):
            """Get the data from one URL."""
            result = await amake_request(
                url, response_callback=response_callback, **kwargs
            )
            if result:
                results.extend(result)

        await asyncio.gather(*[get_one(url) for url in urls])

        if not results:
            raise EmptyDataError("No data was returned for the symbol provided.")

        return sorted(results, key=lambda x: x["fillingDate"], reverse=True)[
            : query.limit
        ]

    @staticmethod
    def transform_data(
        query: FMPCompanyFilingsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPCompanyFilingsData]:
        """Return the transformed data."""
        return [FMPCompanyFilingsData.model_validate(d) for d in data]
