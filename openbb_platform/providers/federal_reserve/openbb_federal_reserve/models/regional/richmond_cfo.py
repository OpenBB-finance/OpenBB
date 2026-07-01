"""Federal Reserve Bank of Richmond CFO Survey Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = (
    "https://www.richmondfed.org/-/media/RichmondFedOrg/research/national_economy"
    "/cfo_survey/current_historical_cfo_data.xlsx"
)

_TABLES = {
    "optimism": "CFO_optimism_all",
    "optimism_by_size": "CFO_optimism_bysize",
    "optimism_by_employment": "CFO_optimism_byempcat",
    "optimism_by_sector": "CFO_optimism_bysector",
    "expectations": "CFO_expectations",
    "expectations_by_employment": "CFO_expectations_byempcat",
    "expectations_by_sector": "CFO_expectations_bysector",
    "spending_3mo": "CFO_spending_3mo",
    "gdp_mean_probability": "CFO_GDP_meanprob",
    "sp500": "CFO_SP500",
    "investment_plans": "CFO_invest_plans",
    "reason_invest": "CFO_reason_invest",
    "reason_not_invest": "CFO_reason_notinvest",
    "new_credit": "CFO_newcredit",
    "credit_received": "CFO_creditreceived",
    "lenders": "CFO_lenders",
    "credit_difficulty": "CFO_credit_difficulty",
    "reason_difficult": "CFO_reason_difficult",
    "reason_easy": "CFO_reason_easy",
    "legacy_through_q1_2020": "through_Q1_2020",
}


class FederalReserveRichmondCFOQueryParams(QueryParams):
    """Richmond Fed CFO Survey Query Parameters."""

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "options": [
                    {"label": "Optimism", "value": "optimism"},
                    {"label": "Optimism by Size", "value": "optimism_by_size"},
                    {
                        "label": "Optimism by Employment",
                        "value": "optimism_by_employment",
                    },
                    {"label": "Optimism by Sector", "value": "optimism_by_sector"},
                    {"label": "Expectations", "value": "expectations"},
                    {
                        "label": "Expectations by Employment",
                        "value": "expectations_by_employment",
                    },
                    {
                        "label": "Expectations by Sector",
                        "value": "expectations_by_sector",
                    },
                    {"label": "Spending 3mo", "value": "spending_3mo"},
                    {"label": "Gdp Mean Probability", "value": "gdp_mean_probability"},
                    {"label": "Sp500", "value": "sp500"},
                    {"label": "Investment Plans", "value": "investment_plans"},
                    {"label": "Reason Invest", "value": "reason_invest"},
                    {"label": "Reason Not Invest", "value": "reason_not_invest"},
                    {"label": "New Credit", "value": "new_credit"},
                    {"label": "Credit Received", "value": "credit_received"},
                    {"label": "Lenders", "value": "lenders"},
                    {"label": "Credit Difficulty", "value": "credit_difficulty"},
                    {"label": "Reason Difficult", "value": "reason_difficult"},
                    {"label": "Reason Easy", "value": "reason_easy"},
                    {
                        "label": "Legacy Through Q1 2020",
                        "value": "legacy_through_q1_2020",
                    },
                ]
            }
        }
    }

    table: Literal[
        "optimism",
        "optimism_by_size",
        "optimism_by_employment",
        "optimism_by_sector",
        "expectations",
        "expectations_by_employment",
        "expectations_by_sector",
        "spending_3mo",
        "gdp_mean_probability",
        "sp500",
        "investment_plans",
        "reason_invest",
        "reason_not_invest",
        "new_credit",
        "credit_received",
        "lenders",
        "credit_difficulty",
        "reason_difficult",
        "reason_easy",
        "legacy_through_q1_2020",
    ] = Field(
        default="optimism",
        description="The CFO Survey table to return: optimism, expectations,"
        " spending, GDP/S&P 500 forecasts, investment plans, or credit conditions"
        " - several broken out by firm size, employment, or sector. The"
        " 'legacy_through_q1_2020' table holds the pre-Q2-2020 Duke CFO Survey"
        " series (optimism, growth expectations, and S&P 500 forecasts).",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveRichmondCFOData(Data):
    """Richmond Fed CFO Survey Data.

    One row per (date, category), with one column per measure (series) within the
    selected table carrying that measure's value. The measures are pivoted to wide,
    so the measure columns are dynamic. ``category`` is the breakdown the row
    applies to where the table is disaggregated (firm size, sector, employment
    category, or the expectation measure); null for undisaggregated tables.
    """

    date: dateType = Field(description="The survey quarter start date.")
    category: str | None = Field(
        default=None,
        description="The breakdown the row applies to, where the table is"
        " disaggregated (e.g. firm size, sector, employment category, or the"
        " expectation measure); null for undisaggregated tables.",
    )


class FederalReserveRichmondCFOFetcher(
    Fetcher[
        FederalReserveRichmondCFOQueryParams,
        list[FederalReserveRichmondCFOData],
    ]
):
    """Richmond Fed CFO Survey Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveRichmondCFOQueryParams:
        """Transform the query params."""
        return FederalReserveRichmondCFOQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveRichmondCFOQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the CFO Survey workbook from the Richmond Fed."""
        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )
        from openbb_federal_reserve.utils.richmond_surveys import request_bytes

        content = cached(
            "richmond_cfo",
            lambda: seconds_until_next_release("quarterly"),
            lambda: request_bytes(URL),
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveRichmondCFOQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveRichmondCFOData]:
        """Build quarter dates from year/quarter and melt the table to long rows."""
        from datetime import date as date_cls
        from io import BytesIO

        from pandas import isna, read_excel, to_numeric

        from openbb_federal_reserve.utils.workbook import pivot_wide

        frame = read_excel(
            BytesIO(data[0]["_raw"]), engine="openpyxl", sheet_name=_TABLES[query.table]
        )
        frame.columns = [str(c) for c in frame.columns]
        keys = {c for c in frame.columns if c.lower() in ("year", "quarter")}
        frame = frame.dropna(subset=list(keys))
        frame["date"] = [
            date_cls(int(year), (int(quarter) - 1) * 3 + 1, 1)
            for year, quarter in zip(frame["year"], frame["quarter"])
        ]
        # A column that holds no numeric values is a breakdown dimension (firm
        # size, sector, expectation measure, ...) carried as rows; keeping it as a
        # key stops several rows per quarter collapsing onto one (date, series).
        value_columns: list[str] = []
        category_columns: list[str] = []
        for column in frame.columns:
            if column in keys or column == "date":
                continue
            coerced = to_numeric(frame[column], errors="coerce")
            if coerced.notna().any():
                frame[column] = coerced
                value_columns.append(column)
            else:
                category_columns.append(column)

        id_vars = ["date", *category_columns]
        melted = frame[[*id_vars, *value_columns]].melt(
            id_vars=id_vars, var_name="series", value_name="value"
        )
        if query.start_date:
            melted = melted[melted["date"] >= query.start_date]
        if query.end_date:
            melted = melted[melted["date"] <= query.end_date]

        long_records: list[dict[str, Any]] = []
        for row in melted.sort_values(["date", "series"]).to_dict(orient="records"):
            parts = [
                str(row[column]).strip()
                for column in category_columns
                if not (isinstance(row[column], float) and isna(row[column]))
                and str(row[column]).strip()
            ]
            value = row["value"]
            if isinstance(value, float) and isna(value):
                value = None
            long_records.append(
                {
                    "date": row["date"],
                    "category": " - ".join(parts) if parts else None,
                    "series": row["series"],
                    "value": value,
                }
            )

        wide = pivot_wide(
            long_records, index=("date", "category"), column="series", value="value"
        )
        return [FederalReserveRichmondCFOData.model_validate(record) for record in wide]
