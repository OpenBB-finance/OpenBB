"""FMP Key Executives Model."""

# pylint: disable=unused-argument

from datetime import (
    date as dateType,
)
from typing import Any, Dict, List, Optional, Union

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.key_executives import (
    KeyExecutivesData,
    KeyExecutivesQueryParams,
)
from openbb_core.provider.utils.helpers import safe_fromtimestamp
from openbb_fmp.utils.helpers import get_data_many
from pydantic import field_validator


class FMPKeyExecutivesQueryParams(KeyExecutivesQueryParams):
    """FMP Key Executives Query.

    Source: https://financialmodelingprep.com/developer/docs/#Key-Executives
    """


class FMPKeyExecutivesData(KeyExecutivesData):
    """FMP Key Executives Data."""

    @field_validator("titleSince", mode="before", check_fields=False)
    @classmethod
    def time_validate(cls, v: Union[float, int]) -> Optional[dateType]:
        """Return the date as a datetime object."""
        if v:
            v = v / 1000
            return safe_fromtimestamp(v)
        return v  # type: ignore


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
    async def aextract_data(
        query: FMPKeyExecutivesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        base_url = "https://financialmodelingprep.com/api/v3"
        url = f"{base_url}/key-executives/{query.symbol}?apikey={api_key}"

        return await get_data_many(url, **kwargs)

    @staticmethod
    def transform_data(
        query: FMPKeyExecutivesQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPKeyExecutivesData]:
        """Return the transformed data."""
        return [FMPKeyExecutivesData.model_validate(d) for d in data]
