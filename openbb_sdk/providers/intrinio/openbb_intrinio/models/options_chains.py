"""Intrinio Options Chains fetcher."""

import concurrent.futures
from datetime import (
    date as dateType,
    datetime,
    timedelta,
)
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests_cache
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.options_chains import (
    OptionsChainsData,
    OptionsChainsQueryParams,
)
from openbb_provider.utils.helpers import make_request
from pydantic import Field, validator

TICKER_EXCEPTIONS = [
    "SPX",
    "XSP",
    "XEO",
    "NDX",
    "XND",
    "VIX",
    "RUT",
    "MRUT",
    "DJX",
    "XAU",
    "OEX",
]

intrinio_session = requests_cache.CachedSession(
    "OpenBB_Intrinio", expire_after=timedelta(days=5), use_cache_dir=True
)


def get_options_tickers(api_key: str) -> List[str]:
    """Returns all tickers that have existing options contracts.

    Parameters
    ----------
    api_key: str
        Intrinio API key.

    Returns
    -------
    List[str]
        List of tickers
    """

    url = f"https://api-v2.intrinio.com/options/tickers?api_key={api_key}"

    r = intrinio_session.get(url, timeout=10)

    return r.json()["tickers"]


def get_options_expirations(
    symbol: str,
    api_key: str,
    after: Optional[Union[datetime, str]] = datetime.now().strftime("%Y-%m-%d"),
    before: Optional[str] = "",
) -> list:
    """Returns a list of all current and upcoming option contract expiration dates for a particular symbol.

    Parameters
    ----------
    symbol: str
        The options symbol, corresponding to the underlying security.
    api_key: str
        Intrinio API key.
    after: str
        Return option contract expiration dates after this date. Format: YYYY-MM-DD
    before: str
        Return option contract expiration dates before this date. Format: YYYY-MM-DD
    """

    url = f"https://api-v2.intrinio.com/options/expirations/{symbol}/eod?before={before}&after={after}&api_key={api_key}"

    r = make_request(url)

    expirations = pd.DatetimeIndex(sorted(list(r.json()["expirations"])))
    return list(filter(lambda x: x > pd.to_datetime(after), expirations))


def generate_url(symbol, expiration, date, api_key):
    return f"https://api-v2.intrinio.com/options/chain/{symbol}/{expiration}/eod?date={date}&api_key={api_key}"


def download_json_files(urls):
    results = []  # List to store the downloaded JSON data

    def download_single_file(url):
        response = make_request(url)
        json_data = response.json()
        results.append(json_data["chain"])

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(download_single_file, urls)

    return results


def get_historical_chain_with_greeks(
    symbol: str, date: Optional[Union[str, dateType]] = "", api_key: str = ""
):
    symbol = symbol.upper()
    SYMBOLS = get_options_tickers(api_key)
    if symbol not in SYMBOLS:
        raise RuntimeError(f"{symbol}", "is not supported by Intrinio.")

    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    # If the symbol is an index, it needs to be preceded with, $.
    if symbol in TICKER_EXCEPTIONS:
        symbol = "$" + symbol

    expirations = get_options_expirations(symbol=symbol, api_key=api_key, after=date)
    urls = []

    for expiration in expirations:
        urls.append(generate_url(symbol, expiration, date, api_key))

    results = download_json_files(urls)

    if len(results) == 0:
        date = pd.to_datetime(date) + timedelta(days=-1)
        for expiration in expirations:
            urls.append(generate_url(symbol, expiration, date, api_key))
        results = download_json_files(urls)

    df = pd.DataFrame()

    for i in range(0, len(results)):
        chains = results[i]

        contract_symbol: List[str] = []
        expiry: List[str] = []
        strikes: List[float] = []
        option_type: List[str] = []
        close: List[float] = []
        close_bid: List[float] = []
        close_ask: List[float] = []
        volume: List[int] = []
        open: List[float] = []
        open_bid: List[float] = []
        open_ask: List[float] = []
        open_interest: List[int] = []
        high: List[float] = []
        low: List[float] = []
        mark: List[float] = []
        ask_high: List[float] = []
        ask_low: List[float] = []
        bid_high: List[float] = []
        bid_low: List[float] = []
        implied_volatility: List[float] = []
        delta: List[float] = []
        gamma: List[float] = []
        theta: List[float] = []
        vega: List[float] = []
        eod_date: List[str] = []

        for item in chains:
            contract_symbol.append(item["option"]["code"])
            expiry.append(item["option"]["expiration"])
            strikes.append(item["option"]["strike"])
            option_type.append(item["option"]["type"])
            close.append(item["prices"]["close"])
            close_bid.append(item["prices"]["close_bid"])
            close_ask.append(item["prices"]["close_ask"])
            volume.append(item["prices"]["volume"])
            open.append(item["prices"]["open"])
            open_bid.append(item["prices"]["open_bid"])
            open_ask.append(item["prices"]["open_ask"])
            open_interest.append(item["prices"]["open_interest"])
            high.append(item["prices"]["high"])
            low.append(item["prices"]["low"])
            mark.append(item["prices"]["mark"])
            ask_high.append(item["prices"]["ask_high"])
            ask_low.append(item["prices"]["ask_low"])
            bid_high.append(item["prices"]["bid_high"])
            bid_low.append(item["prices"]["bid_low"])
            implied_volatility.append(item["prices"]["implied_volatility"])
            delta.append(item["prices"]["delta"])
            gamma.append(item["prices"]["gamma"])
            theta.append(item["prices"]["theta"])
            vega.append(item["prices"]["vega"])
            eod_date.append(item["prices"]["date"])

        data = pd.DataFrame()
        data["contract_symbol"] = contract_symbol
        data["expiration"] = expiry
        data["strike"] = strikes
        data["option_type"] = option_type
        data["close"] = close
        data["close_bid"] = close_bid
        data["close_ask"] = close_ask
        data["volume"] = volume
        data["open"] = open
        data["open_bid"] = open_bid
        data["open_ask"] = open_ask
        data["open_interest"] = open_interest
        data["high"] = high
        data["low"] = low
        data["mark"] = mark
        data["bid_high"] = bid_high
        data["ask_high"] = ask_high
        data["bid_low"] = bid_low
        data["ask_low"] = ask_low
        data["implied_volatility"] = implied_volatility
        data["delta"] = delta
        data["gamma"] = gamma
        data["theta"] = theta
        data["vega"] = vega
        data["eod_date"] = eod_date

        data = data.set_index(["expiration", "strike", "option_type"]).sort_index()

        df = pd.concat([df, data])

    df = df.sort_index().reset_index()
    now = pd.DatetimeIndex(df["eod_date"])
    temp = pd.DatetimeIndex(df["expiration"])
    temp_ = (temp - now).days + 1
    df["dte"] = temp_

    return df


