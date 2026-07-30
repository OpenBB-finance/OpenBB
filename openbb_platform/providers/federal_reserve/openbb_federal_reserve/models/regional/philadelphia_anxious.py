"""Federal Reserve Bank of Philadelphia Anxious Index Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_federal_reserve.utils.philadelphia import MEDIA_URL

URL = (
    f"{MEDIA_URL}/surveys-and-data/survey-of-professional-forecasters"
    "/anxious-index/anxious_index_chart.xlsx"
)


class FederalReservePhiladelphiaAnxiousQueryParams(QueryParams):
    """Philadelphia Fed Anxious Index Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReservePhiladelphiaAnxiousData(Data):
    """Philadelphia Fed Anxious Index Data."""

    date: dateType = Field(description="The survey quarter, as a quarter-start date.")
    anxious_index: float | None = Field(
        default=None,
        description="The probability of a decline in real GDP next quarter, percent.",
    )
    recession: float | None = Field(
        default=None,
        description="The NBER recession indicator for the quarter, when present.",
    )


class FederalReservePhiladelphiaAnxiousFetcher(
    Fetcher[
        FederalReservePhiladelphiaAnxiousQueryParams,
        list[FederalReservePhiladelphiaAnxiousData],
    ]
):
    """Philadelphia Fed Anxious Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReservePhiladelphiaAnxiousQueryParams:
        """Transform the query params."""
        return FederalReservePhiladelphiaAnxiousQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReservePhiladelphiaAnxiousQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Anxious Index workbook."""
        from openbb_federal_reserve.utils.philadelphia import fetch_philadelphia

        content = fetch_philadelphia(URL, "anxious_index", "quarterly")
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReservePhiladelphiaAnxiousQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReservePhiladelphiaAnxiousData]:
        """Parse the Anxious Index sheet, header row 3."""
        from pandas import isna

        from openbb_federal_reserve.utils.philadelphia import (
            quarter_start,
            read_workbook,
        )

        frame = read_workbook(data[0]["_raw"], "Data", header=3)
        frame = frame.rename(
            columns={
                "Obs Year": "year",
                "Obs Quarter": "quarter",
                "Anxious Index": "anxious_index",
                "RECESS": "recession",
            }
        )
        frame = frame.dropna(subset=["year", "quarter"])
        frame["date"] = quarter_start(frame["year"], frame["quarter"])
        frame = frame[["date", "anxious_index", "recession"]]

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        value_columns = ["anxious_index", "recession"]
        records: list[FederalReservePhiladelphiaAnxiousData] = []
        for row in frame.sort_values("date").to_dict(orient="records"):
            cleaned = {
                key: (None if isinstance(value, float) and isna(value) else value)
                for key, value in row.items()
            }
            if any(cleaned.get(column) is not None for column in value_columns):
                records.append(
                    FederalReservePhiladelphiaAnxiousData.model_validate(cleaned)
                )

        if not records:
            raise EmptyDataError("The request was returned empty.")

        return records
