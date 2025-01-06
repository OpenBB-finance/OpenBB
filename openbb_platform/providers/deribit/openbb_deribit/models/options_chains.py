"""Deribit Options Chains Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.options_chains import (
    OptionsChainsData,
    OptionsChainsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_deribit.utils.helpers import DERIBIT_OPTIONS_SYMBOLS
from pydantic import Field, field_validator


class DeribitOptionsChainsQueryParams(OptionsChainsQueryParams):
    """Deribit Options Chains Query Parameters Model."""

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": False,
            "choices": DERIBIT_OPTIONS_SYMBOLS,
        }
    }

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _validate_symbol(cls, v):
        """Validate the symbol."""
        if v.upper() not in DERIBIT_OPTIONS_SYMBOLS:
            raise ValueError(
                f"Invalid Deribit symbol. Supported symbols are: {', '.join(DERIBIT_OPTIONS_SYMBOLS)}",
            )
        return v


class DeribitOptionsChainsData(OptionsChainsData):
    """Deribit Options Chains Data Model."""

    __alias_dict__ = {
        "contract_symbol": "instrument_name",
        "change_percent": "price_change",
        "underlying_symbol": "underlying_index",
        "underlying_spot_price": "index_price",
        "bid_size": "best_bid_amount",
        "ask_size": "best_ask_amount",
        "bid": "best_bid_price",
        "ask": "best_ask_price",
        "implied_volatility": "mark_iv",
        "mark": "mark_price",
        "last_trade_price": "last_price",
        "volume_notional": "volume_usd",
    }

    __doc__ = OptionsChainsData.__doc__

    bid_iv: list[Union[float, None]] = Field(
        default_factory=list,
        description="The implied volatility of the bid price.",
        json_schema_extra={"x-unit_measurement": "decimal"},
    )
    ask_iv: list[Union[float, None]] = Field(
        default_factory=list,
        description="The implied volatility of the ask price.",
        json_schema_extra={"x-unit_measurement": "decimal"},
    )
    interest_rate: list[Union[float, None]] = Field(
        default_factory=list,
        description="The interest rate used by Deribit to calculate greeks.",
    )
    underlying_spot_price: list[float] = Field(
        description="The spot price of the underlying asset."
        " The underlying asset is the specific future or index that the option is based on.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    settlement_price: list[Union[float, None]] = Field(
        default_factory=list,
        description="The settlement price of the contract.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    min_price: list[Union[float, None]] = Field(
        default_factory=list,
        description="The minimum price allowed.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    max_price: list[Union[float, None]] = Field(
        default_factory=list,
        description="The maximum price allowed.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    volume_notional: list[Union[float, None]] = Field(
        default_factory=list,
        description="The notional trading volume of the contract, as USD or USDC.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    timestamp: list[datetime] = Field(
        description="The datetime of the data, as America/New_York time.",
    )


class DeribitOptionsChainsFetcher(
    Fetcher[DeribitOptionsChainsQueryParams, DeribitOptionsChainsData]
):
    """Deribit Options Chains Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitOptionsChainsQueryParams:
        """Transform the query parameters."""
        return DeribitOptionsChainsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitOptionsChainsQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        import json
        import websockets
        from openbb_deribit.utils.helpers import get_options_symbols
        from pandas import to_datetime
        from websockets.asyncio.client import connect
        from warnings import warn

        # We need to identify each option contract in order to fetch the chains data.
        symbols_dict: dict[str, str] = {}

        try:
            symbols_dict = await get_options_symbols(query.symbol)
        except OpenBBError as e:
            raise OpenBBError(e) from e

        # For each expiration, we need to create a websocket connection to fetch the data.
        # We subscribe to each contract symbol and break the connection when we have all the data for an expiry.
        # If it takes too long, we break the connection and return an error message.
        results: list = []
        messages: set = set()

        async def call_api(expiration):
            """Call the Deribit API."""
            symbols = symbols_dict[expiration]
            received_symbols: set = set()
            msg = {
                "jsonrpc": "2.0",
                "id": 3600,
                "method": "public/subscribe",
                "params": {"channels": ["ticker." + d + ".100ms" for d in symbols]},
            }
            async with connect("wss://www.deribit.com/ws/api/v2") as websocket:
                await websocket.send(json.dumps(msg))
                try:
                    await asyncio.wait_for(
                        receive_data(websocket, symbols, received_symbols), timeout=2.0
                    )
                except asyncio.TimeoutError:
                    messages.add(f"Timeout reached for {expiration}, data incomplete.")

        async def receive_data(websocket, symbols, received_symbols):
            """Receive the data from the websocket with a timeout."""
            while True:
                try:
                    response = await websocket.recv()
                except websockets.ConnectionClosed:
                    break
                data = json.loads(response)

                if "params" not in data:
                    continue

                if "error" in data and data.get("error"):
                    messages.add(f"Error while receiving data -> {data['error']}")
                    break

                res = data.get("params", {}).get("data", {})
                symbol = res.get("instrument_name")

                # While we are handling the data, we will parse the message.
                if symbol not in received_symbols:
                    received_symbols.add(symbol)
                    stats = res.pop("stats", {})
                    greeks = res.pop("greeks", {})
                    timestamp = res.pop("timestamp", None)
                    underlying_symbol = res.get("underlying_index")

                    if underlying_symbol == "index_price":
                        res["underlying_index"] = symbol.split("-")[0].replace("_", "-")

                    res["timestamp"] = to_datetime(
                        timestamp, unit="ms", utc=True
                    ).tz_convert("America/New_York")

                    if res.get("estimated_delivery_price") == res.get("index_price"):
                        _ = res.pop("estimated_delivery_price", None)

                    _ = res.pop("state", None)
                    result = {
                        "expiration": to_datetime(symbol.split("-")[1]).date(),
                        "strike": (
                            float(symbol.split("-")[2].replace("d", "."))
                            if "d" in symbol.split("-")[2]
                            else int(symbol.split("-")[2])
                        ),
                        "option_type": (
                            "call"
                            if symbol.endswith("-C")
                            else "put" if symbol.endswith("-P") else None
                        ),
                        **res,
                        **stats,
                        **greeks,
                    }
                    result["dte"] = (
                        result["expiration"] - to_datetime("today").date()
                    ).days
                    results.append(result)

                    if len(received_symbols) == len(symbols):
                        await websocket.close()
                        break

        tasks = [
            asyncio.create_task(call_api(expiration)) for expiration in symbols_dict
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

        if messages and not results:
            raise OpenBBError(", ".join(messages))

        if results and messages:
            for message in messages:
                warn(message)

        if not results and not messages:
            raise EmptyDataError("All requests returned empty with no error messages.")

        return results

    @staticmethod
    def transform_data(
        query: DeribitOptionsChainsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> DeribitOptionsChainsData:
        """Transform the data."""
        # pylint: disable=import-outside-toplevel
        from numpy import nan
        from pandas import DataFrame

        df = DataFrame(data)

        # For BTC and ETH options, we need to convert price units to USD.
        for col in df.columns:
            if col in [
                "last_price",
                "settlement_price",
                "mark_price",
                "min_price",
                "max_price",
                "best_ask_price",
                "best_bid_price",
                "high",
                "low",
            ] and query.symbol.upper() in ["BTC", "ETH"]:
                df.loc[:, col] = df[col].astype(float).multiply(df.index_price).round(2)
            elif col in ["price_change", "mark_iv", "bid_iv", "ask_iv"]:
                df.loc[:, col] = df[col].astype(float).divide(100)

        df = df.replace({nan: None})
        df = df.sort_values(["expiration", "strike", "option_type"])
        df = df.reset_index(drop=True)
        df.loc[:, "contract_size"] = 1
        results = df.to_dict(orient="list")

        return DeribitOptionsChainsData.model_validate(results)