class IntrinioOptionsChainsQueryParams(OptionsChainsQueryParams):
    """Get the complete options chains (Historical) for a ticker from Intrinio.

    source: https://docs.intrinio.com/documentation/web_api/get_options_chain_eod_v2
    """

    date: Optional[Union[str, dateType]] = Field(
        description="Date for which the options chains are returned.",
        default="",
    )


class IntrinioOptionsChainsData(OptionsChainsData):
    """Intrinio Options Chains Data."""

    class Config:
        fields = {
            "bid": "close_bid",
            "ask": "close_ask",
        }

    mark: Optional[float] = Field(
        description="The mid-price between the latest bid-ask spread."
    )
    open_bid: Optional[float] = Field(
        description="The lowest bid price for the option that day."
    )
    open_ask: Optional[float] = Field(
        description="The lowest ask price for the option that day."
    )
    bid_low: Optional[float] = Field(
        description="The lowest bid price for the option that day."
    )
    ask_low: Optional[float] = Field(
        description="The lowest ask price for the option that day."
    )
    bid_high: Optional[float] = Field(
        description="The highest bid price for the option that day."
    )
    ask_high: Optional[float] = Field(
        description="The highest ask price for the option that day."
    )
    open: Optional[float] = Field(description="The open price for the option that day.")
    high: Optional[float] = Field(description="The high price for the option that day.")
    low: Optional[float] = Field(description="The low price for the option that day.")
    close: Optional[float] = Field(
        description="The close price for the option that day."
    )
    implied_volatility: Optional[float] = Field(
        description="The implied volatility for the option at the end of day."
    )
    delta: Optional[float] = Field(description="The delta value at the end of day.")
    gamma: Optional[float] = Field(description="The gamma value at the end of day.")
    vega: Optional[float] = Field(description="The vega value at the end of day.")
    theta: Optional[float] = Field(description="The theta value at the end of day.")
    eod_date: Optional[dateType] = Field(
        description="Historical date for which the options chains data is from.",
    )
    dte: Optional[int] = Field(description="The number of days until expiry.")

    @validator("expiration", pre=True, check_fields=False)
    def date_validate(cls, v):  # pylint: disable=E0213
        """Return the datetime object from the date string"""
        return datetime.strptime(v, "%Y-%m-%d")


class IntrinioOptionsChainsFetcher(
    Fetcher[IntrinioOptionsChainsQueryParams, List[IntrinioOptionsChainsData]]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints"""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioOptionsChainsQueryParams:
        """Transform the query"""
        return IntrinioOptionsChainsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: IntrinioOptionsChainsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""

        api_key = credentials.get("intrinio_api_key") if credentials else ""
        data = get_historical_chain_with_greeks(
            symbol=query.symbol, date=query.date, api_key=api_key  # type: ignore
        )

        return data.to_dict("records")

    @staticmethod
    def transform_data(data: List[Dict]) -> List[IntrinioOptionsChainsData]:
        """Return the transformed data."""
        return [IntrinioOptionsChainsData(**d) for d in data]
