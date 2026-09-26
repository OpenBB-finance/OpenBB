"""Federal Reserve Bank of Chicago Agricultural Credit Conditions Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = "https://api.data.chicagofed.org/Agriculture/Ag-Credit-Conditions.csv"

_COLUMN_MAP = {
    "Loan Demand Index": "loan_demand_index",
    "Fund Availability Index": "fund_availability_index",
    "Loan Repayment Index": "loan_repayment_index",
    "Average Loan-to-deposit Ratio (percent)": "loan_to_deposit_ratio",
}


class FederalReserveChicagoAgCreditQueryParams(QueryParams):
    """Chicago Fed Agricultural Credit Conditions Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveChicagoAgCreditData(Data):
    """Chicago Fed Agricultural Credit Conditions Data."""

    date: dateType = Field(description="The quarter-end month of the observation.")
    loan_demand_index: float | None = Field(
        default=None, description="The loan demand diffusion index."
    )
    fund_availability_index: float | None = Field(
        default=None, description="The fund availability diffusion index."
    )
    loan_repayment_index: float | None = Field(
        default=None, description="The loan repayment rate diffusion index."
    )
    loan_to_deposit_ratio: float | None = Field(
        default=None, description="The average loan-to-deposit ratio, in percent."
    )


class FederalReserveChicagoAgCreditFetcher(
    Fetcher[
        FederalReserveChicagoAgCreditQueryParams,
        list[FederalReserveChicagoAgCreditData],
    ]
):
    """Chicago Fed Agricultural Credit Conditions Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveChicagoAgCreditQueryParams:
        """Transform the query params."""
        return FederalReserveChicagoAgCreditQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveChicagoAgCreditQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Ag Credit Conditions CSV from the Chicago Fed."""
        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )
        from openbb_federal_reserve.utils.chicago import get_text

        text = cached(
            "chicago_ag_credit",
            lambda: seconds_until_next_release("quarterly"),
            lambda: get_text(URL),
        )
        if not text:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": text}]

    @staticmethod
    def transform_data(
        query: FederalReserveChicagoAgCreditQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveChicagoAgCreditData]:
        """Parse the CSV and apply the date filters."""
        from io import StringIO

        from pandas import isna, read_csv, to_datetime

        frame = read_csv(StringIO(data[0]["_raw"]))
        frame = frame.rename(columns=_COLUMN_MAP)
        frame["date"] = to_datetime(frame["YYYYQ"], format="%Y/%m").dt.date
        frame = frame.drop(columns=["YYYYQ"])

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveChicagoAgCreditData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
