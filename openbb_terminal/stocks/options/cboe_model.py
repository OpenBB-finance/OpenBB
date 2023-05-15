"""Model for retrieving public options data from the CBOE."""

from typing import Tuple

import pandas as pd
from requests.exceptions import HTTPError

from openbb_terminal.helper_funcs import request

__docformat__ = "numpy"

# mypy: disable-error-code=no-redef


TICKER_EXCEPTIONS: list[str] = ["NDX", "RUT"]


def get_cboe_directory() -> pd.DataFrame:
    """Gets the US Listings Directory for the CBOE

    Returns
    -------
    pd.DataFrame: CBOE_DIRECTORY
        DataFrame of the CBOE listings directory

    Example
    -------
    CBOE_DIRECTORY = get_cboe_directory()
    """
    CBOE_DIRECTORY: pd.DataFrame = pd.read_csv(
        "https://www.cboe.com/us/options/symboldir/equity_index_options/?download=csv"
    )
    CBOE_DIRECTORY = CBOE_DIRECTORY.rename(
        columns={
            " Stock Symbol": "Symbol",
            " DPM Name": "DPM Name",
            " Post/Station": "Post/Station",
        }
    ).set_index("Symbol")
    return CBOE_DIRECTORY


def get_cboe_index_directory() -> pd.DataFrame:
    """Gets the US Listings Directory for the CBOE

    Returns
    -------
    pd.DataFrame: CBOE_INDEXES

    Example
    -------
    CBOE_INDEXES = get_cboe_index_directory(
    """

    CBOE_INDEXES: pd.DataFrame = pd.read_json(
        "https://cdn.cboe.com/api/global/us_indices/definitions/all_indices.json"
    )

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

    indices_order: list[str] = [
        "Ticker",
        "Name",
        "Description",
        "Currency",
        "Tick Days",
        "Frequency",
        "Period",
        "Time Zone",
    ]

    CBOE_INDEXES = pd.DataFrame(CBOE_INDEXES, columns=indices_order).set_index("Ticker")

    return CBOE_INDEXES


# Gets the list of indexes for parsing the ticker symbol properly.
INDEXES = get_cboe_index_directory().index.tolist()


def get_ticker_info(symbol: str) -> Tuple[pd.DataFrame, list[str]]:
    """Gets basic info for the symbol and expiration dates

    Parameters
    ----------
    symbol: str
        The ticker to lookup

    Returns
    -------
    Tuple[pd.DataFrame, pd.Series]: ticker_details,ticker_expirations

    Examples
    --------
    ticker_details,ticker_expirations = get_ticker_info('AAPL')

    ticker_details,ticker_expirations = get_ticker_info('VIX')
    """
    stock = "stock"
    index = "index"
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

                # Gets the data to return, and if none returns empty Tuple #

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
                        "symbol": "Symbol",
                        "current_price": "Current Price",
                        "bid": "Bid",
                        "ask": "Ask",
                        "bid_size": "Bid Size",
                        "ask_size": "Ask Size",
                        "open": "Open",
                        "high": "High",
                        "low": "Low",
                        "close": "Close",
                        "volume": "Volume",
                        "iv30": "IV30",
                        "prev_day_close": "Previous Close",
                        "price_change": "Change",
                        "price_change_percent": "Change %",
                        "iv30_change": "IV30 Change",
                        "iv30_percent_change": "IV30 Change %",
                        "last_trade_time": "Last Trade Time",
                        "exchange_id": "Exchange ID",
                        "tick": "Tick",
                        "security_type": "Type",
                    }
                )
                details_columns = [
                    "Symbol",
                    "Type",
                    "Tick",
                    "Bid",
                    "Bid Size",
                    "Ask Size",
                    "Ask",
                    "Current Price",
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume",
                    "Previous Close",
                    "Change",
                    "Change %",
                    "IV30",
                    "IV30 Change",
                    "IV30 Change %",
                    "Last Trade Time",
                ]
                ticker_details = (
                    pd.DataFrame(ticker_details, columns=details_columns)
                    .set_index(keys="Symbol")
                    .dropna(axis=1)
                    .transpose()
                )

            if index[0] in type_[0]:
                index_details = symbol_details
                ticker_details = pd.DataFrame(index_details).rename(
                    columns={
                        "symbol": "Symbol",
                        "security_type": "Type",
                        "current_price": "Current Price",
                        "price_change": "Change",
                        "price_change_percent": "Change %",
                        "tick": "Tick",
                        "open": "Open",
                        "high": "High",
                        "low": "Low",
                        "close": "Close",
                        "prev_day_close": "Previous Close",
                        "iv30": "IV30",
                        "iv30_change": "IV30 Change",
                        "iv30_change_percent": "IV30 Change %",
                        "last_trade_time": "Last Trade Time",
                    }
                )

                index_columns = [
                    "Symbol",
                    "Type",
                    "Tick",
                    "Current Price",
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Previous Close",
                    "Change",
                    "Change %",
                    "IV30",
                    "IV30 Change",
                    "IV30 Change %",
                    "Last Trade Time",
                ]

                ticker_details = (
                    pd.DataFrame(ticker_details, columns=index_columns)
                    .set_index(keys="Symbol")
                    .dropna(axis=1)
                    .transpose()
                )

    except HTTPError:
        print("There was an error with the request'\n")
        ticker_details = pd.DataFrame()
        ticker_expirations = list()
        return ticker_details, ticker_expirations

    return ticker_details, ticker_expirations


