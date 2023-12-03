"""Intrinio Options Chains Model."""

from concurrent.futures import ThreadPoolExecutor
from datetime import (
    date as dateType,
    datetime,
    timedelta,
)
from itertools import repeat
from typing import Any, Dict, List, Optional

from dateutil import parser
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.options_chains import (
    OptionsChainsData,
    OptionsChainsQueryParams,
)
from openbb_intrinio.utils.helpers import get_data_many, get_weekday
from pydantic import Field, field_validator


class IntrinioOptionsChainsQueryParams(OptionsChainsQueryParams):
    """Intrinio Options Chains Query.

    source: https://docs.intrinio.com/documentation/web_api/get_options_chain_eod_v2
    """

    date: Optional[dateType] = Field(
        description="Date for which the options chains are returned."
    )


class IntrinioOptionsChainsData(OptionsChainsData):
    """Intrinio Options Chains Data."""

    __alias_dict__ = {
        "contract_symbol": "code",
        "symbol": "ticker",
        "eod_date": "date",
        "option_type": "type",
    }

    @field_validator("expiration", "date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the datetime object from the date string."""
        # only pass it to the parser if it is not a datetime object
        if isinstance(v, str):
            return parser.parse(v)


class IntrinioOptionsChainsFetcher(
    Fetcher[IntrinioOptionsChainsQueryParams, List[IntrinioOptionsChainsData]]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioOptionsChainsQueryParams:
        """Transform the query."""
        transform_params = params

        now = datetime.now().date()
        if params.get("date") is None:
            transform_params["date"] = (now - timedelta(days=1)).strftime("%Y-%m-%d")
        elif isinstance(params["date"], dateType):
            transform_params["date"] = params["date"].strftime("%Y-%m-%d")
        else:
            transform_params["date"] = parser.parse(params["date"]).date()

        return IntrinioOptionsChainsQueryParams(**transform_params)

    @staticmethod
    def extract_data(
        query: IntrinioOptionsChainsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""

        data: List = []
        base_url = "https://api-v2.intrinio.com/options"

        def get_options_chains(
            expiration: str, data: List[IntrinioOptionsChainsData]
        ) -> None:
            """Return the data for the given expiration."""
            url = (
                f"{base_url}/chain/{query.symbol}/{expiration}/eod?"
                f"date={query.date}&api_key={api_key}"
            )
            response = get_data_many(url, "chain", **kwargs)
            data.extend(response)

        def get_data(date: str) -> None:
            """Fetch data for a given date using ThreadPoolExecutor."""
            url = (
                f"{base_url}/expirations/{query.symbol}/eod?"
                f"after={date}&api_key={api_key}"
            )
            expirations = get_data_many(url, "expirations", **kwargs)

            with ThreadPoolExecutor() as executor:
                executor.map(get_options_chains, expirations, repeat(data))

        date = get_weekday(query.date)
        get_data(date)

        if not data:
            date = get_weekday(query.date - timedelta(days=1))
            get_data(date)

        return data

    @staticmethod
    def transform_data(
        query: IntrinioOptionsChainsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioOptionsChainsData]:
        """Return the transformed data."""
        data = [{**item["option"], **item["prices"]} for item in data]
        return [IntrinioOptionsChainsData.model_validate(d) for d in data]
