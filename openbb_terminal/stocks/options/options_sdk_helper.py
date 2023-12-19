"""Options Functions For OpenBB SDK"""

import logging
import re
from datetime import datetime, timedelta
from typing import Optional, Union

import numpy as np
import pandas as pd

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_rf
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options import (
    chartexchange_model,
    intrinio_model,
    nasdaq_model,
    options_chains_model,
    options_chains_view,
    tradier_model,
    yfinance_model,
)
from openbb_terminal.stocks.options.op_helpers import Option, Options

logger = logging.getLogger(__name__)

# pylint:disable=C0302,R0913


@log_start_end(log=logger)
def get_full_option_chain(
    symbol: str, source: str = "Nasdaq", expiration: Union[str, None] = None
) -> pd.DataFrame:
    """Get Option Chain For A Stock.  No greek data is returned

    Parameters
    ----------
    symbol : str
        Symbol to get chain for
    source : str, optional
        Source to get data from, by default "Nasdaq". Can be YahooFinance, Tradier, Nasdaq, or Intrinio.
    expiration : Union[str, None], optional
        Date to get chain for.  By default returns all dates

    Returns
    -------
    pd.DataFrame
        Dataframe of full option chain.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> aapl_option_chain = openbb.stocks.options.chains("AAPL", source = "Nasdaq")

    To get a specific expiration date, use the expiration parameter

    >>> aapl_chain_date = openbb.stocks.options.chains("AAPL", expiration="2023-07-21", source="Nasdaq")
    """

    source = re.sub(r"\s+", "", source.lower())
    df = pd.DataFrame()
    if source == "tradier":
        df = tradier_model.get_full_option_chain(symbol)

    elif source == "nasdaq":
        df = nasdaq_model.get_full_option_chain(symbol)

    elif source == "intrinio":
        df = intrinio_model.get_full_option_chain(symbol)

    else:
        df = yfinance_model.get_full_option_chain(symbol)

    if not isinstance(df, pd.DataFrame) or df.empty:
        logger.info("Invalid Source or Symbol")
        console.print("Invalid Source or Symbol")
        return pd.DataFrame()

    if expiration:
        df = df[df.expiration == expiration]

    return df


def get_option_current_price(
    symbol: str,
    source: str = "Nasdaq",
):
    """Get Option current price for a stock.

    Parameters
    ----------
    symbol : str
        Symbol to get chain for
    source : str, optional
        Source to get data, by default "Nasdaq". Can be Nasdaq, Tradier, or YahooFinance

    Returns
    -------
    float
        float of current price

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> aapl_price = openbb.stocks.options.price("AAPL", source="Nasdaq")
    """

    source = re.sub(r"\s+", "", source.lower())
    output = None
    if source == "tradier":
        output = tradier_model.get_last_price(symbol)
    if source == "nasdaq":
        output = nasdaq_model.get_last_price(symbol)
    if source == "yahoofinance":
        output = yfinance_model.get_last_price(symbol)

    if not output:
        logger.info("Invalid Source or Symbol")
        console.print("Invalid Source or Symbol")
        return 0.0

    return output


@log_start_end(log=logger)
def get_option_expirations(symbol: str, source: str = "Nasdaq") -> list:
    """Get Option Chain Expirations

    Parameters
    ----------
    symbol : str
        Symbol to get chain for
    source : str, optional
        Source to get data from, by default "Nasdaq". Can be Intrinio, Tradier, Nasdaq, or YahooFinance

    Returns
    -------
    pd.DataFrame
        Dataframe of full option chain.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> SPX_expirations = openbb.stocks.options.expirations("SPX", source = "Tradier")
    """
    source = re.sub(r"\s+", "", source.lower())
    output = []
    if source == "tradier":
        output = tradier_model.option_expirations(symbol)
    if source == "yahoofinance":
        output = yfinance_model.option_expirations(symbol)
    if source == "nasdaq":
        output = nasdaq_model.option_expirations(symbol)
    if source == "intrinio":
        output = intrinio_model.get_expiration_dates(symbol)

    if not output:
        logger.info("Invalid Source or Symbol")
        console.print("Invalid Source or Symbol")
        return []

    return output


