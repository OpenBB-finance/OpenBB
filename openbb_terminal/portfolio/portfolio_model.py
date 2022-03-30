"""Portfolio Model"""
__docformat__ = "numpy"

import os
from datetime import timedelta, datetime
from typing import Dict, List, Union
import logging

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS
import yfinance as yf
from pycoingecko import CoinGeckoAPI

from openbb_terminal.portfolio import (
    portfolio_helper,
)
from openbb_terminal.rich_config import console
from openbb_terminal.decorators import log_start_end

# pylint: disable=E1136,W0201,R0902
# pylint: disable=unsupported-assignment-operation
logger = logging.getLogger(__name__)
cg = CoinGeckoAPI()


@log_start_end(log=logger)
def save_df(df: pd.DataFrame, name: str) -> None:
    """Saves the portfolio as a csv

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to be saved
    name : str
        The name of the string
    """
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.abspath(os.path.join(path, "portfolios", name))
    if ".csv" in name:
        df.to_csv(path, index=False)
    elif ".json" in name:
        df.to_json(path, index=False)
    elif ".xlsx" in name:
        df.to_excel(path, index=False, engine="openpyxl")


@log_start_end(log=logger)
def get_rolling_beta(
    df: pd.DataFrame, hist: pd.DataFrame, mark: pd.DataFrame, n: pd.DataFrame
) -> pd.DataFrame:
    """Turns a holdings portfolio into a rolling beta dataframe

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe of daily holdings
    hist : pd.DataFrame
        A dataframe of historical returns
    mark : pd.DataFrame
        The dataframe of market performance
    n : int
        The period to get returns for

    Returns
    ----------
    final : pd.DataFrame
        Dataframe with rolling beta
    """
    df = df["Holding"]
    uniques = df.columns.tolist()
    res = df.div(df.sum(axis=1), axis=0)
    res = res.fillna(0)
    comb = pd.merge(
        hist["Close"], mark["Market"], how="outer", left_index=True, right_index=True
    )
    comb = comb.fillna(method="ffill")
    for col in hist["Close"].columns:
        exog = sm.add_constant(comb["Close"])
        rols = RollingOLS(comb[col], exog, window=252)
        rres = rols.fit()
        res[f"beta_{col}"] = rres.params["Close"]
    final = res.fillna(method="ffill")
    for uni in uniques:
        final[f"prod_{uni}"] = final[uni] * final[f"beta_{uni}"]
    dropped = final[[f"beta_{x}" for x in uniques]].copy()
    final = final.drop(columns=[f"beta_{x}" for x in uniques] + uniques)
    final["total"] = final.sum(axis=1)
    final = final[final.index >= datetime.now() - timedelta(days=n + 1)]
    comb = pd.merge(final, dropped, how="left", left_index=True, right_index=True)
    return comb


@log_start_end(log=logger)
def get_main_text(df: pd.DataFrame) -> str:
    """Get main performance summary from a dataframe with returns

    Parameters
    ----------
    df : pd.DataFrame
        Stock holdings and returns with market returns

    Returns
    ----------
    t : str
        The main summary of performance
    """
    d_debt = np.where(df[("Cash", "Cash")] > 0, 0, 1)
    bcash = 0 if df[("Cash", "Cash")][0] > 0 else abs(df[("Cash", "Cash")][0])
    ecash = 0 if df[("Cash", "Cash")][-1] > 0 else abs(df[("Cash", "Cash")][-1])
    bdte = bcash / (df["holdings"][0] - bcash)
    edte = ecash / (df["holdings"][-1] - ecash)
    if sum(d_debt) > 0:
        t_debt = (
            f"Beginning debt to equity was {bdte:.2%} and ending debt to equity was"
            f" {edte:.2%}. Debt adds risk to a portfolio by amplifying the gains and losses when"
            " equities change in value."
        )
        if bdte > 1 or edte > 1:
            t_debt += " Debt to equity ratios above one represent a significant amount of risk."
    else:
        t_debt = (
            "Margin was not used this year. This reduces this risk of the portfolio."
        )
    text = (
        f"Your portfolio's performance for the period was {df['return'][-1]:.2%}. This was"
        f" {'greater' if df['return'][-1] > df[('Market', 'Return')][-1] else 'less'} than"
        f" the market return of {df[('Market', 'Return')][-1]:.2%}. The variance for the"
        f" portfolio is {np.var(df['return']):.2%}, while the variance for the market was"
        f" {np.var(df[('Market', 'Return')]):.2%}. {t_debt} The following report details"
        f" various analytics from the portfolio. Read below to see the moving beta for a"
        f" stock."
    )
    return text


