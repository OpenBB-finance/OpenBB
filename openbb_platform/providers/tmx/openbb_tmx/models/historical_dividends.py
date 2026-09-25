"""TMX Stock Dividends Model"""

# pylint: disable=unused-argument

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.historical_dividends import (
    HistoricalDividendsData,
    HistoricalDividendsQueryParams,
)
from pydantic import Field


class TmxHistoricalDividendsQueryParams(HistoricalDividendsQueryParams):
    """TMX Historical Dividends Query Params"""


class TmxHistoricalDividendsData(HistoricalDividendsData):
    """TMX Historical Dividends Data"""

    __alias_dict__ = {
        "ex_dividend_date": "exDate",
        "record_date": "recordDate",
        "payment_date": "payableDate",
        "declaration_date": "declarationDate",
    }
    currency: str | None = Field(
        default=None, description="The currency the dividend is paid in."
    )
    declaration_date: dateType | None = Field(
        default=None, description="The date of the announcement."
    )
    record_date: dateType | None = Field(
        default=None,
        description="The record date of ownership for rights to the dividend.",
    )
    payment_date: dateType | None = Field(
        default=None, description="The date the dividend is paid."
    )


class TmxHistoricalDividendsFetcher(
    Fetcher[TmxHistoricalDividendsQueryParams, list[TmxHistoricalDividendsData]]
):
    """TMX Historical Dividends Fetcher"""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxHistoricalDividendsQueryParams:
        """Transform the query."""
        return TmxHistoricalDividendsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxHistoricalDividendsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the TMX endpoint."""
        from openbb_tmx.utils import gql
        from openbb_tmx.utils.cache import amake_gql_request
        from openbb_tmx.utils.helpers import normalize_symbol

        symbol = normalize_symbol(query.symbol)
        response = await amake_gql_request(
            "getDividendsForSymbol",
            gql.DIVIDENDS_FOR_SYMBOL,
            {"symbol": symbol, "page": 1, "batch": 500},
            symbol=symbol,
        )
        history = (response or {}).get("dividendHistory") or {}
        dividends = history.get("dividends") or []

        return sorted(dividends, key=lambda d: d["exDate"])

    @staticmethod
    def transform_data(
        query: TmxHistoricalDividendsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxHistoricalDividendsData]:
        """Return the transformed data."""
        return [TmxHistoricalDividendsData.model_validate(d) for d in data]
