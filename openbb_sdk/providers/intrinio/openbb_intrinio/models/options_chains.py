"""Intrinio Options Chains fetcher."""

from datetime import (
    date as dateType,
    datetime,
    timedelta,
)
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

    __alias_dict__ = {
        "contract_symbol": "code",
        "symbol": "ticker",
    }

    @validator("expiration", "date", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the datetime object from the date string"""
        return datetime.strptime(v, "%Y-%m-%d")


def get_weekday(date: dateType) -> str:
    if date.weekday() in [5, 6]:
        date = date - timedelta(days=2 if date.weekday() == 6 else 1)
    return date.strftime("%Y-%m-%d")


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

        def get_expirations(date: dateType) -> List[str]:
            """Return the expirations for the given date."""
            url = (
                f"{base_url}/expirations/{query.symbol}/eod?"
                f"after={date}&api_key={api_key}"
            )
            return get_data_many(url, "expirations", **kwargs)

        def get_data(expirations: List[str]) -> List[Dict]:
            """Return the data for the given expiration."""
            data = []
            for expiration in expirations:
                url = (
                    f"{base_url}/chain/{query.symbol}/{expiration}/eod?"
                    f"date={query.date}&api_key={api_key}"
                )
                response = get_data_many(url, "chain", **kwargs)
                data.extend(response)

            return data

        if len(data := get_data(get_expirations(get_weekday(query.date)))) == 0:
            data = get_data(
                get_expirations(get_weekday(query.date - timedelta(days=1)))
            )

        return data

    @staticmethod
    def transform_data(data: List[Dict]) -> List[IntrinioOptionsChainsData]:
        """Return the transformed data."""
        data = [{**item["option"], **item["prices"]} for item in data]
        return [IntrinioOptionsChainsData.model_validate(d) for d in data]
