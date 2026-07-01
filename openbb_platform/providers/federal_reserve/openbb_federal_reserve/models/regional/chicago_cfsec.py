"""Federal Reserve Bank of Chicago Survey of Economic Conditions (CFSEC) Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = "https://api.data.chicagofed.org/CFSEC/cfsec-data-xlsx.xlsx"

_COLUMN_MAP = {
    "Activity": "activity",
    "ActivityMfg": "activity_manufacturing",
    "ActivityNmfg": "activity_nonmanufacturing",
    "Outlook": "outlook",
    "Hiring": "hiring",
    "HiringExp": "hiring_expectations",
    "CapXExp": "capital_spending_expectations",
    "LaborCosts": "labor_costs",
    "NonlaborCosts": "nonlabor_costs",
}


class FederalReserveChicagoEconomicConditionsQueryParams(QueryParams):
    """Chicago Fed Survey of Economic Conditions Query Parameters."""

    __json_schema_extra__ = {
        "date_basis": {
            "x-widget_config": {
                "options": [
                    {"label": "Publication Month", "value": "publication"},
                    {"label": "Reference-Period End Date", "value": "reference"},
                ]
            }
        },
    }

    date_basis: Literal["publication", "reference"] = Field(
        default="publication",
        description="Index the series by the survey's publication month or by its"
        " reference-period end date.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveChicagoEconomicConditionsData(Data):
    """Chicago Fed Survey of Economic Conditions Data."""

    date: dateType = Field(description="The survey month.")
    activity: float | None = Field(
        default=None, description="The overall business activity index."
    )
    activity_manufacturing: float | None = Field(
        default=None, description="The manufacturing business activity index."
    )
    activity_nonmanufacturing: float | None = Field(
        default=None, description="The non-manufacturing business activity index."
    )
    outlook: float | None = Field(
        default=None, description="The outlook for the U.S. economy index."
    )
    hiring: float | None = Field(default=None, description="The current hiring index.")
    hiring_expectations: float | None = Field(
        default=None, description="The expected hiring index."
    )
    capital_spending_expectations: float | None = Field(
        default=None, description="The expected capital spending index."
    )
    labor_costs: float | None = Field(
        default=None, description="The labor cost pressures index."
    )
    nonlabor_costs: float | None = Field(
        default=None, description="The non-labor cost pressures index."
    )


class FederalReserveChicagoEconomicConditionsFetcher(
    Fetcher[
        FederalReserveChicagoEconomicConditionsQueryParams,
        list[FederalReserveChicagoEconomicConditionsData],
    ]
):
    """Chicago Fed Survey of Economic Conditions Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveChicagoEconomicConditionsQueryParams:
        """Transform the query params."""
        return FederalReserveChicagoEconomicConditionsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveChicagoEconomicConditionsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the CFSEC workbook from the Chicago Fed."""
        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )
        from openbb_federal_reserve.utils.chicago import get_bytes

        content = cached(
            "chicago_cfsec",
            lambda: seconds_until_next_release("monthly"),
            lambda: get_bytes(URL),
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveChicagoEconomicConditionsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveChicagoEconomicConditionsData]:
        """Parse the survey sheet and apply the date filters."""
        from io import BytesIO

        from pandas import isna, read_excel, to_datetime

        reference = query.date_basis == "reference"
        frame = read_excel(
            BytesIO(data[0]["_raw"]),
            sheet_name="Data by Reference Date" if reference else "Data",
        )
        frame = frame.rename(columns=_COLUMN_MAP)
        frame["date"] = to_datetime(
            frame["Date"], format=None if reference else "%Y-%m"
        ).dt.date
        frame = frame.drop(columns=["Date"])

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        return [
            FederalReserveChicagoEconomicConditionsData.model_validate(
                {
                    k: (None if isinstance(v, float) and isna(v) else v)
                    for k, v in row.items()
                }
            )
            for row in frame.sort_values("date").to_dict(orient="records")
        ]
