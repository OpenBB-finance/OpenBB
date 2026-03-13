"""FMP Company Filings Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    timedelta,
)
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_filings import (
    CompanyFilingsData,
    CompanyFilingsQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
)
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FMPCompanyFilingsQueryParams(CompanyFilingsQueryParams):
    """FMP Company Filings Query.

    Source: https://site.financialmodelingprep.com/developer/docs/sec-filings-api/
    """

    cik: str | None = Field(
        default=None, description="CIK number to look up. Overrides symbol."
    )
    start_date: dateType | None = Field(
        default=None,
        description="Start date for filtering filings. Default is one year ago.",
    )
    end_date: dateType | None = Field(
        default=None, description="End date for filtering filings."
    )
    limit: int = Field(
        default=1000,
        le=1000,
        gt=0,
        description="Number of results to return. Max results is 1000.",
    )
    page: int = Field(
        default=0,
        description="Page number for paginated results. Max page is 100.",
        le=100,
        gt=0,
    )


class FMPCompanyFilingsData(CompanyFilingsData):
    """FMP Company Filings Data."""

    __alias_dict__ = {
        "accepted_date": "acceptedDate",
        "report_type": "formType",
        "filing_url": "link",
        "report_url": "finalLink",
    }
    filing_url: str | None = Field(default=None, description="URL to the filing page.")
    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    cik: str | None = Field(default=None, description=DATA_DESCRIPTIONS.get("cik", ""))
    accepted_date: dateType | None = Field(
        default=None, description="Accepted date of the filing."
    )


class FMPCompanyFilingsFetcher(
    Fetcher[
        FMPCompanyFilingsQueryParams,
        list[FMPCompanyFilingsData],
    ]
):
    """FMP Company Filings Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPCompanyFilingsQueryParams:
        """Transform the query params."""
        return FMPCompanyFilingsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPCompanyFilingsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_fmp.utils.helpers import get_data_many

        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/stable/sec-filings-search"
        url: str = ""

        if query.symbol and not query.cik:
            url = base_url + f"/symbol?symbol={query.symbol}"
        elif query.cik:
            url = base_url + f"/cik?cik={query.cik}"

        if not url:
            raise ValueError("Either symbol or cik must be provided.")

        start_date = (
            query.start_date
            if query.start_date
            else dateType.today() - timedelta(days=360)
        )
        url += f"&from={start_date}"
        end_date = query.end_date if query.end_date else dateType.today()
        url += f"&to={end_date}"
        url += f"&page={query.page}&limit={query.limit}&apikey={api_key}"

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPCompanyFilingsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPCompanyFilingsData]:
        """Return the transformed data."""
        if not data:
            raise EmptyDataError(
                f"No data found for the given query -> {query.model_dump()}"
            )
        return [FMPCompanyFilingsData.model_validate(d) for d in data]
