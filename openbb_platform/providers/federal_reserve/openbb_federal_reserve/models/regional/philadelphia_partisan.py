"""Federal Reserve Bank of Philadelphia Partisan Conflict Index Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_federal_reserve.utils.philadelphia import MEDIA_URL

URL = f"{MEDIA_URL}/data-visualizations/partisan-conflict.xlsx"


class FederalReservePhiladelphiaPartisanQueryParams(QueryParams):
    """Philadelphia Fed Partisan Conflict Index Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReservePhiladelphiaPartisanData(Data):
    """Philadelphia Fed Partisan Conflict Index Data."""

    date: dateType = Field(description="The month, as a month-start date.")
    partisan_conflict: float | None = Field(
        default=None, description="The Partisan Conflict Index value."
    )


class FederalReservePhiladelphiaPartisanFetcher(
    Fetcher[
        FederalReservePhiladelphiaPartisanQueryParams,
        list[FederalReservePhiladelphiaPartisanData],
    ]
):
    """Philadelphia Fed Partisan Conflict Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReservePhiladelphiaPartisanQueryParams:
        """Transform the query params."""
        return FederalReservePhiladelphiaPartisanQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReservePhiladelphiaPartisanQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Partisan Conflict workbook."""
        from openbb_federal_reserve.utils.philadelphia import fetch_philadelphia

        content = fetch_philadelphia(URL, "partisan_conflict", "monthly")
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReservePhiladelphiaPartisanQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReservePhiladelphiaPartisanData]:
        """Parse the Partisan Conflict sheet into a monthly series."""
        from pandas import isna, to_datetime

        from openbb_federal_reserve.utils.philadelphia import read_workbook

        frame = read_workbook(data[0]["_raw"], "Sheet1")
        frame = frame.rename(
            columns={
                "Year": "year",
                "Month": "month",
                "Partisan Conflict": "partisan_conflict",
            }
        )
        frame = frame.dropna(subset=["year", "month"])
        frame["date"] = to_datetime(
            frame["year"].astype(int).astype(str)
            + " "
            + frame["month"].astype(str).str.strip(),
            format="%Y %B",
        ).dt.date
        frame = frame[["date", "partisan_conflict"]]

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReservePhiladelphiaPartisanData.model_validate(
                {
                    key: (None if isinstance(value, float) and isna(value) else value)
                    for key, value in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
