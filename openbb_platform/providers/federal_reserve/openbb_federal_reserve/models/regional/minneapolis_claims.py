"""Federal Reserve Bank of Minneapolis Unemployment Claims Model."""

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
INITIAL_URL = f"{BASE_URL}/mn_initial.csv"
CONTINUED_URL = f"{BASE_URL}/mn_continued.csv"


class FederalReserveMinneapolisClaimsQueryParams(QueryParams):
    """Minneapolis Fed Unemployment Claims Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveMinneapolisClaimsData(Data):
    """Minneapolis Fed Unemployment Claims Data."""

    date: dateType = Field(description="The week-ending date.")
    initial_claims: int | None = Field(
        default=None, description="Initial unemployment insurance claims."
    )
    continued_claims: int | None = Field(
        default=None, description="Continued unemployment insurance claims."
    )


class FederalReserveMinneapolisClaimsFetcher(
    Fetcher[
        FederalReserveMinneapolisClaimsQueryParams,
        list[FederalReserveMinneapolisClaimsData],
    ]
):
    """Minneapolis Fed Unemployment Claims Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveMinneapolisClaimsQueryParams:
        """Transform the query params."""
        return FederalReserveMinneapolisClaimsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveMinneapolisClaimsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the initial and continued claims CSVs from the Minneapolis Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer(url: str) -> str:
            """Fetch the raw claims CSV text for a given URL."""
            response = make_request(url)
            response.raise_for_status()
            return response.text

        initial = cached(
            "minneapolis_claims_initial",
            lambda: seconds_until_next_release("weekly"),
            lambda: _producer(INITIAL_URL),
        )
        continued = cached(
            "minneapolis_claims_continued",
            lambda: seconds_until_next_release("weekly"),
            lambda: _producer(CONTINUED_URL),
        )
        if not initial or not continued:
            raise EmptyDataError("The request was returned empty.")
        return [{"_initial": initial, "_continued": continued}]

    @staticmethod
    def transform_data(
        query: FederalReserveMinneapolisClaimsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveMinneapolisClaimsData]:
        """Parse and merge the weekly initial and continued claims series."""
        from io import StringIO

        from pandas import isna, read_csv, to_datetime

        initial = read_csv(StringIO(data[0]["_initial"])).rename(
            columns={"MN": "initial_claims"}
        )
        initial["date"] = to_datetime(initial["Date"]).dt.date
        initial = initial[["date", "initial_claims"]]

        continued = read_csv(StringIO(data[0]["_continued"])).rename(
            columns={"MN": "continued_claims"}
        )
        continued["date"] = to_datetime(continued["Date"]).dt.date
        continued = continued[["date", "continued_claims"]]

        frame = initial.merge(continued, on="date", how="outer")

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveMinneapolisClaimsData.model_validate(
                {
                    k: (
                        None
                        if isinstance(v, float) and isna(v)
                        else (int(v) if k != "date" and not isna(v) else v)
                    )
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
