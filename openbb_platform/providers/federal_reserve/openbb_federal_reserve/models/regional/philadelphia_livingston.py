"""Federal Reserve Bank of Philadelphia Livingston Survey Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_federal_reserve.utils.philadelphia import MEDIA_URL

_LIVINGSTON_VARIABLES = (
    "RGDPX",
    "GDPX",
    "BFIX",
    "CPAT",
    "IP",
    "TPHS",
    "PPI",
    "CPI",
    "UNPR",
    "WMFG",
    "RTTR",
    "AUTODF",
    "PRIME",
    "TBOND",
    "TBILL",
    "SPIF",
)
_HORIZON_SUFFIXES = ("BP", "ZM", "6M", "12M", "BY", "ZY", "1Y", "2Y", "10Y")


class FederalReservePhiladelphiaLivingstonQueryParams(QueryParams):
    """Philadelphia Fed Livingston Survey Query Parameters."""

    __json_schema_extra__ = {
        "variable": {
            "x-widget_config": {
                "options": [
                    {"label": "Real GDP", "value": "RGDPX"},
                    {"label": "Nominal GDP", "value": "GDPX"},
                    {"label": "Nonresidential Fixed Investment", "value": "BFIX"},
                    {"label": "Corporate Profits After Tax", "value": "CPAT"},
                    {"label": "Industrial Production", "value": "IP"},
                    {"label": "Housing Starts", "value": "TPHS"},
                    {"label": "Producer Price Index", "value": "PPI"},
                    {"label": "Consumer Price Index", "value": "CPI"},
                    {"label": "Unemployment Rate", "value": "UNPR"},
                    {
                        "label": "Average Weekly Earnings, Manufacturing",
                        "value": "WMFG",
                    },
                    {"label": "Retail Trade", "value": "RTTR"},
                    {"label": "Auto Sales", "value": "AUTODF"},
                    {"label": "Prime Rate", "value": "PRIME"},
                    {"label": "10-Year Treasury Bond Rate", "value": "TBOND"},
                    {"label": "3-Month Treasury Bill Rate", "value": "TBILL"},
                    {"label": "S&P 500 Stock Price Index", "value": "SPIF"},
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
    }

    variable: Literal[_LIVINGSTON_VARIABLES] = Field(  # ty: ignore[invalid-type-form]
        default="RGDPX",
        description="The forecast variable sheet code, e.g. 'RGDPX' for real GDP.",
    )
    statistic: Literal["mean", "median"] = Field(
        default="mean",
        description="The cross-forecaster summary statistic.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReservePhiladelphiaLivingstonData(Data):
    """Philadelphia Fed Livingston Survey Data."""

    date: dateType = Field(description="The survey date, June or December.")
    base_prior: float | None = Field(
        default=None, description="The prior-period base value ('BP')."
    )
    base_current: float | None = Field(
        default=None, description="The current-period base value ('ZM')."
    )
    six_month: float | None = Field(
        default=None, description="The six-month-ahead forecast ('6M')."
    )
    twelve_month: float | None = Field(
        default=None, description="The twelve-month-ahead forecast ('12M')."
    )
    base_year: float | None = Field(
        default=None, description="The base-year annual value ('BY')."
    )
    current_year: float | None = Field(
        default=None, description="The current-year annual value ('ZY')."
    )
    one_year: float | None = Field(
        default=None, description="The one-year-ahead annual forecast ('1Y')."
    )
    two_year: float | None = Field(
        default=None, description="The two-year-ahead annual forecast ('2Y')."
    )
    ten_year: float | None = Field(
        default=None, description="The ten-year-ahead annual forecast ('10Y')."
    )


class FederalReservePhiladelphiaLivingstonFetcher(
    Fetcher[
        FederalReservePhiladelphiaLivingstonQueryParams,
        list[FederalReservePhiladelphiaLivingstonData],
    ]
):
    """Philadelphia Fed Livingston Survey Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReservePhiladelphiaLivingstonQueryParams:
        """Transform the query params."""
        return FederalReservePhiladelphiaLivingstonQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReservePhiladelphiaLivingstonQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the Livingston Survey workbook for the selected statistic."""
        from openbb_federal_reserve.utils.philadelphia import fetch_philadelphia

        filename = "means.xlsx" if query.statistic == "mean" else "medians.xlsx"
        url = (
            f"{MEDIA_URL}/surveys-and-data/livingston-survey/historical-data/{filename}"
        )
        content = fetch_philadelphia(url, f"livingston_{query.statistic}", "quarterly")
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content, "variable": query.variable}]

    @staticmethod
    def transform_data(
        query: FederalReservePhiladelphiaLivingstonQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReservePhiladelphiaLivingstonData]:
        """Parse the selected variable sheet into horizon records."""
        from pandas import isna, to_datetime

        from openbb_federal_reserve.utils.philadelphia import read_workbook

        variable = data[0]["variable"]
        frame = read_workbook(data[0]["_raw"], variable)
        rename = {
            "Date": "date",
            f"{variable}_BP": "base_prior",
            f"{variable}_ZM": "base_current",
            f"{variable}_6M": "six_month",
            f"{variable}_12M": "twelve_month",
            f"{variable}_BY": "base_year",
            f"{variable}_ZY": "current_year",
            f"{variable}_1Y": "one_year",
            f"{variable}_2Y": "two_year",
            f"{variable}_10Y": "ten_year",
        }
        frame = frame.rename(columns=rename)
        frame = frame.dropna(subset=["date"])
        frame["date"] = to_datetime(frame["date"]).dt.date
        columns = [
            "date",
            *[value for value in rename.values() if value != "date" and value in frame],
        ]
        frame = frame[columns]

        if query.start_date:
            frame = frame[frame["date"] >= query.start_date]
        if query.end_date:
            frame = frame[frame["date"] <= query.end_date]

        value_columns = [column for column in columns if column != "date"]
        records: list[FederalReservePhiladelphiaLivingstonData] = []
        for row in frame.sort_values("date").to_dict(orient="records"):
            cleaned = {
                key: (None if isinstance(value, float) and isna(value) else value)
                for key, value in row.items()
            }
            if any(cleaned.get(column) is not None for column in value_columns):
                records.append(
                    FederalReservePhiladelphiaLivingstonData.model_validate(cleaned)
                )

        if not records:
            raise EmptyDataError("The request was returned empty.")

        return records
