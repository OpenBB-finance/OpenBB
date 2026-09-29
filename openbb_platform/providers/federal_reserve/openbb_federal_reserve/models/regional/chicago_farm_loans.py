"""Federal Reserve Bank of Chicago New Farm Loan Interest Rates Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = "https://api.data.chicagofed.org/Agriculture/New-Farm-Loans-Interest.csv"

_COLUMN_MAP = {
    "Operating Loans": "operating_loans",
    "Feeder Cattle Loans": "feeder_cattle_loans",
    "Farm Real Estate Loans": "farm_real_estate_loans",
}


class FederalReserveChicagoFarmLoanRatesQueryParams(QueryParams):
    """Chicago Fed New Farm Loan Interest Rates Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveChicagoFarmLoanRatesData(Data):
    """Chicago Fed New Farm Loan Interest Rates Data."""

    date: dateType = Field(description="The quarter-end month of the observation.")
    operating_loans: float | None = Field(
        default=None, description="The average rate on new operating loans, in percent."
    )
    feeder_cattle_loans: float | None = Field(
        default=None,
        description="The average rate on new feeder cattle loans, in percent.",
    )
    farm_real_estate_loans: float | None = Field(
        default=None,
        description="The average rate on new farm real estate loans, in percent.",
    )


class FederalReserveChicagoFarmLoanRatesFetcher(
    Fetcher[
        FederalReserveChicagoFarmLoanRatesQueryParams,
        list[FederalReserveChicagoFarmLoanRatesData],
    ]
):
    """Chicago Fed New Farm Loan Interest Rates Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveChicagoFarmLoanRatesQueryParams:
        """Transform the query params."""
        return FederalReserveChicagoFarmLoanRatesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveChicagoFarmLoanRatesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the New Farm Loans Interest CSV from the Chicago Fed."""
        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )
        from openbb_federal_reserve.utils.chicago import get_text

        text = cached(
            "chicago_farm_loans",
            lambda: seconds_until_next_release("quarterly"),
            lambda: get_text(URL),
        )
        if not text:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": text}]

    @staticmethod
    def transform_data(
        query: FederalReserveChicagoFarmLoanRatesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveChicagoFarmLoanRatesData]:
        """Parse the CSV, drop the note row, and apply the date filters."""
        from io import StringIO

        from pandas import isna, read_csv, to_datetime

        frame = read_csv(StringIO(data[0]["_raw"]))
        frame = frame.rename(columns=_COLUMN_MAP)
        frame["date"] = to_datetime(frame["YYYYQ"], format="%Y/%m", errors="coerce")
        frame = frame.dropna(subset=["date"])
        frame["date"] = frame["date"].dt.date
        frame = frame.drop(columns=["YYYYQ"])

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveChicagoFarmLoanRatesData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