@log_start_end(log=logger)
def get_beta_text(df: pd.DataFrame) -> str:
    """Get beta summary for a dataframe

    Parameters
    ----------
    df : pd.DataFrame
        The beta history of the stock

    Returns
    ----------
    t : str
        The beta history for a ticker
    """
    betas = df[list(filter(lambda score: "beta" in score, list(df.columns)))]
    high = betas.idxmax(axis=1)
    low = betas.idxmin(axis=1)
    text = (
        "Beta is how strongly a portfolio's movements correlate with the market's movements."
        " A stock with a high beta is considered to be riskier. The beginning beta for the period"
        f" was {portfolio_helper.beta_word(df['total'][0])} at {df['total'][0]:.2f}. This went"
        f" {'up' if df['total'][-1] > df['total'][0] else 'down'} to"
        f" {portfolio_helper.beta_word(df['total'][-1])} at {df['total'][-1]:.2f} by the end"
        f" of the period. The ending beta was pulled {'up' if df['total'][-1] > 1 else 'down'} by"
        f" {portfolio_helper.clean_name(high[-1] if df['total'][-1] > 1 else low[-1])}, which had"
        f" an ending beta of {df[high[-1]][-1] if df['total'][-1] > 1 else df[low[-1]][-1]:.2f}."
    )
    return text


performance_text = (
    "The Sharpe ratio is a measure of reward to total volatility. A Sharpe ratio above one is"
    " considered acceptable. The Treynor ratio is a measure of systematic risk to reward."
    " Alpha is the average return above what CAPM predicts. This measure should be above zero"
    ". The information ratio is the excess return on systematic risk. An information ratio of"
    " 0.4 to 0.6 is considered good."
)


@log_start_end(log=logger)
def calculate_drawdown(input_series: pd.Series, is_returns: bool = False) -> pd.Series:
    """Calculate the drawdown (MDD) of historical series.  Note that the calculation is done
     on cumulative returns (or prices).  The definition of drawdown is

     DD = (current value - rolling maximum) / rolling maximum

    Parameters
    ----------
    input_series: pd.DataFrame
        Dataframe of input values
    is_returns: bool
        Flag to indicate inputs are returns

    Returns
    pd.Series
        Drawdown series
    -------
    """
    if is_returns:
        input_series = (1 + input_series).cumprod()
    rolling_max = input_series.cummax()
    drawdown = (input_series - rolling_max) / rolling_max
    return drawdown


