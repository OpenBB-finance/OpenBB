"""Intrinio Equity Info Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_info import (
    EquityInfoData,
    EquityInfoQueryParams,
)
from openbb_intrinio.utils.helpers import get_data_one
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
        IntrinioEquityInfoData,
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioEquityInfoQueryParams:
        """Transform the query."""
        return IntrinioEquityInfoQueryParams(**params)

    @staticmethod
    def extract_data(
        query: IntrinioEquityInfoQueryParams,  # pylint: disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        base_url = "https://api-v2.intrinio.com"
        url = f"{base_url}/companies/{query.symbol}?api_key={api_key}"
        return get_data_one(url, **kwargs)

    @staticmethod
    def transform_data(
        query: IntrinioEquityInfoQueryParams,
        data: List[Dict],
        **kwargs: Any,  # pylint: disable=unused-argument
    ) -> IntrinioEquityInfoData:
        """Transforms the data."""
        return IntrinioEquityInfoData.model_validate(data)
