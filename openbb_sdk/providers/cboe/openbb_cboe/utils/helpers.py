"""CBOE Helpers Module"""

from datetime import date, datetime, timedelta
from io import BytesIO, StringIO
from typing import Any, List, Literal, Optional

import pandas as pd
import requests
import requests_cache

TICKER_EXCEPTIONS = ["NDX", "RUT"]

US_INDEX_COLUMNS = {
    "name": "name",
    "current_price": "price",
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "prev_day_close": "prev_close",
    "price_change": "change",
    "price_change_percent": "change_percent",
    "last_trade_time": "last_trade_timestamp",
    "tick": "tick",
}

EUR_INDEX_COLUMNS = {
    "name": "name",
    "current_price": "price",
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "prev_day_close": "prev_close",
    "price_change": "change",
    "price_change_percent": "change_percent",
    "last_trade_time": "last_trade_timestamp",
}

EUR_INDEX_CONSTITUENTS_COLUMNS = {
    "symbol": "symbol",
    "current_price": "price",
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "volume": "volume",
    "seqno": "seqno",
    "prev_day_close": "prev_close",
    "price_change": "change",
    "price_change_percent": "change_percent",
    "last_trade_time": "last_trade_timestamp",
    "exchange_id": "exchange_id",
    "tick": "tick",
    "security_type": "type",
}


# This will cache certain requests for 7 days.  Ideally to speed up subsequent queries.
# Only used on functions with static values like symbol directories.
cboe_session = requests_cache.CachedSession(
    "OpenBB_CBOE", expire_after=timedelta(days=7), use_cache_dir=True
)


def camel_to_snake(string: str) -> str:
    """Convert camelCase to snake_case."""
    return "".join(["_" + i.lower() if i.isupper() else i for i in string]).lstrip("_")


def get_cboe_directory(**kwargs) -> pd.DataFrame:
    """Get the US Listings Directory for the CBOE.

    Returns
    -------
    pd.DataFrame: CBOE_DIRECTORY
        DataFrame of the CBOE listings directory
    """

    r = cboe_session.get(
        "https://www.cboe.com/us/options/symboldir/equity_index_options/?download=csv",
        timeout=10,
    )

    if r.status_code != 200:
        raise requests.HTTPError(r.status_code)

    r_json = StringIO(r.text)

    CBOE_DIRECTORY = pd.read_csv(r_json)

    CBOE_DIRECTORY = CBOE_DIRECTORY.rename(
        columns={
            " Stock Symbol": "symbol",
            " DPM Name": "dpm_name",
            " Post/Station": "post_station",
            "Company Name": "name",
        }
    ).set_index("symbol")

    return CBOE_DIRECTORY


def get_cboe_index_directory(**kwargs) -> pd.DataFrame:
    """Get the US Listings Directory for the CBOE

    Returns
    -------
    pd.DataFrame: CBOE_INDEXES
    """

    r = cboe_session.get(
        "https://cdn.cboe.com/api/global/us_indices/definitions/all_indices.json",
        timeout=10,
    )

    if r.status_code != 200:
        raise requests.HTTPError(r.status_code)

    CBOE_INDEXES = pd.DataFrame(r.json())

    CBOE_INDEXES = CBOE_INDEXES.rename(
        columns={
            "calc_end_time": "close_time",
            "calc_start_time": "open_time",
            "index_symbol": "symbol",
            "mkt_data_delay": "data_delay",
        },
    )

    indices_order: List[str] = [
        "symbol",
        "name",
        "description",
        "currency",
        "open_time",
        "close_time",
        "tick_days",
        "tick_frequency",
        "tick_period",
        "time_zone",
        "data_delay",
    ]

    CBOE_INDEXES = pd.DataFrame(CBOE_INDEXES, columns=indices_order).set_index("symbol")

    return CBOE_INDEXES


