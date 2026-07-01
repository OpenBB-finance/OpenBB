"""Federal Reserve Bank of New York Corporate Bond Market Distress Index Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = (
    "https://www.newyorkfed.org/medialibrary/research/interactives"
    "/cmdi/downloads/Market%20CMDI.xlsx"
)

_COLUMN_MAP = {
    "Market CMDI": "market",
    "IG CMDI": "investment_grade",
    "HY CMDI": "high_yield",
}


class FederalReserveNewYorkCorporateDistressQueryParams(QueryParams):
    """New York Fed Corporate Bond Market Distress Index Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveNewYorkCorporateDistressData(Data):
    """New York Fed Corporate Bond Market Distress Index Data."""

    date: dateType = Field(description="The end-of-week (Friday) observation date.")
    market: float | None = Field(default=None, description="The aggregate market CMDI.")
    investment_grade: float | None = Field(
        default=None, description="The investment-grade CMDI."
    )
    high_yield: float | None = Field(default=None, description="The high-yield CMDI.")


class FederalReserveNewYorkCorporateDistressFetcher(
    Fetcher[
        FederalReserveNewYorkCorporateDistressQueryParams,
        list[FederalReserveNewYorkCorporateDistressData],
    ]
):
    """New York Fed Corporate Bond Market Distress Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveNewYorkCorporateDistressQueryParams:
        """Transform the query params."""
        return FederalReserveNewYorkCorporateDistressQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveNewYorkCorporateDistressQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the CMDI workbook from the New York Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> bytes:
            """Fetch the raw CMDI workbook bytes."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content

        content = cached(
            "new_york_cmdi", lambda: seconds_until_next_release("weekly"), _producer
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveNewYorkCorporateDistressQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveNewYorkCorporateDistressData]:
        """Parse the CMDI index sheet and apply the date filters."""
        from io import BytesIO

        from pandas import isna, read_excel, to_datetime

        frame = read_excel(BytesIO(data[0]["_raw"]), sheet_name="Index Data", header=5)
        frame = frame.rename(columns={"eow_friday": "date", **_COLUMN_MAP})
        frame = frame[["date", "market", "investment_grade", "high_yield"]]
        frame["date"] = to_datetime(frame["date"], errors="coerce")
        frame = frame.dropna(subset=["date"])
        frame["date"] = frame["date"].dt.date

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveNewYorkCorporateDistressData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
