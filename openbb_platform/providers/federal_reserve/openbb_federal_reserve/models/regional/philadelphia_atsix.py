"""Federal Reserve Bank of Philadelphia ATSIX Inflation Expectations Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

from openbb_federal_reserve.utils.philadelphia import MEDIA_URL

URL = f"{MEDIA_URL}/surveys-and-data/atsix/ATSIX_Vintages.xlsx"

# dataset -> (sheet, column prefix)
_DATASETS = {
    "inflation": ("InfExp", "infexp"),
    "real": ("Real", "real"),
    "factors": ("Factors", ""),
}


class FederalReservePhiladelphiaAtsixQueryParams(QueryParams):
    """Philadelphia Fed ATSIX Inflation Expectations Query Parameters."""

    __json_schema_extra__ = {
        "dataset": {
            "x-widget_config": {
                "options": [
                    {"label": "Inflation", "value": "inflation"},
                    {"label": "Real", "value": "real"},
                    {"label": "Factors", "value": "factors"},
                ]
            }
        }
    }

    dataset: Literal["inflation", "real", "factors"] = Field(
        default="inflation",
        description="The expected-inflation term structure, the ex-ante real-rate"
        + " term structure, or the fitted Nelson-Siegel factors. Every forecast"
        + " horizon, or every Nelson-Siegel factor, is returned as its own column.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReservePhiladelphiaAtsixData(Data):
    """Philadelphia Fed ATSIX Inflation Expectations Data.

    One row per vintage month, with one column per forecast horizon (for the
    term-structure datasets) or per Nelson-Siegel factor (for the factors
    dataset). Rates are in percent.
    """

    date: dateType = Field(description="The vintage month, as a month-start date.")


class FederalReservePhiladelphiaAtsixFetcher(
    Fetcher[
        FederalReservePhiladelphiaAtsixQueryParams,
        list[FederalReservePhiladelphiaAtsixData],
    ]
):
    """Philadelphia Fed ATSIX Inflation Expectations Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReservePhiladelphiaAtsixQueryParams:
        """Transform the query params."""
        return FederalReservePhiladelphiaAtsixQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReservePhiladelphiaAtsixQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the ATSIX vintages workbook."""
        from openbb_federal_reserve.utils.philadelphia import fetch_philadelphia

        content = fetch_philadelphia(URL, "atsix", "monthly")
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReservePhiladelphiaAtsixQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReservePhiladelphiaAtsixData]:
        """Pivot horizon or factor columns to wide rows."""
        from pandas import isna, to_datetime

        from openbb_federal_reserve.utils.philadelphia import read_workbook
        from openbb_federal_reserve.utils.workbook import pivot_wide

        sheet, prefix = _DATASETS[query.dataset]
        frame = read_workbook(data[0]["_raw"], sheet)
        frame = frame.rename(columns={"_date_": "date"})
        frame["date"] = to_datetime(frame["date"], errors="coerce")
        frame = frame.dropna(subset=["date"])
        frame["date"] = frame["date"].dt.date

        if query.dataset == "factors":
            long = frame.melt(id_vars="date", var_name="column", value_name="value")
        else:
            long = frame.melt(id_vars="date", var_name="horizon", value_name="value")
            long["horizon"] = (
                long["horizon"].str.replace(prefix, "", regex=False).astype(int)
            )
            long["column"] = long["horizon"].map(lambda months: f"{months} Months")
            long = long.sort_values(["date", "horizon"])

        if query.start_date:
            long = long[long["date"] >= query.start_date]
        if query.end_date:
            long = long[long["date"] <= query.end_date]

        records = [
            {
                "date": row["date"],
                "column": row["column"],
                "value": (
                    None
                    if isinstance(row["value"], float) and isna(row["value"])
                    else float(row["value"])
                ),
            }
            for row in long.to_dict(orient="records")
        ]
        rows = pivot_wide(records, index="date", column="column", value="value")
        return [FederalReservePhiladelphiaAtsixData.model_validate(row) for row in rows]
