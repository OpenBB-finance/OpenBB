"""Federal Reserve Bank of Richmond Non-Employment Index Model."""

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
    "/non_employ_index/non_employ_index_data.xlsx"
)
SHEET = "Data"

_COLUMN_MAP = {
    "NEI_26_SA": "nei",
    "NEI_26_pter_SA": "nei_plus",
    "u5": "u5",
    "u6": "u6",
    "urate": "unemployment_rate",
}


class FederalReserveRichmondNonEmploymentQueryParams(QueryParams):
    """Richmond Fed Non-Employment Index Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveRichmondNonEmploymentData(Data):
    """Richmond Fed Non-Employment Index Data."""

    date: dateType = Field(description="The observation month.")
    nei: float | None = Field(
        default=None, description="The Non-Employment Index, seasonally adjusted."
    )
    nei_plus: float | None = Field(
        default=None,
        description="The NEI including those marginally attached / part-time"
        " for economic reasons (NEI+PTER).",
    )
    u5: float | None = Field(default=None, description="The official U-5 rate.")
    u6: float | None = Field(default=None, description="The official U-6 rate.")
    unemployment_rate: float | None = Field(
        default=None, description="The official U-3 unemployment rate."
    )


class FederalReserveRichmondNonEmploymentFetcher(
    Fetcher[
        FederalReserveRichmondNonEmploymentQueryParams,
        list[FederalReserveRichmondNonEmploymentData],
    ]
):
    """Richmond Fed Non-Employment Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveRichmondNonEmploymentQueryParams:
        """Transform the query params."""
        return FederalReserveRichmondNonEmploymentQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveRichmondNonEmploymentQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Non-Employment Index workbook from the Richmond Fed."""
        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )
        from openbb_federal_reserve.utils.richmond_surveys import request_bytes

        content = cached(
            "richmond_nei",
            lambda: seconds_until_next_release("monthly"),
            lambda: request_bytes(URL),
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveRichmondNonEmploymentQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveRichmondNonEmploymentData]:
        """Parse the index sheet, build month dates, and apply the filters."""
        from io import BytesIO

        from pandas import isna, read_excel, to_datetime

        frame = read_excel(
            BytesIO(data[0]["_raw"]), engine="openpyxl", sheet_name=SHEET
        )
        frame = frame.dropna(subset=["YEAR", "MONTH"])
        year = frame["YEAR"].astype(int).astype(str)
        month = frame["MONTH"].astype(int).astype(str)
        frame["date"] = to_datetime(year + "-" + month + "-01").dt.date
        frame = frame.rename(columns=_COLUMN_MAP)
        frame = frame[["date", *_COLUMN_MAP.values()]]

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        value_cols = list(_COLUMN_MAP.values())
        records: list[FederalReserveRichmondNonEmploymentData] = []
        for row in frame.sort_values("date").to_dict(orient="records"):
            record = {
                k: (None if isinstance(v, float) and isna(v) else v)
                for k, v in row.items()
            }
            if any(record[col] is not None for col in value_cols):
                records.append(
                    FederalReserveRichmondNonEmploymentData.model_validate(record)
                )

        if not records:
            raise EmptyDataError("All rows were empty after parsing.")

        return records
