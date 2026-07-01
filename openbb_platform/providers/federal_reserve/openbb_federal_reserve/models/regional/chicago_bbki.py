"""Federal Reserve Bank of Chicago Brave-Butters-Kelley Indexes (BBKI) Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = (
    "https://www.chicagofed.org/-/media/publications/bbki"
    "/bbki-monthly-data-series-csv.csv"
)

_COLUMN_MAP = {
    "CoincidentIndex": "coincident_index",
    "LeadingIndex": "leading_index",
    "Cycle": "cycle",
    "CycleLeading": "cycle_leading",
    "CycleLagging": "cycle_lagging",
    "Trend": "trend",
    "Irregular": "irregular",
    "MGDP": "monthly_gdp",
}


class FederalReserveChicagoBraveButtersKelleyQueryParams(QueryParams):
    """Chicago Fed Brave-Butters-Kelley Indexes Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveChicagoBraveButtersKelleyData(Data):
    """Chicago Fed Brave-Butters-Kelley Indexes Data."""

    date: dateType = Field(description="The observation month.")
    coincident_index: float | None = Field(
        default=None, description="The BBK coincident index."
    )
    leading_index: float | None = Field(
        default=None, description="The BBK leading index."
    )
    cycle: float | None = Field(default=None, description="The cyclical component.")
    cycle_leading: float | None = Field(
        default=None, description="The leading cyclical component."
    )
    cycle_lagging: float | None = Field(
        default=None, description="The lagging cyclical component."
    )
    trend: float | None = Field(default=None, description="The trend component.")
    irregular: float | None = Field(
        default=None, description="The irregular component."
    )
    monthly_gdp: float | None = Field(
        default=None, description="The monthly GDP growth estimate."
    )


class FederalReserveChicagoBraveButtersKelleyFetcher(
    Fetcher[
        FederalReserveChicagoBraveButtersKelleyQueryParams,
        list[FederalReserveChicagoBraveButtersKelleyData],
    ]
):
    """Chicago Fed Brave-Butters-Kelley Indexes Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveChicagoBraveButtersKelleyQueryParams:
        """Transform the query params."""
        return FederalReserveChicagoBraveButtersKelleyQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveChicagoBraveButtersKelleyQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the frozen BBKI CSV from the Chicago Fed."""
        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )
        from openbb_federal_reserve.utils.chicago import get_text

        text = cached(
            "chicago_bbki",
            lambda: seconds_until_next_release("quarterly"),
            lambda: get_text(URL),
        )
        if not text:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": text}]

    @staticmethod
    def transform_data(
        query: FederalReserveChicagoBraveButtersKelleyQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveChicagoBraveButtersKelleyData]:
        """Parse the CSV and apply the date filters."""
        from io import StringIO

        from pandas import isna, read_csv, to_datetime

        frame = read_csv(StringIO(data[0]["_raw"]))
        frame = frame.rename(columns=_COLUMN_MAP)
        frame["date"] = to_datetime(frame["Date"], format="%m/%d/%Y").dt.date
        frame = frame.drop(columns=["Date"])

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveChicagoBraveButtersKelleyData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
