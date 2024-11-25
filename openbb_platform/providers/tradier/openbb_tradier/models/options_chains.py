"""Tradier Options Chains Model."""

# pylint: disable = unused-argument

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.options_chains import (
    OptionsChainsData,
    OptionsChainsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_tradier.utils.constants import OPTIONS_EXCHANGES, STOCK_EXCHANGES
from pydantic import Field


class TradierOptionsChainsQueryParams(OptionsChainsQueryParams):
    """Tradier Options Chains Query.

    Source: https://documentation.tradier.com/brokerage-api/markets/get-options-chains

    Greeks/IV data is updated once per hour.
    This data is calculated using the ORATS APIs and is supplied directly from them.
    """


class TradierOptionsChainsData(OptionsChainsData):
    """Tradier Options Chains Data."""

    __doc__ = OptionsChainsData.__doc__
    __alias_dict__ = {
        "expiration": "expiration_date",
        "underlying_symbol": "underlying",
        "contract_symbol": "symbol",
        "last_trade_price": "last",
        "bid_size": "bidsize",
        "ask_size": "asksize",
        "change_percent": "change_percentage",
        "orats_final_iv": "smv_vol",
        "implied_volatility": "mid_iv",
        "greeks_time": "updated_at",
        "prev_close": "prevclose",
        "year_high": "week_52_high",
        "year_low": "week_52_low",
        "last_trade_time": "trade_date",
        "last_trade_size": "last_volume",
        "ask_exchange": "askexch",
        "ask_time": "ask_date",
        "bid_exchange": "bidexch",
        "bid_time": "bid_date",
    }

    phi: List[Union[float, None]] = Field(
        default_factory=list,
        description="Phi of the option. The sensitivity of the option relative to dividend yield.",
    )
    bid_iv: List[Union[float, None]] = Field(
        default_factory=list,
        description="Implied volatility of the bid price.",
    )
    ask_iv: List[Union[float, None]] = Field(
        default_factory=list,
        description="Implied volatility of the ask price.",
    )
    orats_final_iv: List[Union[float, None]] = Field(
        default_factory=list,
        description="ORATS final implied volatility of the option, updated once per hour.",
    )
    year_high: List[Union[float, None]] = Field(
        default_factory=list,
        description="52-week high price of the option.",
    )
    year_low: List[Union[float, None]] = Field(
        default_factory=list,
        description="52-week low price of the option.",
    )
    contract_size: List[Union[int, None]] = Field(
        default_factory=list,
        description="Size of the contract.",
    )
    greeks_time: List[Union[datetime, None]] = Field(
        default_factory=list,
        description="Timestamp of the last greeks update."
        + " Greeks/IV data is updated once per hour.",
    )


class TradierOptionsChainsFetcher(
    Fetcher[TradierOptionsChainsQueryParams, TradierOptionsChainsData]
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
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_core.provider.utils.helpers import amake_request  # noqa
        from openbb_tradier.models.equity_quote import TradierEquityQuoteFetcher  # noqa

        api_key = credentials.get("tradier_api_key") if credentials else ""
        sandbox = True

        if api_key and credentials.get("tradier_account_type") not in ["sandbox", "live"]:  # type: ignore
            raise OpenBBError(
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
            raise OpenBBError(f"No expiration dates found for {query.symbol}")

        results: List = []

        underlying_quote = await TradierEquityQuoteFetcher.fetch_data(
            {"symbol": query.symbol}, credentials
        )
        underlying_price = underlying_quote[0].last_price  # type: ignore

        async def get_one(url, underlying_price):
            """Get the chain for a single expiration."""
            chain = await amake_request(url, headers=HEADERS)
            if chain.get("options") and isinstance(chain["options"].get("option", []), list):  # type: ignore
                data = chain["options"]["option"]  # type: ignore
                for d in data.copy():
                    # Remove any strikes returned without data.
                    keys = ["last", "bid", "ask"]
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
                        "description",
                        "average_volume",
                    ]
                    _ = [d.pop(key) for key in to_pop if key in d]
                    # Add the DTE field to the data for easier filtering later.
                    d["dte"] = (
                        datetime.strptime(d["expiration_date"], "%Y-%m-%d").date()
                        - datetime.now().date()
                    ).days
                    if underlying_price is not None:
                        d["underlying_price"] = underlying_price

                results.extend(data)

        urls = [
            f"{BASE_URL}chains?symbol={query.symbol}&expiration={expiration}&greeks=true"
            for expiration in expirations  # type: ignore
        ]

        await asyncio.gather(*[get_one(url, underlying_price) for url in urls])

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
    ) -> TradierOptionsChainsData:
        """Transform and validate the data."""
        # pylint: disable = import-outside-toplevel
        from dateutil.parser import parse
        from numpy import nan
        from openbb_core.provider.utils.helpers import safe_fromtimestamp
        from pandas import DataFrame
        from pytz import timezone

        def df_apply_dates(v):
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

        def map_exchange(v):
            """Map the exchange from a code to a name."""
            return (
                OPTIONS_EXCHANGES.get(v)
                if v in OPTIONS_EXCHANGES
                else (
                    STOCK_EXCHANGES.get(v) if v in STOCK_EXCHANGES else v if v else None
                )
            )

        output = DataFrame(data)
        for col in output:
            if col not in ["dte", "open_interest", "volume"]:
                output[col] = output[col].replace({0: None})
            elif col in ["bid_date", "ask_date", "trade_date", "updated_at"]:
                output[col] = output[col].apply(df_apply_dates)
            elif col == "change_percentage":
                output[col] = [float(d) / 100 if d else None for d in output[col]]
            elif col in ["bidexch", "askexch"]:
                output[col] = output[col].apply(map_exchange)
            else:
                continue

        output = output.replace({nan: None}).dropna(how="all", axis=1)

        return TradierOptionsChainsData.model_validate(output.to_dict(orient="list"))