def stock_search(query: str, ticker: bool = False, **kwargs) -> dict:
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
    symbols = get_cboe_directory().reset_index()
    target = "name" if not ticker else "symbol"
    idx = symbols[target].str.contains(query, case=False)
    result = symbols[idx].to_dict("records")
    if len(result) > 0:
        data.update({"results": result})
        return data
    print(f"No results found for: {query}.  Try another search query.")
    return {}


def get_ticker_info(symbol: str, **kwargs) -> dict[str, Any]:
    symbol = symbol.upper()
    SYMBOLS = get_cboe_directory()
    INDEXES = get_cboe_index_directory()
    data: dict[str, Any] = {}

    if symbol not in SYMBOLS.index and symbol not in INDEXES.index:
        print(f"Data not found for: {symbol}")
        return data

    url = (
        f"https://cdn.cboe.com/api/global/delayed_quotes/quotes/_{symbol}.json"
        if symbol in INDEXES.index or symbol in TICKER_EXCEPTIONS
        else f"https://cdn.cboe.com/api/global/delayed_quotes/quotes/{symbol}.json"
    )

    r = requests.get(url, timeout=10)

    if r.status_code not in set([200, 403]):
        raise requests.HTTPError(r.status_code)

    if r.status_code == 403:
        raise requests.HTTPError(
            f"Data not found for, {symbol}. Perhaps it is a European symbol?"
        )

    data = r.json()["data"]

    if symbol in SYMBOLS.index.to_list():
        data.update({"name": SYMBOLS.at[symbol, "name"]})
    if symbol in INDEXES.index.to_list():
        data.update({"name": INDEXES.at[symbol, "name"]})

    _data = pd.DataFrame.from_dict(data, orient="index").transpose()

    _data = _data.rename(
        columns={
            "current_price": "price",
            "prev_day_close": "prev_close",
            "price_change": "change",
            "price_change_percent": "change_percent",
            "last_trade_time": "last_trade_timestamp",
            "security_type": "type",
        }
    )

    return _data.transpose()[0].to_dict()


def get_ticker_iv(symbol: str, **kwargs) -> dict[str, float]:
    """Get annualized high/low historical and implied volatility over 30/60/90 day windows.

    Parameters
    ----------
    symbol: str
        The loaded ticker

    Returns
    -------
    pd.DataFrame: ticker_iv
    """

    symbol = symbol.upper()

    INDEXES = get_cboe_index_directory().index.to_list()

    quotes_iv_url = (
        "https://cdn.cboe.com/api/global/delayed_quotes/historical_data/_"
        f"{symbol}"
        ".json"
        if symbol in TICKER_EXCEPTIONS or symbol in INDEXES
        else f"https://cdn.cboe.com/api/global/delayed_quotes/historical_data/{symbol}.json"
    )

    h_iv = requests.get(quotes_iv_url, timeout=10)

    if h_iv.status_code not in set([200, 403]):
        raise requests.HTTPError(h_iv.status_code)

    if h_iv.status_code == 403:
        raise requests.HTTPError(
            f"Data not found for, {symbol}. Perhaps it is a European symbol?"
        )

    data = pd.DataFrame(h_iv.json())[2:-1]["data"].rename(f"{symbol}")

    return data.to_dict()


