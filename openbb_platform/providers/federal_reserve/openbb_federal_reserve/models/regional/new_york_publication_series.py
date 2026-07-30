"""Federal Reserve Bank of New York Publication Series Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FederalReserveNewYorkPublicationSeriesQueryParams(QueryParams):
    """New York Fed Publication Series Query Parameters."""


class FederalReserveNewYorkPublicationSeriesData(Data):
    """New York Fed Publication Series Data."""

    series: str = Field(
        description="The series slug used to filter the publications catalog."
    )
    name: str = Field(description="The human-readable series name.")
    count: int = Field(description="The number of documents published in the series.")


class FederalReserveNewYorkPublicationSeriesFetcher(
    Fetcher[
        FederalReserveNewYorkPublicationSeriesQueryParams,
        list[FederalReserveNewYorkPublicationSeriesData],
    ]
):
    """New York Fed Publication Series Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveNewYorkPublicationSeriesQueryParams:
        """Transform the query params."""
        return FederalReserveNewYorkPublicationSeriesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveNewYorkPublicationSeriesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """List the supported New York Fed publication series with document counts."""
        from openbb_federal_reserve.utils import fedinprint

        data = fedinprint.list_series("ny")
        if not data:
            raise EmptyDataError("The request was returned empty.")
        return data

    @staticmethod
    def transform_data(
        query: FederalReserveNewYorkPublicationSeriesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveNewYorkPublicationSeriesData]:
        """Validate the series records."""
        return [
            FederalReserveNewYorkPublicationSeriesData.model_validate(record)
            for record in data
        ]
