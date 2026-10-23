"""Federal Reserve Bank of New York Staff Nowcast Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = (
    "https://www.newyorkfed.org/medialibrary/Research/Interactives/Data/NowCast"
    "/downloads/New-York-Fed-Staff-Nowcast_download_data"
)


class FederalReserveNewYorkNowcastQueryParams(QueryParams):
    """New York Fed Staff Nowcast Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveNewYorkNowcastData(Data):
    """New York Fed Staff Nowcast Data."""

    date: dateType = Field(description="The forecast vintage date.")
    reference_quarter: str = Field(
        description="The reference quarter the estimates describe, as ``YYYY:QN``."
    )
    backcast: float | None = Field(
        default=None,
        description="Real GDP growth backcast for the previous quarter,"
        + " annualized percent.",
    )
    nowcast: float | None = Field(
        default=None,
        description="Real GDP growth nowcast for the current quarter,"
        + " annualized percent.",
    )
    forecast: float | None = Field(
        default=None,
        description="Real GDP growth forecast for the next quarter,"
        + " annualized percent.",
    )


class FederalReserveNewYorkNowcastFetcher(
    Fetcher[
        FederalReserveNewYorkNowcastQueryParams,
        list[FederalReserveNewYorkNowcastData],
    ]
):
    """New York Fed Staff Nowcast Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveNewYorkNowcastQueryParams:
        """Transform the query params."""
        return FederalReserveNewYorkNowcastQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveNewYorkNowcastQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Nowcast workbook from the New York Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> bytes:
            """Fetch the raw Nowcast workbook bytes."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content

        content = cached(
            "new_york_nowcast",
            lambda: seconds_until_next_release("weekly"),
            _producer,
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveNewYorkNowcastQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveNewYorkNowcastData]:
        """Parse the by-horizon nowcast sheet and apply the date filters."""
        from io import BytesIO

        from pandas import isna, read_excel, to_datetime

        frame = read_excel(
            BytesIO(data[0]["_raw"]), sheet_name="Forecasts By Horizon", header=5
        )
        frame = frame.rename(
            columns={
                "Forecast date": "date",
                "Reference quarter": "reference_quarter",
                "Backcast (previous quarter)": "backcast",
                "Nowcast (current quarter)": "nowcast",
                "Forecast (next quarter)": "forecast",
            }
        )
        frame["date"] = to_datetime(frame["date"], errors="coerce")
        frame = frame.dropna(subset=["date"])
        frame["date"] = frame["date"].dt.date

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        records = [
            FederalReserveNewYorkNowcastData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
        if not records:
            raise EmptyDataError("The request was returned empty.")
        return records
