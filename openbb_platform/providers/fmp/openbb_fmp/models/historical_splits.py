"""FMP Historical Splits Model."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_splits import (
    HistoricalSplitsData,
    HistoricalSplitsQueryParams,
)
from openbb_fmp.utils.helpers import create_url, get_data_many
from pydantic import field_validator


class FMPHistoricalSplitsQueryParams(HistoricalSplitsQueryParams):
    """FMP Historical Splits Query.

    Source: https://site.financialmodelingprep.com/developer/docs/historical-stock-splits-api/
    """


class FMPHistoricalSplitsData(HistoricalSplitsData):
    """FMP Historical Splits Data."""

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def date_validate(cls, v: str):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d") if v else None


class FMPHistoricalSplitsFetcher(
    Fetcher[
        FMPHistoricalSplitsQueryParams,
        List[FMPHistoricalSplitsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPHistoricalSplitsQueryParams:
        """Transform the query params."""
        return FMPHistoricalSplitsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPHistoricalSplitsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3, f"historical-price-full/stock_split/{query.symbol}", api_key
        )

        return await get_data_many(url, "historical", **kwargs)

    @staticmethod
    def transform_data(
        query: FMPHistoricalSplitsQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPHistoricalSplitsData]:
        """Return the transformed data."""
        return [FMPHistoricalSplitsData.model_validate(d) for d in data]
