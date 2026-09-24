"""Federal Reserve Bank of San Francisco Treasury Term Premium Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

URL = "https://www.frbsf.org/wp-content/uploads/FRBSF_Term_Web_Chart_Data.xlsx"

_SHEETS = {2: "Two_year_decomposition", 10: "Ten_year_decomposition"}
_SUFFIX = {2: "02YR", 10: "10YR"}


class FederalReserveSanFranciscoTermPremiumQueryParams(QueryParams):
    """San Francisco Fed Treasury Term Premium Query Parameters."""

    __json_schema_extra__ = {
        "maturity": {
            "x-widget_config": {
                "options": [
                    {"label": "2-Year", "value": 2},
                    {"label": "10-Year", "value": 10},
                ]
            }
        },
    }

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )
    maturity: int = Field(
        default=10,
        description="The Treasury maturity, in years. One of 2 or 10.",
    )

    @field_validator("maturity")
    @classmethod
    def _validate_maturity(cls, value: int) -> int:
        """Restrict the maturity to the published two- and ten-year decompositions."""
        if value not in (2, 10):
            raise ValueError("maturity must be 2 or 10.")
        return value


class FederalReserveSanFranciscoTermPremiumData(Data):
    """San Francisco Fed Treasury Term Premium Data."""

    date: dateType = Field(description="The observation date.")
    yield_zero_coupon: float | None = Field(
        default=None,
        description="The zero-coupon Treasury yield, in percent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    expected_short_rate: float | None = Field(
        default=None,
        description="The average expected short-rate component, in percent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    term_premium: float | None = Field(
        default=None,
        description="The term premium, in percent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )


class FederalReserveSanFranciscoTermPremiumFetcher(
    Fetcher[
        FederalReserveSanFranciscoTermPremiumQueryParams,
        list[FederalReserveSanFranciscoTermPremiumData],
    ]
):
    """San Francisco Fed Treasury Term Premium Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveSanFranciscoTermPremiumQueryParams:
        """Transform the query params."""
        return FederalReserveSanFranciscoTermPremiumQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveSanFranciscoTermPremiumQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Term Premium web-chart workbook from the SF Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> bytes:
            """Fetch the raw Term Premium workbook bytes."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content

        content = cached(
            "san_francisco_term_premium",
            lambda: seconds_until_next_release("daily"),
            _producer,
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveSanFranciscoTermPremiumQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveSanFranciscoTermPremiumData]:
        """Parse the requested-maturity decomposition sheet and filter dates."""
        from io import BytesIO

        from pandas import isna, read_excel, to_datetime

        suffix = _SUFFIX[query.maturity]
        frame = read_excel(
            BytesIO(data[0]["_raw"]),
            engine="openpyxl",
            sheet_name=_SHEETS[query.maturity],
        )
        frame = frame.rename(
            columns={
                f"ZCYLD{suffix}": "yield_zero_coupon",
                f"AVGEXP{suffix}": "expected_short_rate",
                f"ZCTERM{suffix}": "term_premium",
            }
        )
        frame = frame[
            ["date", "yield_zero_coupon", "expected_short_rate", "term_premium"]
        ]
        frame["date"] = to_datetime(frame["date"], errors="coerce")
        frame = frame.dropna(subset=["date"])
        frame["date"] = frame["date"].dt.date

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveSanFranciscoTermPremiumData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