def get_chains(symbol: str, **kwargs) -> pd.DataFrame:
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

    symbol = symbol.upper()

    INDEXES = get_cboe_index_directory()
    SYMBOLS = get_cboe_directory()

    if symbol not in SYMBOLS.index:
        print(f"{symbol} was not found in the CBOE directory.")
        return pd.DataFrame()

    quotes_url = (
        f"https://cdn.cboe.com/api/global/delayed_quotes/options/_{symbol}.json"
        if symbol in TICKER_EXCEPTIONS or symbol in INDEXES.index
        else f"https://cdn.cboe.com/api/global/delayed_quotes/options/{symbol}.json"
    )

    r = requests.get(quotes_url, timeout=10)
    if r.status_code != 200:
        print(f"No options data found for the symbol, {symbol}.")
        return pd.DataFrame()

    r_json = r.json()
    data = pd.DataFrame(r_json["data"])
    options = pd.Series(data.options, index=data.index)
    options_columns = list(options[0])
    options_data = list(options[:])
    options_df = pd.DataFrame(options_data, columns=options_columns)

    options_df = options_df.rename(
        columns={
            "option": "contract_symbol",
            "iv": "implied_volatility",
            "theo": "theoretical",
            "last_trade_price": "last_trade_price",
            "last_trade_time": "last_trade_timestamp",
            "percent_change": "change_percent",
            "prev_day_close": "prev_close",
        }
    )

    # Parses the option symbols into columns for expiration, strike, and option_type

    option_df_index = options_df["contract_symbol"].str.extractall(
        r"^(?P<Ticker>\D*)(?P<expiration>\d*)(?P<option_type>\D*)(?P<strike>\d*)"
    )
    option_df_index = option_df_index.reset_index().drop(columns=["match", "level_0"])
    option_df_index.option_type = option_df_index.option_type.str.replace(
        "C", "call"
    ).str.replace("P", "put")
    option_df_index.strike = [ele.lstrip("0") for ele in option_df_index.strike]
    option_df_index.strike = pd.Series(option_df_index.strike).astype(float)
    option_df_index.strike = option_df_index.strike * (1 / 1000)
    option_df_index.strike = option_df_index.strike.to_list()
    option_df_index.expiration = [ele.lstrip("1") for ele in option_df_index.expiration]
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

    quotes["last_trade_timestamp"] = pd.to_datetime(quotes["last_trade_timestamp"])
    quotes = quotes.set_index(keys=["expiration", "strike", "option_type"]).sort_index()
    quotes["open_interest"] = quotes["open_interest"].astype("int64")
    quotes["volume"] = quotes["volume"].astype("int64")
    quotes["bid_size"] = quotes["bid_size"].astype("int64")
    quotes["ask_size"] = quotes["ask_size"].astype("int64")
    quotes["prev_close"] = round(quotes["prev_close"], 2)
    quotes["change_percent"] = round(quotes["change_percent"], 2)

    return quotes.reset_index()


def __generate_historical_prices_url(
    symbol, data_type: Optional[Literal["intraday", "historical"]] = "historical"
) -> str:
    """Generate the final URL for historical prices data."""

    url: str = ""
    INDEXES = get_cboe_index_directory().index.to_list()

    url = (
        f"https://cdn.cboe.com/api/global/delayed_quotes/charts/{data_type}/_{symbol}.json"
        if symbol in TICKER_EXCEPTIONS or symbol in INDEXES
        else f"https://cdn.cboe.com/api/global/delayed_quotes/charts/{data_type}/{symbol}.json"
    )

    return url


def get_us_eod_prices(
    symbol: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    **kwargs,
) -> pd.DataFrame:
    """Get US EOD data from CBOE.

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
        DataFrame of daily OHLC+V prices.
    """

    SYMBOLS = get_cboe_directory()
    INDEXES = get_cboe_index_directory().index.to_list()
    symbol = symbol.upper()

    if symbol == ("NDX", "^NDX"):
        print("NDX time series data is not currently supported by the CBOE provider.")
        return pd.DataFrame()

    if "^" in symbol:
        symbol = symbol.replace("^", "")

    now = datetime.now()
    start_date = start_date if start_date else now - timedelta(days=50000)
    end_date = end_date if end_date else now

    if symbol not in SYMBOLS.index and symbol not in INDEXES:
        print("The symbol, " f"{symbol}" ", was not found in the CBOE directory.")
        return pd.DataFrame()

    url = __generate_historical_prices_url(symbol)
    r = requests.get(url, timeout=10)

    if r.status_code != 200:
        print(f"Error: {r.status_code}")
        return pd.DataFrame()

    data = (
        pd.DataFrame(r.json()["data"])[
            ["date", "open", "high", "low", "close", "volume"]
        ]
    ).set_index("date")

    # Fill in missing data from current or most recent trading session.

    today = pd.to_datetime(datetime.now().date())
    if today.weekday() > 4:
        day_minus = today.weekday() - 4
        today = pd.to_datetime(today - timedelta(days=day_minus))
    if today != data.index[-1]:
        _today = pd.Series(get_ticker_info(symbol))
        today_df = pd.Series(dtype="object")
        today_df["open"] = round(_today["open"], 2)
        today_df["high"] = round(_today["high"], 2)
        today_df["low"] = round(_today["low"], 2)
        today_df["close"] = round(_today["close"], 2)
        if symbol not in INDEXES and symbol not in TICKER_EXCEPTIONS:
            data = data[data["volume"] > 0]
            today_df["volume"] = _today["volume"]
        today_df["date"] = today.date()
        today_df = pd.DataFrame(today_df).transpose().set_index("date")

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


