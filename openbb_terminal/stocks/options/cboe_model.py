"""Model for retrieving public options data from the CBOE."""

from datetime import datetime
from typing import Tuple

import pandas as pd
from requests.exceptions import HTTPError

from openbb_terminal.helper_funcs import request
from openbb_terminal.stocks.options.op_helpers import Options, PydanticOptions

__docformat__ = "numpy"


TICKER_EXCEPTIONS: list[str] = ["NDX", "RUT"]


def get_cboe_directory() -> pd.DataFrame:
    """Gets the US Listings Directory for the CBOE.

    Returns
    -------
    pd.DataFrame: CBOE_DIRECTORY
        DataFrame of the CBOE listings directory

    Examples
    -------
    >>> from openbb_terminal.stocks.options import cboe_model
    >>> CBOE_DIRECTORY = cboe_model.get_cboe_directory()
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

    Examples
    -------
    >>> from openb_terminal.stocks.options import cboe_model
    >>> CBOE_INDEXES = cboe_model.get_cboe_index_directory()
    """

    CBOE_INDEXES: pd.DataFrame = pd.DataFrame(
        pd.read_json(
            "https://cdn.cboe.com/api/global/us_indices/definitions/all_indices.json"
        )
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
SYMBOLS = get_cboe_directory()


def get_ticker_info(symbol: str) -> Tuple[pd.DataFrame, list[str]]:
    """Gets basic info for the symbol and expiration dates

    Parameters
    ----------
    symbol: str
        The ticker to lookup

    Returns
    -------
    Tuple: [pd.DataFrame, pd.Series]
        ticker_details
        ticker_expirations

    Examples
    --------
    >>> from openbb_terminal.stocks.options import cboe_model
    >>> ticker_details,ticker_expirations = cboe_model.get_ticker_info('AAPL')
    >>> vix_details,vix_expirations = cboe_model.get_ticker_info('VIX')
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

                # Gets the data to return, and if none returns empty Tuple #

        symbol_info_url = (
            "https://www.cboe.com/education/tools/trade-optimizer/symbol-info/?symbol="
            f"{new_ticker}"
        )

        symbol_info = request(symbol_info_url)
        symbol_info_json = symbol_info.json()
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
    >>> from openbb_terminal.stocks.options import cboe_model
    >>> ticker_iv = cboe_model.get_ticker_iv('AAPL')
    >>> ndx_iv = cboe_model.get_ticker_iv('NDX')
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
                "hv60_annual_low": "hvsixtyOneYearLow",
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
            "hvsixtyOneYearLow",
            "ivNinetyOneYearHigh",
            "hvNinetyOneYearHigh",
            "ivNinetyOneYearLow",
            "hvNinetyOneYearLow",
        ]

        ticker_iv = pd.DataFrame(h_data).transpose()
    except HTTPError:
        print("There was an error with the request'\n")

    return pd.DataFrame(ticker_iv, columns=iv_order).transpose()


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

    Examples
    --------
    >>> from openbb_terminal.stocks.options import cboe_model
    >>> xsp = cboe_model.Options().get_chains('XSP')
    >>> xsp_chains = xsp.chains
    """
    # Checks ticker to determine if ticker is an index or an exception that requires modifying the request's URLs.

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
                "percent_change": "changePercent",
                "prev_day_close": "previousClose",
            }
        )

        # Pareses the option symbols into columns for expiration, strike, and optionType

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

        quotes = quotes.set_index(
            keys=["expiration", "strike", "optionType"]
        ).sort_index()
        quotes["openInterest"] = quotes["openInterest"].astype(int)
        quotes["volume"] = quotes["volume"].astype(int)
        quotes["bidSize"] = quotes["bidSize"].astype(int)
        quotes["askSize"] = quotes["askSize"].astype(int)
        quotes["previousClose"] = round(quotes["previousClose"], 2)
        quotes["changePercent"] = round(quotes["changePercent"], 2)

    except HTTPError:
        print("There was an error with the request'\n")
        return pd.DataFrame()

    return quotes.reset_index()


