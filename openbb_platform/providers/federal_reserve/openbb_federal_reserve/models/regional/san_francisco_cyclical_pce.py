"""Federal Reserve Bank of San Francisco Cyclical & Acyclical Core PCE Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = "https://www.frbsf.org/wp-content/uploads/cyclical-acyclical-core-pce-data.xlsx"

_COLUMN_MAP = {
    "Cyclical core PCE inflation (y/y)": "cyclical_inflation_yoy",
    "Acyclical core PCE inflation (y/y)": "acyclical_inflation_yoy",
    "Cyclical core PCE contribution (y/y)": "cyclical_contribution_yoy",
    "Ayclical core PCE contribution (y/y)": "acyclical_contribution_yoy",
    "Health-care services portion of acyclical contribution (y/y)": (
        "acyclical_healthcare_contribution_yoy"
    ),
    "Non-health-care portion of acyclical contribution (y/y)": (
        "acyclical_non_healthcare_contribution_yoy"
    ),
    "Cyclical core PCE inflation (m/m, ar)": "cyclical_inflation_mom",
    "Acyclical core PCE inflation (m/m, ar)": "acyclical_inflation_mom",
    "Cyclical core PCE contribution (m/m, ar)": "cyclical_contribution_mom",
    "Ayclical core PCE contribution (m/m, ar)": "acyclical_contribution_mom",
    "Health-care services portion of acyclical contribution (m/m, ar)": (
        "acyclical_healthcare_contribution_mom"
    ),
    "Non-health-care portion of acyclical contribution (m/m, ar)": (
        "acyclical_non_healthcare_contribution_mom"
    ),
}


class FederalReserveSanFranciscoCyclicalPceQueryParams(QueryParams):
    """San Francisco Fed Cyclical & Acyclical Core PCE Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveSanFranciscoCyclicalPceData(Data):
    """San Francisco Fed Cyclical & Acyclical Core PCE Inflation Data."""

    date: dateType = Field(description="The observation month.")
    cyclical_inflation_yoy: float | None = Field(
        default=None, description="Cyclical core PCE inflation, year-over-year."
    )
    acyclical_inflation_yoy: float | None = Field(
        default=None, description="Acyclical core PCE inflation, year-over-year."
    )
    cyclical_contribution_yoy: float | None = Field(
        default=None,
        description="Cyclical contribution to core PCE inflation, year-over-year.",
    )
    acyclical_contribution_yoy: float | None = Field(
        default=None,
        description="Acyclical contribution to core PCE inflation, year-over-year.",
    )
    acyclical_healthcare_contribution_yoy: float | None = Field(
        default=None,
        description="Health-care services portion of the acyclical contribution,"
        + " year-over-year.",
    )
    acyclical_non_healthcare_contribution_yoy: float | None = Field(
        default=None,
        description="Non-health-care portion of the acyclical contribution,"
        + " year-over-year.",
    )
    cyclical_inflation_mom: float | None = Field(
        default=None,
        description="Cyclical core PCE inflation, month-over-month annualized.",
    )
    acyclical_inflation_mom: float | None = Field(
        default=None,
        description="Acyclical core PCE inflation, month-over-month annualized.",
    )
    cyclical_contribution_mom: float | None = Field(
        default=None,
        description="Cyclical contribution to core PCE inflation,"
        + " month-over-month annualized.",
    )
    acyclical_contribution_mom: float | None = Field(
        default=None,
        description="Acyclical contribution to core PCE inflation,"
        + " month-over-month annualized.",
    )
    acyclical_healthcare_contribution_mom: float | None = Field(
        default=None,
        description="Health-care services portion of the acyclical contribution,"
        + " month-over-month annualized.",
    )
    acyclical_non_healthcare_contribution_mom: float | None = Field(
        default=None,
        description="Non-health-care portion of the acyclical contribution,"
        + " month-over-month annualized.",
    )


class FederalReserveSanFranciscoCyclicalPceFetcher(
    Fetcher[
        FederalReserveSanFranciscoCyclicalPceQueryParams,
        list[FederalReserveSanFranciscoCyclicalPceData],
    ]
):
    """San Francisco Fed Cyclical & Acyclical Core PCE Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveSanFranciscoCyclicalPceQueryParams:
        """Transform the query params."""
        return FederalReserveSanFranciscoCyclicalPceQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveSanFranciscoCyclicalPceQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Cyclical & Acyclical PCE workbook from the SF Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> bytes:
            """Fetch the raw Cyclical & Acyclical PCE workbook bytes."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content

        content = cached(
            "san_francisco_cyclical_pce",
            lambda: seconds_until_next_release("monthly"),
            _producer,
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveSanFranciscoCyclicalPceQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveSanFranciscoCyclicalPceData]:
        """Parse the PCE sheet, normalize the YYYYmM dates, and filter."""
        from io import BytesIO

        from pandas import isna, read_excel, to_datetime

        frame = read_excel(
            BytesIO(data[0]["_raw"]), engine="openpyxl", sheet_name="Data"
        )
        frame = frame.rename(columns={"time_month": "date", **_COLUMN_MAP})
        frame["date"] = to_datetime(
            frame["date"].astype(str).str.strip(), format="%Ym%m", errors="coerce"
        )
        frame = frame.dropna(subset=["date"])
        frame["date"] = frame["date"].dt.date

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveSanFranciscoCyclicalPceData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
