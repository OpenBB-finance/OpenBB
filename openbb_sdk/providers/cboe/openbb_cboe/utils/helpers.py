"""CBOE Helpers Module"""

import os
from datetime import date, datetime, timedelta
from io import StringIO
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import pandas as pd
import requests
import requests_cache

TICKER_EXCEPTIONS = ["NDX", "RUT"]
# This will cache the import requests for 7 days.  Ideally to speed up subsequent imports.
# Only used on functions run on import
cboe_session = requests_cache.CachedSession(
    "OpenBB_CBOE", expire_after=timedelta(days=7), use_cache_dir=True
)


def get_user_agent() -> str:
    """Get a not very random user agent."""
    user_agent_strings = [
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:86.1) Gecko/20100101 Firefox/86.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:86.1) Gecko/20100101 Firefox/86.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:82.1) Gecko/20100101 Firefox/82.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:83.0) Gecko/20100101 Firefox/83.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:84.0) Gecko/20100101 Firefox/84.0",
    ]

    return np.random.choice(user_agent_strings)  # nosec


def request(
    url: str, method: str = "GET", timeout: int = 10, **kwargs
) -> requests.Response:
    """Abstract helper to make requests from a url with potential headers and params.

    Parameters
    ----------
    url : str
        Url to make the request to
    method : str, optional
        HTTP method to use.  Can be "GET" or "POST", by default "GET"
    timeout : int, optional
        Timeout in seconds, by default 10

    Returns
    -------
    requests.Response
        Request response object

    Raises
    ------
    ValueError
        If invalid method is passed
    """

    # If there are headers, check if there is a user agent, if not add one.
    # Some requests seem to work only with a specific user agent, so we want to be able to override it.
    headers = kwargs.pop("headers", {})

    if "User-Agent" not in headers:
        headers["User-Agent"] = get_user_agent()

    if (func := getattr(requests, method.lower(), None)) is not None:
        return func(
            url,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    raise ValueError("Method must be valid HTTP method")


def camel_to_snake(string: str) -> str:
    """Convert camelCase to snake_case."""
    return "".join(["_" + i.lower() if i.isupper() else i for i in string]).lstrip("_")


def get_cboe_directory() -> pd.DataFrame:
    """Get the US Listings Directory for the CBOE.

    Returns
    -------
    pd.DataFrame: CBOE_DIRECTORY
        DataFrame of the CBOE listings directory
    """
    try:
        CBOE_DIRECTORY: pd.DataFrame = pd.read_csv(
            StringIO(
                cboe_session.get(
                    "https://www.cboe.com/us/options/symboldir/equity_index_options/?download=csv",
                    timeout=10,
                ).text
            )
        )
        CBOE_DIRECTORY = CBOE_DIRECTORY.rename(
            columns={
                " Stock Symbol": "Symbol",
                " DPM Name": "DPM Name",
                " Post/Station": "Post/Station",
            }
        ).set_index("Symbol")
        return CBOE_DIRECTORY
    except requests.HTTPError:
        return pd.DataFrame()


def get_cboe_index_directory() -> pd.DataFrame:
    """Get the US Listings Directory for the CBOE

    Returns
    -------
    pd.DataFrame: CBOE_INDEXES
    """
    try:
        r = cboe_session.get(
            "https://cdn.cboe.com/api/global/us_indices/definitions/all_indices.json",
            timeout=10,
        )

        if r.status_code != 200:
            raise requests.HTTPError

        CBOE_INDEXES = pd.DataFrame(r.json())

        CBOE_INDEXES = CBOE_INDEXES.rename(
            columns={
                "calc_end_time": "Close Time",
                "calc_start_time": "Open Time",
                "currency": "Currency",
                "description": "Description",
                "display": "Display",
                "featured": "Featured",
                "featured_order": "Featured Order",
                "index_symbol": "Ticker",
                "mkt_data_delay": "Data Delay",
                "name": "Name",
                "tick_days": "Tick Days",
                "tick_frequency": "Frequency",
                "tick_period": "Period",
                "time_zone": "Time Zone",
            },
        )

        indices_order: List[str] = [
            "Ticker",
            "Name",
            "Description",
            "Currency",
            "Tick Days",
            "Frequency",
            "Period",
            "Time Zone",
        ]

        CBOE_INDEXES = pd.DataFrame(CBOE_INDEXES, columns=indices_order).set_index(
            "Ticker"
        )

        return CBOE_INDEXES

    except requests.HTTPError:
        return pd.DataFrame()


INDEXES = get_cboe_index_directory().index.tolist()
SYMBOLS = pd.DataFrame()
try:
    SYMBOLS = get_cboe_directory()
except SYMBOLS.empty:
    current_dir = os.path.dirname(os.path.realpath(__file__))
    file = "cboe_companies.json"
    SYMBOLS = pd.read_json(Path(current_dir, file))


def stock_search(query: str, ticker: bool = False) -> dict:
    """Search the CBOE company directory by name or ticker.
    Parameters
    -----------
    query: str
        The search query
    ticker: bool
        Whether to search by ticker. Default is False.

    Returns
    -------
    dict
        Dictionary of the results.
    """
    data = {}
    symbols = SYMBOLS.copy() if not SYMBOLS.empty else get_cboe_directory()
    symbols = symbols.reset_index()
    target = "Company Name" if not ticker else "Symbol"
    idx = symbols[target].str.contains(query, case=False)
    result = symbols[idx].to_dict("records")
    if len(result) > 0:
        data.update({"results": result})
        return data
    print(f"No results found for: {query}.  Try another search query.")
    return pd.DataFrame()


def get_ticker_info(symbol: str) -> Tuple[pd.DataFrame, List[str]]:
    """Get basic info for the symbol and expiration dates

    Parameters
    ----------
    symbol: str
        The ticker to lookup

    Returns
    -------
    Tuple: [pd.DataFrame, pd.Series]
        ticker_details
        ticker_expirations
    """

    stock = "stock"
    index = "index"
    symbol = symbol.upper()
    new_ticker: str = ""
    ticker_details = pd.DataFrame()
    ticker_expirations: list = []
    try:
        if symbol in TICKER_EXCEPTIONS:
            new_ticker = "^" + symbol
        else:
            if symbol not in INDEXES:
                new_ticker = symbol

            elif symbol in INDEXES:
                new_ticker = "^" + symbol

                # Get the data to return, and if none returns empty Tuple #

        symbol_info_url = (
            "https://www.cboe.com/education/tools/trade-optimizer/symbol-info/?symbol="
            f"{new_ticker}"
        )

        symbol_info = request(symbol_info_url)
        symbol_info_json = pd.Series(symbol_info.json())

        if symbol_info_json.success is False:
            ticker_details = pd.DataFrame()
            ticker_expirations = []
            print("No data found for the symbol: " f"{symbol}" "")
        else:
            symbol_details = pd.Series(symbol_info_json["details"])
            symbol_details = pd.DataFrame(symbol_details).transpose()
            symbol_details = symbol_details.reset_index()
            ticker_expirations = symbol_info_json["expirations"]

            # Cleans columns depending on if the security type is a stock or an index

            type_ = symbol_details.security_type

            if stock[0] in type_[0]:
                stock_details = symbol_details
                ticker_details = pd.DataFrame(stock_details).rename(
                    columns={
                        "current_price": "price",
                        "bid_size": "bidSize",
                        "ask_size": "askSize",
                        "iv30": "ivThirty",
                        "prev_day_close": "previousClose",
                        "price_change": "change",
                        "price_change_percent": "changePercent",
                        "iv30_change": "ivThirtyChange",
                        "iv30_percent_change": "ivThirtyChangePercent",
                        "last_trade_time": "lastTradeTimestamp",
                        "exchange_id": "exchangeID",
                        "tick": "tick",
                        "security_type": "type",
                    }
                )
                details_columns = [
                    "symbol",
                    "type",
                    "tick",
                    "bid",
                    "bidSize",
                    "askSize",
                    "ask",
                    "price",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "previousClose",
                    "change",
                    "changePercent",
                    "ivThirty",
                    "ivThirtyChange",
                    "ivThirtyChangePercent",
                    "lastTradeTimestamp",
                ]
                ticker_details = (
                    pd.DataFrame(ticker_details, columns=details_columns)
                    .set_index(keys="symbol")
                    .dropna(axis=1)
                    .transpose()
                )

            if index[0] in type_[0]:
                index_details = symbol_details
                ticker_details = pd.DataFrame(index_details).rename(
                    columns={
                        "symbol": "symbol",
                        "security_type": "type",
                        "current_price": "price",
                        "price_change": "change",
                        "price_change_percent": "changePercent",
                        "prev_day_close": "previousClose",
                        "iv30": "ivThirty",
                        "iv30_change": "ivThirtyChange",
                        "iv30_change_percent": "ivThirtyChangePercent",
                        "last_trade_time": "lastTradeTimestamp",
                    }
                )

                index_columns = [
                    "symbol",
                    "type",
                    "tick",
                    "price",
                    "open",
                    "high",
                    "low",
                    "close",
                    "previousClose",
                    "change",
                    "changePercent",
                    "ivThirty",
                    "ivThirtyChange",
                    "ivThirtyChangePercent",
                    "lastTradeTimestamp",
                ]

                ticker_details = (
                    pd.DataFrame(ticker_details, columns=index_columns)
                    .set_index(keys="symbol")
                    .dropna(axis=1)
                    .transpose()
                ).rename(columns={f"{new_ticker}": f"{symbol}"})

    except requests.HTTPError:
        print("There was an error with the request'\n")
        ticker_details = pd.DataFrame()
        ticker_expirations = list()
        return ticker_details, ticker_expirations

    return ticker_details, ticker_expirations


def get_ticker_iv(symbol: str) -> pd.DataFrame:
    """Get annualized high/low historical and implied volatility over 30/60/90 day windows.

    Parameters
    ----------
    symbol: str
        The loaded ticker

    Returns
    -------
    pd.DataFrame: ticker_iv
    """

    # Checks ticker to determine if ticker is an index or an exception that requires modifying the request's URLs

    try:
        if symbol in TICKER_EXCEPTIONS:
            quotes_iv_url = (
                "https://cdn.cboe.com/api/global/delayed_quotes/historical_data/_"
                f"{symbol}"
                ".json"
            )
        else:
            if symbol not in INDEXES:
                quotes_iv_url = (
                    "https://cdn.cboe.com/api/global/delayed_quotes/historical_data/"
                    f"{symbol}"
                    ".json"
                )

            elif symbol in INDEXES:
                quotes_iv_url = (
                    "https://cdn.cboe.com/api/global/delayed_quotes/historical_data/_"
                    f"{symbol}"
                    ".json"
                )
        h_iv = request(quotes_iv_url)

        if h_iv.status_code != 200:
            print("No data found for the symbol: " f"{symbol}" "")
            return pd.DataFrame()

        data = h_iv.json()
        h_data = pd.DataFrame(data)[2:-1]["data"].rename(f"{symbol}")
        h_data.rename(
            {
                "hv30_annual_high": "hvThirtyOneYearHigh",
                "hv30_annual_low": "hvThirtyOneYearLow",
                "hv60_annual_high": "hvSixtyOneYearHigh",
                "hv60_annual_low": "hvSixtyOneYearLow",
                "hv90_annual_high": "hvNinetyOneYearHigh",
                "hv90_annual_low": "hvNinetyOneYearLow",
                "iv30_annual_high": "ivThirtyOneYearHigh",
                "iv30_annual_low": "ivThirtyOneYearLow",
                "iv60_annual_high": "ivSixtyOneYearHigh",
                "iv60_annual_low": "ivSixtyOneYearLow",
                "iv90_annual_high": "ivNinetyOneYearHigh",
                "iv90_annual_low": "ivNinetyOneYearLow",
            },
            inplace=True,
        )

        iv_order = [
            "ivThirtyOneYearHigh",
            "hvThirtyOneYearHigh",
            "ivThirtyOneYearLow",
            "hvThirtyOneYearLow",
            "ivSixtyOneYearHigh",
            "hvSixtyOneYearHigh",
            "ivSixtyOneYearLow",
            "hvSixtyOneYearLow",
            "ivNinetyOneYearHigh",
            "hvNinetyOneYearHigh",
            "ivNinetyOneYearLow",
            "hvNinetyOneYearLow",
        ]

        ticker_iv = pd.DataFrame(h_data).transpose()
    except requests.HTTPError:
        print("There was an error with the request'\n")

    return pd.DataFrame(ticker_iv, columns=iv_order).transpose()


def get_chains(symbol: str) -> pd.DataFrame:
    """Get the complete options chains for a ticker.

    Parameters
    ----------
    symbol: str
        The ticker get options data for

    Returns
    -------
    pd.DataFrame
        DataFrame with all active options contracts for the underlying symbol.
    """

    # Checks ticker to determine if ticker is an index or an exception that requires modifying the request's URLs.
    symbol = symbol.upper()
    try:
        if symbol in TICKER_EXCEPTIONS:
            quotes_url = (
                "https://cdn.cboe.com/api/global/delayed_quotes/options/_"
                f"{symbol}"
                ".json"
            )
        else:
            if symbol not in INDEXES:
                quotes_url = (
                    "https://cdn.cboe.com/api/global/delayed_quotes/options/"
                    f"{symbol}"
                    ".json"
                )
            if symbol in INDEXES:
                quotes_url = (
                    "https://cdn.cboe.com/api/global/delayed_quotes/options/_"
                    f"{symbol}"
                    ".json"
                )

        result = request(quotes_url)
        if result.status_code != 200:
            print("No data found for the symbol: " f"{symbol}" "")
            return pd.DataFrame()

        r_json = result.json()
        data = pd.DataFrame(r_json["data"])
        options = pd.Series(data.options, index=data.index)
        options_columns = list(options[0])
        options_data = list(options[:])
        options_df = pd.DataFrame(options_data, columns=options_columns)

        options_df = options_df.rename(
            columns={
                "option": "contractSymbol",
                "bid_size": "bidSize",
                "ask_size": "askSize",
                "iv": "impliedVolatility",
                "open_interest": "openInterest",
                "theo": "theoretical",
                "last_trade_price": "lastTradePrice",
                "last_trade_time": "lastTradeTimestamp",
                "percent_change": "changePercent",
                "prev_day_close": "previousClose",
            }
        )

        # Parses the option symbols into columns for expiration, strike, and optionType

        option_df_index = options_df["contractSymbol"].str.extractall(
            r"^(?P<Ticker>\D*)(?P<expiration>\d*)(?P<optionType>\D*)(?P<strike>\d*)"
        )
        option_df_index = option_df_index.reset_index().drop(
            columns=["match", "level_0"]
        )
        option_df_index.optionType = option_df_index.optionType.str.replace(
            "C", "call"
        ).str.replace("P", "put")
        option_df_index.strike = [ele.lstrip("0") for ele in option_df_index.strike]
        option_df_index.strike = pd.Series(option_df_index.strike).astype(float)
        option_df_index.strike = option_df_index.strike * (1 / 1000)
        option_df_index.strike = option_df_index.strike.to_list()
        option_df_index.expiration = [
            ele.lstrip("1") for ele in option_df_index.expiration
        ]
        option_df_index.expiration = pd.DatetimeIndex(
            option_df_index.expiration, yearfirst=True
        ).astype(str)
        option_df_index = option_df_index.drop(columns=["Ticker"])

        # Joins the parsed symbol into the dataframe.

        quotes = option_df_index.join(options_df)

        now = datetime.now()
        temp = pd.DatetimeIndex(quotes.expiration)
        temp_ = (temp - now).days + 1
        quotes["dte"] = temp_

        quotes["lastTradeTimestamp"] = pd.to_datetime(quotes["lastTradeTimestamp"])
        quotes = quotes.set_index(
            keys=["expiration", "strike", "optionType"]
        ).sort_index()
        quotes["openInterest"] = quotes["openInterest"].astype("int64")
        quotes["volume"] = quotes["volume"].astype("int64")
        quotes["bidSize"] = quotes["bidSize"].astype("int64")
        quotes["askSize"] = quotes["askSize"].astype("int64")
        quotes["previousClose"] = round(quotes["previousClose"], 2)
        quotes["changePercent"] = round(quotes["changePercent"], 2)

    except requests.HTTPError:
        print("There was an error with the request'\n")
        return pd.DataFrame()

    return quotes.reset_index()


def __generate_historical_prices_url(
    symbol, data_type: Optional[str] = "historical"
) -> str:
    """Generate the final URL for historical prices data."""

    url: str = ""

    if data_type not in ["historical", "intraday"]:
        print(
            "Invalid data_type. Must be either 'historical' or 'intraday'. Defaulting to 'historical'."
        )
        data_type = "historical"

    if symbol in TICKER_EXCEPTIONS:
        url = (
            f"https://cdn.cboe.com/api/global/delayed_quotes/charts/{data_type}/_"
            f"{symbol}"
            ".json"
        )
    else:
        if symbol not in INDEXES:
            url = (
                f"https://cdn.cboe.com/api/global/delayed_quotes/charts/{data_type}/"
                f"{symbol}"
                ".json"
            )

        elif symbol in INDEXES:
            url = (
                f"https://cdn.cboe.com/api/global/delayed_quotes/charts/{data_type}/_"
                f"{symbol}"
                ".json"
            )
    return url


def get_eod_prices(
    symbol: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> pd.DataFrame:
    """Get EOD data from CBOE.

    Parameters
    ----------
    symbol: str
        The symbol of the company.
    start_date: Optional[date]
        The start date. [YYYY-MM-DD]
    end_date: Optional[date]
        The end date. [YYYY-MM-DD]

    Returns
    -------
    pd.DataFrame
        DataFrame of daily EOD OHLC+V prices.
    """

    symbol = symbol.upper()
    if symbol == ("NDX", "^NDX"):
        print("NDX time series data is not currently supported by the CBOE provider.")
        return pd.DataFrame()
    if "^" in symbol:
        symbol = symbol.replace("^", "")
    now = datetime.now()
    start_date = start_date if start_date else now - timedelta(days=50000)
    end_date = end_date if end_date else now
    if symbol not in SYMBOLS.index:
        print("The symbol, " f"{symbol}" ", was not found in the CBOE directory.")
        return pd.DataFrame()

    url = __generate_historical_prices_url(symbol)
    result = request(url)

    if result.status_code != 200:
        print(f"Error: {result.status_code}")
        return pd.DataFrame()

    data = (
        pd.DataFrame(result.json()["data"])[
            ["date", "open", "high", "low", "close", "volume"]
        ]
    ).set_index("date")

    # Fill in missing data from current or most recent trading session.

    today = pd.to_datetime(datetime.now().date())
    if today.weekday() > 4:
        day_minus = today.weekday() - 4
        today = pd.to_datetime(today - timedelta(days=day_minus))
    if today != data.index[-1]:
        _today, _ = get_ticker_info(symbol)
        today_df = pd.DataFrame()
        today_df["open"] = round(_today.loc["open"].astype(float), 2)
        today_df["high"] = round(_today.loc["high"].astype(float), 2)
        today_df["low"] = round(_today.loc["low"].astype(float), 2)
        today_df["close"] = round(_today.loc["close"].astype(float), 2)
        if symbol not in INDEXES and symbol not in TICKER_EXCEPTIONS:
            data = data[data["volume"] > 0]
            today_df["volume"] = _today.loc["volume"]
        today_df["date"] = today
        today_df = today_df.reset_index(drop=True).set_index("date")

        data = pd.concat([data, today_df], axis=0)

    # If ticker is an index there is no volume data and the types must be set.

    if symbol in INDEXES or symbol in TICKER_EXCEPTIONS:
        data = data[["open", "high", "low", "close", "volume"]]
        data["open"] = round(data.open.astype(float), 2)
        data["high"] = round(data.high.astype(float), 2)
        data["low"] = round(data.low.astype(float), 2)
        data["close"] = round(data.close.astype(float), 2)
        data["volume"] = 0

    data.index = pd.to_datetime(data.index, format="%Y-%m-%d")
    data = data[data["open"] > 0]

    data = data[
        (data.index >= pd.to_datetime(start_date, format="%Y-%m-%d"))
        & (data.index <= pd.to_datetime(end_date, format="%Y-%m-%d"))
    ]
    data.index = data.index.strftime("%Y-%m-%d")
    return data.reset_index()


def get_info(symbol: str) -> pd.DataFrame:
    """Get information and current statistics for a ticker.

    Parameters
    ----------
    symbol: str
        The symbol of the company.

    Returns
    -------
    pd.DataFrame
        Pandas DataFrame with results.
    """

    symbol = symbol.upper()
    info = pd.DataFrame()

    _info = get_ticker_info(symbol)[0]
    _iv = get_ticker_iv(symbol)
    info = pd.concat([_info, _iv])
    info.index = [camel_to_snake(c) for c in info.index]
    info.loc["symbol", symbol] = symbol
    info.loc["name", symbol] = SYMBOLS[SYMBOLS.index == symbol]["Company Name"][0]

    return info[symbol]