def get_ticker_iv(symbol: str) -> pd.DataFrame:
    """Gets annualized high/low historical and implied volatility over 30/60/90 day windows.

    Parameters
    ----------
    symbol: str
        The loaded ticker

    Returns
    -------
    pd.DataFrame: ticker_iv

    Examples
    --------
    ticker_iv = get_ticker_iv('AAPL')

    ticker_iv = get_ticker_iv('NDX')
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

        h_iv_json = pd.DataFrame(h_iv.json())
        h_columns = [
            "annual_high",
            "annual_low",
            "hv30_annual_high",
            "hv30_annual_low",
            "hv60_annual_high",
            "hv60_annual_low",
            "hv90_annual_high",
            "hv90_annual_low",
            "iv30_annual_high",
            "iv30_annual_low",
            "iv60_annual_high",
            "iv60_annual_low",
            "iv90_annual_high",
            "iv90_annual_low",
            "symbol",
        ]
        h_data = h_iv_json[1:]
        h_data = pd.DataFrame(h_iv_json).transpose()
        h_data = h_data[1:2]
        quotes_iv_df = pd.DataFrame(data=h_data, columns=h_columns).reset_index()

        quotes_iv_df = quotes_iv_df.rename(
            columns={
                "annual_high": "1Y High",
                "annual_low": "1Y Low",
                "hv30_annual_high": "HV30 1Y High",
                "hv30_annual_low": "HV30 1Y Low",
                "hv60_annual_high": "HV60 1Y High",
                "hv60_annual_low": "HV60 1Y Low",
                "hv90_annual_high": "HV90 1Y High",
                "hv90_annual_low": "HV90 1Y Low",
                "iv30_annual_high": "IV30 1Y High",
                "iv30_annual_low": "IV30 1Y Low",
                "iv60_annual_high": "IV60 1Y High",
                "iv60_annual_low": "IV60 1Y Low",
                "iv90_annual_high": "IV90 1Y High",
                "iv90_annual_low": "IV90 1Y Low",
                "symbol": "Symbol",
            },
        )

        quotes_iv_df = quotes_iv_df.set_index(keys="Symbol")

        iv_order = [
            "IV30 1Y High",
            "HV30 1Y High",
            "IV30 1Y Low",
            "HV30 1Y Low",
            "IV60 1Y High",
            "HV60 1Y High",
            "IV60 1Y Low",
            "HV60 1Y low",
            "IV90 1Y High",
            "HV90 1Y High",
            "IV90 1Y Low",
            "HV 90 1Y Low",
        ]

        ticker_iv = (
            pd.DataFrame(quotes_iv_df, columns=iv_order).fillna(value="N/A").transpose()
        )
    except HTTPError:
        print("There was an error with the request'\n")

    return ticker_iv


def get_quotes(symbol: str) -> pd.DataFrame:
    """Gets the complete options chains for a ticker.

    Parameters
    ----------
    symbol: str
        The ticker get options data for

    Returns
    -------
    pd.DataFrame
        DataFrame with all active options contracts for the underlying symbol.

    Example
    -------
    >>> chains = get_quotes('SPX')
    """
    # Checks ticker to determine if ticker is an index or an exception that requires modifying the request's URLs

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

        r = request(quotes_url)
        if r.status_code != 200:
            print("No data found for the symbol: " f"{symbol}" "")
            return pd.DataFrame()

        r_json = r.json()
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
                "percent_change": "percentChange",
                "prev_day_close": "previousClose",
            }
        )

        # Pareses the option symbols into columns for expiration, strike, and optionType

        option_df_index = pd.Series(options_df["contractSymbol"]).str.extractall(
            r"^(?P<Ticker>\D*)(?P<expiration>\d*)(?P<optionType>\D*)(?P<strike>\d*)"
        )
        option_df_index: pd.DataFrame = option_df_index.reset_index().drop(
            columns=["match", "level_0"]
        )
        option_df_index.optionType = option_df_index.optionType.str.replace(
            "C", "Call"
        ).str.replace("P", "Put")
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
        quotes = quotes.set_index(
            keys=["expiration", "strike", "optionType"]
        ).sort_index()
        quotes["openInterest"] = quotes["openInterest"].astype(int)
        quotes["volume"] = quotes["volume"].astype(int)
        quotes["bidSize"] = quotes["bidSize"].astype(int)
        quotes["askSize"] = quotes["askSize"].astype(int)

    except HTTPError:
        print("There was an error with the request'\n")
        return pd.DataFrame()

    return quotes.reset_index()


class Options:
    """Options data object for CBOE.

    Attributes
    ----------
    SYMBOLS: pd.DataFrame
        The CBOE symbol directory
    symbol: str
        The symbol entered by the user.
    source: str
        The source of the data, "CBOE".
    chains: pd.DataFrame
        The complete options chain for the ticker.
    expirations: list[str]
        List of unique expiration dates. (YYYY-MM-DD)
    strikes: list[float]
        List of unique strike prices.
    last_price: float
        The last price of the underlying asset.
    underlying_name: str
        The name of the underlying asset.
    underlying_price: pd.Series
        The price and recent performance of the underlying asset.
    hasIV: bool
        Returns implied volatility.
    hasGreeks: bool
        Returns greeks.
    """

    def __init__(self) -> None:
        self.SYMBOLS: pd.DataFrame = get_cboe_directory()
        self.symbol: str = ""
        self.source: str = "CBOE"
        self.chains = pd.DataFrame()
        self.expirations: list = []
        self.strikes: list = []
        self.last_price: float = 0
        self.underlying_name: str = ""
        self.underlying_price = pd.Series(dtype=object)
        self.hasIV: bool
        self.hasGreeks: bool

    def get_quotes(self, symbol: str) -> object:
        self.symbol = symbol.upper()
        if self.symbol not in self.SYMBOLS.index:
            print("The symbol, " f"{symbol}" ", was not found in the CBOE directory.")
            return self
        info, _ = get_ticker_info(self.symbol)
        if not info.empty:
            iv = get_ticker_iv(self.symbol)
            info = pd.concat([info, iv])
            self.underlying_name = self.SYMBOLS.reset_index().query(
                "`Symbol` == @self.symbol"
            )["Company Name"]
            self.underlying_price = info
            self.last_price = info.loc["Current Price"]
            self.chains = get_quotes(self.symbol)
            self.expirations = []
            self.strikes = []
            if not self.chains.empty:
                self.expirations = (
                    self.chains["expiration"].astype(str).unique().tolist()
                )
                self.strikes = self.chains["strike"].sort_values().unique().tolist()
            self.hasIV = "impliedVolatility" in self.chains.columns
            self.hasGreeks = "gamma" in self.chains.columns

            return self
        return self


def load_options(symbol: str) -> object:
    """Options data object for CBOE.

    Parameters
    ----------
    symbol : str
        The ticker symbol to load.

    Returns
    -------
    SYMBOLS: list[str]
        The CBOE symbol directory.
    symbol: str
        The symbol entered by the user.
    source: str
        The source of the data, "CBOE".
    chains: pd.DataFrame
        The complete options chain for the ticker.
    expirations: list[str]
        List of unique expiration dates. (YYYY-MM-DD)
    strikes: list[float]
        List of unique strike prices.
    last_price: float
        The last price of the underlying asset.
    underlying_name: str
        The name of the underlying asset.
    underlying_price: pd.Series
        The price and recent performance of the underlying asset.
    hasIV: bool
        Returns implied volatility.
    hasGreeks: bool
        Returns greeks data.
    """

    options = Options()
    options.get_quotes(symbol)

    return options