@log_start_end(log=logger)
def hist(
    symbol: str,
    exp: str,
    strike: Union[int, Union[float, str]],
    call: bool = True,
    source="ChartExchange",
) -> pd.DataFrame:
    """Get historical option pricing.

    Parameters
    ----------
    symbol : str
        Symbol to get data for
    exp : str
        Expiration date
    strike : Union[int ,Union[float,str]]
        Strike price
    call : bool, optional
        Flag to indicate a call, by default True
    source : str, optional
        Source to get data from, by default "ChartExchange". Can be ChartExchange, Intrinio, or Tradier

    Returns
    -------
    pd.DataFrame
        DataFrame of historical option pricing

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> aapl_150_call = openbb.stocks.options.hist("AAPL", "2022-11-18", 150, call=True, source="ChartExchange")

    Because this generates a dataframe, we can easily plot the close price for a SPY put:
    (Note that Tradier requires an API key)
    >>> openbb.stocks.options.hist("SPY", "2022-11-18", 400, call=False, source="Tradier").plot(y="close")
    """

    source = re.sub(r"\s+", "", source.lower())
    output = pd.DataFrame()
    if source == "chartexchange":
        output = chartexchange_model.get_option_history(symbol, exp, call, strike)
    if source == "tradier":
        output = tradier_model.get_historical_options(symbol, exp, strike, not call)
    if source == "intrinio":
        occ_symbol = f"{symbol}{''.join(exp[2:].split('-'))}{'C' if call else 'P'}{str(int(1000*strike)).zfill(8)}"
        output = intrinio_model.get_historical_options(occ_symbol)

    if not isinstance(output, pd.DataFrame) or output.empty:
        logger.info("No data found for symbol, check symbol and expiration date")
        console.print("No data found for symbol, check symbol and expiration date")
        return pd.DataFrame()

    return output


def get_greeks(
    current_price: float,
    chain: pd.DataFrame,
    expire: str,
    div_cont: float = 0,
    rf: Optional[float] = None,
) -> pd.DataFrame:
    """
    Gets the greeks for a given option

    Parameters
    ----------
    current_price: float
        The current price of the underlying
    chain: pd.DataFrame
        The dataframe with option chains
    div_cont: float
        The dividend continuous rate
    expire: str
        The date of expiration
    rf: float
        The risk-free rate

    Returns
    -------
    pd.DataFrame
        Dataframe with calculated option greeks

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> aapl_chain = openbb.stocks.options.chains("AAPL", source="Tradier")
    >>> aapl_last_price = openbb.stocks.options.last_price("AAPL")
    >>> greeks = openbb.stocks.options.greeks(aapl_last_price, aapl_chain, aapl_chain.iloc[0, 2])
    """

    chain = chain.rename(columns={"iv": "impliedVolatility"})
    chain_columns = chain.columns.tolist()
    if not all(
        col in chain_columns for col in ["strike", "impliedVolatility", "optionType"]
    ):
        if "delta" not in chain_columns:
            console.print(
                "[red]It's not possible to calculate the greeks without the following "
                "columns: `strike`, `impliedVolatility`, `optionType`.\n[/red]"
            )
        return pd.DataFrame()

    risk_free = rf if rf is not None else get_rf()
    expire_dt = datetime.strptime(expire, "%Y-%m-%d")
    dif = (expire_dt - datetime.now() + timedelta(hours=16)).total_seconds() / (
        60 * 60 * 24
    )
    strikes = []
    for _, row in chain.iterrows():
        vol = row["impliedVolatility"]
        is_call = row["optionType"] == "call"
        try:
            opt = Option(
                current_price, row["strike"], risk_free, div_cont, dif, vol, is_call
            )
            tmp = [
                opt.Delta(),
                opt.Gamma(),
                opt.Vega(),
                opt.Theta(),
                opt.Rho(),
                opt.Phi(),
                opt.Charm(),
                opt.Vanna(0.01),
                opt.Vomma(0.01),
            ]
        except ValueError:
            tmp = [np.nan] * 9
        result = [row[col] for col in row.index.tolist()]
        result += tmp

        strikes.append(result)

    greek_columns = [
        "Delta",
        "Gamma",
        "Vega",
        "Theta",
        "Rho",
        "Phi",
        "Charm",
        "Vanna",
        "Vomma",
    ]
    columns = chain_columns + greek_columns

    df = pd.DataFrame(strikes, columns=columns)

    return df


