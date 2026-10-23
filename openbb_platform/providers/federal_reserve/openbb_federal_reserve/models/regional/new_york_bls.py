"""Federal Reserve Bank of New York Business Leaders Survey Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = (
    "https://www.newyorkfed.org/medialibrary/media/Survey"
    "/business_leaders/bls_chart_data.csv"
)


class FederalReserveNewYorkBusinessLeadersQueryParams(QueryParams):
    """New York Fed Business Leaders Survey Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveNewYorkBusinessLeadersData(Data):
    """New York Fed Business Leaders Survey Data."""

    date: dateType = Field(description="The survey month.")
    current: float | None = Field(
        default=None, description="The current business activity diffusion index."
    )
    expected: float | None = Field(
        default=None,
        description="The six-month-ahead expected business activity diffusion index.",
    )


class FederalReserveNewYorkBusinessLeadersFetcher(
    Fetcher[
        FederalReserveNewYorkBusinessLeadersQueryParams,
        list[FederalReserveNewYorkBusinessLeadersData],
    ]
):
    """New York Fed Business Leaders Survey Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveNewYorkBusinessLeadersQueryParams:
        """Transform the query params."""
        return FederalReserveNewYorkBusinessLeadersQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveNewYorkBusinessLeadersQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Business Leaders Survey CSV from the New York Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> str:
            """Fetch the raw survey CSV text."""
            response = make_request(URL)
            response.raise_for_status()
            return response.text

        text = cached(
            "new_york_bls", lambda: seconds_until_next_release("monthly"), _producer
        )
        if not text:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": text}]

    @staticmethod
    def transform_data(
        query: FederalReserveNewYorkBusinessLeadersQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveNewYorkBusinessLeadersData]:
        """Parse the survey CSV and apply the date filters."""
        from io import StringIO

        from pandas import isna, read_csv, to_datetime

        frame = read_csv(StringIO(data[0]["_raw"]))
        frame = frame.rename(
            columns={"Dates": "date", "Current": "current", "Expected": "expected"}
        )
        frame["date"] = to_datetime(frame["date"], format="%m/%d/%Y").dt.date

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveNewYorkBusinessLeadersData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
