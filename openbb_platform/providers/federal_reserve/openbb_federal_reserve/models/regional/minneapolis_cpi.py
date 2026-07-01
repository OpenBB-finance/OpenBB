"""Federal Reserve Bank of Minneapolis Regional CPI Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

BASE_URL = (
    "https://www.minneapolisfed.org/~/media/Assets/Pages/regional-economic-indicators"
)
CPI_U_URL = f"{BASE_URL}/CPI_U.csv"
CORE_URL = f"{BASE_URL}/CPI_U_less_food_energy.csv"

_GEOGRAPHIES = ["US", "West North Central", "Mountain"]
_MEASURES = (("CPI-U", "_cpi_u"), ("Core", "_core"))


class FederalReserveMinneapolisCpiQueryParams(QueryParams):
    """Minneapolis Fed Regional CPI Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveMinneapolisCpiData(Data):
    """Minneapolis Fed Regional CPI Data.

    One row per observation month, with one column per CPI measure and geography
    carrying the year-over-year percent change. Columns are labelled by measure
    (headline ``CPI-U`` or ``Core``) and geography (the United States or a Census
    division that overlaps the Ninth District).
    """

    date: dateType = Field(description="The observation month.")


class FederalReserveMinneapolisCpiFetcher(
    Fetcher[
        FederalReserveMinneapolisCpiQueryParams,
        list[FederalReserveMinneapolisCpiData],
    ]
):
    """Minneapolis Fed Regional CPI Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveMinneapolisCpiQueryParams:
        """Transform the query params."""
        return FederalReserveMinneapolisCpiQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveMinneapolisCpiQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the headline and core CPI CSVs from the Minneapolis Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer(url: str) -> str:
            """Fetch the raw CPI CSV text for a given URL."""
            response = make_request(url)
            response.raise_for_status()
            return response.text

        cpi_u = cached(
            "minneapolis_cpi_u",
            lambda: seconds_until_next_release("monthly"),
            lambda: _producer(CPI_U_URL),
        )
        core = cached(
            "minneapolis_cpi_core",
            lambda: seconds_until_next_release("monthly"),
            lambda: _producer(CORE_URL),
        )
        if not cpi_u or not core:
            raise EmptyDataError("The request was returned empty.")
        return [{"_cpi_u": cpi_u, "_core": core}]

    @staticmethod
    def transform_data(
        query: FederalReserveMinneapolisCpiQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveMinneapolisCpiData]:
        """Parse both already-wide CSVs into one column per measure and geography."""
        from io import StringIO

        from pandas import isna, read_csv, to_datetime, to_numeric

        rows: dict[dateType, dict[str, Any]] = {}
        columns: list[str] = []
        for label, key in _MEASURES:
            frame = read_csv(StringIO(data[0][key]))
            frame["date"] = to_datetime(frame["Date"], format="%b %Y").dt.date
            for geography in (g for g in _GEOGRAPHIES if g in frame.columns):
                column = f"{label} {geography}"
                columns.append(column)
                series = to_numeric(frame[geography], errors="coerce")
                for observed, value in zip(frame["date"], series):
                    rows.setdefault(observed, {"date": observed})[column] = (
                        None if isna(value) else value
                    )

        records: list[FederalReserveMinneapolisCpiData] = []
        for observed in sorted(rows):
            if query.start_date and observed < query.start_date:
                continue
            if query.end_date and observed > query.end_date:
                continue
            row = rows[observed]
            if any(row.get(column) is not None for column in columns):
                records.append(FederalReserveMinneapolisCpiData.model_validate(row))
        if not records:
            raise EmptyDataError("The request was returned empty.")
        return records
