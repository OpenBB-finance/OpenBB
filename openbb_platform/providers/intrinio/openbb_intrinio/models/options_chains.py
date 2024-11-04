"""Intrinio Options Chains Model."""

# pylint: disable=unused-argument
from datetime import (
    date as dateType,
    datetime,
)
from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.options_chains import (
    OptionsChainsData,
    OptionsChainsQueryParams,
)
from openbb_core.provider.utils.errors import OpenBBError
from openbb_intrinio.models.equity_historical import IntrinioEquityHistoricalFetcher
from openbb_intrinio.models.index_historical import IntrinioIndexHistoricalFetcher
from pydantic import Field, field_validator, model_validator


class IntrinioOptionsChainsQueryParams(OptionsChainsQueryParams):
    """Intrinio Options Chains Query.

    source: https://docs.intrinio.com/documentation/web_api/get_options_chain_eod_v2
    """

    __alias_dict__ = {
        "strike_gt": "strike_greater_than",
        "strike_lt": "strike_less_than",
        "volume_gt": "volume_greater_than",
        "volume_lt": "volume_less_than",
        "oi_gt": "open_interest_greater_than",
        "oi_lt": "open_interest_less_than",
        "option_type": "type",
    }
    __json_schema_extra__ = {
        "moneyness": {
            "multiple_items_allowed": False,
            "choices": ["otm", "itm", "all"],
        },
        "delay": {
            "multiple_items_allowed": False,
            "choices": ["eod", "realtime", "delayed"],
        },
        "option_type": {
            "multiple_items_allowed": False,
            "choices": ["call", "put"],
        },
        "model": {
            "multiple_items_allowed": False,
            "choices": ["black_scholes", "bjerk"],
        },
    }

    delay: Literal["eod", "realtime", "delayed"] = Field(
        description="Whether to return delayed, realtime, or eod data.",
        default="eod",
    )
    date: Optional[dateType] = Field(
        default=None, description="The end-of-day date for options chains data."
    )
    option_type: Optional[Literal["call", "put"]] = Field(
        default=None,
        description="The option type, call or put, 'None' is both (default).",
    )
    moneyness: Literal["otm", "itm", "all"] = Field(
        default="all",
        description="Return only contracts that are in or out of the money, default is 'all'."
        + " Parameter is ignored when a date is supplied.",
    )
    strike_gt: Optional[int] = Field(
        default=None,
        description="Return options with a strike price greater than the given value."
        + " Parameter is ignored when a date is supplied.",
    )
    strike_lt: Optional[int] = Field(
        default=None,
        description="Return options with a strike price less than the given value."
        + " Parameter is ignored when a date is supplied.",
    )
    volume_gt: Optional[int] = Field(
        default=None,
        description="Return options with a volume greater than the given value."
        + " Parameter is ignored when a date is supplied.",
    )
    volume_lt: Optional[int] = Field(
        default=None,
        description="Return options with a volume less than the given value."
        + " Parameter is ignored when a date is supplied.",
    )
    oi_gt: Optional[int] = Field(
        default=None,
        description="Return options with an open interest greater than the given value."
        + " Parameter is ignored when a date is supplied.",
    )
    oi_lt: Optional[int] = Field(
        default=None,
        description="Return options with an open interest less than the given value."
        + " Parameter is ignored when a date is supplied.",
    )
    model: Literal["black_scholes", "bjerk"] = Field(
        default="black_scholes",
        description="The pricing model to use for options chains data, default is 'black_scholes'."
        + " Parameter is ignored when a date is supplied.",
    )
    show_extended_price: bool = Field(
        default=True,
        description="Whether to include OHLC type fields, default is True."
        + " Parameter is ignored when a date is supplied.",
    )
    include_related_symbols: bool = Field(
        default=False,
        description="Include related symbols that end in a 1 or 2 because of a corporate action,"
        + " default is False.",
    )

    @model_validator(mode="after")
    @classmethod
    def date_not_allowed_with_realtime(cls, values: Any) -> Any:
        """Return an error if the date is supplied when delay is realtime."""
        if values.delay != "eod" and values.date:
            warn("Date is ignored when accessing realtime or delayed data.")
        return values


