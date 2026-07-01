"""Federal Reserve Bank of Minneapolis Job Openings and Hiring Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

BASE_URL = (
    "https://www.minneapolisfed.org/~/media/Assets/Pages/regional-economic-indicators"
)
_STATES = ["MN", "MT", "ND", "SD", "WI"]


def _state_url(state: str) -> str:
    """Return the hiring/job-opening CSV URL for a state code."""
    return f"{BASE_URL}/hiring_job_{state.lower()}.csv"


class FederalReserveMinneapolisJobOpeningsQueryParams(QueryParams):
    """Minneapolis Fed Job Openings and Hiring Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveMinneapolisJobOpeningsData(Data):
    """Minneapolis Fed Job Openings and Hiring Data.

    One row per observation month, with one column per Ninth District state and
    metric carrying the job opening rate and the hiring rate, in percent.
    """

    date: dateType = Field(description="The observation month.")


class FederalReserveMinneapolisJobOpeningsFetcher(
    Fetcher[
        FederalReserveMinneapolisJobOpeningsQueryParams,
        list[FederalReserveMinneapolisJobOpeningsData],
    ]
):
    """Minneapolis Fed Job Openings and Hiring Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveMinneapolisJobOpeningsQueryParams:
        """Transform the query params."""
        return FederalReserveMinneapolisJobOpeningsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveMinneapolisJobOpeningsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the five state hiring/job-opening CSVs from the Minneapolis Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer(state: str) -> str:
            """Fetch the raw hiring/job-opening CSV text for a state."""
            response = make_request(_state_url(state))
            response.raise_for_status()
            return response.text

        frames = {
            state: cached(
                f"minneapolis_job_openings_{state.lower()}",
                lambda: seconds_until_next_release("monthly"),
                lambda state=state: _producer(state),
            )
            for state in _STATES
        }
        if not any(frames.values()):
            raise EmptyDataError("The request was returned empty.")
        return [{"_frames": frames}]

    @staticmethod
    def transform_data(
        query: FederalReserveMinneapolisJobOpeningsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveMinneapolisJobOpeningsData]:
        """Merge the already-wide per-state CSVs into one column per state metric."""
        from io import StringIO

        from pandas import isna, read_csv, to_datetime, to_numeric

        rows: dict[dateType, dict[str, Any]] = {}
        columns: list[str] = []
        for state, raw in data[0]["_frames"].items():
            if not raw:
                continue
            frame = read_csv(StringIO(raw))
            frame["date"] = to_datetime(frame["Date"], format="%b %Y").dt.date
            for column in (
                f"{state} Job Opening Rate",
                f"{state} Hiring Rate",
            ):
                if column not in frame.columns:
                    continue
                columns.append(column)
                series = to_numeric(frame[column], errors="coerce")
                for observed, value in zip(frame["date"], series):
                    rows.setdefault(observed, {"date": observed})[column] = (
                        None if isna(value) else value
                    )

        records: list[FederalReserveMinneapolisJobOpeningsData] = []
        for observed in sorted(rows):
            if query.start_date and observed < query.start_date:
                continue
            if query.end_date and observed > query.end_date:
                continue
            row = rows[observed]
            if any(row.get(column) is not None for column in columns):
                records.append(
                    FederalReserveMinneapolisJobOpeningsData.model_validate(row)
                )
        if not records:
            raise EmptyDataError("The request was returned empty.")
        return records
