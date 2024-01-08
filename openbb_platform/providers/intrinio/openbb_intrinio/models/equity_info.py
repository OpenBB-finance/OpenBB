"""Intrinio Equity Info Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_info import (
    EquityInfoData,
    EquityInfoQueryParams,
)
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    amake_requests,
)
from pydantic import Field


class IntrinioEquityInfoQueryParams(EquityInfoQueryParams):
    """Intrinio Equity Info Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_company_v2
    """


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

    @staticmethod
    async def aextract_data(
        query: IntrinioEquityInfoQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        base_url = "https://api-v2.intrinio.com"

        async def callback(response: ClientResponse, _: Any) -> dict:
            """Return the response."""
            if response.status != 200:
                return {}

            response_data = await response.json()
            response_data["symbol"] = response.url.parts[-1]

            return response_data

        urls = [
            f"{base_url}/companies/{s.strip()}?api_key={api_key}"
            for s in query.symbol.split(",")
        ]

        return await amake_requests(urls, callback, **kwargs)

    @staticmethod
    def transform_data(
        query: IntrinioEquityInfoQueryParams,
        data: List[Dict],
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> List[IntrinioEquityInfoData]:
        """Transforms the data."""
        return [IntrinioEquityInfoData.model_validate(d) for d in data]
