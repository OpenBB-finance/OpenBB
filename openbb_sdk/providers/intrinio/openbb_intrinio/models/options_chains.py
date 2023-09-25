"""Intrinio Options Chains fetcher."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from openbb_intrinio.utils.helpers import get_data_many
from openbb_intrinio.utils.references import TICKER_EXCEPTIONS
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.options_chains import (
    OptionsChainsData,
    OptionsChainsQueryParams,
)
from pydantic import Field, validator


class IntrinioOptionsChainsQueryParams(OptionsChainsQueryParams):
    """Get the complete options chains (Historical) for a ticker from Intrinio.

    source: https://docs.intrinio.com/documentation/web_api/get_options_chain_eod_v2
    """

    date: Optional[str] = Field(
        description="Date for which the options chains are returned."
    )


class IntrinioOptionsChainsData(OptionsChainsData):
    """Intrinio Options Chains Data."""

    class Config:
        fields = {
            "contract_symbol": "code",
            "symbol": "ticker",
        }

    @validator("expiration", "date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the datetime object from the date string"""
        return datetime.strptime(v, "%Y-%m-%d")


class IntrinioOptionsChainsFetcher(
    Fetcher[IntrinioOptionsChainsQueryParams, List[IntrinioOptionsChainsData]]
):
    """Perform TET for the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioOptionsChainsQueryParams:
        """Transform the query."""
        transform_params = params

        now = datetime.now().date()
        if params.get("date") is None:
            transform_params["date"] = now - timedelta(days=1)

        return IntrinioOptionsChainsQueryParams(**transform_params)

    @staticmethod
    def extract_data(
        query: IntrinioOptionsChainsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        base_url = "https://api-v2.intrinio.com/options"

        if query.symbol in TICKER_EXCEPTIONS:
            query.symbol = f"${query.symbol}"

        url = (
            f"{base_url}/expirations/{query.symbol}/eod?"
            f"after={query.date}&api_key={api_key}"
        )
        expirations = get_data_many(url, "expirations", **kwargs)

        data = []

        for expiration in expirations:
            url = (
                f"{base_url}/chain/{query.symbol}/{expiration}/eod?"
                f"date={query.date}&api_key={api_key}"
            )
            response = get_data_many(url, "chain", **kwargs)
            data.extend(response)

        return data

    @staticmethod
    def transform_data(data: List[Dict]) -> List[IntrinioOptionsChainsData]:
        """Return the transformed data."""
        data = [{**item["option"], **item["prices"]} for item in data]
        return [IntrinioOptionsChainsData.parse_obj(d) for d in data]
