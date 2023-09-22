"""FMP Key Executives Fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.key_executives import (
    KeyExecutivesData,
    KeyExecutivesQueryParams,
)
from pydantic import validator


class FMPKeyExecutivesQueryParams(KeyExecutivesQueryParams):
    """FMP Key Executives QueryParams.

    Source: https://financialmodelingprep.com/developer/docs/#Key-Executives
    """


class FMPKeyExecutivesData(KeyExecutivesData):
    """FMP Key Executives Data."""

    @validator("titleSince", pre=True, check_fields=False)
    def time_validate(cls, v):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.fromtimestamp(v / 1000)


class FMPKeyExecutivesFetcher(
    Fetcher[
        FMPKeyExecutivesQueryParams,
        List[FMPKeyExecutivesData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPKeyExecutivesQueryParams:
        """Transform the query params."""
        return FMPKeyExecutivesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPKeyExecutivesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        url = f"{base_url}/key-executives/{query.symbol}?apikey={api_key}"

        return get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPKeyExecutivesData]:
        """Return the transformed data."""
        return [FMPKeyExecutivesData.parse_obj(d) for d in data]