class Chains(Options):
    """OptionsChains data object for CBOE."""

    def __init__(self) -> None:
        self.SYMBOLS = SYMBOLS
        self.source = "CBOE"
        return

    def get_chains(self, symbol: str) -> object:
        """Gets the complete options chain from CBOE.

        Parameters
        ----------
        symbol: str
            The ticker symbol of the underlying asset.

        Returns
        -------
        object: Options
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

        Examples
        --------
        >>> from openbb_terminal.stocks.options import cboe_model
        >>> data = cboe_model.Chains().get_chains("AAPL")
        >>> chains = data.chains
        """
        self.source = "CBOE"
        self.symbol = symbol.upper()
        self.chains = pd.DataFrame()
        self.underlying_name = ""
        self.underlying_price = pd.Series(dtype=object)
        self.last_price = 0
        self.expirations = []
        self.strikes = []

        if self.symbol not in self.SYMBOLS.index:
            print("The symbol, " f"{symbol}" ", was not found in the CBOE directory.")
            return self
        info, _ = get_ticker_info(self.symbol)
        if not info.empty:
            iv = get_ticker_iv(self.symbol)
            info = pd.concat([info, iv])
            info = pd.Series(info[f"{self.symbol}"])
            self.underlying_name = (
                self.SYMBOLS.reset_index()
                .query("`Symbol` == @self.symbol")["Company Name"]
                .iloc[0]
            )
            self.underlying_price = info
            self.last_price = round(info.loc["price"], 2)
            self.chains = get_quotes(self.symbol)
            if not self.chains.empty:
                self.expirations = (
                    self.chains["expiration"].astype(str).unique().tolist()
                )
                self.strikes = self.chains["strike"].sort_values().unique().tolist()
            self.hasIV = "impliedVolatility" in self.chains.columns
            self.hasGreeks = "gamma" in self.chains.columns

            return self
        return None


def load_options(symbol: str, pydantic: bool = False) -> object:
    """Options data object for CBOE.

    Parameters
    ----------
    symbol: str
        The ticker symbol to load.
    pydantic: bool
        Whether to return the object as a Pydantic Model or a subscriptable Pandas Object.  Default is False.

    Returns
    -------
    object: OptionsChains
        SYMBOLS: pd.DataFrame
            The CBOE symbol directory.  Only returned if pydantic is False.
        symbol: str
            The symbol entered by the user.
        source: str
            The source of the data, "CBOE".
        chains: dict
            The complete options chain for the ticker.  Returns as a Pandas DataFrame if pydantic is False.
        expirations: list[str]
            List of unique expiration dates. (YYYY-MM-DD)
        strikes: list[float]
            List of unique strike prices.
        last_price: float
            The last price of the underlying asset.
        underlying_name: str
            The name of the underlying asset.
        underlying_price: dict
            The price and recent performance of the underlying asset.  Returns as a Pandas Series if pydantic is False.
        hasIV: bool
            Returns implied volatility.
        hasGreeks: bool
            Returns greeks data.

    Examples
    --------
    Get current options chains for AAPL.
    >>> from openbb_terminal.stocks.options.cboe_model import load_options
    >>> data = load_options("AAPL")
    >>> chains = data.chains

    Return the object as a Pydantic Model.
    >>> from openbb_terminal.stocks.options.cboe_model import load_options
    >>> data = load_options("AAPL", pydantic=True)
    """

    options = Chains()
    options.get_chains(symbol)

    if not pydantic:
        return options

    if not options.chains.empty:
        options_chains = PydanticOptions(
            source=options.source,
            symbol=options.symbol,
            underlying_name=options.underlying_name,
            last_price=options.last_price,
            expirations=options.expirations,
            strikes=options.strikes,
            hasIV=options.hasIV,
            hasGreeks=options.hasGreeks,
            underlying_price=options.underlying_price.to_dict(),
            chains=options.chains.to_dict(),
        )
        return options_chains
    return None