def get_us_info(symbol: str, **kwargs) -> pd.DataFrame:
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

    info = pd.DataFrame()
    symbol = symbol.upper()
    INDEXES = get_cboe_index_directory().index.to_list()
    SYMBOLS = get_cboe_directory()

    if symbol not in SYMBOLS.index and symbol not in INDEXES:
        print(f"The symbol, {symbol}, was not found in the CBOE directory.")
        return pd.DataFrame()

    _info = pd.Series(get_ticker_info(symbol))
    _iv = pd.Series(get_ticker_iv(symbol))
    info = pd.concat([_info, _iv])
    info = pd.DataFrame(info).transpose()
    info = info[
        [
            "name",
            "symbol",
            "type",
            "exchange_id",
            "tick",
            "price",
            "change",
            "change_percent",
            "open",
            "high",
            "low",
            "close",
            "prev_close",
            "volume",
            "iv30",
            "iv30_change",
            "iv30_change_percent",
            "iv30_annual_high",
            "iv30_annual_low",
            "hv30_annual_high",
            "hv30_annual_low",
            "iv60_annual_high",
            "iv60_annual_low",
            "hv60_annual_high",
            "hv60_annual_low",
            "iv90_annual_high",
            "iv90_annual_low",
            "hv90_annual_high",
            "hv90_annual_low",
            "last_trade_timestamp",
            "seqno",
        ]
    ]

    return info.transpose()[0].to_dict()


def list_futures(**kwargs) -> List[dict]:
    """List of CBOE futures and their underlying symbols.

    Returns
    --------
    pd.DataFrame
        Pandas DataFrame with results.
    """

    r = requests.get(
        "https://cdn.cboe.com/api/global/delayed_quotes/symbol_book/futures-roots.json",
        timeout=10,
    )

    if r.status_code != 200:
        raise requests.HTTPError(r.status_code)

    return r.json()["data"]


