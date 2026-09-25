"""Deribit Futures Info Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.futures_info import (
    FuturesInfoData,
    FuturesInfoQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field

from openbb_deribit.models.ticker import DeribitTickerData
from openbb_deribit.utils.constants import (
    INSTRUMENT_CHOICES_ENDPOINT,
    SYMBOL_STYLE,
)


class DeribitFuturesInfoQueryParams(FuturesInfoQueryParams):
    """Deribit Futures Info Query.

    Source: https://docs.deribit.com/api-reference/market-data/public-ticker
    """

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": INSTRUMENT_CHOICES_ENDPOINT,
                "style": SYMBOL_STYLE,
            },
        }
    }

    symbol: str = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + " A perpetual can be given by its currency pair - SOLUSDC - or by its"
        + " full instrument name - SOL_USDC-PERPETUAL."
    )


class DeribitFuturesInfoData(DeribitTickerData, FuturesInfoData):
    """Deribit Futures Info Data."""

    model_config = ConfigDict(extra="ignore")


class DeribitFuturesInfoFetcher(
    Fetcher[DeribitFuturesInfoQueryParams, list[DeribitFuturesInfoData]]
):
    """Transform the query, extract and transform the data from the Deribit endpoint."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitFuturesInfoQueryParams:
        """Transform the query."""
        return DeribitFuturesInfoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitFuturesInfoQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Deribit endpoint.

        Raises
        ------
        EmptyDataError
            If none of the instruments published a quote.
        """
        from openbb_deribit.utils.helpers import get_perpetual_symbols, get_tickers

        symbols = [s.strip().upper() for s in query.symbol.split(",") if s.strip()]
        perpetuals = await get_perpetual_symbols()
        resolved = [perpetuals.get(symbol, symbol) for symbol in symbols]
        data = await get_tickers(resolved)

        if not data:
            raise EmptyDataError(
                f"Deribit published no quote for {', '.join(resolved)}."
            )

        return sorted(
            data,
            key=lambda d: (
                resolved.index(d["instrument_name"])
                if d["instrument_name"] in resolved
                else len(resolved)
            ),
        )

    @staticmethod
    def transform_data(
        query: DeribitFuturesInfoQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DeribitFuturesInfoData]:
        """Transform the data to the model."""
        return [DeribitFuturesInfoData.model_validate(record) for record in data]
