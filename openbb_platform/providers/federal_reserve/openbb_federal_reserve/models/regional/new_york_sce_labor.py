"""Federal Reserve Bank of New York SCE Labor Market Survey Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = (
    "https://www.newyorkfed.org/medialibrary/media/research/microeconomics"
    "/interactive/downloads/sce-labor-chart-data-public.xlsx?sc_lang=en"
)


class FederalReserveNewYorkConsumerLaborMarketQueryParams(QueryParams):
    """New York Fed SCE Labor Market Survey Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveNewYorkConsumerLaborMarketData(Data):
    """New York Fed SCE Labor Market Survey Data."""

    date: dateType = Field(description="The survey month.")
    average_reservation_wage: float | None = Field(
        default=None,
        description="The average reservation wage, in U.S. dollars.",
    )


class FederalReserveNewYorkConsumerLaborMarketFetcher(
    Fetcher[
        FederalReserveNewYorkConsumerLaborMarketQueryParams,
        list[FederalReserveNewYorkConsumerLaborMarketData],
    ]
):
    """New York Fed SCE Labor Market Survey Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveNewYorkConsumerLaborMarketQueryParams:
        """Transform the query params."""
        return FederalReserveNewYorkConsumerLaborMarketQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveNewYorkConsumerLaborMarketQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the SCE Labor Market workbook from the New York Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> bytes:
            """Fetch the raw SCE Labor Market workbook bytes."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content

        content = cached(
            "new_york_sce_labor",
            lambda: seconds_until_next_release("monthly"),
            _producer,
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveNewYorkConsumerLaborMarketQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveNewYorkConsumerLaborMarketData]:
        """Parse the earnings sheet and apply the date filters."""
        from io import BytesIO

        from pandas import isna, read_excel, to_datetime, to_numeric

        frame = read_excel(
            BytesIO(data[0]["_raw"]),
            engine="openpyxl",
            sheet_name="Data",
            header=5,
        )
        frame = frame.rename(
            columns={frame.columns[0]: "date", "Mean": "average_reservation_wage"}
        )
        frame = frame[["date", "average_reservation_wage"]]
        frame["date"] = to_datetime(frame["date"], format="%b %Y", errors="coerce")
        frame = frame.dropna(subset=["date"])
        frame["date"] = frame["date"].dt.date
        frame["average_reservation_wage"] = (
            to_numeric(frame["average_reservation_wage"], errors="coerce") * 1000
        )

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveNewYorkConsumerLaborMarketData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