def get_settlement_prices(
    settlement_date: Optional[date] = None,
    options: bool = False,
    archives: bool = False,
    final_settlement: bool = False,
    **kwargs,
) -> pd.DataFrame:
    """Gets the settlement prices of CBOE futures.

    Parameters
    -----------
    settlement_date: Optional[date]
        The settlement date. Only valid for active contracts. [YYYY-MM-DD]
    options: bool
        If true, returns options on futures.
    archives: bool
        Settlement price archives for select years and products.  Overridden by other parameters.
    final_settlement: bool
        Final settlement prices for expired contracts.  Overrides archives.

    Returns
    -------
    pd.DataFrame
        Pandas DataFrame with results.
    """

    if archives is True:
        url = "https://cdn.cboe.com/resources/futures/archive/volume-and-price/CFE_FinalSettlement_Archive.csv"

    if settlement_date is not None:
        url = f"https://www.cboe.com/us/futures/market_statistics/settlement/csv?dt={settlement_date}"
        if options is True:
            url = f"https://www.cboe.com/us/futures/market_statistics/settlement/csv?options=t&dt={settlement_date}"

    if settlement_date is None:
        url = "https://www.cboe.com/us/futures/market_statistics/settlement/csv"
        if options is True:
            url = "https://www.cboe.com/us/futures/market_statistics/settlement/csv?options=t"

    if final_settlement is True:
        url = "https://www.cboe.com/us/futures/market_statistics/final_settlement_prices/csv/"

    r = requests.get(url, timeout=10)

    if r.status_code != 200:
        raise requests.HTTPError(r.status_code)

    data = pd.read_csv(BytesIO(r.content), index_col=None, parse_dates=True)

    if data.empty:
        print(
            f"No results found for, {settlement_date}."
        ) if settlement_date is not None else "No results found."
        return pd.DataFrame()

    data.columns = [camel_to_snake(c.replace(" ", "")) for c in data.columns]
    data = data.rename(columns={"expiration_date": "expiration"})

    if len(data) > 0:
        return data

    return pd.DataFrame()


def get_curve(
    symbol: str = "VX", date: Optional[date] = None, **kwargs
) -> pd.DataFrame:
    """Gets the term structure for a given futures product.
    Parameters
    ----------
    symbol: str
        The root symbol of the future.  VIX is known as VX.

    date: Optional[date]
        The date of the term structure.  Only valid for active contracts. [YYYY-MM-DD].
    Returns
    -------
    pd.DataFrame
        Pandas DataFrame with results."""

    symbol = symbol.upper()
    FUTURES = get_settlement_prices(settlement_date=date)
    if len(FUTURES) == 0:
        return pd.DataFrame()

    if symbol not in FUTURES["product"].unique().tolist():
        print(
            "The symbol, "
            f"{symbol}"
            ", is not valid.  Chose from: "
            f"{FUTURES['product'].unique().tolist()}"
        )
        return pd.DataFrame()

    data = get_settlement_prices(settlement_date=date)
    data = data.query("`product` == @symbol")

    return data.set_index("expiration")[["symbol", "price"]]


