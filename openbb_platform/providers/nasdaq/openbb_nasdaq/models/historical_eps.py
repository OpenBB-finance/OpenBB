"""Nasdaq Historical EPS Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_eps import (
    HistoricalEpsData,
    HistoricalEpsQueryParams,
)
from pydantic import Field

from openbb_nasdaq.utils.constants import SYMBOL_CHOICES_ENDPOINT


class NasdaqHistoricalEpsQueryParams(HistoricalEpsQueryParams):
    """Nasdaq Historical EPS Query.

    Source: https://www.nasdaq.com/market-activity/stocks
    """

    __json_schema_extra__ = {
        "symbol": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": SYMBOL_CHOICES_ENDPOINT,
                "style": {"popupWidth": 850},
            },
        },
    }


class NasdaqHistoricalEpsData(HistoricalEpsData):
    """Nasdaq Historical EPS Data."""

    fiscal_period_ending: str | None = Field(
        default=None, description="The fiscal quarter the report covers."
    )
    surprise_percent: float | None = Field(
        default=None,
        description="The earnings surprise, as a normalized percentage.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )


class NasdaqHistoricalEpsFetcher(
    Fetcher[
        NasdaqHistoricalEpsQueryParams,
        list[NasdaqHistoricalEpsData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqHistoricalEpsQueryParams:
        """Transform the query."""
        return NasdaqHistoricalEpsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqHistoricalEpsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import get_nasdaq_data, rows_from_table

        symbol = query.symbol.upper()
        data = await get_nasdaq_data(f"company/{symbol}/earnings-surprise")
        rows = rows_from_table((data or {}).get("earningsSurpriseTable"))

        if not rows:
            raise EmptyDataError(f"No earnings history was found for {symbol}.")

        return [{**row, "symbol": symbol} for row in rows]

    @staticmethod
    def transform_data(
        query: NasdaqHistoricalEpsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqHistoricalEpsData]:
        """Transform the data to the standard format."""
        from openbb_nasdaq.utils.helpers import to_date, to_number, to_percent

        results = [
            NasdaqHistoricalEpsData.model_validate(
                {
                    "symbol": row["symbol"],
                    "date": to_date(row.get("dateReported")),
                    "eps_actual": to_number(row.get("eps")),
                    "eps_estimated": to_number(row.get("consensusForecast")),
                    "surprise_percent": to_percent(row.get("percentageSurprise")),
                    "fiscal_period_ending": row.get("fiscalQtrEnd"),
                }
            )
            for row in data
            if to_date(row.get("dateReported")) is not None
        ]

        return sorted(results, key=lambda r: r.date, reverse=True)
