"""Federal Reserve Bank of San Francisco Publication Series Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FederalReserveSanFranciscoPublicationSeriesQueryParams(QueryParams):
    """San Francisco Fed Publication Series Query Parameters."""


class FederalReserveSanFranciscoPublicationSeriesData(Data):
    """San Francisco Fed Publication Series Data."""

    series: str = Field(
        description="The series slug used to filter the publications catalog."
    )
    name: str = Field(description="The human-readable series name.")
    count: int = Field(description="The number of documents published in the series.")


class FederalReserveSanFranciscoPublicationSeriesFetcher(
    Fetcher[
        FederalReserveSanFranciscoPublicationSeriesQueryParams,
        list[FederalReserveSanFranciscoPublicationSeriesData],
    ]
):
    """San Francisco Fed Publication Series Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveSanFranciscoPublicationSeriesQueryParams:
        """Transform the query params."""
        return FederalReserveSanFranciscoPublicationSeriesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveSanFranciscoPublicationSeriesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """List the supported San Francisco Fed publication series with document counts."""
        from openbb_federal_reserve.utils import fedinprint

        data = fedinprint.list_series("sf")
        if not data:
            raise EmptyDataError("The request was returned empty.")
        return data

    @staticmethod
    def transform_data(
        query: FederalReserveSanFranciscoPublicationSeriesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveSanFranciscoPublicationSeriesData]:
        """Validate the series records."""
        return [
            FederalReserveSanFranciscoPublicationSeriesData.model_validate(record)
            for record in data
        ]
