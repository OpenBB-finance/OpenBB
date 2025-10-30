"""Stockgrid Short Volume Model."""

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.short_volume import (
    ShortVolumeData,
    ShortVolumeQueryParams,
)
from pydantic import Field, field_validator


class StockgridShortVolumeQueryParams(ShortVolumeQueryParams):
    """Stockgrid Short Volume Query.

    Source: https://www.stockgrid.io/
    """


class StockgridShortVolumeData(ShortVolumeData):
    """Stockgrid Short Volume Data."""

    __alias_dict__ = {"short_volume_percent": "short_volume%", "symbol": "ticker"}

    close: float | None = Field(
        default=None, description="Closing price of the stock on the date."
    )

    short_volume_percent: float | None = Field(
        default=None,
        description="Percentage of the total volume that was short volume.",
    )

    @field_validator("date", mode="before", check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the datetime object from the date string."""
        return datetime.strptime(v, "%Y-%m-%d").date()


class StockgridShortVolumeFetcher(
    Fetcher[StockgridShortVolumeQueryParams, list[StockgridShortVolumeData]]
):
    """Transform the query, extract and transform the data from the Stockgrid endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> StockgridShortVolumeQueryParams:
        """Transform query params."""
        return StockgridShortVolumeQueryParams(**params)

    # pylint: disable=unused-argument
    @staticmethod
    def extract_data(
        query: StockgridShortVolumeQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Get data from Stockgrid."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import make_request

        url = f"https://www.stockgrid.io/get_dark_pool_individual_data?ticker={query.symbol}"
        data = make_request(url).json()
        return data["individual_short_volume_table"]["data"]

    @staticmethod
    def transform_data(
        query: ShortVolumeQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[StockgridShortVolumeData]:
        """Transform data."""
        return [StockgridShortVolumeData.model_validate(d) for d in data]
