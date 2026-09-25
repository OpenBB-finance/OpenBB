"""Federal Reserve Bank of Philadelphia Survey of Professional Forecasters Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_federal_reserve.utils.philadelphia import MEDIA_URL

_SPF_VARIABLES = (
    "NGDP",
    "PGDP",
    "RGDP",
    "RCONSUM",
    "RNRESIN",
    "RRESINV",
    "RFEDGOV",
    "RSLGOV",
    "REXPORT",
    "RCBI",
    "HOUSING",
    "INDPROD",
    "EMP",
    "UNEMP",
    "CPI",
    "CORECPI",
    "PCE",
    "COREPCE",
    "TBILL",
    "TBOND",
    "BOND",
    "BAABOND",
    "CPROF",
    "RECESS",
    "CPI10",
    "PCE10",
    "RGDP10",
    "PROD10",
    "BOND10",
)
_LONG_RUN_VARIABLES = ("CPI10", "PCE10", "RGDP10", "PROD10", "BOND10")


class FederalReservePhiladelphiaSpfQueryParams(QueryParams):
    """Philadelphia Fed Survey of Professional Forecasters Query Parameters."""

    __json_schema_extra__ = {
        "variable": {
            "x-widget_config": {
                "options": [
                    {"label": "Nominal GDP", "value": "NGDP"},
                    {"label": "GDP Price Index", "value": "PGDP"},
                    {"label": "Real GDP", "value": "RGDP"},
                    {"label": "Real Consumption", "value": "RCONSUM"},
                    {
                        "label": "Real Nonresidential Fixed Investment",
                        "value": "RNRESIN",
                    },
                    {"label": "Real Residential Fixed Investment", "value": "RRESINV"},
                    {"label": "Real Federal Government Spending", "value": "RFEDGOV"},
                    {
                        "label": "Real State & Local Government Spending",
                        "value": "RSLGOV",
                    },
                    {"label": "Real Net Exports", "value": "REXPORT"},
                    {"label": "Real Change in Private Inventories", "value": "RCBI"},
                    {"label": "Housing Starts", "value": "HOUSING"},
                    {"label": "Industrial Production", "value": "INDPROD"},
                    {"label": "Nonfarm Payroll Employment", "value": "EMP"},
                    {"label": "Unemployment Rate", "value": "UNEMP"},
                    {"label": "CPI Inflation", "value": "CPI"},
                    {"label": "Core CPI Inflation", "value": "CORECPI"},
                    {"label": "PCE Inflation", "value": "PCE"},
                    {"label": "Core PCE Inflation", "value": "COREPCE"},
                    {"label": "3-Month Treasury Bill Rate", "value": "TBILL"},
                    {"label": "10-Year Treasury Bond Rate", "value": "TBOND"},
                    {"label": "Aaa Corporate Bond Rate", "value": "BOND"},
                    {"label": "Baa Corporate Bond Rate", "value": "BAABOND"},
                    {"label": "Corporate Profits After Tax", "value": "CPROF"},
                    {
                        "label": "Anxious Index (Recession Probability)",
                        "value": "RECESS",
                    },
                    {"label": "10-Year CPI Inflation", "value": "CPI10"},
                    {"label": "10-Year PCE Inflation", "value": "PCE10"},
                    {"label": "10-Year Real GDP Growth", "value": "RGDP10"},
                    {"label": "10-Year Productivity Growth", "value": "PROD10"},
                    {
                        "label": "10-Year Treasury Bond Rate (Long-Run)",
                        "value": "BOND10",
                    },
                ]
            }
        },
        "statistic": {
            "x-widget_config": {
                "options": [
                    {"label": "Mean", "value": "mean"},
                    {"label": "Median", "value": "median"},
                ]
            }
        },
        "transform": {
            "x-widget_config": {
                "options": [
                    {"label": "Level", "value": "level"},
                    {"label": "Growth", "value": "growth"},
                ]
            }
        },
    }

    variable: Literal[_SPF_VARIABLES] = Field(  # ty: ignore[invalid-type-form]
        default="RGDP",
        description="The forecast variable code, e.g. 'RGDP' for real GDP. Codes"
        + " ending in '10' (e.g. 'CPI10', 'RGDP10') are long-run, ten-year-average"
        + " projections published only as a level.",
    )
    statistic: Literal["mean", "median"] = Field(
        default="median",
        description="The cross-forecaster summary statistic.",
    )
    transform: Literal["level", "growth"] = Field(
        default="level",
        description="The series transform; 'growth' is only published for"
        + " level-and-growth variables.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReservePhiladelphiaSpfData(Data):
    """Philadelphia Fed Survey of Professional Forecasters Data."""

    date: dateType = Field(description="The survey quarter, as a quarter-start date.")
    horizon_1: float | None = Field(
        default=None, description="The current-quarter forecast."
    )
    horizon_2: float | None = Field(
        default=None, description="The one-quarter-ahead forecast."
    )
    horizon_3: float | None = Field(
        default=None, description="The two-quarter-ahead forecast."
    )
    horizon_4: float | None = Field(
        default=None, description="The three-quarter-ahead forecast."
    )
    horizon_5: float | None = Field(
        default=None, description="The four-quarter-ahead forecast."
    )
    horizon_6: float | None = Field(
        default=None, description="The five-quarter-ahead forecast."
    )
    annual_a: float | None = Field(
        default=None, description="The forecast for the current year."
    )
    annual_b: float | None = Field(
        default=None, description="The forecast for the next year."
    )
    annual_c: float | None = Field(
        default=None, description="The forecast for two years ahead."
    )
    annual_d: float | None = Field(
        default=None, description="The forecast for three years ahead."
    )
    long_run: float | None = Field(
        default=None,
        description="The ten-year-average projection, for long-run variables.",
    )


class FederalReservePhiladelphiaSpfFetcher(
    Fetcher[
        FederalReservePhiladelphiaSpfQueryParams,
        list[FederalReservePhiladelphiaSpfData],
    ]
):
    """Philadelphia Fed Survey of Professional Forecasters Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReservePhiladelphiaSpfQueryParams:
        """Transform the query params."""
        return FederalReservePhiladelphiaSpfQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReservePhiladelphiaSpfQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the selected SPF variable workbook."""
        from openbb_federal_reserve.utils.philadelphia import fetch_philadelphia

        statistic = query.statistic.capitalize()
        transform = (
            "Level"
            if query.variable in _LONG_RUN_VARIABLES
            else query.transform.capitalize()
        )
        url = (
            f"{MEDIA_URL}/surveys-and-data/survey-of-professional-forecasters"
            f"/data-files/files/{statistic}_{query.variable}_{transform}.xlsx"
        )
        content = fetch_philadelphia(
            url,
            f"spf_{query.statistic}_{query.variable}_{transform.lower()}",
            "quarterly",
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content, "variable": query.variable, "transform": transform}]

    @staticmethod
    def transform_data(
        query: FederalReservePhiladelphiaSpfQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReservePhiladelphiaSpfData]:
        """Parse the SPF workbook into long horizon/annual records."""
        from pandas import isna

        from openbb_federal_reserve.utils.philadelphia import (
            quarter_start,
            read_workbook,
        )

        statistic = query.statistic.capitalize()
        transform = data[0]["transform"]
        frame = read_workbook(data[0]["_raw"], f"{statistic}_{transform}")
        prefix = ("D" if transform == "Growth" else "") + data[0]["variable"]
        rename = {
            prefix: "long_run",
            **{f"{prefix}{index}": f"horizon_{index}" for index in range(1, 7)},
            **{
                f"{prefix}{letter}": f"annual_{letter.lower()}"
                for letter in ("A", "B", "C", "D")
            },
        }
        frame = frame.rename(columns=rename)
        frame["date"] = quarter_start(frame["YEAR"], frame["QUARTER"])
        columns = ["date", *[value for value in rename.values() if value in frame]]
        frame = frame[columns]

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        value_columns = [column for column in columns if column != "date"]
        records: list[FederalReservePhiladelphiaSpfData] = []
        for row in frame.sort_values("date").to_dict(orient="records"):
            cleaned = {
                key: (None if isinstance(value, float) and isna(value) else value)
                for key, value in row.items()
            }
            if any(cleaned.get(column) is not None for column in value_columns):
                records.append(
                    FederalReservePhiladelphiaSpfData.model_validate(cleaned)
                )

        if not records:
            raise EmptyDataError("The request was returned empty.")

        return records
