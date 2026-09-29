"""Federal Reserve Bank of Chicago National Financial Conditions Index Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = "https://www.chicagofed.org/-/media/publications/nfci/nfci-data-series-csv.csv"

_COLUMN_MAP = {
    "NFCI": "nfci",
    "ANFCI": "adjusted_nfci",
    "Risk": "risk",
    "Credit": "credit",
    "Leverage": "leverage",
    "Nonfinancial_Leverage": "nonfinancial_leverage",
}


class FederalReserveChicagoFinancialConditionsQueryParams(QueryParams):
    """Chicago Fed National Financial Conditions Index Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveChicagoFinancialConditionsData(Data):
    """Chicago Fed National Financial Conditions Index Data."""

    date: dateType = Field(description="The Friday of the observation week.")
    nfci: float | None = Field(default=None, description="The NFCI index value.")
    adjusted_nfci: float | None = Field(
        default=None,
        description="The adjusted NFCI (ANFCI), relative to economic conditions.",
    )
    risk: float | None = Field(default=None, description="The risk subindex.")
    credit: float | None = Field(default=None, description="The credit subindex.")
    leverage: float | None = Field(default=None, description="The leverage subindex.")
    nonfinancial_leverage: float | None = Field(
        default=None, description="The nonfinancial leverage subindex."
    )


class FederalReserveChicagoFinancialConditionsFetcher(
    Fetcher[
        FederalReserveChicagoFinancialConditionsQueryParams,
        list[FederalReserveChicagoFinancialConditionsData],
    ]
):
    """Chicago Fed National Financial Conditions Index Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveChicagoFinancialConditionsQueryParams:
        """Transform the query params."""
        return FederalReserveChicagoFinancialConditionsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveChicagoFinancialConditionsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the NFCI CSV from the Chicago Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> str:
            """Fetch the raw NFCI CSV text."""
            response = make_request(URL)
            response.raise_for_status()
            return response.text

        text = cached(
            "chicago_nfci", lambda: seconds_until_next_release("weekly"), _producer
        )
        if not text:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": text}]

    @staticmethod
    def transform_data(
        query: FederalReserveChicagoFinancialConditionsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveChicagoFinancialConditionsData]:
        """Parse the CSV and apply the date filters."""
        from io import StringIO

        from pandas import isna, read_csv, to_datetime

        frame = read_csv(StringIO(data[0]["_raw"]))
        frame = frame.rename(columns=_COLUMN_MAP)
        frame["date"] = to_datetime(frame["Friday_of_Week"], format="%m/%d/%Y").dt.date
        frame = frame.drop(columns=["Friday_of_Week"])

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveChicagoFinancialConditionsData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
