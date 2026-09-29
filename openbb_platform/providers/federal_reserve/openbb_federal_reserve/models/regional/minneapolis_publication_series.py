"""Federal Reserve Bank of Minneapolis Publication Series Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FederalReserveMinneapolisPublicationSeriesQueryParams(QueryParams):
    """Minneapolis Fed Publication Series Query Parameters."""


class FederalReserveMinneapolisPublicationSeriesData(Data):
    """Minneapolis Fed Publication Series Data."""

    series: str = Field(
        description="The series slug used to filter the publications catalog."
    )
    name: str = Field(description="The human-readable series name.")
    count: int = Field(description="The number of documents published in the series.")


class FederalReserveMinneapolisPublicationSeriesFetcher(
    Fetcher[
        FederalReserveMinneapolisPublicationSeriesQueryParams,
        list[FederalReserveMinneapolisPublicationSeriesData],
    ]
):
    """Minneapolis Fed Publication Series Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveMinneapolisPublicationSeriesQueryParams:
        """Transform the query params."""
        return FederalReserveMinneapolisPublicationSeriesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveMinneapolisPublicationSeriesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """List the supported Minneapolis Fed publication series with document counts."""
        from openbb_federal_reserve.utils import fedinprint

        data = fedinprint.list_series("minneapolis")
        if not data:
            raise EmptyDataError("The request was returned empty.")
        return data

    @staticmethod
    def transform_data(
        query: FederalReserveMinneapolisPublicationSeriesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveMinneapolisPublicationSeriesData]:
        """Validate the series records."""
        return [
            FederalReserveMinneapolisPublicationSeriesData.model_validate(record)
            for record in data
        ]
