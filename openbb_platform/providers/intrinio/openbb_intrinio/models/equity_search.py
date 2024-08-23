"""Intrinio Equity Search Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_search import (
    EquitySearchData,
    EquitySearchQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.helpers import get_querystring
from openbb_intrinio.utils.helpers import get_data_one
from pydantic import Field


class IntrinioEquitySearchQueryParams(EquitySearchQueryParams):
    """Intrinio Equity Search Query.

    Source: https://docs.intrinio.com/documentation/web_api/search_companies_v2
    """

    __alias_dict__ = {
        "limit": "page_size",
    }

    active: bool = Field(
        default=True,
        description="When true, return companies that are actively traded (having stock prices within the past 14 days)."
        + " When false, return companies that are not actively traded or never have been traded.",
    )
    limit: Optional[int] = Field(
        default=10000,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
    )


class IntrinioEquitySearchData(EquitySearchData):
    """Intrinio Equity Search Data."""

    __alias_dict__ = {
        "intrinio_id": "id",
        "symbol": "ticker",
    }

    cik: Optional[str] = Field(description=DATA_DESCRIPTIONS.get("CIK", ""))
    lei: Optional[str] = Field(
        description="The Legal Entity Identifier (LEI) of the company."
    )
    intrinio_id: str = Field(description="The Intrinio ID of the company.")


class IntrinioEquitySearchFetcher(
    Fetcher[
        IntrinioEquitySearchQueryParams,
        List[IntrinioEquitySearchData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioEquitySearchQueryParams:
        """Transform the query."""
        return IntrinioEquitySearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioEquitySearchQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""

        api_key = credentials.get("intrinio_api_key") if credentials else ""
        query_str = get_querystring(query.model_dump(by_alias=True), ["is_symbol"])
        base_url = "https://api-v2.intrinio.com/companies/search?"
        url = f"{base_url}{query_str}&api_key={api_key}"
        data = await get_data_one(url, **kwargs)
        return data

    @staticmethod
    def transform_data(
        query: IntrinioEquitySearchQueryParams, data: Dict, **kwargs: Any
    ) -> List[IntrinioEquitySearchData]:
        """Transform the data to the standard format."""

        return [IntrinioEquitySearchData.model_validate(d) for d in data["companies"]]
