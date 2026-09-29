"""Federal Reserve Bank of Dallas U.S. Lithium Projects Map Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = "https://www.dallasfed.org/-/media/documents/research/energy/lithium.xlsx"


class FederalReserveDallasLithiumQueryParams(QueryParams):
    """Dallas Fed U.S. Lithium Projects Map Query Parameters."""


class FederalReserveDallasLithiumData(Data):
    """Dallas Fed U.S. Lithium Projects Map Data."""

    project_name: str | None = Field(default=None, description="The project name.")
    company: str | None = Field(default=None, description="The developer.")
    type: str | None = Field(default=None, description="The lithium resource type.")
    stage: str | None = Field(default=None, description="The development stage.")
    latitude: float | None = Field(default=None, description="The latitude.")
    longitude: float | None = Field(default=None, description="The longitude.")


class FederalReserveDallasLithiumFetcher(
    Fetcher[
        FederalReserveDallasLithiumQueryParams,
        list[FederalReserveDallasLithiumData],
    ]
):
    """Dallas Fed U.S. Lithium Projects Map Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveDallasLithiumQueryParams:
        """Transform the query params."""
        return FederalReserveDallasLithiumQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveDallasLithiumQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the lithium projects workbook from the Dallas Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> bytes:
            """Fetch the raw lithium projects workbook bytes."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content

        content = cached(
            "dallas_lithium",
            lambda: seconds_until_next_release("monthly"),
            _producer,
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveDallasLithiumQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveDallasLithiumData]:
        """Read the project table into records."""
        from openbb_federal_reserve.utils.dallas import read_records

        records = read_records(data[0]["_raw"], "Data")
        return [
            FederalReserveDallasLithiumData.model_validate(record) for record in records
        ]
