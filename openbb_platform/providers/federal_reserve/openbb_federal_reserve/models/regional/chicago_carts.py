"""Federal Reserve Bank of Chicago Advance Retail Trade Summary (CARTS) Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

BASE_URL = "https://api.data.chicagofed.org/CARTS/carts-dashboard-{figure}.csv"

_FIGURE_FILES = {
    "weekly": "fig1",
    "current_month": "fig2",
    "monthly": "fig3",
    "nowcast_contributions": "fig4",
    "vs_census_visa": "fig5",
    "vs_bea_cpi": "fig6",
}

_WEEKLY_LABELS = {
    "Mils. $": "Retail and Food Services Sales (Mils. $)",
    "Mils. 2017$": "Retail and Food Services Sales (Mils. 2017$)",
}
_MONTHLY_LABELS = {
    "Mils. $": "Sales, m/m % chg.",
    "CARTS Nowcast": "Sales Nowcast, m/m % chg.",
    "Mils. 2017$": "Inflation-adjusted Sales, m/m % chg.",
    "Inflation-adjusted Nowcast": "Inflation-adjusted Sales Nowcast, m/m % chg.",
}
_CENSUS_LABELS = {
    "Census": "Census Retail Sales, m/m % chg.",
    "VISA SMI (minus 100)": "VISA Spending Momentum Index (minus 100)",
    "CARTS Nowcast": "CARTS Nowcast, m/m % chg.",
}
_BEA_LABELS = {
    "BEA": "BEA PCE Goods, m/m % chg.",
    "CPI": "CPI, m/m % chg.",
    "CARTS Nowcast": "CARTS Nowcast, m/m % chg.",
}

_TIMESERIES = {
    "weekly": (_WEEKLY_LABELS, "%Y-%m-%d"),
    "monthly": (_MONTHLY_LABELS, "%b-%Y"),
    "vs_census_visa": (_CENSUS_LABELS, "%b-%Y"),
    "vs_bea_cpi": (_BEA_LABELS, "%b-%Y"),
}


class FederalReserveChicagoRetailTradeQueryParams(QueryParams):
    """Chicago Fed Advance Retail Trade Summary Query Parameters."""

    __json_schema_extra__ = {
        "figure": {
            "x-widget_config": {
                "options": [
                    {"label": "Weekly Sales Index", "value": "weekly"},
                    {"label": "Monthly m/m % Change", "value": "monthly"},
                    {"label": "Current Month Snapshot", "value": "current_month"},
                    {
                        "label": "Nowcast Contributions",
                        "value": "nowcast_contributions",
                    },
                    {"label": "Nowcast vs. Census / VISA", "value": "vs_census_visa"},
                    {"label": "Nowcast vs. BEA / CPI", "value": "vs_bea_cpi"},
                ]
            }
        },
    }

    figure: Literal[
        "weekly",
        "monthly",
        "current_month",
        "nowcast_contributions",
        "vs_census_visa",
        "vs_bea_cpi",
    ] = Field(
        default="weekly",
        description="The dashboard figure to return: the weekly sales index"
        " (``weekly``), the monthly m/m percent changes with nowcast"
        " (``monthly``), the latest month's sales and prices snapshot"
        " (``current_month``), the latest nowcast contribution breakdown"
        " (``nowcast_contributions``), or the nowcast benchmarked against the"
        " Census/VISA (``vs_census_visa``) or BEA/CPI (``vs_bea_cpi``) series.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveChicagoRetailTradeData(Data):
    """Chicago Fed Advance Retail Trade Summary Data."""

    date: dateType = Field(description="The observation date.")


class FederalReserveChicagoRetailTradeFetcher(
    Fetcher[
        FederalReserveChicagoRetailTradeQueryParams,
        list[FederalReserveChicagoRetailTradeData],
    ]
):
    """Chicago Fed Advance Retail Trade Summary Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveChicagoRetailTradeQueryParams:
        """Transform the query params."""
        return FederalReserveChicagoRetailTradeQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveChicagoRetailTradeQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the requested CARTS dashboard figure from the Chicago Fed."""
        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )
        from openbb_federal_reserve.utils.chicago import get_text

        figures = [query.figure]
        if query.figure == "nowcast_contributions":
            figures.append("current_month")

        payload: dict[str, str] = {}
        for figure in figures:
            url = BASE_URL.format(figure=_FIGURE_FILES[figure])
            text = cached(
                f"chicago_carts_{figure}",
                lambda: seconds_until_next_release("weekly"),
                lambda url=url: get_text(url),
            )
            if not text:
                raise EmptyDataError("The request was returned empty.")
            payload[figure] = text

        return [payload]

    @staticmethod
    def transform_data(
        query: FederalReserveChicagoRetailTradeQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveChicagoRetailTradeData]:
        """Pivot the selected figure to wide ``date`` + one column per series."""
        from io import StringIO

        from pandas import isna, read_csv, to_datetime, to_numeric

        from openbb_federal_reserve.utils.workbook import pivot_wide, round_value

        payload = data[0]

        if query.figure in _TIMESERIES:
            labels, date_format = _TIMESERIES[query.figure]
            frame = read_csv(StringIO(payload[query.figure])).rename(columns=labels)
            frame["date"] = to_datetime(frame["date"], format=date_format).dt.date
            value_columns = list(labels.values())
            melted = frame.melt(
                id_vars=["date"],
                value_vars=value_columns,
                var_name="series",
                value_name="value",
            )
            melted["value"] = to_numeric(melted["value"], errors="coerce")
        elif query.figure == "current_month":
            frame = read_csv(StringIO(payload["current_month"]))
            frame["date"] = to_datetime(frame["date"], format="%b-%Y").dt.date
            frame["value"] = to_numeric(
                frame["value"].astype(str).str.replace("%", "", regex=False),
                errors="coerce",
            )
            melted = frame.rename(columns={"metric": "series"})[
                ["date", "series", "value"]
            ]
        else:
            frame = read_csv(StringIO(payload["nowcast_contributions"]))
            snapshot = read_csv(StringIO(payload["current_month"]))
            year = to_datetime(snapshot["date"].iloc[0], format="%b-%Y").year
            frame = frame.rename(columns={frame.columns[0]: "series"})
            frame["date"] = to_datetime(
                frame["month"] + f"-{year}", format="%b-%Y"
            ).dt.date
            frame["value"] = to_numeric(frame["value"], errors="coerce")
            melted = frame[["date", "series", "value"]]

        if query.start_date:
            melted = melted[melted["date"] >= query.start_date]
        if query.end_date:
            melted = melted[melted["date"] <= query.end_date]

        records = [
            {
                "date": row["date"],
                "series": row["series"],
                "value": (
                    None
                    if isinstance(row["value"], float) and isna(row["value"])
                    else round_value(float(row["value"]))
                ),
            }
            for row in melted.sort_values(["date", "series"]).to_dict(orient="records")
        ]
        rows = pivot_wide(records, index="date", column="series", value="value")
        return [
            FederalReserveChicagoRetailTradeData.model_validate(row) for row in rows
        ]
