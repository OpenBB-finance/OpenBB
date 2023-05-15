"""Model for retrieving public options data from the Montreal Options Exchange."""

from datetime import timedelta
from typing import Optional

import pandas as pd
import pandas_market_calendars as mcal
from pandas.tseries.holiday import next_workday

from openbb_terminal.helper_funcs import request

__docformat__ = "numpy"

# mypy: disable-error-code=no-redef


cal = mcal.get_calendar(name="TSX")
holidays = list(cal.regular_holidays.holidays().strftime("%Y-%m-%d"))


def check_weekday(date: str) -> str:
    """Helper function to check if the input date is a weekday."""

    if pd.to_datetime(date).weekday() not in range(0, 5):
        date_ = next_workday(pd.to_datetime(date)).strftime("%Y-%m-%d")
        date = date_
    return date


def get_all_ticker_symbols() -> pd.DataFrame:
    """Returns a DataFrame with all valid ticker symbols."""

    options_listings = pd.read_html("https://www.m-x.ca/en/trading/data/options-list")
    listings = pd.concat(options_listings)
    listings = listings.set_index("Option Symbol").drop_duplicates().sort_index()
    SYMBOLS = listings[:-1]
    SYMBOLS = SYMBOLS.fillna(value="")
    SYMBOLS["Underlying Symbol"] = (
        SYMBOLS["Underlying Symbol"].str.replace(" u", ".UN").str.replace("––", "")
    )
    return SYMBOLS


def get_underlying_price(symbol: str) -> pd.Series:
    """Gets the current price and performance of the underlying asset from the Canadian Securities Exchange."""

    data: object = ()
    symbol = symbol.upper()
    URL = f"https://webapi.thecse.com/trading/other/securities/{symbol}.json"

    response = request(URL)

    if response.status_code != 200:
        print("No price data found for the underlying security, " f"{symbol}")
        return data

    data = response.json()["ticker"]
    data = pd.Series(data).rename(f"{symbol}")

    return data