class OptionsChains(Options):  # pylint: disable=too-few-public-methods
    """OptionsChains class for loading and interacting with the Options data object.

    Parameters
    ----------
    symbol: str
        The ticker symbol to load the data for.
    source: str
        The source for the data. Defaults to "CBOE". ["CBOE", "Intrinio", "Nasdaq", "TMX", "Tradier", "YahooFinance"]
    date: str
        The date for EOD chains data.  Only available for "Intrinio" and "TMX".
    pydantic: bool
        Whether to return as a Pydantic Model or as a Pandas object.  Defaults to False.

    Returns
    -------
    OptionsChains
        chains: pd.DataFrame
            The complete options chain for the ticker. Returns as a dictionary if pydantic is True.
        expirations: list[str]
            List of unique expiration dates. (YYYY-MM-DD)
        strikes: list[float]
            List of unique strike prices.
        last_price: float
            The last price of the underlying asset.
        underlying_name: str
            The name of the underlying asset.
        underlying_price: pd.Series
            The price and recent performance of the underlying asset. Returns as a dictionary if pydantic is True.
        hasIV: bool
            Returns implied volatility.
        hasGreeks: bool
            Returns greeks data.
        symbol: str
            The symbol entered by the user.
        source: str
            The source of the data.
        date: str
            The date, when the chains data is historical EOD.
        SYMBOLS: pd.DataFrame
            The symbol directory for the source, when available. Returns as a dictionary if pydantic is True.

        Methods
        ---------
        chart_skew: Callable
            Function to chart the implied volatility skew.
        chart_stats: Callable
            Function to chart a variety of volume and open interest statistics.
        chart_surface: Callable
            Function to chart the volatility as a 3-D surface.
        chart_volatility: Callable
            Function to chart the implied volatility smile.
        get_skew: Callable
            Function to calculate horizontal and vertical skewness.
        get_stats: Callable
            Function to return a table of summary statistics, by strike or by expiration.
        get_straddle: Callable
            Function to calculate straddles and the payoff profile.
        get_strangle: Callable
            Function to calculate strangles and the payoff profile.
        get_synthetic_long: Callable
            Function to calculate a synthetic long position.
        get_synthetic_short: Callable
            Function to calculate a synthetic short position.
        get_vertical_call_spread: Callable
            Function to calculate vertical call spreads.
        get_vertical_put_spreads: Callable
            Function to calculate vertical put spreads.
        get_strategies: Callable
            Function for calculating multiple straddles and strangles at different expirations and moneyness.

    Examples
    ----------
    >>> from openbb_terminal.stocks.options.options_sdk_helper import OptionsChains
    >>> spy = OptionsChains("SPY")
    >>> spy.__dict__

    >>> spy.chains.query("`expiration` == spy.expirations[1]")

    >>> xiu = OptionsChains("xiu.to", "TMX")
    >>> xiu.get_straddle()
    """

    def __init__(self, symbol, source="CBOE", date="", pydantic=False):
        try:
            options = options_chains_model.load_options_chains(
                symbol, source, date, pydantic
            )
            items = list(options.__dict__.keys())
            for item in items:
                setattr(self, item, options.__dict__[item])
            if hasattr(self, "date") is False:
                setattr(self, "date", "")
        except Exception:
            self.chains = pd.DataFrame()

    def __repr__(self) -> str:
        return f"OptionsChains(symbol={self.symbol}, source={self.source})"

    def get_stats(self, by="expiration", query=None):
        """Calculates basic statistics for the options chains, like OI and Vol/OI ratios.

        Parameters
        ----------
        by: str
            Whether to calculate by strike or expiration.  Default is expiration.
        query: DataFrame
            Entry point to perform DataFrame operations on self.chains at the input stage.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame with the calculated statistics.

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> data = openbb.stocks.options.load_options_chains("SPY")

        By expiration date:
        >>> data.calculate_stats()

        By strike:
        >>> data.calculate_stats(data, "strike")

        Query:
        >>> data = OptionsChains("XIU", "TMX")
        >>> data.get_stats(query = data.chains.query("`openInterest` > 0"), by = "strike")
        """

        if query is not None:
            if isinstance(query, pd.DataFrame):
                return options_chains_model.calculate_stats(query, by)
            console.print("Query must be passed a Pandas DataFrame with chains data.")

        return options_chains_model.calculate_stats(self, by)

    def get_straddle(self, days=0, strike=0):
        """Calculates the cost of a straddle and its payoff profile. Use a negative strike price for short options.

        Parameters
        -----------
        days: int
            The target number of days until expiry. Default is 30 days.
        strike: float
            The target strike price. Enter a negative value for short options.
            Default is the last price of the underlying stock.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame with the results. Strike1 is the nearest call strike, strike2 is the nearest put strike.

        Examples
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> data = openbb.stocks.options.load_options_chains('SPY')
        >>> data.get_straddle()
        """

        return options_chains_model.calculate_straddle(self, days, strike)

    def get_strangle(self, days=0, moneyness=0):
        """Calculates the cost of a strangle and its payoff profile.
        Use a negative value for moneyness for short options.

        Parameters
        -----------
        days: int
            The target number of days until expiry.  Default is 30 days.
        moneyness: float
            The percentage of OTM moneyness, expressed as a percent between -100 < 0 < 100.
            Enter a negative number for short options.
            Default is 5.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame with the results.
            Strike 1 is the nearest call strike, and strike 2 is the nearest put strike.

        Examples
        --------
        >>> data = openbb.stocks.options.load_options_chains("SPY")
        >>> data.get_strangle()
        """

        return options_chains_model.calculate_strangle(self, days, moneyness)

    def get_synthetic_long(
        self,
        days: Optional[int] = 30,
        strike: float = 0,
    ) -> pd.DataFrame:
        """Calculates the cost of a synthetic long position at a given strike.
        It is expressed as the difference between a bought call and a sold put.
        Requires the Options data object.

        Parameters
        -----------
        days: int
            The target number of days until expiry. Default is 30 days.
        strike: float
            The target strike price. Default is the last price of the underlying stock.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame with the results. Strike1 is the purchased call strike, strike2 is the sold put strike.

        Example
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> data = openbb.stocks.options.load_options_chains('SPY')
        >>> data.get_synthetic_long()
        """
        return options_chains_model.calculate_synthetic_long(self, days, strike)

    def get_synthetic_short(
        self,
        days: Optional[int] = 30,
        strike: float = 0,
    ) -> pd.DataFrame:
        """Calculates the cost of a synthetic short position at a given strike.
        It is expressed as the difference between a sold call and a purchased put.
        Requires the Options data object.

        Parameters
        -----------
        days: int
            The target number of days until expiry. Default is 30 days.
        strike: float
            The target strike price. Default is the last price of the underlying stock.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame with the results. Strike1 is the sold call strike, strike2 is the purchased put strike.

        Example
        --------
        >>> from openbb_terminal.sdk import openbb
        >>> data = openbb.stocks.options.load_options_chains('SPY')
        >>> data.get_synthetic_short()
        """
        return options_chains_model.calculate_synthetic_short(self, days, strike)

    def get_vertical_call_spread(self, days=0, sold_strike=0, bought_strike=0):
        """Calculates the vertical call spread for the target DTE.
        A bull call spread is when the sold strike is above the bought strike.

        Parameters
        ----------
        days: int
            The target number of days until expiry. This value will be used to get the nearest valid DTE.
            Default is 30 days.
        sold_strike: float
            The target strike price for the short leg of the vertical call spread.
            Default is the 5% OTM above the last price of the underlying.
        bought_strike: float
            The target strike price for the long leg of the vertical call spread.
            Default is the last price of the underlying.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame with the results. Strike 1 is the sold strike, and strike 2 is the bought strike.

        Examples
        --------
        Load the data:
        >>> from openbb_terminal.sdk import openbb
        >>> data = openbb.stocks.options.load_options_chains("SPY")

        For a bull call spread:
        >>> data.get_vertical_call_spread(days=10, sold_strike=355, bought_strike=350)

        For a bear call spread:
        >>> data.get_vertical_call_spread(days=10, sold_strike=350, bought_strike=355)
        """

        return options_chains_model.calculate_vertical_call_spread(
            self, days, sold_strike, bought_strike
        )

    def get_vertical_put_spread(self, days=0, sold_strike=0, bought_strike=0):
        """Calculates the vertical put spread for the target DTE.
        A bear put spread is when the bought strike is above the sold strike.

        Parameters
        ----------
        days: int
            The target number of days until expiry. This value will be used to get the nearest valid DTE.
            Default is 30 days.
        sold_strike: float
            The target strike price for the short leg of the vertical put spread.
            Default is the last price of the underlying.
        bought_strike: float
            The target strike price for the long leg of the vertical put spread.
            Default is the 5% OTM above the last price of the underlying.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame with the results. Strike 1 is the sold strike, strike 2 is the bought strike.

        Examples
        --------
        Load the data:
        >>> from openbb_terminal.sdk import openbb
        >>> data = openbb.stocks.options.load_options_chains("QQQ")

        For a bull put spread:
        >>> data.get_vertical_put_spread(days=10, sold_strike=355, bought_strike=350)

        For a bear put spread:
        >>> data.get_vertical_put_spread(days=10, sold_strike=355, bought_strike=350)
        """

        return options_chains_model.calculate_vertical_put_spread(
            self, days, sold_strike, bought_strike
        )

    def get_strategies(
        self,
        days: Optional[list[int]] = None,
        straddle_strike: Optional[float] = None,
        strangle_moneyness: Optional[float] = None,
        synthetic_longs: Optional[list[float]] = None,
        synthetic_shorts: Optional[list[float]] = None,
        vertical_calls: Optional[list[float]] = None,
        vertical_puts: Optional[list[float]] = None,
    ):
        """Gets options strategies for all, or a list of, DTE(s).
        Currently supports straddles, strangles, and vertical spreads.
        Multiple strategies, expirations, and % moneyness can be returned.
        A negative value for `straddle_strike` or `strangle_moneyness` returns short options.
        A synthetic long/short position is a bought/sold call and sold/bought put at the same strike.
        A sold call strike that is lower than the bought strike,
        or a sold put strike that is higher than the bought strike,
        is a bearish vertical spread.

        Parameters
        ----------
        days: list[int]
            List of DTE(s) to get strategies for. Enter a single value, or multiple as a list. Defaults to all.
        strike_price: float
            The target strike price. Defaults to the last price of the underlying stock.
        strangle_moneyness: list[float]
            List of OTM moneyness to target, expressed as a percent value between 0 and 100.
            Enter a single value, or multiple as a list. Defaults to 5.
        synthetic_long: list[float]
            List of strikes for a synthetic long position.
        synthetic_short: list[float]
            List of strikes for a synthetic short position.
        vertical_calls: list[float]
            Call strikes for vertical spreads, listed as [sold strike, bought strike].
        vertical_puts: list[float]
            Put strikes for vertical spreads, listed as [sold strike, bought strike].

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame with the results.

        Examples
        --------
        Load data
        >>> from openbb_terminal.sdk import openbb
        >>> data = openbb.stocks.options.load_options_chains("SPY")

        Return just long straddles for every expiry.
        >>> data.get_strategies()

        Return strangles for every expiry.
        >>> data.get_strategies(strangle_moneyness = [2.5,5,10])

        Return multiple values for both moneness and days:
        >>> data.get_strategies(days = [10,30,60,90], moneyness = [2.5,-5,10,-20])

        Return vertical spreads for all expirations.
        >>> data.get_strategies(vertical_calls=[430,427], vertical_puts=[420,426])

        Return synthetic short and long positions:
        >>> data.get_strategies(days = [30,60], synthetic_short = [450,445], synthetic_long = [450,455])
        """

        if strangle_moneyness is None:
            strangle_moneyness = 0

        return options_chains_model.get_strategies(
            self,
            days,
            straddle_strike,
            strangle_moneyness,
            synthetic_longs,
            synthetic_shorts,
            vertical_calls,
            vertical_puts,
        )

    def get_skew(
        self, expiration: Optional[str] = "", moneyness: Optional[float] = None
    ):
        """
        Returns the skewness of the options, either vertical or horizontal.

        The vertical skew for each expiry and option is calculated by subtracting the IV of the ATM call or put.
        Returns only where the IV is greater than 0.

        Horizontal skew is returned if a value for moneyness is supplied.
        It is expressed as the difference between skews of two equidistant OTM strikes (the closest call and put).

        Parameters
        -----------
        expiration: str
            The expiration date to target.  Defaults to all.
        moneyness: float
            The moneyness to target for calculating horizontal skew.  This parameter overrides a defined expiration date.

        Returns
        --------
        pd.DataFrame
            Pandas DataFrame with the results.

        Examples
        ----------
        >>> from openbb_terminal.sdk import openbb
        >>> data = openbb.stocks.options.load_options_chains("SPY")

        Vertical skew at a given expiry:
        >>> skew = data.get_skew("2025-12-19")

        Vertical skew at all expirations:
        >>> skew = data.get_skew()

        Horizontal skew at a given % OTM:
        >>> skew = data.get_skew(moneyness = 10)
        """
        return options_chains_model.calculate_skew(self, expiration, moneyness)

    def chart_stats(
        self,
        by: str = "expiration",
        expiry: str = "",
        oi: Optional[bool] = False,
        percent: Optional[bool] = True,
        ratios: Optional[bool] = False,
        raw: bool = False,
        export: str = "",
        sheet_name: Optional[str] = "",
        external_axes: bool = False,
    ) -> Union[None, OpenBBFigure]:
        """Chart a variety of volume and open interest statistics.

        Parameters
        -----------
        by: str
            Statistics can be displayed by either "expiration" or "strike". Default is "expiration".
        expiry: str
            The target expiration date to display. Only valid when `percent` is False.
        oi: bool
            Display open interest if True, else volume. Default is False.
        percent: bool
            Displays volume or open interest as a percentage of the total across all expirations. Default is False.
        ratios: bool
            Displays Put/Call ratios. This parameter overrides the others when True. Default is False.
        raw: bool
            Displays the raw data table instead of a chart.
        export: str
            Export the data to a csv,json,xlsx file.
        sheet_name: str
            Name of the sheet to save the data to. Only valid when `export` is a `xlsx` file.
        external_axes: bool
            Return the OpenBB Figure Object to a variable.

        Examples
        ----------
        >>> from openbb_terminal.sdk import openbb
        >>> spy = options_chains_model.load_options_chains("SPY")

        Display volume by expiration:
        >>> spy.chart_stats()

        Display volume by strike:
        >>> spy.chart_stats("strike")

        Display open interest by expiration:
        >>> spy.chart_stats(oi=True)

        Display open interest, by expiration, as a percentage of the total:
        >>> spy.chart_stats(oi=True, percent=True)

        Display volume and open interest put/call ratios:
        >>> spy.chart_stats(ratios=True)
        """
        return options_chains_view.display_stats(
            self,
            by,
            expiry,
            oi,
            percent,
            ratios,
            raw,
            export,
            sheet_name,
            external_axes,
        )

    def chart_surface(
        self,
        option_type: str = "otm",
        dte_range: Optional[list[int]] = None,
        strike_range: Optional[list[float]] = None,
        moneyness: Optional[float] = None,
        oi: bool = False,
        volume: bool = False,
        raw: bool = False,
        export: str = "",
        sheet_name: Optional[str] = "",
        external_axes: bool = False,
    ) -> Union[None, OpenBBFigure]:
        """Chart the volatility as a 3-D surface.

        Parameters
        -----------
        option_type: str
            The type of data to display. Default is "otm".
            Choices are: ["otm", "itm", "puts", "calls"]
        dte_range: list[int]
            Specify a min/max range of DTE to display.
        moneyness: float
            Specify a % moneyness to target for display.
        strike_range: list[float]
            Specify a min/max range of strike prices to display.
        oi: bool
            Filter for only options that have open interest. Default is False.
        volume: bool
            Filter for only options that have trading volume. Default is False.
        raw: bool
            Display the raw data instead of the chart.
        export: str
            Export dataframe data to csv,json,xlsx file.
        external_axes: bool
            Return the OpenBB Figure Object to a variable.

        Examples
        ----------
        >>> from openbb_terminal.sdk import openbb
        >>> spy = openbb.stocks.options.load_options_chains("SPY")
        >>> spy.chart_surface()

        Display only calls:
        >>> spy.chart_surface("calls")

        Display only puts:
        >>> spy.chart_surface("puts")

        Display a range of expirations:
        >>> spy.chart_surface(dte_range=[7, 60])

        Filter for a range of strike prices and include only those with open interest and trading volume:
        >>> spy.chart_surface(strike_range=[400, 500], oi=True, volume=True)
        """
        return options_chains_view.display_surface(
            self,
            option_type,
            dte_range,
            moneyness,
            strike_range,
            oi,
            volume,
            raw,
            export,
            sheet_name,
            external_axes,
        )

    def chart_skew(
        self,
        expirations: Optional[list[str]] = None,
        moneyness: Optional[float] = None,
        strike: Optional[float] = None,
        atm: Optional[bool] = False,
        otm_only: Optional[bool] = False,
        raw: Optional[bool] = False,
        export: Optional[str] = "",
        sheet_name: Optional[str] = "",
        external_axes: Optional[bool] = False,
    ) -> Union[None, OpenBBFigure]:
        """Chart the vertical skew of an option expiration, or the horizontal skew of equidistant % moneyness options.

        The vertical skew for each expiry and option is calculated by subtracting the IV of the ATM call or put.
        Returns only where the IV is greater than 0.

        Horizontal skew is returned if a value for moneyness, or a strike price, is supplied.
        With a strike price specified, both call and put IV skew are displayed. For moneyness,
        it is expressed as the difference between skews of two equidistant OTM strikes (the closest call and put).

        Parameters
        -----------
        expirations: list[str]
            The expiration date, or a list of dates. The closest date will be returned for each entry.
            Format as YYYY-MM-DD.
        moneyness: float
            The % moneyess. When specified, this returns the forward skew curve at the target moneyness.
        strike: float
            A target strike price to observe the skew vs. contract. This argument overrides other parameters.
        atm: bool
            When true, returns the ATM skew curve. This will override other parameters, but is overridden by strike.
        otm_only: bool
            When true, returns only OTM portions of the put/call skew curves.
        raw: bool
            Returns a table instead of a plot.
        export: str
            Export the data to csv, json, xlsx file.
        sheet_name: str
            The name of the sheet to save the data to. Only valid when `export` is a `xlsx` file.
        external_axes: bool
            Returns the OpenBB Figure Object to a variable.

        Examples
        ----------
        >>> from openbb_terminal.sdk import openbb
        >>> spy = openbb.stocks.options.load_options_chains("SPY")

        >>> spy.chart_skew()

        Display only OTM IV:
        >>> spy.chart_skew(otm_only=True)

        Display more than one chain:
        >>> spy.chart_skew(expirations=spy.expirations[1:5])

        When otm_only is True, and there is more than one expiration, calls and puts share a colour.
        >>> spy.chart_skew(expirations=spy.expirations[1:11], otm_only=True)
        """
        return options_chains_view.display_skew(
            self,
            expirations,
            moneyness,
            strike,
            atm,
            otm_only,
            raw,
            export,
            sheet_name,
            external_axes,
        )

    def chart_volatility(
        self,
        expirations: Optional[list[str]] = None,
        moneyness: Optional[float] = None,
        strike: Optional[float] = None,
        oi: bool = False,
        volume: bool = False,
        raw: bool = False,
        export: str = "",
        sheet_name: Optional[str] = "",
        external_axes: bool = False,
    ) -> Union[None, OpenBBFigure]:
        """Chart the implied volatility smile.

        Parameters
        -----------
        expirations: list[str]
            Select up to five expiration(s) to display.  Overridden by moneyness or strike. Format as YYYY-MM-DD.
        moneyness: float
            Specify a target % moneyness to display vs. contract dates. This argument overrides expirations.
        strike: float
            Specify a target strike price to display vs. contract dates.
            Returned strike price is estimated as the closest one listed at approximately one year forward.
            This argument overrides moneyness and expirations.
        oi: bool
            Return only contracts with open interest. Only valid for IV vs. Strike charts. Default is False.
        volume: bool
            Return only contracts with trading volume. Only valid for IV vs. Strike charts. Default is False.
        raw: bool
            Display the raw data instead of the chart.
        export: str
            Export dataframe data to csv,json,xlsx file.
        external_axes: bool
            Return the OpenBB Figure Object to a variable.

        Examples
        ----------
        >>> from openbb_terminal.sdk import openbb
        >>> spy = openbb.stocks.options.load_options_chains("SPY")
        >>> spy.chart_volatility()

        Plot IV @ Strike vs. contract dates:
        >>> spy.chart_volatility(strike=450)

        Plot IV @ % OTM vs. contract dates:
        >>> spy.chart_volatility(moneyness=20)

        Plot multiple expirations at once, and filter for only contracts with open interest:
        >>> spy.chart_volatility(expirations=["2024-12-30", "2025-12-30"], oi=True)
        """
        return options_chains_view.display_volatility(
            self,
            expirations,
            moneyness,
            strike,
            oi,
            volume,
            raw,
            export,
            sheet_name,
            external_axes,
        )


