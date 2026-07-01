"""Federal Reserve Bank of Minneapolis Regional Employment Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = (
    "https://www.minneapolisfed.org/~/media/Assets/Pages"
    "/regional-economic-indicators/employment_data.csv"
)

_GEOGRAPHIES = ["MN", "MT", "ND", "SD", "WI", "US"]


class FederalReserveMinneapolisEmploymentQueryParams(QueryParams):
    """Minneapolis Fed Regional Employment Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveMinneapolisEmploymentData(Data):
    """Minneapolis Fed Regional Employment Data.

    One row per observation month, with one column per Ninth District state and
    the United States carrying total nonfarm employment indexed to 100 at the
    series start.
    """

    date: dateType = Field(description="The observation month.")


class FederalReserveMinneapolisEmploymentFetcher(
    Fetcher[
        FederalReserveMinneapolisEmploymentQueryParams,
        list[FederalReserveMinneapolisEmploymentData],
    ]
):
    """Minneapolis Fed Regional Employment Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveMinneapolisEmploymentQueryParams:
        """Transform the query params."""
        return FederalReserveMinneapolisEmploymentQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveMinneapolisEmploymentQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the regional employment CSV from the Minneapolis Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> str:
            """Fetch the raw employment CSV text."""
            response = make_request(URL)
            response.raise_for_status()
            return response.text

        text = cached(
            "minneapolis_employment",
            lambda: seconds_until_next_release("monthly"),
            _producer,
        )
        if not text:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": text}]

    @staticmethod
    def transform_data(
        query: FederalReserveMinneapolisEmploymentQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveMinneapolisEmploymentData]:
        """Parse the already-wide CSV and return one column per geography."""
        from io import StringIO

        from pandas import isna, read_csv, to_datetime, to_numeric

        frame = read_csv(StringIO(data[0]["_raw"]))
        frame["date"] = to_datetime(frame["Date"], format="%b %Y").dt.date
        value_columns = [c for c in _GEOGRAPHIES if c in frame.columns]
        for column in value_columns:
            frame[column] = to_numeric(frame[column], errors="coerce")

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        records: list[FederalReserveMinneapolisEmploymentData] = []
        for row in frame.sort_values("date").to_dict(orient="records"):
            record = {
                "date": row["date"],
                **{
                    column: (None if isna(row[column]) else row[column])
                    for column in value_columns
                },
            }
            if any(record[column] is not None for column in value_columns):
                records.append(
                    FederalReserveMinneapolisEmploymentData.model_validate(record)
                )
        if not records:
            raise EmptyDataError("The request was returned empty.")
        return records
