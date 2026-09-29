"""Federal Reserve Bank of Dallas Texas Leading Index Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = "https://www.dallasfed.org/~/media/documents/research/econdata/leadi.xlsx"

_COLUMN_MAP = {
    "Index": "index",
    "Annual Average": "annual_average",
    "Year/Year Pct Change": "yoy_change",
    "Dec/Dec Pct Change": "dec_dec_change",
}


class FederalReserveDallasLeadingIndexQueryParams(QueryParams):
    """Dallas Fed Texas Leading Index Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveDallasLeadingIndexData(Data):
    """Dallas Fed Texas Leading Index Data."""

    date: dateType = Field(description="The observation month.")
    index: float | None = Field(
        default=None, description="The Texas Leading Index level (1987 = 100)."
    )
    annual_average: float | None = Field(
        default=None, description="The annual average index level."
    )
    yoy_change: float | None = Field(
        default=None, description="The year-over-year percent change."
    )
    dec_dec_change: float | None = Field(
        default=None, description="The December-to-December percent change."
    )


class FederalReserveDallasLeadingIndexFetcher(
    Fetcher[
        FederalReserveDallasLeadingIndexQueryParams,
        list[FederalReserveDallasLeadingIndexData],
    ]
):
    """Dallas Fed Texas Leading Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveDallasLeadingIndexQueryParams:
        """Transform the query params."""
        return FederalReserveDallasLeadingIndexQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveDallasLeadingIndexQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Texas Leading Index workbook."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> bytes:
            """Fetch the raw workbook bytes."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content

        content = cached(
            "dallas_tli", lambda: seconds_until_next_release("monthly"), _producer
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveDallasLeadingIndexQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveDallasLeadingIndexData]:
        """Parse the leading-index sheet past its header offset and filter dates."""
        from io import BytesIO

        from pandas import isna, read_excel, to_datetime

        frame = read_excel(
            BytesIO(data[0]["_raw"]),
            engine="openpyxl",
            sheet_name="LEADI",
            header=5,
        )
        frame = frame.rename(columns={"Date": "date", **_COLUMN_MAP})
        keep = ["date", *[c for c in _COLUMN_MAP.values() if c in frame.columns]]
        frame = frame[keep]
        frame["date"] = to_datetime(frame["date"], errors="coerce")
        frame = frame.dropna(subset=["date"])
        frame["date"] = frame["date"].dt.date

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveDallasLeadingIndexData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
