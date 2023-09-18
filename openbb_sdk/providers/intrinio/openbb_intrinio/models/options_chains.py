"""Intrinio Options Chains fetcher."""

from concurrent.futures import ThreadPoolExecutor
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
    after: Optional[datetime] = None,
    before: Optional[datetime] = None,
) -> list:
    """Returns a list of all current and upcoming option contract expiration dates for a particular symbol.

    Parameters
    ----------
    symbol: str
        The options symbol, corresponding to the underlying security.
    api_key: str
        Intrinio API key.
    after: datetime
        Return option contract expiration dates after this date.
    before: datetime
        Return option contract expiration dates before this date.
    """
    after = after.strftime("%Y-%m-%d") if after else ""
    before = before.strftime("%Y-%m-%d") if before else ""

    url = f"https://api-v2.intrinio.com/options/expirations/{symbol}/eod?before={before}&after={after}&api_key={api_key}"
    r = make_request(url)

    expirations = pd.DatetimeIndex(sorted(list(r.json()["expirations"])))
    return list(filter(lambda x: x > pd.to_datetime(after), expirations))


def generate_url(
    symbol: str, expiration: dateType, date: dateType, api_key: str
) -> str:
    date = date.strftime("%Y-%m-%d")
    expiration = expiration.strftime("%Y-%m-%d")
    return f"https://api-v2.intrinio.com/options/chain/{symbol}/{expiration}/eod?date={date}&api_key={api_key}"


def download_json_files(urls):
    results = []  # List to store the downloaded JSON data

    def download_single_file(url):
        results.append(make_request(url).json().get("chain", []))

    with ThreadPoolExecutor() as executor:
        executor.map(download_single_file, urls)

    return results


def get_weekday(date: dateType):
    if date.weekday() in [5, 6]:
        date = date - timedelta(days=2 if date.weekday() == 6 else 1)
    return date


def get_historical_chain_with_greeks(
    symbol: str, date: Optional[Union[str, dateType]] = "", api_key: str = ""
) -> pd.DataFrame:
    SYMBOLS = get_options_tickers(api_key)
    if symbol not in SYMBOLS:
        raise RuntimeError(f"{symbol}", "is not supported by Intrinio.")

    date = date if date else datetime.now()

    if date.weekday() in [5, 6]:
        date = get_weekday(date)

    # If the symbol is an index, it needs to be preceded with, $.
    if symbol in TICKER_EXCEPTIONS:
        symbol = "$" + symbol

    expirations = get_options_expirations(symbol=symbol, api_key=api_key, after=date)
    urls = [
        generate_url(symbol, expiration, date, api_key) for expiration in expirations
    ]

    if len(results := download_json_files(urls)) == 0:
        date = get_weekday(date - timedelta(days=1))
        results = download_json_files(
            [
                generate_url(symbol, expiration, date, api_key)
                for expiration in expirations
            ]
        )

    data = [
        {
            "contract_symbol": item["option"]["code"],
            "expiration": item["option"]["expiration"],
            "strike": item["option"]["strike"] or 0,
            "option_type": item["option"]["type"],
            "close": item["prices"]["close"] or 0,
            "close_bid": item["prices"]["close_bid"] or 0,
            "close_ask": item["prices"]["close_ask"] or 0,
            "volume": item["prices"]["volume"] or 0,
            "open": item["prices"]["open"] or 0,
            "open_bid": item["prices"]["open_bid"] or 0,
            "open_ask": item["prices"]["open_ask"] or 0,
            "open_interest": item["prices"]["open_interest"] or 0,
            "high": item["prices"]["high"] or 0,
            "low": item["prices"]["low"] or 0,
            "mark": item["prices"]["mark"],
            "bid_high": item["prices"]["bid_high"] or 0,
            "ask_high": item["prices"]["ask_high"] or 0,
            "bid_low": item["prices"]["bid_low"] or 0,
            "ask_low": item["prices"]["ask_low"] or 0,
            "implied_volatility": item["prices"]["implied_volatility"] or 0,
            "delta": item["prices"]["delta"] or 0,
            "gamma": item["prices"]["gamma"] or 0,
            "theta": item["prices"]["theta"] or 0,
            "vega": item["prices"]["vega"] or 0,
            "eod_date": item["prices"]["date"],
        }
        for chains in results
        for item in chains
    ]

    df = (
        pd.DataFrame(data)
        .set_index(["expiration", "strike", "option_type"])
        .sort_index()
        .reset_index()
    )
    now = pd.DatetimeIndex(df["eod_date"])
    temp = pd.DatetimeIndex(df["expiration"])
    temp_ = (temp - now).days + 1
    df["dte"] = temp_

    return df


class IntrinioOptionsChainsQueryParams(OptionsChainsQueryParams):
    """Get the complete options chains (Historical) for a ticker from Intrinio.

    source: https://docs.intrinio.com/documentation/web_api/get_options_chain_eod_v2
    """

    date: Optional[dateType] = Field(
        default=None,
        description="Date for which the options chains are returned.",
    )


class IntrinioOptionsChainsData(OptionsChainsData):
    """Intrinio Options Chains Data."""

    __alias_dict__ = {"bid": "close_bid", "ask": "close_ask"}

    mark: Optional[float] = Field(
        default=None, description="The mid-price between the latest bid-ask spread."
    )
    open_bid: Optional[float] = Field(
        default=None, description="The lowest bid price for the option that day."
    )
    open_ask: Optional[float] = Field(
        default=None, description="The lowest ask price for the option that day."
    )
    bid_low: Optional[float] = Field(
        default=None, description="The lowest bid price for the option that day."
    )
    ask_low: Optional[float] = Field(
        default=None, description="The lowest ask price for the option that day."
    )
    bid_high: Optional[float] = Field(
        default=None, description="The highest bid price for the option that day."
    )
    ask_high: Optional[float] = Field(
        default=None, description="The highest ask price for the option that day."
    )
    open: Optional[float] = Field(
        default=None, description="Opening price of the option."
    )
    high: Optional[float] = Field(default=None, description="High price of the option.")
    low: Optional[float] = Field(default=None, description="Low price of the option.")
    close: Optional[float] = Field(
        default=None, description="Close price for the option that day."
    )
    implied_volatility: Optional[float] = Field(
        default=None, description="Implied volatility of the option."
    )
    delta: Optional[float] = Field(default=None, description="Delta of the option.")
    gamma: Optional[float] = Field(default=None, description="Gamma of the option.")
    vega: Optional[float] = Field(default=None, description="Vega of the option.")
    theta: Optional[float] = Field(default=None, description="Theta of the option.")
    eod_date: Optional[dateType] = Field(
        default=None,
        description="Historical date for which the options chains data is from.",
    )
    dte: Optional[int] = Field(
        default=None, description="Days to expiration for the option."
    )

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

        return data.to_dict(orient="records")

    @staticmethod
    def transform_data(data: List[Dict]) -> List[IntrinioOptionsChainsData]:
        """Return the transformed data."""
        return [IntrinioOptionsChainsData(**d) for d in data]
