"""Federal Reserve Bank of Chicago Labor Market Indicators (CFLMI) Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = "https://api.data.chicagofed.org/CFLMI/chi-labor-market-indicators.xlsx"

_TABLES = {
    "rates": ("1. Rates", False),
    "realtime_unemployment": ("2. Chicago Fed Real-Time UR", False),
    "unemployment_contributions": ("3. Real-Time UR Contributions", False),
    "unemployment_probabilities": ("4. Real-Time UR Probs", True),
}

_RATE_LABELS = {
    "layoffs_other_seps": "Layoffs and Other Separations",
    "hiring_rate_uw": "Hiring Rate (Unemployment-Weighted)",
    "fcr": "Fundamental Churn Rate",
    "s": "Separation Rate",
    "f": "Job-Finding Rate",
}


class FederalReserveChicagoLaborMarketQueryParams(QueryParams):
    """Chicago Fed Labor Market Indicators Query Parameters."""

    __json_schema_extra__ = {
        "table": {
            "x-widget_config": {
                "options": [
                    {"label": sheet.split(". ", 1)[-1], "value": code}
                    for code, (sheet, _) in _TABLES.items()
                ]
            }
        },
    }

    table: Literal[
        "rates",
        "realtime_unemployment",
        "unemployment_contributions",
        "unemployment_probabilities",
    ] = Field(
        default="rates",
        description="The labor-market flow rates, the real-time unemployment-rate"
        " nowcast, its component contributions, or its forecast probabilities.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveChicagoLaborMarketData(Data):
    """Chicago Fed Labor Market Indicators Data."""

    date: dateType = Field(description="The observation month.")
    release: str | None = Field(
        default=None,
        description="The estimate vintage, where applicable ('advance' or 'final')."
        " Real-time unemployment tables publish two estimates per date.",
    )


class FederalReserveChicagoLaborMarketFetcher(
    Fetcher[
        FederalReserveChicagoLaborMarketQueryParams,
        list[FederalReserveChicagoLaborMarketData],
    ]
):
    """Chicago Fed Labor Market Indicators Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveChicagoLaborMarketQueryParams:
        """Transform the query params."""
        return FederalReserveChicagoLaborMarketQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveChicagoLaborMarketQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the CFLMI workbook from the Chicago Fed."""
        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )
        from openbb_federal_reserve.utils.chicago import get_bytes

        content = cached(
            "chicago_cflmi",
            lambda: seconds_until_next_release("monthly"),
            lambda: get_bytes(URL),
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveChicagoLaborMarketQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveChicagoLaborMarketData]:
        """Pivot the selected table to wide ``(date, release)`` + series columns."""
        from openbb_federal_reserve.utils.workbook import melt_sheet, pivot_wide

        sheet, group_header = _TABLES[query.table]
        records = melt_sheet(
            data[0]["_raw"],
            sheet,
            group_header=group_header,
            labels=_RATE_LABELS if query.table == "rates" else None,
            key_columns=("release",),
            start_date=query.start_date,
            end_date=query.end_date,
        )
        rows = pivot_wide(
            records, index=("date", "release"), column="series", value="value"
        )
        return [
            FederalReserveChicagoLaborMarketData.model_validate(row) for row in rows
        ]
