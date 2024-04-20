"""Tradier Options Chains Model."""

# pylint: disable = unused-argument

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil.parser import parse
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.options_chains import (
    OptionsChainsData,
    OptionsChainsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request, safe_fromtimestamp
from openbb_tradier.utils.constants import OPTIONS_EXCHANGES, STOCK_EXCHANGES
from pydantic import Field, field_validator, model_validator
from pytz import timezone


class TradierOptionsChainsQueryParams(OptionsChainsQueryParams):
    """Tradier Options Chains Query.

    Source: https://documentation.tradier.com/brokerage-api/markets/get-options-chains

    Greeks/IV data is updated once per hour.
    This data is calculated using the ORATS APIs and is supplied directly from them.
    """


class TradierOptionsChainsData(OptionsChainsData):
    """Tradier Options Chains Data."""

    __alias_dict__ = {
        "expiration": "expiration_date",
        "contract_symbol": "symbol",
        "last_trade_price": "last",
        "bid_size": "bidsize",
        "ask_size": "asksize",
        "change_percent": "change_percentage",
        "orats_final_iv": "smv_vol",
        "implied_volatility": "mid_iv",
        "greeks_timestamp": "updated_at",
        "prev_close": "prevclose",
        "year_high": "week_52_high",
        "year_low": "week_52_low",
        "last_trade_timestamp": "trade_date",
        "last_trade_volume": "last_volume",
        "ask_exchange": "askexch",
        "ask_timestamp": "ask_date",
        "bid_exchange": "bidexch",
        "bid_timestamp": "bid_date",
    }

    phi: Optional[float] = Field(
        default=None,
        description="Phi of the option. The sensitivity of the option relative to dividend yield.",
    )
    bid_iv: Optional[float] = Field(
        default=None,
        description="Implied volatility of the bid price.",
    )
    ask_iv: Optional[float] = Field(
        default=None,
        description="Implied volatility of the ask price.",
    )
    orats_final_iv: Optional[float] = Field(
        default=None,
        description="ORATS final implied volatility of the option, updated once per hour.",
    )
    year_high: Optional[float] = Field(
        default=None,
        description="52-week high price of the option.",
    )
    year_low: Optional[float] = Field(
        default=None,
        description="52-week low price of the option.",
    )
    last_trade_volume: Optional[int] = Field(
        default=None,
        description="Volume of the last trade.",
    )
    dte: Optional[int] = Field(
        default=None,
        description="Days to expiration.",
    )
    contract_size: Optional[int] = Field(
        default=None,
        description="Size of the contract.",
    )
    bid_exchange: Optional[str] = Field(
        default=None,
        description="Exchange of the bid price.",
    )
    bid_timestamp: Optional[datetime] = Field(
        default=None,
        description="Timestamp of the bid price.",
    )
    ask_exchange: Optional[str] = Field(
        default=None,
        description="Exchange of the ask price.",
    )
    ask_timestamp: Optional[datetime] = Field(
        default=None,
        description="Timestamp of the ask price.",
    )
    greeks_timestamp: Optional[datetime] = Field(
        default=None,
        description="Timestamp of the last greeks update."
        + " Greeks/IV data is updated once per hour.",
    )
    last_trade_timestamp: Optional[datetime] = Field(
        default=None, description="Timestamp of the last trade."
    )

    @field_validator(
        "last_trade_timestamp",
        "greeks_timestamp",
        "ask_timestamp",
        "bid_timestamp",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def validate_dates(cls, v):
        """Validate the dates."""
        if v != 0 and v is not None and isinstance(v, int):
            v = int(v) / 1000  # milliseconds to seconds
            v = safe_fromtimestamp(v)
            v = v.replace(microsecond=0)
            v = v.astimezone(timezone("America/New_York"))
            return v
        if v is not None and isinstance(v, str):
            v = parse(v)
            v = v.replace(microsecond=0, tzinfo=timezone("UTC"))
            v = v.astimezone(timezone("America/New_York"))
            return v
        return None

    @field_validator("change_percent", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Normalize the percentage."""
        return float(v) / 100 if v else None

    @field_validator("bid_exchange", "ask_exchange", mode="before", check_fields=False)
    @classmethod
    def map_exchange(cls, v):
        """Map the exchange from a code to a name."""
        if v:
            return (
                OPTIONS_EXCHANGES.get(v, v)
                if v in OPTIONS_EXCHANGES
                else STOCK_EXCHANGES.get(v, v)
            )
        return None

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):
        """Check for zero values and replace with None."""
        return (
            {
                k: None if (v == 0 or str(v) == "0") and k != "dte" else v
                for k, v in values.items()
            }
            if isinstance(values, dict)
            else values
        )


class TradierOptionsChainsFetcher(
    Fetcher[TradierOptionsChainsQueryParams, List[TradierOptionsChainsData]]
):
    """Tradier Options Chains Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TradierOptionsChainsQueryParams:
        """Transform the query parameters."""
        return TradierOptionsChainsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TradierOptionsChainsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Tradier endpoint."""
        api_key = credentials.get("tradier_api_key") if credentials else ""
        sandbox = True

        if api_key and credentials.get("tradier_account_type") not in ["sandbox", "live"]:  # type: ignore
            raise ValueError(
                "Invalid account type for Tradier. Must be either 'sandbox' or 'live'."
            )

        if api_key:
            sandbox = (
                credentials.get("tradier_account_type") == "sandbox"
                if credentials
                else False
            )

        BASE_URL = (
            "https://api.tradier.com/v1/markets/options/"
            if sandbox is False
            else "https://sandbox.tradier.com/v1/markets/options/"
        )

        HEADERS = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        }

        # Get the expiration dates for the symbol so we can gather the chains data.
        async def get_expirations(symbol):
            """Get the expiration dates for the given symbol."""
            url = (
                f"{BASE_URL}expirations?symbol={symbol}&includeAllRoots=true"
                "&strikes=false&contractSize=false&expirationType=false"
            )
            response = await amake_request(url, headers=HEADERS)
            if response.get("expirations") and isinstance(response["expirations"].get("date"), list):  # type: ignore
                expirations = response["expirations"].get("date")  # type: ignore
                return expirations if expirations else []

        expirations = await get_expirations(query.symbol)
        if expirations == []:
            raise ValueError(f"No expiration dates found for {query.symbol}")

        results = []

        async def get_one(url):
            """Get the chain for a single expiration."""
            chain = await amake_request(url, headers=HEADERS)
            if chain.get("options") and isinstance(chain["options"].get("option", []), list):  # type: ignore
                data = chain["options"]["option"]  # type: ignore
                for d in data.copy():
                    # Remove any strikes returned without data.
                    keys = ["volume", "open_interest", "last", "bid", "ask"]
                    if all(d.get(key) in [0, "0", None] for key in keys):
                        data.remove(d)
                        continue
                    # Flatten the nested greeks dictionary
                    greeks = d.pop("greeks")
                    if greeks is not None:
                        d.update(**greeks)
                    # Pop fields that are duplicate information or not of interest.
                    to_pop = [
                        "root_symbol",
                        "exch",
                        "type",
                        "expiration_type",
                        "underlying",
                        "description",
                        "average_volume",
                    ]
                    _ = [d.pop(key) for key in to_pop if key in d]
                    # Add the DTE field to the data for easier filtering later.
                    d["dte"] = (
                        datetime.strptime(d["expiration_date"], "%Y-%m-%d").date()
                        - datetime.now().date()
                    ).days

                results.extend(data)

        urls = [
            f"{BASE_URL}chains?symbol={query.symbol}&expiration={expiration}&greeks=true"
            for expiration in expirations  # type: ignore
        ]

        tasks = [get_one(url) for url in urls]

        await asyncio.gather(*tasks)

        if not results:
            raise EmptyDataError(f"No options chains data found for {query.symbol}.")
        return sorted(
            results, key=lambda x: [x["expiration_date"], x["strike"], x["symbol"]]
        )

    @staticmethod
    def transform_data(
        query: TradierOptionsChainsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TradierOptionsChainsData]:
        """Transform and validate the data."""
        return [TradierOptionsChainsData.model_validate(d) for d in data]
