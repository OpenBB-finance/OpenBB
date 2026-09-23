"""Federal Reserve Bank of Chicago Midwest Economy Index (MEI) Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = "https://www.chicagofed.org/-/media/publications/mei/mei-data-series-csv.csv"

_COLUMN_MAP = {
    "MEI": "mei",
    "ILIndex": "illinois",
    "INIndex": "indiana",
    "IAIndex": "iowa",
    "MIIndex": "michigan",
    "WIIndex": "wisconsin",
    "Regional": "regional",
    "Manufacturing": "manufacturing",
    "Construction": "construction",
    "Services": "services",
    "Consumer": "consumer",
}


class FederalReserveChicagoMidwestEconomyQueryParams(QueryParams):
    """Chicago Fed Midwest Economy Index Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveChicagoMidwestEconomyData(Data):
    """Chicago Fed Midwest Economy Index Data."""

    date: dateType = Field(description="The observation month.")
    mei: float | None = Field(default=None, description="The Midwest Economy Index.")
    illinois: float | None = Field(
        default=None, description="The Illinois state contribution."
    )
    indiana: float | None = Field(
        default=None, description="The Indiana state contribution."
    )
    iowa: float | None = Field(default=None, description="The Iowa state contribution.")
    michigan: float | None = Field(
        default=None, description="The Michigan state contribution."
    )
    wisconsin: float | None = Field(
        default=None, description="The Wisconsin state contribution."
    )
    regional: float | None = Field(
        default=None, description="The relative regional MEI."
    )
    manufacturing: float | None = Field(
        default=None, description="The manufacturing sector contribution."
    )
    construction: float | None = Field(
        default=None, description="The construction and mining sector contribution."
    )
    services: float | None = Field(
        default=None, description="The service sector contribution."
    )
    consumer: float | None = Field(
        default=None, description="The consumer spending sector contribution."
    )


class FederalReserveChicagoMidwestEconomyFetcher(
    Fetcher[
        FederalReserveChicagoMidwestEconomyQueryParams,
        list[FederalReserveChicagoMidwestEconomyData],
    ]
):
    """Chicago Fed Midwest Economy Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveChicagoMidwestEconomyQueryParams:
        """Transform the query params."""
        return FederalReserveChicagoMidwestEconomyQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveChicagoMidwestEconomyQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the frozen MEI CSV from the Chicago Fed."""
        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )
        from openbb_federal_reserve.utils.chicago import get_text

        text = cached(
            "chicago_mei",
            lambda: seconds_until_next_release("quarterly"),
            lambda: get_text(URL),
        )
        if not text:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": text}]

    @staticmethod
    def transform_data(
        query: FederalReserveChicagoMidwestEconomyQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveChicagoMidwestEconomyData]:
        """Parse the CSV and apply the date filters."""
        from io import StringIO

        from pandas import isna, read_csv, to_datetime

        frame = read_csv(StringIO(data[0]["_raw"]))
        frame = frame.rename(columns=_COLUMN_MAP)
        frame["date"] = to_datetime(frame["Year/Month"], format="%Y/%m").dt.date
        frame = frame.drop(columns=["Year/Month"])

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveChicagoMidwestEconomyData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
