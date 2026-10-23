"""Federal Reserve Bank of San Francisco Supply & Demand-Driven PCE Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = "https://www.frbsf.org/wp-content/uploads/supply-demand-pce-inflation.xlsx"

_COLUMN_MAP = {
    "Demand-driven Inflation (core, y/y)": "demand_core_yoy",
    "Ambiguous (core, y/y)": "ambiguous_core_yoy",
    "Supply-driven Inflation (core, y/y)": "supply_core_yoy",
    "Demand-driven Inflation (core, m/m)": "demand_core_mom",
    "Ambiguous (core, m/m)": "ambiguous_core_mom",
    "Supply-driven Inflation (core, m/m)": "supply_core_mom",
    "Demand-driven Inflation (headline, y/y)": "demand_headline_yoy",
    "Ambiguous (headline, y/y)": "ambiguous_headline_yoy",
    "Supply-driven Inflation (headline, y/y)": "supply_headline_yoy",
    "Demand-driven Inflation (headline, m/m)": "demand_headline_mom",
    "Ambiguous (headline, m/m)": "ambiguous_headline_mom",
    "Supply-driven Inflation (headline, m/m)": "supply_headline_mom",
}


class FederalReserveSanFranciscoSupplyDemandPceQueryParams(QueryParams):
    """San Francisco Fed Supply & Demand-Driven PCE Query Parameters."""

    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveSanFranciscoSupplyDemandPceData(Data):
    """San Francisco Fed Supply & Demand-Driven PCE Inflation Data."""

    date: dateType = Field(description="The observation month.")
    demand_core_yoy: float | None = Field(
        default=None, description="Demand-driven core inflation, year-over-year."
    )
    ambiguous_core_yoy: float | None = Field(
        default=None, description="Ambiguous core inflation, year-over-year."
    )
    supply_core_yoy: float | None = Field(
        default=None, description="Supply-driven core inflation, year-over-year."
    )
    demand_core_mom: float | None = Field(
        default=None, description="Demand-driven core inflation, month-over-month."
    )
    ambiguous_core_mom: float | None = Field(
        default=None, description="Ambiguous core inflation, month-over-month."
    )
    supply_core_mom: float | None = Field(
        default=None, description="Supply-driven core inflation, month-over-month."
    )
    demand_headline_yoy: float | None = Field(
        default=None,
        description="Demand-driven headline inflation, year-over-year.",
    )
    ambiguous_headline_yoy: float | None = Field(
        default=None, description="Ambiguous headline inflation, year-over-year."
    )
    supply_headline_yoy: float | None = Field(
        default=None,
        description="Supply-driven headline inflation, year-over-year.",
    )
    demand_headline_mom: float | None = Field(
        default=None,
        description="Demand-driven headline inflation, month-over-month.",
    )
    ambiguous_headline_mom: float | None = Field(
        default=None, description="Ambiguous headline inflation, month-over-month."
    )
    supply_headline_mom: float | None = Field(
        default=None,
        description="Supply-driven headline inflation, month-over-month.",
    )


class FederalReserveSanFranciscoSupplyDemandPceFetcher(
    Fetcher[
        FederalReserveSanFranciscoSupplyDemandPceQueryParams,
        list[FederalReserveSanFranciscoSupplyDemandPceData],
    ]
):
    """San Francisco Fed Supply & Demand-Driven PCE Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveSanFranciscoSupplyDemandPceQueryParams:
        """Transform the query params."""
        return FederalReserveSanFranciscoSupplyDemandPceQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveSanFranciscoSupplyDemandPceQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Supply & Demand-Driven PCE workbook from the SF Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> bytes:
            """Fetch the raw Supply & Demand-Driven PCE workbook bytes."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content

        content = cached(
            "san_francisco_supply_demand_pce",
            lambda: seconds_until_next_release("monthly"),
            _producer,
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveSanFranciscoSupplyDemandPceQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveSanFranciscoSupplyDemandPceData]:
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
            FederalReserveSanFranciscoSupplyDemandPceData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
