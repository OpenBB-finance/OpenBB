"""Federal Reserve Bank of Chicago National Activity Index (CFNAI) Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = "https://www.chicagofed.org/-/media/publications/cfnai/cfnai-data-series-csv.csv"

_COLUMN_MAP = {
    "P_I": "production_income",
    "EU_H": "employment",
    "C_H": "consumption_housing",
    "SO_I": "sales_orders_inventories",
    "CFNAI": "cfnai",
    "CFNAI_MA3": "cfnai_ma3",
    "DIFFUSION": "diffusion",
}


class FederalReserveChicagoNationalActivityQueryParams(QueryParams):
    """Chicago Fed National Activity Index Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveChicagoNationalActivityData(Data):
    """Chicago Fed National Activity Index Data."""

    date: dateType = Field(description="The observation month.")
    cfnai: float | None = Field(default=None, description="The CFNAI index value.")
    cfnai_ma3: float | None = Field(
        default=None, description="The three-month moving average of the CFNAI."
    )
    diffusion: float | None = Field(
        default=None, description="The CFNAI diffusion index."
    )
    production_income: float | None = Field(
        default=None, description="Production and income contribution."
    )
    employment: float | None = Field(
        default=None, description="Employment, unemployment, and hours contribution."
    )
    consumption_housing: float | None = Field(
        default=None, description="Personal consumption and housing contribution."
    )
    sales_orders_inventories: float | None = Field(
        default=None, description="Sales, orders, and inventories contribution."
    )


class FederalReserveChicagoNationalActivityFetcher(
    Fetcher[
        FederalReserveChicagoNationalActivityQueryParams,
        list[FederalReserveChicagoNationalActivityData],
    ]
):
    """Chicago Fed National Activity Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveChicagoNationalActivityQueryParams:
        """Transform the query params."""
        return FederalReserveChicagoNationalActivityQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveChicagoNationalActivityQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the CFNAI CSV from the Chicago Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> str:
            """Fetch the raw CFNAI CSV text."""
            response = make_request(URL)
            response.raise_for_status()
            return response.text

        text = cached(
            "chicago_cfnai", lambda: seconds_until_next_release("monthly"), _producer
        )
        if not text:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": text}]

    @staticmethod
    def transform_data(
        query: FederalReserveChicagoNationalActivityQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveChicagoNationalActivityData]:
        """Parse the CSV and apply the date filters."""
        from io import StringIO

        from pandas import isna, read_csv, to_datetime

        frame = read_csv(StringIO(data[0]["_raw"]))
        frame = frame.rename(columns=_COLUMN_MAP)
        frame["date"] = to_datetime(frame["Date"], format="%Y/%m").dt.date
        frame = frame.drop(columns=["Date"])

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveChicagoNationalActivityData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