class Options:
    """Options data object for TMX.

    Attributes
    ----------
    SYMBOLS: pd.DataFrame
        The available symbols and company names.
    symbol: str
        The symbol entered by the user.
    source: str
        The source of the data, "TMX".
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
        True if implied volatility is returned.
    hasGreeks: bool
        Greeks data is not returned.
    """

    def __init__(self) -> None:
        self.SYMBOLS = get_all_ticker_symbols()
        self.symbol: str = ""
        self.source: str = "TMX"
        self.chains = pd.DataFrame()
        self.expirations: list = []
        self.strikes: list = []
        self.last_price: float = 0
        self.underlying_name: str = ""
        self.underlying_price = pd.Series(dtype=object)
        self.hasIV: bool
        self.hasGreeks: bool

    def check_symbol(self, symbol: str) -> bool:
        """Checks if the symbol is valid."""
        symbol = symbol.upper()
        return len(self.SYMBOLS.query("`Underlying Symbol` == @symbol")) == 1

    def get_quotes(self, symbol: str = "") -> object:
        """Gets the current quotes for the complete options chain.
        No implied volatility is returned from this method.
        Use `get_eodchains()` to get the implied volatility.

        Parameters
        ----------
        symbol: str
            The ticker symbol of the underlying asset.

        Returns
        -------
        self.chains: pd.DataFrame
            DataFrame with current quotes for the complete options chain.
        self.expirations: list
            List of all expiration dates.
        self.strikes: list
            List of all strike prices.
        self.underlying_price: pd.Series
            Series of the current price and performance of the underlying asset.
        self.last_price: float
            The last price of the underlying asset.
        self.underlying_name: str
            The name of the underlying asset.

        Example
        -------
        >>> ticker = tmx_model.Ticker().get_quotes("AC")
        >>> chains = ticker.chains
        """
        self.symbol: str = ""
        self.chains = pd.DataFrame()
        self.expirations: list = []
        self.strikes: list = []
        self.last_price: float = 0
        self.underlying_name: str = ""
        self.underlying_price = pd.Series(dtype=object)

        if symbol == "":
            print("Please enter a symbol.")
            return self

        symbol = symbol.upper()

        if ".TO" in symbol:
            symbol = symbol.replace(".TO", "")

        if self.check_symbol(symbol):
            symbol = list(
                self.SYMBOLS.query("`Underlying Symbol` == @symbol").index.values
            )[0]

        if symbol not in self.SYMBOLS.index:
            print(
                "The symbol, " f"{symbol}" ", is not a valid TMX listing.",
                sep=None,
            )
            return self
        self.symbol = symbol

        QUOTES_URL = (
            "https://www.m-x.ca/en/trading/data/quotes?symbol=" f"{self.symbol}" "*"
        )

        cols = [
            "expiration",
            "strike",
            "bid",
            "ask",
            "lastPrice",
            "change",
            "openInterest",
            "volume",
            "optionType",
        ]
        data = pd.DataFrame()
        data = pd.read_html(QUOTES_URL)[0]
        data = data.iloc[:-1]

        expirations = (
            data["Unnamed: 0_level_0"]["Expiry date"].astype(str).rename("expiration")
        )

        expirations = expirations.str.strip("(Weekly)")

        self.expirations = list(
            pd.DatetimeIndex(expirations.unique()).astype(str).sort_values()
        )

        strikes = (data["Unnamed: 7_level_0"].dropna().sort_values("Strike")).rename(
            columns={"Strike": "strike"}
        )

        self.strikes = list(strikes["strike"].unique())

        calls = pd.concat([expirations, strikes, data["Calls"]], axis=1)
        calls["expiration"] = pd.DatetimeIndex(calls["expiration"]).astype(str)
        calls["optionType"] = "call"
        calls.columns = cols
        calls = calls.set_index(["expiration", "strike", "optionType"])

        puts = pd.concat([expirations, strikes, data["Puts"]], axis=1)
        puts["expiration"] = pd.DatetimeIndex(puts["expiration"]).astype(str)
        puts["optionType"] = "put"
        puts.columns = cols
        puts = puts.set_index(["expiration", "strike", "optionType"])

        chains = pd.concat([calls, puts])
        chains["openInterest"] = chains["openInterest"].astype(int)
        chains["volume"] = chains["volume"].astype(int)
        chains["change"] = chains["change"].astype(float)
        chains["lastPrice"] = chains["lastPrice"].astype(float)
        chains["bid"] = chains["bid"].astype(float)
        chains["ask"] = chains["ask"].astype(float)
        chains = chains.sort_index()

        self.chains = chains.reset_index()

        self.underlying_name = self.SYMBOLS.loc[self.symbol][
            "Name of Underlying Instrument"
        ]

        try:
            self.underlying_price = get_underlying_price(self.symbol)
            self.last_price = self.underlying_price["Last Price"]
        except TypeError:
            self.last_price = 0
            self.underlying_price = 0

        self.hasIV = "impliedVolatility" in self.chains.columns
        self.hasGreeks = "gamma" in self.chains.columns

        return self

    def get_eodchains(self, symbol: str = "", date: str = "") -> object:
        """Gets the complete options chain for the EOD on a specific date.
        Open Interest values are from the previous day.

        Parameters
        ----------
        symbol: str
            The ticker symbol of the underlying asset.
        date: str
            The date to get the EOD chain for. Formatted as YYYY-MM-DD.

        Returns
        -------
        self.chains: pd.DataFrame
            DataFrame with the complete options chain for the chosen date.
        self.expirations: list
            List of all expiration dates available on the date.
        self.strikes: list
            List of all strike prices for that date.
        self.underlying_price: pd.Series
            Series of the price and performance of the underlying asset on the date.
        self.last_price: float
            The last price of the underlying asset on the date.
        self.underlying_name: str
            The name of the underlying asset.

        Example
        -------
        >>> xiu = Ticker().get_eodchains("XIU", "2009-01-01")
        """
        self.symbol: str = ""
        self.chains = pd.DataFrame()
        self.expirations: list = []
        self.strikes: list = []
        self.last_price: float = 0
        self.underlying_name: str = ""
        self.underlying_price = pd.Series(dtype=object)

        symbol = symbol.upper()
        BASE_URL = "https://www.m-x.ca/en/trading/data/historical?symbol="

        if symbol == "":
            print("Please enter a symbol.")
            return self

        if symbol not in self.SYMBOLS.index:
            print(
                "The symbol, " f"{symbol}" ", was not found in the TMX listings.",
                sep=None,
            )
            return self

        self.symbol = symbol

        if date == "":
            EOD_URL = BASE_URL + f"{self.symbol}" "&dnld=1#quotes"
        if date != "":
            if pd.to_datetime(date) < pd.to_datetime("2009-01-01"):
                print("Historical options data begins on 2009-01-02.")
            date = check_weekday(date)
            if date in holidays:
                date = (pd.to_datetime(date) + timedelta(days=1)).strftime("%Y-%m-%d")
            date = check_weekday(date)
            if date in holidays:
                date = (pd.to_datetime(date) + timedelta(days=1)).strftime("%Y-%m-%d")

            EOD_URL = (
                BASE_URL + f"{self.symbol}"
                "&from="
                f"{date}"
                "&to="
                f"{date}"
                "&dnld=1#quotes"
            )

        data = pd.read_csv(EOD_URL)

        contractSymbol = []

        for i in data.index:
            contractSymbol.append(data["Symbol"].iloc[i].replace(" ", ""))
        data["contractSymbol"] = contractSymbol

        data["optionType"] = data["Call/Put"].replace(0, "call").replace(1, "put")

        data = data.drop(
            columns=[
                "Symbol",
                "Class Symbol",
                "Root Symbol",
                "Underlying Symbol",
                "Ins. Type",
                "Call/Put",
            ]
        )

        cols = [
            "date",
            "strike",
            "expiration",
            "bid",
            "ask",
            "bidSize",
            "askSize",
            "lastPrice",
            "volume",
            "previousClose",
            "change",
            "open",
            "high",
            "low",
            "totalValue",
            "transactions",
            "settlementPrice",
            "openInterest",
            "impliedVolatility",
            "contractSymbol",
            "optionType",
        ]

        data.columns = cols

        self.expirations = list(
            pd.DatetimeIndex(data["expiration"].iloc[1:].unique()).astype(str)
        )

        self.strikes = list(data["strike"].iloc[1:].unique())

        data["expiration"] = pd.to_datetime(data["expiration"], format="%Y-%m-%d")
        data["date"] = pd.to_datetime(data["date"], format="%Y-%m-%d")
        data["impliedVolatility"] = 0.01 * data["impliedVolatility"]
        data = data.set_index(["expiration", "strike", "optionType"])
        data = data.sort_index()

        self.underlying_name = self.SYMBOLS.loc[self.symbol][
            "Name of Underlying Instrument"
        ]

        self.chains = data.reset_index()

        self.underlying_price = (
            self.chains.iloc[-1].drop(
                index=[
                    "impliedVolatility",
                    "strike",
                    "optionType",
                    "settlementPrice",
                    "openInterest",
                    "expiration",
                ]
            )
        ).rename(f"{self.underlying_name}")

        self.underlying_price.rename({"contractSymbol": "ticker"}, inplace=True)
        self.last_price = self.underlying_price["lastPrice"]
        self.chains = self.chains.iloc[:-1]

        self.hasIV = "impliedVolatility" in self.chains.columns
        self.hasGreeks = "gamma" in self.chains.columns

        return self


def load_options(symbol: str, date: Optional[str] = "") -> object:
    """Options data object for TMX.

    Parameters
    ----------
    symbol : str
        The ticker symbol to load.
    date: Optional[str]
        The date for EOD chains data.

    Returns
    -------
    SYMBOLS: pd.DataFrame
        The available symbols and company names.
    symbol: str
        The symbol entered by the user.
    source: str
        The source of the data, "TMX".
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
        True if implied volatility is returned.
    hasGreeks: bool
        Greeks data is not returned.
    """

    options = Options()
    if date != "":
        options.get_eodchains(symbol, date)
        return options
    options.get_quotes(symbol)
    return options
