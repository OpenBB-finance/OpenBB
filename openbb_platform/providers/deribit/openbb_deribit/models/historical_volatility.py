"""Deribit Historical Volatility Model."""

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_deribit.utils.constants import REALIZED_VOLATILITY_CURRENCIES


class DeribitHistoricalVolatilityQueryParams(QueryParams):
    """Deribit Historical Volatility Query.

    A currency pegged to the unit it is measured against has no volatility to
    realize: USDC and USDT read a few tenths of a percent, which is the peg
    moving rather than the asset, so neither is offered. EURR is a euro token
    measured against the dollar, so what it reads is the euro rate, and it is.

    Source: https://docs.deribit.com/api-reference/market-data/public-get_historical_volatility
    """

    __json_schema_extra__ = {
        "currency": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "options": [
                    {"label": name, "value": name}
                    for name in REALIZED_VOLATILITY_CURRENCIES
                ]
            },
        }
    }

    currency: str = Field(
        default="BTC", description="The currency whose realized volatility to read."
    )

    @field_validator("currency", mode="before")
    @classmethod
    def _listed_currencies(cls, value):
        """Accept one currency or several, and refuse any the exchange omits.

        Raises
        ------
        ValueError
            If a currency the exchange does not publish this for is asked for.
        """
        chosen = [
            item.strip().upper() for item in str(value).split(",") if item.strip()
        ]
        unlisted = [
            item for item in chosen if item not in REALIZED_VOLATILITY_CURRENCIES
        ]

        if unlisted:
            raise ValueError(
                f"Deribit publishes no realized volatility for {unlisted}."
                f" It publishes {list(REALIZED_VOLATILITY_CURRENCIES)}."
            )

        return ",".join(chosen)


class DeribitHistoricalVolatilityData(Data):
    """Deribit Historical Volatility Data."""

    date: datetime = Field(
        description="When the reading was published.",
        json_schema_extra={"x-widget_config": {"chartDataType": "category"}},
    )
    currency: str = Field(
        description="The currency the reading belongs to.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    volatility: float = Field(
        description="The realized volatility over the trailing window.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"chartDataType": "series"},
        },
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def validate_date(cls, v):
        """Read the timestamp as a datetime."""
        from openbb_deribit.utils.helpers import from_timestamp

        return from_timestamp(v)


class DeribitHistoricalVolatilityFetcher(
    Fetcher[
        DeribitHistoricalVolatilityQueryParams,
        list[DeribitHistoricalVolatilityData],
    ]
):
    """Transform the query, extract and transform the data from the Deribit endpoint."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> DeribitHistoricalVolatilityQueryParams:
        """Transform the query."""
        return DeribitHistoricalVolatilityQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitHistoricalVolatilityQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Deribit endpoint.

        Raises
        ------
        EmptyDataError
            If the currency published no readings.
        """
        from openbb_deribit.utils.client import gather

        currencies = [c.strip().upper() for c in query.currency.split(",") if c.strip()]
        results = await gather(
            [
                ("get_historical_volatility", {"currency": currency})
                for currency in currencies
            ]
        )
        data = [
            {"date": point[0], "currency": currency, "volatility": point[1]}
            for currency, result in zip(currencies, results)
            if isinstance(result, list)
            for point in result
        ]

        if not data:
            raise EmptyDataError(
                f"Deribit published no realized volatility for {', '.join(currencies)}."
            )

        return data

    @staticmethod
    def transform_data(
        query: DeribitHistoricalVolatilityQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DeribitHistoricalVolatilityData]:
        """Transform the data to the model."""
        return [
            DeribitHistoricalVolatilityData.model_validate(record)
            for record in sorted(data, key=lambda d: (d["date"], d["currency"]))
        ]
