"""Federal Reserve Bank of Chicago Publication Series Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FederalReserveChicagoPublicationSeriesQueryParams(QueryParams):
    """Chicago Fed Publication Series Query Parameters."""


class FederalReserveChicagoPublicationSeriesData(Data):
    """Chicago Fed Publication Series Data."""

    series: str = Field(
        description="The series slug used to filter the publications catalog."
    )
    name: str = Field(description="The human-readable series name.")
    count: int = Field(description="The number of documents published in the series.")


class FederalReserveChicagoPublicationSeriesFetcher(
    Fetcher[
        FederalReserveChicagoPublicationSeriesQueryParams,
        list[FederalReserveChicagoPublicationSeriesData],
    ]
):
    """Chicago Fed Publication Series Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveChicagoPublicationSeriesQueryParams:
        """Transform the query params."""
        return FederalReserveChicagoPublicationSeriesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveChicagoPublicationSeriesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """List the supported Chicago Fed publication series with document counts."""
        from openbb_federal_reserve.utils import fedinprint

        data = fedinprint.list_series("chicago")
        if not data:
            raise EmptyDataError("The request was returned empty.")
        return data

    @staticmethod
    def transform_data(
        query: FederalReserveChicagoPublicationSeriesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveChicagoPublicationSeriesData]:
        """Validate the series records."""
        return [
            FederalReserveChicagoPublicationSeriesData.model_validate(record)
            for record in data
        ]
