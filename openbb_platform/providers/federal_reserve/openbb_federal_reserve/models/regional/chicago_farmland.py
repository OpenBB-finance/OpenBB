"""Federal Reserve Bank of Chicago Farmland Values Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = "https://api.data.chicagofed.org/Agriculture/Farmland-Values.csv"

_COLUMN_MAP = {
    "Year-over-year": "year_over_year",
    "Illinois": "illinois",
    "Indiana": "indiana",
    "Iowa": "iowa",
    "Wisconsin": "wisconsin",
}
_VALUE_COLUMNS = ["year_over_year", "illinois", "indiana", "iowa", "wisconsin"]


class FederalReserveChicagoFarmlandValuesQueryParams(QueryParams):
    """Chicago Fed Farmland Values Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveChicagoFarmlandValuesData(Data):
    """Chicago Fed Farmland Values Data."""

    date: dateType = Field(description="The quarter-end month of the observation.")
    year_over_year: float | None = Field(
        default=None,
        description="The District year-over-year percent change in farmland values.",
    )
    illinois: float | None = Field(
        default=None, description="The Illinois year-over-year percent change."
    )
    indiana: float | None = Field(
        default=None, description="The Indiana year-over-year percent change."
    )
    iowa: float | None = Field(
        default=None, description="The Iowa year-over-year percent change."
    )
    wisconsin: float | None = Field(
        default=None, description="The Wisconsin year-over-year percent change."
    )


class FederalReserveChicagoFarmlandValuesFetcher(
    Fetcher[
        FederalReserveChicagoFarmlandValuesQueryParams,
        list[FederalReserveChicagoFarmlandValuesData],
    ]
):
    """Chicago Fed Farmland Values Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveChicagoFarmlandValuesQueryParams:
        """Transform the query params."""
        return FederalReserveChicagoFarmlandValuesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveChicagoFarmlandValuesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Farmland Values CSV from the Chicago Fed."""
        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )
        from openbb_federal_reserve.utils.chicago import get_text

        text = cached(
            "chicago_farmland",
            lambda: seconds_until_next_release("quarterly"),
            lambda: get_text(URL),
        )
        if not text:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": text}]

    @staticmethod
    def transform_data(
        query: FederalReserveChicagoFarmlandValuesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveChicagoFarmlandValuesData]:
        """Parse the CSV and apply the date filters."""
        from io import StringIO

        from pandas import isna, read_csv, to_datetime, to_numeric

        frame = read_csv(StringIO(data[0]["_raw"]))
        frame = frame.rename(columns=_COLUMN_MAP)
        frame["date"] = to_datetime(frame["YYYYQ"], format="%Y/%m").dt.date
        frame = frame[["date", *_VALUE_COLUMNS]]
        for column in _VALUE_COLUMNS:
            frame[column] = to_numeric(frame[column], errors="coerce")

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveChicagoFarmlandValuesData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
