"""Deribit Mark Price History Model."""

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_deribit.utils.constants import (
    MARK_PRICE_CHOICES_ENDPOINT,
    SYMBOL_STYLE,
)


class DeribitMarkPriceHistoryQueryParams(QueryParams):
    """Deribit Mark Price History Query.

    Source: https://docs.deribit.com/api-reference/market-data/public-get_mark_price_history
    """

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": MARK_PRICE_CHOICES_ENDPOINT,
                "style": SYMBOL_STYLE,
            },
        }
    }

    symbol: str | None = Field(
        default=None,
        description="One or more instrument names. Left out, the strike nearest"
        + " the index on the front volatility index expiration is used.",
    )
    start_date: Any | None = Field(
        default=None, description="Return marks from this date onwards."
    )
    end_date: Any | None = Field(
        default=None, description="Return marks up to this date."
    )


class DeribitMarkPriceHistoryData(Data):
    """Deribit Mark Price History Data."""

    date: datetime = Field(
        description="When the mark was published.",
        json_schema_extra={"x-widget_config": {"chartDataType": "category"}},
    )
    symbol: str = Field(
        description="The name of the instrument.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    mark_price: float = Field(
        description="The price the exchange marked the instrument at.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "series"},
        },
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def validate_date(cls, v):
        """Read the timestamp as a datetime."""
        from openbb_deribit.utils.helpers import from_timestamp

        return from_timestamp(v)


class DeribitMarkPriceHistoryFetcher(
    Fetcher[DeribitMarkPriceHistoryQueryParams, list[DeribitMarkPriceHistoryData]]
):
    """Transform the query, extract and transform the data from the Deribit endpoint."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> DeribitMarkPriceHistoryQueryParams:
        """Transform the query."""
        return DeribitMarkPriceHistoryQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitMarkPriceHistoryQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Deribit endpoint.

        Raises
        ------
        EmptyDataError
            If none of the instruments published a mark. The exchange keeps this
            history only for the options its volatility indexes are built from.
        """
        from datetime import (
            datetime as dt,
            timedelta,
            timezone,
        )

        from openbb_deribit.utils.client import gather
        from openbb_deribit.utils.helpers import (
            default_volatility_option,
            get_perpetual_symbols,
            to_timestamp,
        )

        now = dt.now(timezone.utc)
        start = (
            to_timestamp(query.start_date)
            if query.start_date
            else to_timestamp(now - timedelta(days=1))
        )
        end = to_timestamp(query.end_date) if query.end_date else to_timestamp(now)
        if query.symbol:
            symbols = [s.strip().upper() for s in query.symbol.split(",") if s.strip()]
            perpetuals = await get_perpetual_symbols()
            resolved = [perpetuals.get(symbol, symbol) for symbol in symbols]
        else:
            resolved = [await default_volatility_option()]
        results = await gather(
            [
                (
                    "get_mark_price_history",
                    {
                        "instrument_name": symbol,
                        "start_timestamp": start,
                        "end_timestamp": end,
                    },
                )
                for symbol in resolved
            ]
        )
        data = [
            {"date": point[0], "symbol": symbol, "mark_price": point[1]}
            for symbol, result in zip(resolved, results)
            if isinstance(result, list)
            for point in result
        ]

        if not data:
            raise EmptyDataError(
                f"Deribit published no mark price history for"
                f" {', '.join(resolved)}. The exchange keeps this history only"
                " for the options its volatility indexes are built from."
            )

        return data

    @staticmethod
    def transform_data(
        query: DeribitMarkPriceHistoryQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DeribitMarkPriceHistoryData]:
        """Transform the data to the model."""
        return [
            DeribitMarkPriceHistoryData.model_validate(record)
            for record in sorted(data, key=lambda d: (d["date"], d["symbol"]))
        ]
