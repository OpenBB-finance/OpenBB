"""Federal Reserve Bank of Philadelphia Publication Series Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FederalReservePhiladelphiaPublicationSeriesQueryParams(QueryParams):
    """Philadelphia Fed Publication Series Query Parameters."""


class FederalReservePhiladelphiaPublicationSeriesData(Data):
    """Philadelphia Fed Publication Series Data."""

    series: str = Field(
        description="The series slug used to filter the publications catalog."
    )
    name: str = Field(description="The human-readable series name.")
    count: int = Field(description="The number of documents published in the series.")


class FederalReservePhiladelphiaPublicationSeriesFetcher(
    Fetcher[
        FederalReservePhiladelphiaPublicationSeriesQueryParams,
        list[FederalReservePhiladelphiaPublicationSeriesData],
    ]
):
    """Philadelphia Fed Publication Series Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReservePhiladelphiaPublicationSeriesQueryParams:
        """Transform the query params."""
        return FederalReservePhiladelphiaPublicationSeriesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReservePhiladelphiaPublicationSeriesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """List the supported Philadelphia Fed publication series with document counts."""
        from openbb_federal_reserve.utils import fedinprint

        data = fedinprint.list_series("philadelphia")
        if not data:
            raise EmptyDataError("The request was returned empty.")
        return data

    @staticmethod
    def transform_data(
        query: FederalReservePhiladelphiaPublicationSeriesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReservePhiladelphiaPublicationSeriesData]:
        """Validate the series records."""
        return [
            FederalReservePhiladelphiaPublicationSeriesData.model_validate(record)
            for record in data
        ]
