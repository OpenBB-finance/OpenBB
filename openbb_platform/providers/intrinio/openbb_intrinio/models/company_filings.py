"""Intrinio Company Filings Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.annotated_result import AnnotatedResult
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_filings import (
    CompanyFilingsData,
    CompanyFilingsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, field_validator


class IntrinioCompanyFilingsQueryParams(CompanyFilingsQueryParams):
    """Intrinio Company Filings Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_company_filings_v2
    """

    __alias_dict__ = {"form_type": "report_type", "limit": "page_size"}

    form_type: Optional[str] = Field(
        default=None, description="SEC form type to filter by."
    )
    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["start_date"],
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["end_date"],
    )
    limit: Optional[int] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["limit"],
    )
    thea_enabled: Optional[bool] = Field(
        default=None,
        description="Return filings that have been read by Intrinio's Thea NLP.",
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _validate_symbol(cls, v):
        """Validate symbol."""
        if not v:
            raise ValueError("Symbol is required for Intrinio.")
        return v


class IntrinioCompanyFilingsData(CompanyFilingsData):
    """Intrinio Company Filings Data."""

    id: str = Field(description="Intrinio ID of the filing.")
    period_end_date: Optional[dateType] = Field(
        default=None,
        description="Ending date of the fiscal period for the filing.",
    )
    accepted_date: Optional[datetime] = Field(
        default=None, description="Accepted date of the filing."
    )
    sec_unique_id: str = Field(description="SEC unique ID of the filing.")
    filing_url: Optional[str] = Field(
        default=None, description="URL to the filing page."
    )
    instance_url: Optional[str] = Field(
        default=None,
        description="URL for the XBRL filing for the report.",
    )
    industry_group: str = Field(description="Industry group of the company.")
    industry_category: str = Field(description="Industry category of the company.")
    word_count: Optional[int] = Field(
        default=None, description="Number of words in the filing, if available."
    )


class IntrinioCompanyFilingsFetcher(
    Fetcher[
        IntrinioCompanyFilingsQueryParams,
        list[IntrinioCompanyFilingsData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> IntrinioCompanyFilingsQueryParams:
        """Transform the query."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None and params.get("form_type") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)
        if params.get("end_date") is None and params.get("form_type") is None:
            transformed_params["end_date"] = now

        return IntrinioCompanyFilingsQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: IntrinioCompanyFilingsQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the Intrinio endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.errors import EmptyDataError, OpenBBError
        from openbb_core.provider.utils.helpers import (
            get_async_requests_session,
            get_querystring,
        )

        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com/companies"
        query_str = get_querystring(
            query.model_dump(by_alias=True), ["symbol", "limit", "page_size"]
        )
        url = f"{base_url}/{query.symbol}/filings?{query_str}&page_size={query.limit or 10000}&api_key={api_key}"
        results: list = []
        metadata: dict = {}
        session = await get_async_requests_session()

        async with await session.get(url) as response:
            if response.status != 200:
                raise OpenBBError(
                    f"Error fetching data from Intrinio: {response.status} -> {response.text}"
                )
            result = await response.json()
            if filings := result.get("filings", []):
                results.extend(filings)

            metadata = result.get("company", {})

            while next_page := result.get("next_page"):
                url += f"&next_page={next_page}"
                async with await session.get(url) as next_response:
                    if response.status != 200:
                        raise OpenBBError(
                            f"Error fetching data from Intrinio: {response.status} -> {response.text}"
                        )
                    result = await next_response.json()
                    if filings := result.get("filings", []):
                        results.extend(filings)

        if not results:
            raise EmptyDataError("No data was returned for the symbol provided.")

        return {"data": results, "metadata": metadata}

    @staticmethod
    def transform_data(
        query: IntrinioCompanyFilingsQueryParams, data: dict, **kwargs: Any
    ) -> AnnotatedResult[list[IntrinioCompanyFilingsData]]:
        """Return the transformed data."""
        return AnnotatedResult(
            result=[
                IntrinioCompanyFilingsData.model_validate(
                    {
                        k: v
                        for k, v in d.items()
                        if k not in ["thea_enabled", "earnings_release"]
                    }
                )
                for d in data.get("data", [])
            ],
            metadata=data.get("metadata", {}),
        )
