"""Federal Reserve Bank of Dallas U.S. Gigafactory Map Model."""

from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = "https://www.dallasfed.org/-/media/documents/research/energy/battery.xlsx"

_SHEETS = {"battery_cells": "Data 1", "cathode": "Data 2"}


class FederalReserveDallasGigafactoryQueryParams(QueryParams):
    """Dallas Fed U.S. Gigafactory Map Query Parameters."""

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "options": [
                    {"label": "Battery Cells", "value": "battery_cells"},
                    {"label": "Cathode", "value": "cathode"},
                ]
            }
        },
    }

    table: Literal["battery_cells", "cathode"] = Field(
        default="battery_cells",
        description="Battery cell and pack plants, or cathode and chemical plants.",
    )


class FederalReserveDallasGigafactoryData(Data):
    """Dallas Fed U.S. Gigafactory Map Data."""

    facility_name: str | None = Field(default=None, description="The facility name.")
    operator: str | None = Field(default=None, description="The plant operator.")
    state: str | None = Field(default=None, description="The U.S. state.")
    latitude: float | None = Field(default=None, description="The latitude.")
    longitude: float | None = Field(default=None, description="The longitude.")


class FederalReserveDallasGigafactoryFetcher(
    Fetcher[
        FederalReserveDallasGigafactoryQueryParams,
        list[FederalReserveDallasGigafactoryData],
    ]
):
    """Dallas Fed U.S. Gigafactory Map Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveDallasGigafactoryQueryParams:
        """Transform the query params."""
        return FederalReserveDallasGigafactoryQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveDallasGigafactoryQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the gigafactory workbook from the Dallas Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> bytes:
            """Fetch the raw gigafactory workbook bytes."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content

        content = cached(
            "dallas_gigafactory",
            lambda: seconds_until_next_release("monthly"),
            _producer,
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveDallasGigafactoryQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveDallasGigafactoryData]:
        """Read the facility table into records."""
        from openbb_federal_reserve.utils.dallas import read_records

        records = read_records(data[0]["_raw"], _SHEETS[query.table])
        return [
            FederalReserveDallasGigafactoryData.model_validate(record)
            for record in records
        ]