class Portfolio:
    """
    Class for portfolio analysis in GST

    Attributes
    -------
    portfolio_value: pd.Series
        Series containing value at each day
    returns: pd.Series
        Series containing daily returns
    ItemizedReturns: pd.DataFrame
        Dataframe of Holdings by class
    portfolio: pd.DataFrame
        Dataframe containing all relevant holdings data

    Methods
    -------
    add_trade:
        Adds a trade to the dataframe of trades
    generate_holdings_from_trades:
        Takes a list of trades and converts to holdings on each day
    get_yahoo_close_prices:
        Gets close prices or adj close prices from yfinance
    add_benchmark
        Adds a benchmark to the class

    """

    @log_start_end(log=logger)
    def __init__(self, trades: pd.DataFrame = pd.DataFrame(), rf=0):
        """Initialize Portfolio class"""
        # Allow for empty initialization
        self.empty = True
        self.rf = rf
        if not trades.empty:
            if "cash" not in trades.Name.to_list():
                logger.warning(
                    "No initial cash deposit. Calculations may be off as this assumes trading from a "
                    "funded account"
                )
                console.print(
                    "[red]No initial cash deposit. Calculations may be off as this assumes trading from a "
                    "funded account[/red]."
                )
            # Load in trades df and do some quick editing
            trades.Name = trades.Name.map(lambda x: x.upper())
            trades["Side"] = trades["Side"].map(
                lambda x: 1
                if x.lower() in ["deposit", "buy"]
                else (-1 if x.lower() == "sell" else 0)
            )
            trades["Value"] = trades.Quantity * trades.Price * trades.Side
            # Make selling negative for cumulative sum of quantity later
            trades["Quantity"] = trades["Quantity"] * trades["Side"]
            # Should be simply extended for crypto/bonds etc
            # Treat etf as stock for yfinance historical.
            self._stock_tickers = list(
                set(trades[trades.Type == "stock"].Name.to_list())
            )

            self._etf_tickers = list(set(trades[trades.Type == "etf"].Name.to_list()))

            self._crypto_tickers = list(
                set(trades[trades.Type == "crypto"].Name.to_list())
            )
            self._start_date = trades.Date[0]
            # Copy pandas notation
            self.empty = False
        self.trades = trades
        self.portfolio = pd.DataFrame()

    @log_start_end(log=logger)
    def add_trade(self, trade_info: Dict):
        self.trades = self.trades.append([trade_info])
        self.empty = False

    @log_start_end(log=logger)
    def add_rf(self, risk_free_rate: float):
        """Sets the risk free rate for calculation purposes"""
        self.rf = risk_free_rate

    @log_start_end(log=logger)
    def generate_holdings_from_trades(self, yfinance_use_close: bool = False):
        """Generates portfolio data from list of trades"""
        # Load historical prices from yahoo (option to get close instead of adj close)
        self.get_yahoo_close_prices(use_close=yfinance_use_close)
        self.get_crypto_yfinance()

        # Pivot list of trades on Name.  This will give a multi-index df where the multiindex are the individual ticker
        # and the values from the table
        portfolio = self.trades.pivot(
            index="Date",
            columns="Name",
            values=["Quantity", "Price", "Fees", "Premium", "Side", "Value"],
        )
        # Merge with historical close prices (and fillna)
        portfolio = pd.merge(
            portfolio,
            self._historical_prices,
            how="right",
            left_index=True,
            right_index=True,
        ).fillna(0)

        is_there_stock_or_etf = self._stock_tickers + self._etf_tickers

        # Merge with crypto
        if self._crypto_tickers:
            portfolio = pd.merge(
                portfolio,
                self._historical_crypto,
                how="left" if is_there_stock_or_etf else "right",
                left_index=True,
                right_index=True,
            ).fillna(0)
        else:
            portfolio[pd.MultiIndex.from_product([["Close"], ["crypto"]])] = 0

        # Add cumulative Quantity held
        portfolio["Quantity"] = portfolio["Quantity"].cumsum()

        # Add holdings for each 'type'.  Will check for tickers matching type.

        if self._stock_tickers:
            # Find end of day holdings for each stock
            portfolio[
                pd.MultiIndex.from_product([["StockHoldings"], self._stock_tickers])
            ] = (
                portfolio["Quantity"][self._stock_tickers]
                * portfolio["Close"][self._stock_tickers]
            )
        else:
            portfolio[pd.MultiIndex.from_product([["StockHoldings"], ["temp"]])] = 0

        if self._etf_tickers:
            # Find end of day holdings for each ETF
            portfolio[
                pd.MultiIndex.from_product([["ETFHoldings"], self._etf_tickers])
            ] = (
                portfolio["Quantity"][self._etf_tickers]
                * portfolio["Close"][self._etf_tickers]
            )
        else:
            portfolio[pd.MultiIndex.from_product([["ETFHoldings"], ["temp"]])] = 0
        if self._crypto_tickers:
            # Find end of day holdings for each stock
            portfolio[
                pd.MultiIndex.from_product([["CryptoHoldings"], self._crypto_tickers])
            ] = (
                portfolio["Quantity"][self._crypto_tickers]
                * portfolio["Close"][self._crypto_tickers]
            )
        else:
            portfolio[pd.MultiIndex.from_product([["CryptoHoldings"], ["temp"]])] = 0

        # Find amount of cash held in account.  Defined as deposited cash - stocks bought + stocks sold
        portfolio["CashHold"] = portfolio["Value"]["CASH"] - portfolio["Value"][
            self._stock_tickers + self._etf_tickers + self._crypto_tickers
        ].sum(axis=1)

        # Subtract Fees or Premiums from cash holdings
        portfolio["CashHold"] = (
            portfolio["CashHold"]
            - portfolio["Fees"].sum(axis=1)
            - portfolio["Premium"].sum(axis=1)
        )
        portfolio["CashHold"] = portfolio["CashHold"].cumsum()

        portfolio["TotalHoldings"] = (
            portfolio["CashHold"]
            + portfolio["StockHoldings"].sum(axis=1)
            + portfolio["ETFHoldings"].sum(axis=1)
            + portfolio["CryptoHoldings"].sum(axis=1)
        )

        self.portfolio_value = portfolio["TotalHoldings"]
        self.returns = portfolio["TotalHoldings"].pct_change().dropna()
        self.ItemizedHoldings = pd.DataFrame(
            {
                "Stocks": portfolio["StockHoldings"][self._stock_tickers].sum(axis=1),
                "ETFs": portfolio["ETFHoldings"][self._etf_tickers].sum(axis=1),
                "Crypto": portfolio["CryptoHoldings"][self._crypto_tickers].sum(axis=1),
                "Cash": portfolio["CashHold"],
            }
        )
        self.portfolio = portfolio.copy()

    # TODO: Add back dividends
    @log_start_end(log=logger)
    def get_yahoo_close_prices(self, use_close: bool = False):
        """Gets historical adj close prices for tickers in list of trades"""
        tickers_to_download = self._stock_tickers + self._etf_tickers
        if tickers_to_download:
            if not use_close:
                self._historical_prices = yf.download(
                    tickers_to_download, start=self._start_date, progress=False
                )["Adj Close"]
            else:
                self._historical_prices = yf.download(
                    tickers_to_download, start=self._start_date, progress=False
                )["Close"]

            # Adjust for case of only 1 ticker
            if len(tickers_to_download) == 1:
                self._historical_prices = pd.DataFrame(self._historical_prices)
                self._historical_prices.columns = tickers_to_download

        else:
            data_for_index_purposes = yf.download(
                "AAPL", start=self._start_date, progress=False
            )["Adj Close"]
            self._historical_prices = pd.DataFrame()
            self._historical_prices.index = data_for_index_purposes.index
            self._historical_prices["stock"] = 0

        self._historical_prices["CASH"] = 1

        # Make columns a multi-index.  This helps the merging.
        self._historical_prices.columns = pd.MultiIndex.from_product(
            [["Close"], self._historical_prices.columns]
        )

    @log_start_end(log=logger)
    def get_crypto_yfinance(self):
        """Gets historical coin data from coingecko"""
        if self._crypto_tickers:
            list_of_coins = [f"{coin}-USD" for coin in self._crypto_tickers]
            self._historical_crypto = yf.download(
                list_of_coins, start=self._start_date, progress=False
            )["Close"]

            if len(list_of_coins) == 1:
                self._historical_crypto = pd.DataFrame(self._historical_crypto)
                self._historical_crypto.columns = list_of_coins

            self._historical_crypto.columns = pd.MultiIndex.from_product(
                [["Close"], [col[:-4] for col in self._historical_crypto.columns]]
            )

        else:
            self._historical_crypto = pd.DataFrame()
            self._historical_crypto[
                pd.MultiIndex.from_product([["Close"], ["crypto"]])
            ] = 0

    @log_start_end(log=logger)
    def add_benchmark(self, benchmark: str):
        """Adds benchmark dataframe"""
        self.benchmark = yf.download(benchmark, start=self._start_date, progress=False)[
            "Adj Close"
        ]
        self.benchmark_returns = self.benchmark.pct_change().dropna()

    # pylint:disable=no-member
    @classmethod
    @log_start_end(log=logger)
    def from_csv(cls, csv_path: str):
        """Class method that generates a portfolio object from a csv file

        Parameters
        ----------
        csv_path: str
            Path to csv of trade data

        Returns
        -------
        Portfolio
            Initialized portfolio object
        """
        # Load in a list of trades
        trades = pd.read_csv(csv_path)
        # Convert the date to what pandas understands
        trades.Date = pd.to_datetime(trades.Date)
        # Sort by date to make more sense of trades
        trades = trades.sort_values(by="Date")
        # Build the portfolio object
        return cls(trades)

    # pylint:enable=no-member
    @classmethod
    @log_start_end(log=logger)
    def from_custom_inputs_and_weights(
        cls,
        start_date: str,
        list_of_symbols: List[str],
        list_of_weights: List[float],
        list_of_types: List[str],
        amount: float = 100_000,
    ):
        """Create a class instance from supplied weights and tickers.
        This first will generate a dataframe of trades then pass to generator.

        Parameters
        ----------
        start_date: str
            Start date
        list_of_symbols: List[str]
            List of symbols to consider
        list_of_weights: List[float]
            List of weights (in theory negative should be fine),  Must add to 1
        list_of_types: List[str]
            List of asset type (stock or crypto)
        amount: float
            Amount for portfolio allocation

        Returns
        -------
        Portfolio
            Class instance
        """
        if not np.isclose(np.sum(list_of_weights), 1, 0.03):
            logger.error("Weights do not add to 1")
            console.print("[red]Weights do not add to 1[/red].")
            return cls()
        list_of_amounts = [weight * amount for weight in list_of_weights]
        # Name,Type,Quantity,Date,Price,Fees,Premium,Side
        inputs: Dict[str, List[Union[str, float, int]]] = {}
        inputs["Name"] = ["cash"]
        inputs["Type"] = ["cash"]
        inputs["Quantity"] = [1]
        inputs["Price"] = [amount]
        inputs["Fees"] = [0]
        inputs["Premium"] = [0]
        inputs["Side"] = ["deposit"]
        inputs["Date"] = [start_date]
        for ticker, type_, amounts in zip(
            list_of_symbols, list_of_types, list_of_amounts
        ):
            inputs["Name"].append(ticker)
            inputs["Type"].append(type_)
            inputs["Fees"].append(0)
            inputs["Premium"].append(0)
            inputs["Side"].append("buy")
            if type_ == "crypto":
                ticker += "-USD"
            # Find how much of each ticker we can buy
            temp = yf.download(ticker, start=start_date, progress=False)["Adj Close"]
            price_on_date = temp[0]
            inputs["Date"].append(temp.index[0].strftime("%Y-%m-%d"))
            inputs["Quantity"].append(amounts / price_on_date)
            inputs["Price"].append(price_on_date)
        trades = pd.DataFrame.from_dict(inputs)
        trades.Date = pd.to_datetime(trades.Date)
        # Make sure to fix the 'cash' date if it is weekend
        if trades.Date[1] != trades.Date[0]:
            trades.Date[0] = trades.Date[1]
        return cls(trades)
