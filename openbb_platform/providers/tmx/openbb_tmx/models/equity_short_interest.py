"""TMX Equity Short Interest Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field, field_validator


class TmxShortInterestQueryParams(QueryParams):
    """TMX Short Interest Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    use_cache: bool = Field(
        default=True,
        description="Whether to use the on-disk response cache. Set to False to bypass.",
    )


class TmxShortInterestData(Data):
    """TMX Short Interest Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    settlement_date: dateType | None = Field(
        default=None, description="The settlement date of the reported position."
    )
    short_interest: int | None = Field(
        default=None, description="Number of shares held short."
    )
    short_interest_percent: float | None = Field(
        default=None,
        description="Short interest as a percent of the outstanding float.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    days_to_cover_10d: float | None = Field(
        default=None,
        description="Days to cover, against the ten-day average volume.",
    )
    days_to_cover_30d: float | None = Field(
        default=None,
        description="Days to cover, against the thirty-day average volume.",
    )
    days_to_cover_90d: float | None = Field(
        default=None,
        description="Days to cover, against the ninety-day average volume.",
    )

    @field_validator("short_interest_percent", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Return the percent as a decimal."""
        return float(v) / 100 if v is not None else None


class TmxShortInterestFetcher(
    Fetcher[TmxShortInterestQueryParams, list[TmxShortInterestData]]
):
    """TMX Short Interest Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxShortInterestQueryParams:
        """Transform the query."""
        return TmxShortInterestQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxShortInterestQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the TMX endpoint."""
        import asyncio

        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_tmx.utils import gql
        from openbb_tmx.utils.cache import amake_gql_request
        from openbb_tmx.utils.helpers import normalize_symbol

        results: list[dict] = []

        async def create_task(symbol: str) -> None:
            """Fetch the short interest for a single symbol."""
            symbol = normalize_symbol(symbol)
            response = await amake_gql_request(
                "GetCompanyShortInterest",
                gql.SHORT_INTEREST,
                {"symbol": symbol},
                symbol=symbol,
                use_cache=query.use_cache,
            )
            record = (response or {}).get("getCompanyShortInterest")

            if record:
                results.append({"requested_symbol": symbol, **record})

        await asyncio.gather(*(create_task(s) for s in query.symbol.split(",")))

        if not results:
            raise EmptyDataError(f"No short interest was returned for {query.symbol}.")

        return results

    @staticmethod
    def transform_data(
        query: TmxShortInterestQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxShortInterestData]:
        """Transform the data and validate the model."""
        return [
            TmxShortInterestData.model_validate(
                {
                    "symbol": d.get("requested_symbol"),
                    "settlement_date": d.get("BUSINESS_DATE"),
                    "short_interest": d.get("SHORT_INTEREST"),
                    "short_interest_percent": d.get("SHORTINTERESTPCT"),
                    "days_to_cover_10d": d.get("DAYSTOCOVER10DAY"),
                    "days_to_cover_30d": d.get("DAYSTOCOVER30DAY"),
                    "days_to_cover_90d": d.get("DAYSTOCOVER90DAY"),
                }
            )
            for d in data
        ]
