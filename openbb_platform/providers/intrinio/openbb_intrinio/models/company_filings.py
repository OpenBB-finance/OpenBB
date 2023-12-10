"""Intrinio Company Filings Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.company_filings import (
    CompanyFilingsData,
    CompanyFilingsQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.helpers import get_querystring
from openbb_intrinio.utils.helpers import get_data_many
from pydantic import Field


class IntrinioCompanyFilingsQueryParams(CompanyFilingsQueryParams):
    """Intrinio Company Filings Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_company_filings_v2
    """

    __alias_dict__ = {
        "form_type": "report_type",
        "limit": "page_size",
    }

    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["start_date"],
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS["end_date"],
    )
    thea_enabled: Optional[bool] = Field(
        default=None,
        description="Return filings that have been read by Intrinio's Thea NLP.",
    )


class IntrinioCompanyFilingsData(CompanyFilingsData):
    """Intrinio Company Filings Data."""

    id: str = Field(description="Intrinio ID of the filing.")
    period_end_date: Optional[dateType] = Field(
        default=None,
        description="Ending date of the fiscal period for the filing.",
    )
    sec_unique_id: str = Field(description="SEC unique ID of the filing.")
    instance_url: Optional[str] = Field(
        default=None,
        description="URL for the XBRL filing for the report.",
    )
    industry_group: str = Field(description="Industry group of the company.")
    industry_category: str = Field(description="Industry category of the company.")


class IntrinioCompanyFilingsFetcher(
    Fetcher[
        IntrinioCompanyFilingsQueryParams,
        List[IntrinioCompanyFilingsData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioCompanyFilingsQueryParams:
        """Transform the query."""
        transformed_params = params

        now = datetime.now().date()
        if params.get("start_date") is None:
            transformed_params["start_date"] = now - relativedelta(years=1)
        if params.get("end_date") is None:
            transformed_params["end_date"] = now

        return IntrinioCompanyFilingsQueryParams(**transformed_params)

    @staticmethod
    async def aextract_data(
        query: IntrinioCompanyFilingsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com/companies"
        query_str = get_querystring(query.model_dump(by_alias=True), ["symbol"])
        url = f"{base_url}/{query.symbol}/filings?{query_str}&api_key={api_key}"
        return await get_data_many(url, "filings", **kwargs)

    @staticmethod
    def transform_data(
        query: IntrinioCompanyFilingsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioCompanyFilingsData]:
        """Return the transformed data."""
        return [IntrinioCompanyFilingsData.model_validate(d) for d in data]
