"""FMP Key Executives Fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.models.key_executives import (
    KeyExecutivesData,
    KeyExecutivesQueryParams,
)
from pydantic import validator

from openbb_fmp.utils.helpers import get_data_many


class FMPKeyExecutivesQueryParams(KeyExecutivesQueryParams):
    """FMP Key Executives QueryParams.

    Source: https://financialmodelingprep.com/developer/docs/#Key-Executives
    """


class FMPKeyExecutivesData(KeyExecutivesData):
    """FMP Key Executives Data."""

    class Config:
        fields = {
            "currency_pay": "currencyPay",
            "year_born": "yearBorn",
            "title_since": "titleSince",
        }

    @validator("titleSince", pre=True, check_fields=False)
    def time_validate(cls, v):  # pylint: disable=E0213
        return datetime.fromtimestamp(v / 1000)


class FMPKeyExecutivesFetcher(
    Fetcher[
        FMPKeyExecutivesQueryParams,
        List[FMPKeyExecutivesData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPKeyExecutivesQueryParams:
        return FMPKeyExecutivesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPKeyExecutivesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[FMPKeyExecutivesData]:
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        url = f"{base_url}/key-executives/{query.symbol}?apikey={api_key}"

        return get_data_many(url, FMPKeyExecutivesData, **kwargs)

    @staticmethod
    def transform_data(
        data: List[FMPKeyExecutivesData],
    ) -> List[FMPKeyExecutivesData]:
        return data
