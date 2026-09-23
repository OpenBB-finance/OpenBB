"""Deribit Funding Chart Model."""

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_deribit.utils.constants import (
    PERPETUAL_CHOICES_ENDPOINT,
    SYMBOL_STYLE,
    FundingLengths,
)


class DeribitFundingChartQueryParams(QueryParams):
    """Deribit Funding Chart Query.

    Source: https://docs.deribit.com/api-reference/market-data/public-get_funding_chart_data
    """

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": PERPETUAL_CHOICES_ENDPOINT,
                "style": SYMBOL_STYLE,
            },
        }
    }

    symbol: str = Field(
        default="BTC-PERPETUAL",
        description="One or more perpetual instrument names. A perpetual can also"
        + " be given by its shortened root, such as 'SOLUSDC'.",
    )
    length: FundingLengths = Field(
        default="8h", description="How far back the series runs."
    )


class DeribitFundingChartData(Data):
    """Deribit Funding Chart Data."""

    __alias_dict__ = {"date": "timestamp"}

    date: datetime = Field(
        description="When the rate was published.",
        json_schema_extra={"x-widget_config": {"chartDataType": "category"}},
    )
    symbol: str = Field(
        description="The name of the instrument.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    interest_8h: float | None = Field(
        default=None,
        description="The funding rate over the trailing eight hours.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {
                "headerName": "Interest 8H",
                "chartDataType": "series",
            },
        },
    )
    index_price: float | None = Field(
        default=None,
        description="The level of the index when the rate was published.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    current_interest: float | None = Field(
        default=None,
        description="The funding rate accrued so far in the current interval.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )

    @field_validator("date", mode="before", check_fields=False)
    @classmethod
    def validate_date(cls, v):
        """Read the timestamp as a datetime."""
        from openbb_deribit.utils.helpers import from_timestamp

        return from_timestamp(v)

    @field_validator(
        "interest_8h",
        "current_interest",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def as_percent(cls, v):
        """Return a rate the exchange sends as a fraction in percent units."""
        return v * 100 if v is not None else None


class DeribitFundingChartFetcher(
    Fetcher[DeribitFundingChartQueryParams, list[DeribitFundingChartData]]
):
    """Transform the query, extract and transform the data from the Deribit endpoint."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitFundingChartQueryParams:
        """Transform the query."""
        return DeribitFundingChartQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitFundingChartQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Deribit endpoint.

        Raises
        ------
        EmptyDataError
            If none of the instruments published funding over the span.
        """
        from openbb_deribit.utils.client import gather
        from openbb_deribit.utils.helpers import get_perpetual_symbols

        symbols = [s.strip().upper() for s in query.symbol.split(",") if s.strip()]
        perpetuals = await get_perpetual_symbols()
        resolved = [perpetuals.get(symbol, symbol) for symbol in symbols]
        results = await gather(
            [
                (
                    "get_funding_chart_data",
                    {"instrument_name": symbol, "length": query.length},
                )
                for symbol in resolved
            ]
        )
        data = [
            {
                "symbol": symbol,
                "current_interest": result.get("current_interest"),
                **record,
            }
            for symbol, result in zip(resolved, results)
            if isinstance(result, dict)
            for record in result.get("data") or []
        ]

        if not data:
            raise EmptyDataError(
                f"Deribit published no funding over the span for {', '.join(resolved)}."
            )

        return data

    @staticmethod
    def transform_data(
        query: DeribitFundingChartQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DeribitFundingChartData]:
        """Transform the data to the model."""
        return [
            DeribitFundingChartData.model_validate(record)
            for record in sorted(
                data, key=lambda d: (d.get("timestamp") or 0, d["symbol"])
            )
        ]
