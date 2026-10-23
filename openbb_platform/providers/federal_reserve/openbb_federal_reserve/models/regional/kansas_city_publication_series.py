"""Federal Reserve Bank of Kansas City Publication Series Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field


class FederalReserveKansasCityPublicationSeriesQueryParams(QueryParams):
    """Kansas City Fed Publication Series Query Parameters."""


class FederalReserveKansasCityPublicationSeriesData(Data):
    """Kansas City Fed Publication Series Data."""

    series: str = Field(
        description="The series slug used to filter the publications catalog."
    )
    name: str = Field(description="The human-readable series name.")
    count: int = Field(description="The number of documents published in the series.")


class FederalReserveKansasCityPublicationSeriesFetcher(
    Fetcher[
        FederalReserveKansasCityPublicationSeriesQueryParams,
        list[FederalReserveKansasCityPublicationSeriesData],
    ]
):
    """Kansas City Fed Publication Series Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveKansasCityPublicationSeriesQueryParams:
        """Transform the query params."""
        return FederalReserveKansasCityPublicationSeriesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveKansasCityPublicationSeriesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """List the supported Kansas City Fed publication series with document counts."""
        from openbb_federal_reserve.utils import fedinprint

        data = fedinprint.list_series("kc")
        if not data:
            raise EmptyDataError("The request was returned empty.")
        return data

    @staticmethod
    def transform_data(
        query: FederalReserveKansasCityPublicationSeriesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveKansasCityPublicationSeriesData]:
        """Validate the series records."""
        return [
            FederalReserveKansasCityPublicationSeriesData.model_validate(record)
            for record in data
        ]
