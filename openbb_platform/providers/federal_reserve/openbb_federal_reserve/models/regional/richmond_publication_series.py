"""Federal Reserve Bank of Richmond Publication Series Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FederalReserveRichmondPublicationSeriesQueryParams(QueryParams):
    """Richmond Fed Publication Series Query Parameters."""


class FederalReserveRichmondPublicationSeriesData(Data):
    """Richmond Fed Publication Series Data."""

    series: str = Field(
        description="The series slug used to filter the publications catalog."
    )
    name: str = Field(description="The human-readable series name.")
    count: int = Field(description="The number of documents published in the series.")


class FederalReserveRichmondPublicationSeriesFetcher(
    Fetcher[
        FederalReserveRichmondPublicationSeriesQueryParams,
        list[FederalReserveRichmondPublicationSeriesData],
    ]
):
    """Richmond Fed Publication Series Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveRichmondPublicationSeriesQueryParams:
        """Transform the query params."""
        return FederalReserveRichmondPublicationSeriesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveRichmondPublicationSeriesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """List the supported Richmond Fed publication series with document counts."""
        from openbb_federal_reserve.utils import fedinprint

        data = fedinprint.list_series("richmond")
        if not data:
            raise EmptyDataError("The request was returned empty.")
        return data

    @staticmethod
    def transform_data(
        query: FederalReserveRichmondPublicationSeriesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveRichmondPublicationSeriesData]:
        """Validate the series records."""
        return [
            FederalReserveRichmondPublicationSeriesData.model_validate(record)
            for record in data
        ]
