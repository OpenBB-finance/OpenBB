"""Federal Reserve Bank of Richmond SOS Recession Indicator Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = (
    "https://www.richmondfed.org/-/media/RichmondFedOrg/assets/data"
    "/sos_recession_indicator.xlsx"
)
SHEET = "Data"

_COLUMN_MAP = {
    "SOS indicator": "sos",
    "Recession Threshold": "recession_threshold",
}


class FederalReserveRichmondRecessionIndicatorQueryParams(QueryParams):
    """Richmond Fed SOS Recession Indicator Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveRichmondRecessionIndicatorData(Data):
    """Richmond Fed SOS Recession Indicator Data."""

    date: dateType = Field(description="The end-of-week observation date.")
    sos: float | None = Field(
        default=None, description="The Sum of Stalls recession indicator value."
    )
    recession_threshold: float | None = Field(
        default=None, description="The constant recession-signal threshold (0.2)."
    )


class FederalReserveRichmondRecessionIndicatorFetcher(
    Fetcher[
        FederalReserveRichmondRecessionIndicatorQueryParams,
        list[FederalReserveRichmondRecessionIndicatorData],
    ]
):
    """Richmond Fed SOS Recession Indicator Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveRichmondRecessionIndicatorQueryParams:
        """Transform the query params."""
        return FederalReserveRichmondRecessionIndicatorQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveRichmondRecessionIndicatorQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the SOS Recession Indicator workbook from the Richmond Fed."""
        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )
        from openbb_federal_reserve.utils.richmond_surveys import request_bytes

        content = cached(
            "richmond_sos",
            lambda: seconds_until_next_release("weekly"),
            lambda: request_bytes(URL),
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveRichmondRecessionIndicatorQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveRichmondRecessionIndicatorData]:
        """Parse the indicator sheet and apply the date filters."""
        from io import BytesIO

        from pandas import isna, read_excel, to_datetime

        frame = read_excel(
            BytesIO(data[0]["_raw"]), engine="openpyxl", sheet_name=SHEET
        )
        frame = frame.rename(columns={"Date": "date", **_COLUMN_MAP})
        frame["date"] = to_datetime(frame["date"], errors="coerce")
        frame = frame.dropna(subset=["date"])
        frame["date"] = frame["date"].dt.date
        frame = frame[["date", *_COLUMN_MAP.values()]]

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveRichmondRecessionIndicatorData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
