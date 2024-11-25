"""Intrinio Equity Info Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_info import (
    EquityInfoData,
    EquityInfoQueryParams,
)
from openbb_core.provider.utils.helpers import (
    amake_requests,
)
from openbb_intrinio.utils.helpers import response_callback
from pydantic import Field


class IntrinioEquityInfoQueryParams(EquityInfoQueryParams):
    """Intrinio Equity Info Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_company_v2
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class IntrinioEquityInfoData(EquityInfoData):
    """Intrinio Equity Info Data."""

    __alias_dict__ = {
        "symbol": "ticker",
    }

    id: str = Field(default=None, description="Intrinio ID for the company.")
    thea_enabled: Optional[bool] = Field(
        default=None, description="Whether the company has been enabled for Thea."
    )


class IntrinioEquityInfoFetcher(
    Fetcher[
        IntrinioEquityInfoQueryParams,
        List[IntrinioEquityInfoData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioEquityInfoQueryParams:
        """Transform the query."""
        return IntrinioEquityInfoQueryParams(**params)

    # pylint: disable=W0613:unused-argument
    @staticmethod
    async def aextract_data(
        query: IntrinioEquityInfoQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        base_url = "https://api-v2.intrinio.com"

        urls = [
            f"{base_url}/companies/{s.strip()}?api_key={api_key}"
            for s in query.symbol.split(",")
        ]

        return await amake_requests(urls, response_callback, **kwargs)

    # pylint: disable=W0613:unused-argument
    @staticmethod
    def transform_data(
        query: IntrinioEquityInfoQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[IntrinioEquityInfoData]:
        """Transform the data."""
        return [IntrinioEquityInfoData.model_validate(d) for d in data]
