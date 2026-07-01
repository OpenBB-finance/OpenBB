"""Federal Reserve Bank of Cleveland Inflation Nowcasting Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

BASE_URL = "https://www.clevelandfed.org/-/media/files/webcharts/inflationnowcasting"

_FILES = {
    "month": "nowcast_month.json",
    "quarter": "nowcast_quarter.json",
    "year": "nowcast_year.json",
}


def _target_date(subcaption: str) -> dateType | None:
    """Decode a chart subcaption into the target period's start date."""
    import re

    text = str(subcaption).strip()
    quarter = re.match(r"^(\d{4}):?Q(\d)$", text)
    if quarter:
        year, qtr = int(quarter.group(1)), int(quarter.group(2))
        return dateType(year, (qtr - 1) * 3 + 1, 1)
    month = re.match(r"^(\d{4})[-/](\d{1,2})$", text)
    if month:
        return dateType(int(month.group(1)), int(month.group(2)), 1)
    year_only = re.match(r"^(\d{4})$", text)
    if year_only:
        return dateType(int(year_only.group(1)), 1, 1)
    return None


class FederalReserveClevelandInflationNowcastQueryParams(QueryParams):
    """Cleveland Fed Inflation Nowcasting Query Parameters."""

    __json_schema_extra__ = {
        "frequency": {
            "x-widget_config": {
                "options": [
                    {"label": "Month-over-Month", "value": "month"},
                    {"label": "Quarterly Annualized", "value": "quarter"},
                    {"label": "Year-over-Year", "value": "year"},
                ]
            }
        },
    }

    frequency: Literal["month", "quarter", "year"] = Field(
        default="month",
        description="The nowcast horizon: month-over-month, quarterly annualized,"
        " or year-over-year.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveClevelandInflationNowcastData(Data):
    """Cleveland Fed Inflation Nowcasting Data.

    One row per target period, with one column per inflation measure (or its
    actual outturn) carrying that measure's final value, in percent. The
    measures are pivoted to wide, so the columns vary with the requested data.
    """

    date: dateType = Field(description="The target period being nowcast.")


class FederalReserveClevelandInflationNowcastFetcher(
    Fetcher[
        FederalReserveClevelandInflationNowcastQueryParams,
        list[FederalReserveClevelandInflationNowcastData],
    ]
):
    """Cleveland Fed Inflation Nowcasting Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveClevelandInflationNowcastQueryParams:
        """Transform the query params."""
        return FederalReserveClevelandInflationNowcastQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveClevelandInflationNowcastQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the nowcast chart payload for the requested horizon."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        filename = _FILES[query.frequency]

        def _producer() -> str:
            """Fetch the nowcast JSON text."""
            response = make_request(f"{BASE_URL}/{filename}")
            response.raise_for_status()
            return response.content.decode("utf-8-sig", "replace")

        text = cached(
            ("cleveland_inflation_nowcast", query.frequency),
            lambda: seconds_until_next_release("daily"),
            _producer,
        )
        if not text:
            raise EmptyDataError("The request was returned empty.")
        return [{"_text": text}]

    @staticmethod
    def transform_data(
        query: FederalReserveClevelandInflationNowcastQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveClevelandInflationNowcastData]:
        """Take each period's final value per series, then pivot to wide rows."""
        from json import loads

        from openbb_federal_reserve.utils.workbook import pivot_wide

        charts = loads(data[0]["_text"])
        records: list[dict] = []
        for chart in charts:
            target = _target_date(chart.get("chart", {}).get("subcaption", ""))
            if target is None:
                continue
            if query.start_date and target < query.start_date:
                continue
            if query.end_date and target > query.end_date:
                continue
            for series in chart.get("dataset", []):
                name = series.get("seriesname")
                final: float | None = None
                for point in series.get("data", []):
                    raw = point.get("value")
                    if raw not in (None, ""):
                        final = float(raw)
                if final is not None:
                    records.append({"date": target, "series": name, "value": final})

        ordered = sorted(records, key=lambda r: (r["date"], r["series"]))
        rows = pivot_wide(ordered, index="date", column="series", value="value")
        return [
            FederalReserveClevelandInflationNowcastData.model_validate(record)
            for record in rows
        ]
