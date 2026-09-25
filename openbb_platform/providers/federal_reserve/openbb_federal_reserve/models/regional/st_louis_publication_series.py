"""Federal Reserve Bank of St. Louis Publication Series Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FederalReserveStLouisPublicationSeriesQueryParams(QueryParams):
    """St. Louis Fed Publication Series Query Parameters."""


class FederalReserveStLouisPublicationSeriesData(Data):
    """St. Louis Fed Publication Series Data."""

    series: str = Field(
        description="The series slug used to filter the publications catalog."
    )
    name: str = Field(description="The human-readable series name.")
    count: int = Field(description="The number of documents published in the series.")


class FederalReserveStLouisPublicationSeriesFetcher(
    Fetcher[
        FederalReserveStLouisPublicationSeriesQueryParams,
        list[FederalReserveStLouisPublicationSeriesData],
    ]
):
    """St. Louis Fed Publication Series Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveStLouisPublicationSeriesQueryParams:
        """Transform the query params."""
        return FederalReserveStLouisPublicationSeriesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveStLouisPublicationSeriesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """List the supported publication series with their document counts."""
        from openbb_federal_reserve.utils.st_louis import list_series

        data = list_series()
        if not data:
            raise EmptyDataError("The request was returned empty.")
        return data

    @staticmethod
    def transform_data(
        query: FederalReserveStLouisPublicationSeriesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveStLouisPublicationSeriesData]:
        """Validate the series records."""
        return [
            FederalReserveStLouisPublicationSeriesData.model_validate(record)
            for record in data
        ]
