"""FMP Historical Splits Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_splits import (
    HistoricalSplitsData,
    HistoricalSplitsQueryParams,
)
from openbb_fmp.utils.helpers import get_data_many
from pydantic import field_validator


class FMPHistoricalSplitsQueryParams(HistoricalSplitsQueryParams):
    """FMP Historical Splits Query.

    Source: https://site.financialmodelingprep.com/developer/docs#splits-company
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
        list[FMPHistoricalSplitsData],
    ]
):
    """FMP Historical Splits Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPHistoricalSplitsQueryParams:
        """Transform the query params."""
        return FMPHistoricalSplitsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPHistoricalSplitsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = f"https://financialmodelingprep.com/stable/splits?symbol={query.symbol}&apikey={api_key}"

        return await get_data_many(url, "historical", **kwargs)

    @staticmethod
    def transform_data(
        query: FMPHistoricalSplitsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPHistoricalSplitsData]:
        """Return the transformed data."""
        return [FMPHistoricalSplitsData.model_validate(d) for d in data]