class Europe:
    """Class for European CBOE data."""

    @staticmethod
    def get_all_index_definitions(**kwargs) -> dict[Any, Any]:
        """Get the full list of European index definitions.

        Returns
        -------
        dict[Any, Any]
            Dictionary with results.
        """

        r = cboe_session.get(
            "https://cdn.cboe.com/api/global/european_indices/definitions/all-definitions.json",
            timeout=10,
        )

        if r.status_code != 200:
            raise requests.HTTPError(r.status_code)
        return r.json()["data"]

    @staticmethod
    def get_all_index_quotes(**kwargs) -> pd.DataFrame:
        """Get the complete list of European indices and their current quotes.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame with results.
        """

        r = requests.get(
            "https://cdn.cboe.com/api/global/european_indices/index_quotes/all-indices.json",
            timeout=10,
        )

        if r.status_code != 200:
            raise requests.HTTPError(r.status_code)

        data = (
            pd.DataFrame.from_records(r.json()["data"])
            .drop(columns=["symbol"])
            .rename(columns={"index": "symbol"})
            .set_index("symbol")
            .round(2)
        )

        INDEXES = get_cboe_index_directory()

        for i in data.index:
            data.loc[i, ("name")] = INDEXES.at[i, "name"]

        data = data[list(EUR_INDEX_COLUMNS.keys())]
        data.columns = list(EUR_INDEX_COLUMNS.values())

        return data.reset_index()

    @staticmethod
    def list_indices(**kwargs) -> pd.DataFrame:
        """Gets names, currencies, ISINs, regions, and symbols for European indices.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame with results.
        """

        data = Europe.get_all_index_definitions()
        data = (
            pd.DataFrame.from_records(pd.DataFrame(data)["index"])
            .drop(columns=["short_name"])
            .rename(columns={"long_name": "name"})
        )
        return data

    @staticmethod
    def list_index_constituents(symbol: str, **kwargs) -> list[str]:
        """List symbols for constituents of a European index.

        Parameters
        ----------
        symbol: str
            The symbol of the index.

        Returns
        -------
        list[str]
            List of constituents as ticker symbols.
        """

        SYMBOLS = Europe.list_indices()["symbol"].to_list()
        symbol = symbol.upper()

        if symbol not in SYMBOLS:
            print(
                f"The symbol, {symbol}, was not found in the CBOE European Index directory.",
                "Use `get_european_indices_info()` to see the full list of indices.",
                sep="\n",
            )
            return []

        url = f"https://cdn.cboe.com/api/global/european_indices/definitions/{symbol}.json"
        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            raise requests.HTTPError(r.status_code)

        r_json = r.json()["constituents"]

        return [r_json[i]["constituent_symbol"] for i in range(0, len(r_json))]

    @staticmethod
    def get_index_constituents_quotes(symbol: str, **kwargs) -> pd.DataFrame:
        """Get the current quotes for constituents of an index.

        Parameters
        ----------
        symbol: str
            The symbol of the index.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame with results.
        """

        symbol = symbol.upper()
        SYMBOLS = Europe.list_indices()["symbol"].to_list()

        if symbol not in SYMBOLS:
            print(
                "The symbol, "
                f"{symbol}"
                ", is not a valid CBOE European index. Use `list_european_indices()` to see the full list of indices."
            )
            return pd.DataFrame()

        url = f"https://cdn.cboe.com/api/global/european_indices/constituent_quotes/{symbol}.json"

        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            raise requests.HTTPError(r.status_code)

        r_json = r.json()

        data = (
            pd.DataFrame.from_records(r_json["data"])[
                list(EUR_INDEX_CONSTITUENTS_COLUMNS.keys())
            ]
            .rename(columns=EUR_INDEX_CONSTITUENTS_COLUMNS)
            .round(2)
        )

        return data

    @staticmethod
    def get_index_intraday(symbol: str, **kwargs) -> pd.DataFrame:
        """Get one-minute prices for a European index during the most recent trading day.

        Parameters
        ----------
        symbol: str
            The symbol of the index.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame with results.
        """

        SYMBOLS = Europe.list_indices()["symbol"].to_list()

        if symbol not in SYMBOLS:
            print(
                "The symbol, "
                f"{symbol}"
                ", was not found in the CBOE European Index directory."
            )
            return pd.DataFrame()

        url = f"https://cdn.cboe.com/api/global/european_indices/intraday_chart_data/{symbol}.json"

        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            raise requests.HTTPError(r.status_code)

        r_json = r.json()["data"]

        data = pd.DataFrame.from_records(pd.DataFrame(r_json)["price"])
        data["datetime"] = pd.DataFrame(r_json)["datetime"]
        data["utc_datetime"] = pd.DataFrame(r_json)["utc_datetime"]

        return round(
            data[["utc_datetime", "datetime", "open", "high", "low", "close"]], 2
        )

    @staticmethod
    def get_index_eod(symbol: str, **kwargs) -> List[dict[str, float]]:
        """Get historical closing levels for a European index.

        Parameters
        ----------
        symbol: str
            The symbol of the index.

        Returns
        -------
        List[dict[str, float]]
            Records of closing levels on each trading day.
        """

        symbol = symbol.upper()
        SYMBOLS = Europe.list_indices()["symbol"].to_list()

        if symbol not in SYMBOLS:
            print(
                "The symbol, "
                f"{symbol}"
                ", was not found in the CBOE European Index directory."
            )
            return pd.DataFrame()

        url = f"https://cdn.cboe.com/api/global/european_indices/index_history/{symbol}.json"

        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            raise requests.HTTPError(r.status_code)

        r_json = r.json()

        return r_json["data"]
