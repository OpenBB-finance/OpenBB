"""Nasdaq Nordic Knocked-Out Instruments Model."""

from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

KNOCKED_OUT_STATES = {"buyback": "BUYBACK", "trading_halt": "TRADING_HALT"}


class NasdaqNordicKnockedOutQueryParams(QueryParams):
    """Nasdaq Nordic Knocked-Out Instruments Query.

    Source: https://www.nasdaq.com/european-market-activity/warrants-certificates/knocked-out-instruments
    """

    __json_schema_extra__ = {"state": {"choices": list(KNOCKED_OUT_STATES)}}

    state: Literal["buyback", "trading_halt"] = Field(
        default="buyback",
        description="Whether the instrument is in buyback or halted.",
    )


class NasdaqNordicKnockedOutData(Data):
    """Nasdaq Nordic Knocked-Out Instruments Data.

    Leverage instruments whose barrier has been breached. Nasdaq withdraws the
    ticker on a knock-out, so the instruments are identified by ISIN and name.
    """

    isin: str | None = Field(default=None, description="The instrument ISIN.")
    name: str | None = Field(default=None, description="The instrument name.")
    status: str | None = Field(default=None, description="The knock-out status.")
    asset_class: str | None = Field(
        default=None, description="The Nasdaq Nordic asset class."
    )
    exchange_symbol: str | None = Field(default=None, description="The venue MIC.")
    orderbook_id: str | None = Field(
        default=None, description="The Nasdaq Nordic orderbook identifier."
    )


class NasdaqNordicKnockedOutFetcher(
    Fetcher[
        NasdaqNordicKnockedOutQueryParams,
        list[NasdaqNordicKnockedOutData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqNordicKnockedOutQueryParams:
        """Transform the query."""
        return NasdaqNordicKnockedOutQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqNordicKnockedOutQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        from openbb_nasdaq.utils.helpers import get_nasdaq_data

        data = await get_nasdaq_data(
            "nordic/screener/knocked-out?tableonly=true&lang=en&size=1000&page=1"
            f"&category={KNOCKED_OUT_STATES[query.state]}"
        )

        return ((data or {}).get("instrumentListing") or {}).get("rows") or []

    @staticmethod
    def transform_data(
        query: NasdaqNordicKnockedOutQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqNordicKnockedOutData]:
        """Transform the data to the standard format.

        Raises
        ------
        EmptyDataError
            If no instrument is in the requested state.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import clean_value

        if not data:
            raise EmptyDataError(f"No instruments are currently in '{query.state}'.")

        return [
            NasdaqNordicKnockedOutData.model_validate(
                {
                    "isin": clean_value(row.get("isin")),
                    "name": clean_value(row.get("fullName")),
                    "status": clean_value(row.get("noteDescription")),
                    "asset_class": clean_value(row.get("assetClass")),
                    "exchange_symbol": clean_value(row.get("exchangeSymbol")),
                    "orderbook_id": clean_value(row.get("orderbookId")),
                }
            )
            for row in data
        ]
