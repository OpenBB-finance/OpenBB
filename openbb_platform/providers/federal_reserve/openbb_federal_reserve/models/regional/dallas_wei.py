"""Federal Reserve Bank of Dallas Weekly Economic Index Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = (
    "https://www.dallasfed.org/-/media/documents/research"
    "/wei/weekly-economic-index.xlsx"
)


class FederalReserveDallasWeeklyEconomicQueryParams(QueryParams):
    """Dallas Fed Weekly Economic Index Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveDallasWeeklyEconomicData(Data):
    """Dallas Fed Weekly Economic Index Data."""

    date: dateType = Field(description="The week-ending observation date.")
    wei: float | None = Field(
        default=None, description="The Weekly Economic Index value."
    )


class FederalReserveDallasWeeklyEconomicFetcher(
    Fetcher[
        FederalReserveDallasWeeklyEconomicQueryParams,
        list[FederalReserveDallasWeeklyEconomicData],
    ]
):
    """Dallas Fed Weekly Economic Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveDallasWeeklyEconomicQueryParams:
        """Transform the query params."""
        return FederalReserveDallasWeeklyEconomicQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveDallasWeeklyEconomicQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Weekly Economic Index workbook."""
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
            "dallas_wei", lambda: seconds_until_next_release("weekly"), _producer
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveDallasWeeklyEconomicQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveDallasWeeklyEconomicData]:
        """Parse the current-vintage sheet and apply the date filters."""
        from io import BytesIO

        from pandas import isna, read_excel, to_datetime

        frame = read_excel(
            BytesIO(data[0]["_raw"]), engine="openpyxl", sheet_name="2008-current"
        )
        frame = frame[["Date", "WEI"]].rename(columns={"Date": "date", "WEI": "wei"})
        frame["date"] = to_datetime(frame["date"], format="%m/%d/%Y", errors="coerce")
        frame = frame.dropna(subset=["date"])
        frame["date"] = frame["date"].dt.date

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveDallasWeeklyEconomicData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