@log_start_end(log=logger)
def load_options_chains(
    symbol: str, source: str = "CBOE", date: str = "", pydantic: bool = False
) -> OptionsChains:
    """Loads all options chains from a specific source, fields returned to each attribute will vary.

    Parameters
    -----------
    symbol: str
        The ticker symbol to load the data for.
    source: str
        The source for the data. Defaults to "CBOE". ["CBOE", "Intrinio", "Nasdaq", "TMX", "Tradier", "YahooFinance"]
    date: str
        The date for EOD chains data.  Only available for "Intrinio" and "TMX".
    pydantic: bool
        Whether to return as a Pydantic Model or as a Pandas object.  Defaults to False.

    Returns
    ------
    Class: OptionsChains
        chains: pd.DataFrame
            The complete options chain for the ticker. Returns as a dictionary if pydantic is True.
        expirations: list[str]
            List of unique expiration dates. (YYYY-MM-DD)
        strikes: list[float]
            List of unique strike prices.
        last_price: float
            The last price of the underlying asset.
        underlying_name: str
            The name of the underlying asset.
        underlying_price: pd.Series
            The price and recent performance of the underlying asset. Returns as a dictionary if pydantic is True.
        hasIV: bool
            Returns implied volatility.
        hasGreeks: bool
            Returns greeks data.
        symbol: str
            The symbol entered by the user.
        source: str
            The source of the data.
        date: str
            The date, when the chains data is historical EOD.
        SYMBOLS: pd.DataFrame
            The symbol directory for the source, when available. Returns as a dictionary if pydantic is True.

        Methods
        ------
        chart_skew: Callable
            Function to chart the implied volatility skew.
        chart_stats: Callable
            Function to chart a variety of volume and open interest statistics.
        chart_surface: Callable
            Function to chart the volatility as a 3-D surface.
        chart_volatility: Callable
            Function to chart the implied volatility smile.
        get_skew: Callable
            Function to calculate horizontal and vertical skewness.
        get_stats: Callable
            Function to return a table of summary statistics, by strike or by expiration.
        get_straddle: Callable
            Function to calculate straddles and the payoff profile.
        get_strangle: Callable
            Function to calculate strangles and the payoff profile.
        get_synthetic_long: Callable
            Function to calculate a synthetic long position.
        get_synthetic_short: Callable
            Function to calculate a synthetic short position.
        get_vertical_call_spread: Callable
            Function to calculate vertical call spreads.
        get_vertical_put_spreads: Callable
            Function to calculate vertical put spreads.
        get_strategies: Callable
            Function for calculating multiple straddles and strangles at different expirations and moneyness.

    Examples
    ------
    Loads SPY data from CBOE, returns as a Pydantic Model, and displays the longest-dated expiration chain.

    >>> from openbb_terminal.sdk import openbb
    >>> import pandas as pd
    >>> data = openbb.stocks.options.load_options_chains("SPY", pydantic = True)
    >>> chains = pd.DataFrame(data.chains)
    >>> chains[chains["expiration"] == data.expirations[-1]]

    Loads QQQ data from Tradier as a Pydantic Model.

    >>> from openbb_terminal.sdk import openbb
    >>> data = openbb.stocks.options.load_options_chains("QQQ", source = "Tradier", pydantic = True)

    Loads VIX data from YahooFinance as a Pandas object.

    >>> from openbb_terminal.sdk import openbb
    >>> data = openbb.stocks.options.load_options_chains("^VIX", source = "YahooFinance")

    Loads XIU data from TMX and displays the 25 highest open interest options.

    >>> from openbb_terminal.sdk  import openbb
    >>> data = openbb.stocks.options.load_options_chains("XIU", "TMX")
    >>> data.chains.sort_values("openInterest", ascending=False).head(25)

    Loads the EOD chains data for XIU.TO from March 15, 2020, sorted by number of transactions.

    >>> from openbb_terminal.sdk  import openbb
    >>> data = openbb.stocks.options.load_options_chains("XIU.TO", "TMX", "2020-03-15")
    >>> data.chains.sort_values("transactions", ascending=False).head(25)
    """
    return OptionsChains(symbol, source, date, pydantic)
