"""Federal Reserve Bank of Dallas Trimmed Mean PCE Inflation Rate Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = "https://www.dallasfed.org/~/media/documents/research/pce/pcehist"

_COLUMN_MAP = {
    "1-month": "one_month",
    "6-month": "six_month",
    "12-month": "twelve_month",
}


class FederalReserveDallasTrimmedMeanPCEQueryParams(QueryParams):
    """Dallas Fed Trimmed Mean PCE Inflation Rate Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveDallasTrimmedMeanPCEData(Data):
    """Dallas Fed Trimmed Mean PCE Inflation Rate Data."""

    date: dateType = Field(description="The observation month.")
    one_month: float | None = Field(
        default=None, description="The one-month annualized trimmed mean PCE rate."
    )
    six_month: float | None = Field(
        default=None, description="The six-month annualized trimmed mean PCE rate."
    )
    twelve_month: float | None = Field(
        default=None, description="The twelve-month trimmed mean PCE rate."
    )


class FederalReserveDallasTrimmedMeanPCEFetcher(
    Fetcher[
        FederalReserveDallasTrimmedMeanPCEQueryParams,
        list[FederalReserveDallasTrimmedMeanPCEData],
    ]
):
    """Dallas Fed Trimmed Mean PCE Inflation Rate Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveDallasTrimmedMeanPCEQueryParams:
        """Transform the query params."""
        return FederalReserveDallasTrimmedMeanPCEQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveDallasTrimmedMeanPCEQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Trimmed Mean PCE workbook."""
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
            "dallas_pce", lambda: seconds_until_next_release("monthly"), _producer
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveDallasTrimmedMeanPCEQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveDallasTrimmedMeanPCEData]:
        """Parse the historical sheet, coerce ``#NAN`` strings, and filter dates."""
        from io import BytesIO

        from pandas import isna, read_excel, to_datetime, to_numeric

        frame = read_excel(
            BytesIO(data[0]["_raw"]),
            engine="openpyxl",
            sheet_name="Web - Historical",
            header=3,
        )
        frame = frame.rename(columns={frame.columns[0]: "date", **_COLUMN_MAP})
        keep = ["date", *[c for c in _COLUMN_MAP.values() if c in frame.columns]]
        frame = frame[keep]
        frame["date"] = to_datetime(frame["date"], errors="coerce")
        frame = frame.dropna(subset=["date"])
        frame["date"] = frame["date"].dt.date
        for column in _COLUMN_MAP.values():
            frame[column] = to_numeric(frame[column], errors="coerce")

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        value_columns = list(_COLUMN_MAP.values())
        records: list[dict] = []
        for row in frame.sort_values("date").to_dict(orient="records"):
            record = {
                k: (None if isinstance(v, float) and isna(v) else v)
                for k, v in row.items()
            }
            if any(record.get(column) is not None for column in value_columns):
                records.append(record)

        if not records:
            raise EmptyDataError("No data was found for the given query parameters.")

        return [
            FederalReserveDallasTrimmedMeanPCEData.model_validate(record)
            for record in records
        ]
