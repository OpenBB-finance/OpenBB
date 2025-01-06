"""Deribit Futures Instruments Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.futures_instruments import (
    FuturesInstrumentsData,
    FuturesInstrumentsQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import ConfigDict, Field, field_validator


class DeribitFuturesInstrumentsQueryParams(FuturesInstrumentsQueryParams):
    """Deribit Futures Instruments Query."""


class DeribitFuturesInstrumentData(FuturesInstrumentsData):
    """Deribit Futures Instrument Data."""

    __alias_dict__ = {
        "symbol": "instrument_name",
    }

    model_config = ConfigDict(extra="ignore")

    instrument_id: int = Field(description="Deribit Instrument ID")
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    base_currency: str = Field(description="The underlying currency being traded.")
    counter_currency: str = Field(description="Counter currency for the instrument.")
    quote_currency: str = Field(
        description="The currency in which the instrument prices are quoted."
    )
    settlement_currency: Optional[str] = Field(
        default=None, description="Settlement currency for the instrument."
    )
    future_type: str = Field(description="Type of the instrument. linear or reversed")
    settlement_period: Optional[str] = Field(
        default=None, description="The settlement period."
    )
    price_index: str = Field(
        description="Name of price index that is used for this instrument"
    )
    contract_size: float = Field(description="Contract size for instrument.")
    is_active: bool = Field(
        description="Indicates if the instrument can currently be traded."
    )
    creation_timestamp: datetime = Field(
        description="The time when the instrument was first created (milliseconds since the UNIX epoch)."
    )
    expiration_timestamp: Optional[datetime] = Field(
        default=None,
        description="The time when the instrument will expire (milliseconds since the UNIX epoch).",
    )
    tick_size: float = Field(
        description="Specifies minimal price change and, as follows, the number of decimal places for instrument prices."
    )
    min_trade_amount: float = Field(
        description="Minimum amount for trading, in USD units."
    )
    max_leverage: int = Field(description="Maximal leverage for instrument.")
    max_liquidation_commission: float = Field(
        description="Maximal liquidation trade commission for instrument."
    )
    block_trade_commission: float = Field(
        description="Block Trade commission for instrument."
    )
    block_trade_min_trade_amount: float = Field(
        description="Minimum amount for block trading."
    )
    block_trade_tick_size: float = Field(
        description="Specifies minimal price change for block trading."
    )

    maker_commission: Optional[float] = Field(
        default=None, description="Maker commission for instrument."
    )
    taker_commission: Optional[float] = Field(
        default=None, description="Taker commission for instrument."
    )

    @field_validator("expiration_timestamp", mode="before", check_fields=False)
    @classmethod
    def _validate_expiration(cls, v):
        """Validate the expiration timestamp."""
        if int(v) == 32503708800000:
            return None
        return v


class DeribitFuturesInstrumentsFetcher(
    Fetcher[DeribitFuturesInstrumentsQueryParams, list[DeribitFuturesInstrumentData]]
):
    """Deribit Futures Instruments Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitFuturesInstrumentsQueryParams:
        """Transform the query."""
        return DeribitFuturesInstrumentsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitFuturesInstrumentsQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list:
        """Extract data from Deribit API."""
        # pylint: disable=import-outside-toplevel
        from openbb_deribit.utils.helpers import get_instruments

        try:
            data = await get_instruments("all", "future")
        except Exception as e:  # pylint: disable=broad-except
            raise OpenBBError(f"Error fetching data: {e}") from e
        if not data:
            raise OpenBBError(
                "There was an error with the request and it was returned empty."
            )

        return data

    @staticmethod
    def transform_data(
        query: DeribitFuturesInstrumentsQueryParams,
        data: list,
        **kwargs: Any,
    ) -> list[DeribitFuturesInstrumentData]:
        """Transform the data."""
        return [DeribitFuturesInstrumentData.model_validate(d) for d in data]
