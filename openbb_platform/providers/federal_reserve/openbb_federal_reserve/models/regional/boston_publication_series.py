"""Federal Reserve Bank of Boston Publication Series Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FederalReserveBostonPublicationSeriesQueryParams(QueryParams):
    """Boston Fed Publication Series Query Parameters."""


class FederalReserveBostonPublicationSeriesData(Data):
    """Boston Fed Publication Series Data."""

    series: str = Field(
        description="The series slug used to filter the publications catalog."
    )
    name: str = Field(description="The human-readable series name.")
    count: int = Field(description="The number of documents published in the series.")


class FederalReserveBostonPublicationSeriesFetcher(
    Fetcher[
        FederalReserveBostonPublicationSeriesQueryParams,
        list[FederalReserveBostonPublicationSeriesData],
    ]
):
    """Boston Fed Publication Series Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveBostonPublicationSeriesQueryParams:
        """Transform the query params."""
        return FederalReserveBostonPublicationSeriesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveBostonPublicationSeriesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """List the supported Boston Fed publication series with document counts."""
        from openbb_federal_reserve.utils import fedinprint

        data = fedinprint.list_series("boston")
        if not data:
            raise EmptyDataError("The request was returned empty.")
        return data

    @staticmethod
    def transform_data(
        query: FederalReserveBostonPublicationSeriesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveBostonPublicationSeriesData]:
        """Validate the series records."""
        return [
            FederalReserveBostonPublicationSeriesData.model_validate(record)
            for record in data
        ]
