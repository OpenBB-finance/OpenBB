"""Federal Reserve Bank of Cleveland Publication Series Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FederalReserveClevelandPublicationSeriesQueryParams(QueryParams):
    """Cleveland Fed Publication Series Query Parameters."""


class FederalReserveClevelandPublicationSeriesData(Data):
    """Cleveland Fed Publication Series Data."""

    series: str = Field(
        description="The series slug used to filter the publications catalog."
    )
    name: str = Field(description="The human-readable series name.")
    count: int = Field(description="The number of documents published in the series.")


class FederalReserveClevelandPublicationSeriesFetcher(
    Fetcher[
        FederalReserveClevelandPublicationSeriesQueryParams,
        list[FederalReserveClevelandPublicationSeriesData],
    ]
):
    """Cleveland Fed Publication Series Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveClevelandPublicationSeriesQueryParams:
        """Transform the query params."""
        return FederalReserveClevelandPublicationSeriesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveClevelandPublicationSeriesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """List the supported Cleveland Fed publication series with document counts."""
        from openbb_federal_reserve.utils import fedinprint

        data = fedinprint.list_series("cleveland")
        if not data:
            raise EmptyDataError("The request was returned empty.")
        return data

    @staticmethod
    def transform_data(
        query: FederalReserveClevelandPublicationSeriesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveClevelandPublicationSeriesData]:
        """Validate the series records."""
        return [
            FederalReserveClevelandPublicationSeriesData.model_validate(record)
            for record in data
        ]