class IntrinioOptionsChainsData(OptionsChainsData):
    """Intrinio Options Chains Data."""

    __doc__ = OptionsChainsData.__doc__
    __alias_dict__ = {
        "contract_symbol": "code",
        "symbol": "ticker",
        "eod_date": "date",
        "option_type": "type",
        "last_trade_time": "last_timestamp",
        "last_trade_price": "last",
        "last_trade_size": "last_size",
        "ask_time": "ask_timestamp",
        "bid_time": "bid_timestamp",
        "open": "trade_open",
        "high": "trade_high",
        "low": "trade_low",
        "close": "trade_close",
    }

    @field_validator(
        "close_time",
        "close_ask_time",
        "close_bid_time",
        "ask_time",
        "bid_time",
        "last_trade_time",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def _date_validate(cls, v):
        """Return the datetime object from the date string."""
        # pylint: disable=import-outside-toplevel
        from dateutil import parser
        from pytz import timezone

        if not v:
            return None
        new_v: list = []
        for item in v:
            if item:
                dt = parser.parse(item)
                dt = dt.replace(tzinfo=timezone("UTC"))
                dt = dt.astimezone(timezone("America/New_York"))
                new_v.append(dt.replace(microsecond=0))
            else:
                new_v.append(None)

        return new_v

    @field_validator("volume", "open_interest", mode="before", check_fields=False)
    @classmethod
    def _volume_oi_validate(cls, v):
        """Return the volume as an integer."""
        return [0 if item is None else item for item in v]


class IntrinioOptionsChainsFetcher(
    Fetcher[IntrinioOptionsChainsQueryParams, IntrinioOptionsChainsData]
):
    """Intrinio Options Chains Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioOptionsChainsQueryParams:
        """Transform the query."""
        return IntrinioOptionsChainsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioOptionsChainsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the Intrinio endpoint."""
        # pylint: disable=import-outside-toplevel
        from datetime import timedelta  # noqa
        from openbb_core.provider.utils.helpers import (
            amake_requests,
            get_querystring,
        )
        from openbb_intrinio.utils.helpers import (
            get_data_many,
            get_weekday,
            response_callback,
        )

        api_key = credentials.get("intrinio_api_key") if credentials else ""

        base_url = "https://api-v2.intrinio.com/options"

        date = query.date if query.date is not None else datetime.now().date()
        date = get_weekday(date)

        if query.symbol in ["SPX", "^SPX", "^GSPC"]:
            query.symbol = "SPX"
            warn("For weekly SPX options, use the symbol SPXW instead of SPX.")

        async def get_urls(date: str) -> List[str]:
            """Return the urls for the given date."""
            date = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=1)).strftime(
                "%Y-%m-%d"
            )
            url = (
                f"{base_url}/expirations/{query.symbol}/"
                f"{'eod' if query.delay == 'eod' else 'realtime'}?"
                f"{'after=' + date + '&' if query.delay == 'eod' else 'source=' + query.delay + '&'}"
                f"api_key={api_key}"
            )
            expirations = await get_data_many(url, "expirations", **kwargs)

            def generate_url(expiration) -> str:
                url = f"{base_url}/chain/{query.symbol}/{expiration}/"
                if query.date is not None:
                    query_string = get_querystring(
                        query.model_dump(exclude_none=True),
                        [
                            "symbol",
                            "date",
                            "model",
                            "volume_greater_than",
                            "volume_less_than",
                            "moneyness",
                            "open_interest_greater_than",
                            "open_interest_less_than",
                            "show_extended_price",
                        ],
                    )
                    url = url + f"eod?date={query.date}&{query_string}"
                else:
                    if query.moneyness:
                        moneyness = (
                            "out_of_the_money"
                            if query.moneyness == "otm"
                            else "in_the_money" if query.moneyness == "itm" else "all"
                        )

                    query_string = get_querystring(
                        query.model_dump(exclude_none=True),
                        ["symbol", "date", "moneyness"],
                    )
                    url = url + f"realtime?{query_string}&moneyness={moneyness}"

                return url + f"&api_key={api_key}"

            return [generate_url(expiration) for expiration in expirations]

        async def callback(response, _) -> list:
            """Return the response."""
            response_data = await response_callback(response, _)
            return response_data.get("chain", [])  # type: ignore

        results = await amake_requests(
            await get_urls(date.strftime("%Y-%m-%d")), callback, **kwargs
        )
        # If the EOD chains are not available for the given date, try the previous day
        if not results and query.date is not None:
            date = get_weekday(date - timedelta(days=1)).strftime("%Y-%m-%d")
            urls = await get_urls(date)  # type: ignore
            results = await amake_requests(urls, response_callback=callback, **kwargs)

        if not results:
            raise OpenBBError(f"No data found for the given symbol: {query.symbol}")

        output: Dict = {}
        underlying_price: Dict = {}
        # If the EOD chains are requested, get the underlying price on the given date.
        if query.date is not None:
            if query.symbol.endswith("W") and query.symbol.startswith("SPX"):
                query.symbol = query.symbol[:-1]
            temp = None
            try:
                temp = await IntrinioEquityHistoricalFetcher.fetch_data(
                    {"symbol": query.symbol, "start_date": date, "end_date": date},
                    credentials,
                )
                temp = temp[0]  # type: ignore
            # If the symbol is SPX, or similar, try to get the underlying price from the index.
            except Exception as e:
                try:
                    temp = await IntrinioIndexHistoricalFetcher.fetch_data(
                        {"symbol": query.symbol, "start_date": date, "end_date": date},
                        credentials,
                    )
                    temp = temp[0]  # type: ignore
                except Exception:
                    warn(f"Failed to get underlying price for {query.symbol}: {e}")
            if temp:
                underlying_price["symbol"] = query.symbol
                underlying_price["price"] = temp.close
                underlying_price["date"] = temp.date.strftime("%Y-%m-%d")

        output = {"underlying": underlying_price, "data": results}

        return output

    @staticmethod
    def transform_data(
        query: IntrinioOptionsChainsQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> IntrinioOptionsChainsData:
        """Return the transformed data."""
        # pylint: disable=import-outside-toplevel
        from numpy import nan
        from pandas import DataFrame

        results: List = []
        chains = data.get("data", [])
        underlying = data.get("underlying", {})
        last_price = underlying.get("price")
        if query.date is not None:
            for item in chains:
                new_item = {**item["option"], **item["prices"]}
                new_item["dte"] = (
                    datetime.strptime(new_item["expiration"], "%Y-%m-%d").date()
                    - datetime.strptime(new_item["date"], "%Y-%m-%d").date()
                ).days
                if last_price:
                    new_item["underlying_price"] = last_price
                _ = new_item.pop("exercise_style", None)
                new_item["underlying_symbol"] = new_item.pop("ticker")
                results.append(new_item)
        else:
            for item in chains:
                new_item = {
                    **item["option"],
                    **item["price"],
                    **item["stats"],
                    **item["extended_price"],
                }
                dte = (
                    datetime.strptime(new_item["expiration"], "%Y-%m-%d").date()
                    - datetime.now().date()
                ).days
                new_item["dte"] = dte
                new_item["underlying_symbol"] = new_item.pop(
                    "underlying_price_ticker", None
                )
                underlying["date"] = datetime.now().date()
                new_item["underlying_price"] = new_item.pop("underlying_price", None)
                _ = new_item.pop("ticker", None)
                _ = new_item.pop("trade_exchange", None)
                _ = new_item.pop("exercise_style", None)
                results.append(new_item)

        output = DataFrame(results).replace({nan: None}).dropna(how="all", axis=1)
        output = output.sort_values(by=["expiration", "strike", "type"])

        return IntrinioOptionsChainsData.model_validate(output.to_dict(orient="list"))
