"""Portfolio Model"""
__docformat__ = "numpy"

import logging
from datetime import timedelta, datetime

import numpy as np
import scipy
import pandas as pd
import statsmodels.api as sm
import yfinance as yf
from sklearn.metrics import r2_score
from pycoingecko import CoinGeckoAPI
from statsmodels.regression.rolling import RollingOLS

from openbb_terminal.decorators import log_start_end
from openbb_terminal.portfolio import portfolio_helper, allocation_model
from openbb_terminal.rich_config import console

# pylint: disable=E1136,W0201,R0902
# pylint: disable=unsupported-assignment-operation
logger = logging.getLogger(__name__)
cg = CoinGeckoAPI()

pd.options.mode.chained_assignment = None


# CHECK OUT WHAT TO DO WITH THIS
# @log_start_end(log=logger)
# def get_rolling_beta(
#     df: pd.DataFrame, hist: pd.DataFrame, mark: pd.DataFrame, n: pd.DataFrame
# ) -> pd.DataFrame:
#     """Turns the holdings of a portfolio into a rolling beta dataframe

#     Parameters
#     ----------
#     df : pd.DataFrame
#         The dataframe of daily holdings
#     hist : pd.DataFrame
#         A dataframe of historical returns
#     mark : pd.DataFrame
#         The dataframe of market performance
#     n : int
#         The period to get returns for

#     Returns
#     ----------
#     final : pd.DataFrame
#         A Dataframe with rolling beta
#     """
#     df = df["Holding"]
#     uniques = df.columns.tolist()
#     res = df.div(df.sum(axis=1), axis=0)
#     res = res.fillna(0)
#     comb = pd.merge(
#         hist["Close"], mark["Market"], how="outer", left_index=True, right_index=True
#     )
#     comb = comb.fillna(method="ffill")
#     for col in hist["Close"].columns:
#         exog = sm.add_constant(comb["Close"])
#         rols = RollingOLS(comb[col], exog, window=252)
#         rres = rols.fit()
#         res[f"beta_{col}"] = rres.params["Close"]
#     final = res.fillna(method="ffill")
#     for uni in uniques:
#         final[f"prod_{uni}"] = final[uni] * final[f"beta_{uni}"]
#     dropped = final[[f"beta_{x}" for x in uniques]].copy()
#     final = final.drop(columns=[f"beta_{x}" for x in uniques] + uniques)
#     final["total"] = final.sum(axis=1)
#     final = final[final.index >= datetime.now() - timedelta(days=n + 1)]
#     comb = pd.merge(final, dropped, how="left", left_index=True, right_index=True)
#     return comb


# @log_start_end(log=logger)
# def get_main_text(df: pd.DataFrame) -> str:
#     """Get main performance summary from a dataframe with returns

#     Parameters
#     ----------
#     df : pd.DataFrame
#         Stock holdings and returns with market returns

#     Returns
#     ----------
#     t : str
#         The main summary of performance
#     """
#     d_debt = np.where(df[("Cash", "Cash")] > 0, 0, 1)
#     bcash = 0 if df[("Cash", "Cash")][0] > 0 else abs(df[("Cash", "Cash")][0])
#     ecash = 0 if df[("Cash", "Cash")][-1] > 0 else abs(df[("Cash", "Cash")][-1])
#     bdte = bcash / (df["holdings"][0] - bcash)
#     edte = ecash / (df["holdings"][-1] - ecash)
#     if sum(d_debt) > 0:
#         t_debt = (
#             f"Beginning debt to equity was {bdte:.2%} and ending debt to equity was"
#             f" {edte:.2%}. Debt adds risk to a portfolio by amplifying the gains and losses when"
#             " equities change in value."
#         )
#         if bdte > 1 or edte > 1:
#             t_debt += " Debt to equity ratios above one represent a significant amount of risk."
#     else:
#         t_debt = (
#             "Margin was not used this year. This reduces this risk of the portfolio."
#         )
#     text = (
#         f"Your portfolio's performance for the period was {df['return'][-1]:.2%}. This was"
#         f" {'greater' if df['return'][-1] > df[('Market', 'Return')][-1] else 'less'} than"
#         f" the market return of {df[('Market', 'Return')][-1]:.2%}. The variance for the"
#         f" portfolio is {np.var(df['return']):.2%}, while the variance for the market was"
#         f" {np.var(df[('Market', 'Return')]):.2%}. {t_debt} The following report details"
#         f" various analytics from the portfolio. Read below to see the moving beta for a"
#         f" stock."
#     )
#     return text


# @log_start_end(log=logger)
# def get_beta_text(df: pd.DataFrame) -> str:
#     """Get beta summary for a dataframe

#     Parameters
#     ----------
#     df : pd.DataFrame
#         The beta history of the stock

#     Returns
#     ----------
#     t : str
#         The beta history for a ticker
#     """
#     betas = df[list(filter(lambda score: "beta" in score, list(df.columns)))]
#     high = betas.idxmax(axis=1)
#     low = betas.idxmin(axis=1)
#     text = (
#         "Beta is how strongly a portfolio's movements correlate with the market's movements."
#         " A stock with a high beta is considered to be riskier. The beginning beta for the period"
#         f" was {portfolio_helper.beta_word(df['total'][0])} at {df['total'][0]:.2f}. This went"
#         f" {'up' if df['total'][-1] > df['total'][0] else 'down'} to"
#         f" {portfolio_helper.beta_word(df['total'][-1])} at {df['total'][-1]:.2f} by the end"
#         f" of the period. The ending beta was pulled {'up' if df['total'][-1] > 1 else 'down'} by"
#         f" {portfolio_helper.clean_name(high[-1] if df['total'][-1] > 1 else low[-1])}, which had"
#         f" an ending beta of {df[high[-1]][-1] if df['total'][-1] > 1 else df[low[-1]][-1]:.2f}."
#     )
#     return text


# performance_text = (
#     "The Sharpe ratio is a measure of reward to total volatility. A Sharpe ratio above one is"
#     " considered acceptable. The Treynor ratio is a measure of systematic risk to reward."
#     " Alpha is the average return above what CAPM predicts. This measure should be above zero"
#     ". The information ratio is the excess return on systematic risk. An information ratio of"
#     " 0.4 to 0.6 is considered good."
# )






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
    ----------
    pd.Series
        Drawdown series
    -------
    """
    if is_returns:
        input_series = (1 + input_series).cumprod()

    rolling_max = input_series.cummax()
    drawdown = (input_series - rolling_max) / rolling_max

    return drawdown


def get_cumulative_returns(returns: pd.Series, period) -> pd.Series:
    """Calculate cumulative returns filtered by period

    Parameters
    ----------
    returns : pd.Series
        Returns series
    period : str
        Period to compare cumulative returns and benchmark

    Returns
    ----------
    pd.Series
        Cumulative returns series
    -------
    """
    filtered_returns = portfolio_helper.filter_df_by_period(returns, period)

    cumulative_returns = 100 * (
        (1 + filtered_returns.shift(periods=1, fill_value=0)).cumprod() - 1
    )
    return cumulative_returns


class Portfolio:
    """
    Implements a Portfolio and related methods. A Portfolio is created by loading
    an orderbook into itself.

    Attributes
    -------


    Methods
    -------
    read_orderbook: Class method to read orderbook from file

    __set_orderbook:
        preprocess_orderbook: Method to preprocess, format and compute auxiliary fields

    load_benchmark: Adds benchmark ticker, info, prices and returns
        mimic_trades_for_benchmark: Mimic trades from the orderbook based on chosen benchmark assuming partial shares

    generate_portfolio_data: Generates portfolio data from orderbook
        load_portfolio_historical_prices: Loads historical adj close prices for tickers in list of trades
        populate_historical_trade_data: Create a new dataframe to store historical prices by ticker
        calculate_holdings: Calculate holdings from historical data

    calculate_reserves:

    calculate_allocations:

    set_risk_free_rate: Sets risk free rate

    calculate_metrics:

    """

    def __init__(self, orderbook: pd.DataFrame = pd.DataFrame()):
        """Initialize Portfolio class"""

        # Portfolio
        self.tickers = {}
        self.inception_date = None
        self.static_data = pd.DataFrame()
        self.historical_trade_data = pd.DataFrame()
        self.returns = pd.DataFrame()
        self.itemized_holdings = pd.DataFrame()
        self.portfolio_trades = pd.DataFrame()
        self.portfolio_value = None

        self.portfolio_assets_allocation = pd.DataFrame()
        self.portfolio_regional_allocation = pd.DataFrame()
        self.portfolio_country_allocation = pd.DataFrame()
        # calculate cumulative returns here
        # rolling cumulative cumulative returns

        # Prices
        self.portfolio_historical_prices = pd.DataFrame()
        self.risk_free_rate = float(0)

        # Benchmark
        self.benchmark_ticker: str = ""
        self.benchmark_info = None
        self.benchmark_historical_prices = pd.DataFrame()
        self.benchmark_returns = pd.DataFrame()
        self.benchmark_trades = pd.DataFrame()

        self.benchmark_assets_allocation = pd.DataFrame()
        self.benchmark_regional_allocation = pd.DataFrame()
        self.benchmark_country_allocation = pd.DataFrame()

        
        if orderbook.empty:
            # Allow for empty initialization
            self.empty = True
        else:
            # Set and preprocess orderbook
            self.__set_orderbook(orderbook)

    def __set_orderbook(self, orderbook):
        self.__orderbook = orderbook
        self.preprocess_orderbook()
        self.empty = False

    def get_orderbook(self):
        return self.__orderbook
        
    @staticmethod
    def read_orderbook(path: str) -> pd.DataFrame:
        """Class method to read orderbook from file

        Args:
            path (str): path to orderbook file
        """
        # Load orderbook from file
        if path.endswith(".xlsx"):
            orderbook = pd.read_excel(path)
        elif path.endswith(".csv"):
            orderbook = pd.read_csv(path)

        return orderbook

    def preprocess_orderbook(self):
        """Method to preprocess, format and compute auxiliary fields"""
        try:
            # Convert Date to datetime
            self.__orderbook["Date"] = pd.to_datetime(self.__orderbook["Date"])

            # Sort orderbook by date
            self.__orderbook = self.__orderbook.sort_values(by="Date")

            # Capitalize Ticker and Type [of instrument...]
            self.__orderbook["Ticker"] = self.__orderbook["Ticker"].map(
                lambda x: x.upper()
            )
            self.__orderbook["Type"] = self.__orderbook["Type"].map(lambda x: x.upper())

            # Translate side: ["deposit", "buy"] -> 1 and ["withdrawal", "sell"] -> -1
            self.__orderbook["Side"] = self.__orderbook["Side"].map(
                lambda x: 1
                if x.lower() in ["deposit", "buy"]
                else (-1 if x.lower() in ["withdrawal", "sell"] else 0)
            )

            # Convert quantity to signed integer
            self.__orderbook["Quantity"] = (
                self.__orderbook["Quantity"] * self.__orderbook["Side"]
            )

            # Determining the investment/divestment value
            self.__orderbook["Investment"] = (
                self.__orderbook["Quantity"] * self.__orderbook["Price"]
            )

            # Reformat crypto tickers to yfinance format (e.g. BTC -> BTC-USD)
            crypto_trades = self.__orderbook[self.__orderbook.Type == "CRYPTO"]
            self.__orderbook.loc[
                (self.__orderbook.Type == "CRYPTO"), "Ticker"
            ] = [
                f"{crypto}-{currency}"
                for crypto, currency in zip(
                    crypto_trades.Ticker, crypto_trades.Currency
                )
            ]

            # Create tickers dictionary with structure {'Type': [Ticker]}
            for type in set(self.__orderbook["Type"]):
                self.tickers[type] = list(
                    set(
                        self.__orderbook[self.__orderbook["Type"].isin([type])][
                            "Ticker"
                        ]
                    )
                )

            # Create list with tickers except cash
            self.tickers_except_cash = list(set(self.__orderbook["Ticker"]))
            if "CASH" in self.tickers_except_cash:
                self.tickers_except_cash.remove("CASH")

            # Warn user if no cash deposit in account
            if "CASH" not in self.tickers.keys():
                logger.warning(
                    "No initial cash deposit. Calculations may be off as this assumes trading from a "
                    "funded account"
                )
                console.print(
                    "[red]No initial cash deposit. Calculations may be off as this assumes trading from a "
                    "funded account[/red]."
                )

            # Save orderbook inception date
            self.inception_date = self.__orderbook["Date"][0]

            # Save trades static data
            self.static_data = self.__orderbook.pivot(
                index="Ticker",
                columns=[],
                values=["Type", "Sector", "Industry", "Country"],
            )

        except:
            raise Exception("Could not preprocess orderbook.")

    def load_benchmark(self, ticker: str = "SPY"):
        """Adds benchmark dataframe

        Args:
            ticker (str): benchmark ticker to download data
        """
        self.benchmark_ticker = ticker
        self.benchmark_historical_prices = yf.download(
            ticker, start=self.inception_date, threads=False, progress=False
        )["Adj Close"]
        self.benchmark_returns = self.benchmark_historical_prices.pct_change().dropna()
        self.benchmark_info = yf.Ticker(ticker).info
        self.mimic_trades_for_benchmark()

    def mimic_trades_for_benchmark(self):
        """Mimic trades from the orderbook based on chosen benchmark assuming partial shares"""
        # Create dataframe to store benchmark trades
        self.benchmark_trades = self.__orderbook[["Date", "Type", "Investment"]].copy()
        # Set current price of benchmark
        self.benchmark_trades["Last price"] = self.benchmark_historical_prices[-1]
        self.benchmark_trades[["Benchmark Quantity", "Trade price"]] = float(0)

        # Iterate over orderbook to replicate trades on benchmark (skip CASH)
        for index, trade in self.__orderbook.iterrows():
            if trade["Type"] != "CASH":
                # Select date to search (if not in historical prices, get closest value)
                if trade["Date"] not in self.benchmark_historical_prices.index:
                    date = self.benchmark_historical_prices.index.searchsorted(
                        trade["Date"]
                    )
                else:
                    date = trade["Date"]

                # Populate benchmark orderbook trades
                self.benchmark_trades["Trade price"][
                    index
                ] = self.benchmark_historical_prices[date]
                self.benchmark_trades["Benchmark Quantity"][index] = (
                    trade["Investment"] / self.benchmark_trades["Trade price"][index]
                )

        self.benchmark_trades["Benchmark Investment"] = (
            self.benchmark_trades["Trade price"]
            * self.benchmark_trades["Benchmark Quantity"]
        )
        self.benchmark_trades["Benchmark Value"] = (
            self.benchmark_trades["Last price"]
            * self.benchmark_trades["Benchmark Quantity"]
        )
        self.benchmark_trades["Benchmark % Return"] = (
            self.benchmark_trades["Benchmark Value"]
            / self.benchmark_trades["Benchmark Investment"]
            - 1
        )
        self.benchmark_trades["Benchmark Abs Return"] = (
            self.benchmark_trades["Benchmark Value"]
            - self.benchmark_trades["Benchmark Investment"]
        )
        # TODO: To add alpha here, we must pull prices from original trades and get last price
        # for each of those trades. Then just calculate returns and compare to benchmark
        self.benchmark_trades.fillna(0, inplace=True)

    def generate_portfolio_data(self):
        """Generates portfolio data from orderbook"""
        self.load_portfolio_historical_prices()
        self.populate_historical_trade_data()
        self.calculate_holdings()

        # Determine the returns, replace inf values with NaN and then drop any missing values
        self.returns = self.historical_trade_data["Holdings"]["Total"].pct_change()
        self.returns.replace([np.inf, -np.inf], np.nan, inplace=True)
        self.returns = self.returns.dropna()

        # Determine invested amount, relative and absolute return based on last close
        last_price = self.historical_trade_data["Close"].iloc[-1]

        # self.portfolio_trades = pd.DataFrame(self.__orderbook["Date"])
        self.portfolio_trades = self.__orderbook.copy()
        self.portfolio_trades[
            [
                "Portfolio Investment",
                "Close",
                "Portfolio Value",
                "% Portfolio Return",
                "Abs Portfolio Return",
            ]
        ] = float(0)

        for index, trade in self.__orderbook.iterrows():
            if trade["Type"] != "CASH":
                self.portfolio_trades["Close"][index] = last_price[trade["Ticker"]]
                self.portfolio_trades["Portfolio Investment"][index] = trade[
                    "Investment"
                ]
                self.portfolio_trades["Portfolio Value"][index] = (
                    self.portfolio_trades["Close"][index] * trade["Quantity"]
                )
                self.portfolio_trades["% Portfolio Return"][index] = (
                    self.portfolio_trades["Portfolio Value"][index]
                    / self.portfolio_trades["Portfolio Investment"][index]
                ) - 1
                self.portfolio_trades["Abs Portfolio Return"].loc[index] = (
                    self.portfolio_trades["Portfolio Value"][index]
                    - self.portfolio_trades["Portfolio Investment"][index]
                )

    def load_portfolio_historical_prices(self, use_close: bool = False):
        """Loads historical adj close prices for tickers in list of trades"""

        for type in self.tickers.keys():
            if type == "STOCK" or type == "ETF":
                # Download yfinance data
                price_data = yf.download(
                    self.tickers[type], start=self.inception_date, progress=False
                )["Close" if use_close else "Adj Close"]

                # Set up column name if only 1 ticker (pd.DataFrame only does this if >1 ticker)
                if len(self.tickers[type]) == 1:
                    price_data = pd.DataFrame(price_data)
                    price_data.columns = self.tickers[type]

                # Add to historical_prices dataframe
                self.portfolio_historical_prices = pd.concat(
                    [self.portfolio_historical_prices, price_data], axis=1
                )

            elif type == "CRYPTO":

                # Download yfinance data
                price_data = yf.download(
                    self.tickers[type], start=self.inception_date, progress=False
                )["Close"]

                # Set up column name if only 1 ticker (pd.DataFrame only does this if >1 ticker)
                if len(self.tickers[type]) == 1:
                    price_data = pd.DataFrame(price_data)
                    price_data.columns = self.tickers[type]

                # Add to historical_prices dataframe
                self.portfolio_historical_prices = pd.concat(
                    [self.portfolio_historical_prices, price_data], axis=1
                )

            elif type == "CASH":
                # Set CASH price to 1
                self.portfolio_historical_prices["CASH"] = 1

            else:
                raise Exception("Type not supported in the orderbook.")

            # Fill missing values with last known price
            self.portfolio_historical_prices.fillna(method="ffill", inplace=True)

    def populate_historical_trade_data(self):
        """Create a new dataframe to store historical prices by ticker"""
        trade_data = self.__orderbook.pivot(
            index="Date",
            columns="Ticker",
            values=[
                "Type",
                "Sector",
                "Industry",
                "Country",
                "Price",
                "Quantity",
                "Fees",
                "Premium",
                "Investment",
                "Side",
                "Currency",
            ],
        )

        # Make historical prices columns a multi-index. This helps the merging.
        self.portfolio_historical_prices.columns = pd.MultiIndex.from_product(
            [["Close"], self.portfolio_historical_prices.columns]
        )

        # Merge with historical close prices (and fillna)
        trade_data = pd.merge(
            trade_data,
            self.portfolio_historical_prices,
            how="right",
            left_index=True,
            right_index=True,
        ).fillna(0)

        # Accumulate quantity held by trade date
        trade_data["Quantity"] = trade_data["Quantity"].cumsum()

        self.historical_trade_data = trade_data

    def calculate_holdings(self):
        """Calculate holdings from historical data"""
        trade_data = self.historical_trade_data

        # For each type [STOCK, ETF, etc] calculate holdings value by trade date
        # and add it to historical_trade_data
        for type in self.tickers.keys():
            trade_data[
                pd.MultiIndex.from_product([["Holdings"], self.tickers[type]])
            ] = (
                trade_data["Quantity"][self.tickers[type]]
                * trade_data["Close"][self.tickers[type]]
            )

        # Find amount of cash held in account. If CASH exist within the Orderbook,
        # the cash hold is defined as deposited cash - stocks bought + stocks sold
        # Otherwise, the cash hold will equal the invested amount.
        if "CASH" in self.tickers:
            trade_data.loc[:, ("Holdings", "CASH")] = (
                trade_data["Investment"]["CASH"]
                - trade_data["Investment"][self.tickers_except_cash].sum(axis=1)
                - trade_data["Fees"].sum(axis=1)
                - trade_data["Premium"].sum(axis=1)
            ).cumsum()
        else:
            trade_data.loc[:, ("Holdings", "CASH")] = (
                trade_data["Investment"][self.tickers_except_cash].sum(axis=1)
            ).cumsum()

        trade_data.loc[:, ("Holdings", "Total")] = trade_data["Holdings"][
            "CASH"
        ] + trade_data["Holdings"][self.tickers_except_cash].sum(axis=1)

        self.portfolio_value = trade_data["Holdings"]["Total"]

        for type in self.tickers.keys():
            self.itemized_holdings[type] = trade_data["Holdings"][
                self.tickers[type]
            ].sum(axis=1)

        self.historical_trade_data = trade_data

    def calculate_reserves(self):
        """_summary_"""
        # TODO: Add back cash dividends and deduct exchange costs
        pass

    def calculate_allocations(self):
        """Determine allocations based on assets, sectors, countries and regional."""

        # Determine asset allocation
        (
            self.benchmark_assets_allocation,
            self.portfolio_assets_allocation,
        ) = allocation_model.obtain_assets_allocation(
            self.benchmark_info, self.portfolio_trades
        )

        # Determine sector allocation
        (
            self.benchmark_sectors_allocation,
            self.portfolio_sectors_allocation,
        ) = allocation_model.obtain_sector_allocation(
            self.benchmark_info, self.portfolio_trades
        )

        # Determine regional and country allocations
        (
            self.benchmark_regional_allocation,
            self.benchmark_country_allocation,
        ) = allocation_model.obtain_benchmark_regional_and_country_allocation(
            self.benchmark_ticker
        )

        (
            self.portfolio_regional_allocation,
            self.portfolio_country_allocation,
        ) = allocation_model.obtain_portfolio_regional_and_country_allocation(
            self.portfolio_trades
        )

    def set_risk_free_rate(self, risk_free_rate: float):
        """Sets risk free rate

        Args:
            risk_free (float): risk free rate in decimal format
        """
        self.risk_free_rate = risk_free_rate


    # SHOULD WE MAKE THIS CLASS METHODS?
    # OR SPIN OFF AND ARE THEN CALLED FROM INSIDE THE CLASS
    @log_start_end(log=logger)
    def get_r2_score(self) -> pd.DataFrame:
        """Class method that retrieves R2 Score for portfolio and benchmark selected

        Returns
        -------
        pd.DataFrame
            DataFrame with R2 Score between portfolio and benchmark for different periods
        """
        vals = list()
        for period in portfolio_helper.PERIODS:
            vals.append(
                round(
                    r2_score(
                        portfolio_helper.filter_df_by_period(self.returns, period),
                        portfolio_helper.filter_df_by_period(
                            self.benchmark_returns, period
                        ),
                    ),
                    3,
                )
            )
        return pd.DataFrame(vals, index=portfolio_helper.PERIODS, columns=["R2 Score"])

    @log_start_end(log=logger)
    def get_skewness(self) -> pd.DataFrame:
        """Class method that retrieves skewness for portfolio and benchmark selected

        Returns
        -------
        pd.DataFrame
            DataFrame with skewness for portfolio and benchmark for different periods
        """
        vals = list()
        for period in portfolio_helper.PERIODS:
            vals.append(
                [
                    round(
                        scipy.stats.skew(
                            portfolio_helper.filter_df_by_period(self.returns, period)
                        ),
                        3,
                    ),
                    round(
                        scipy.stats.skew(
                            portfolio_helper.filter_df_by_period(
                                self.benchmark_returns, period
                            )
                        ),
                        3,
                    ),
                ]
            )
        return pd.DataFrame(
            vals, index=portfolio_helper.PERIODS, columns=["Portfolio", "Benchmark"]
        )

    @log_start_end(log=logger)
    def get_kurtosis(self) -> pd.DataFrame:
        """Class method that retrieves kurtosis for portfolio and benchmark selected

        Returns
        -------
        pd.DataFrame
            DataFrame with kurtosis for portfolio and benchmark for different periods
        """
        vals = list()
        for period in portfolio_helper.PERIODS:
            vals.append(
                [
                    round(
                        scipy.stats.kurtosis(
                            portfolio_helper.filter_df_by_period(self.returns, period)
                        ),
                        3,
                    ),
                    round(
                        scipy.stats.skew(
                            portfolio_helper.filter_df_by_period(
                                self.benchmark_returns, period
                            )
                        ),
                        3,
                    ),
                ]
            )
        return pd.DataFrame(
            vals, index=portfolio_helper.PERIODS, columns=["Portfolio", "Benchmark"]
        )

    @log_start_end(log=logger)
    def get_stats(self, period: str = "all") -> pd.DataFrame:
        """Class method that retrieves stats for portfolio and benchmark selected based on a certain period

        Returns
        -------
        pd.DataFrame
            DataFrame with overall stats for portfolio and benchmark for a certain periods
        period : str
            Period to consider. Choices are: mtd, qtd, ytd, 3m, 6m, 1y, 3y, 5y, 10y, all
        """
        df = (
            portfolio_helper.filter_df_by_period(self.returns, period)
            .describe()
            .to_frame()
            .join(
                portfolio_helper.filter_df_by_period(
                    self.benchmark_returns, period
                ).describe()
            )
        )
        df.columns = ["Portfolio", "Benchmark"]
        return df

    @log_start_end(log=logger)
    def get_volatility(self) -> pd.DataFrame:
        """Class method that retrieves volatility for portfolio and benchmark selected

        Returns
        -------
        pd.DataFrame
            DataFrame with volatility for portfolio and benchmark for different periods
        """
        vals = list()
        for period in portfolio_helper.PERIODS:
            port_rets = portfolio_helper.filter_df_by_period(self.returns, period)
            bench_rets = portfolio_helper.filter_df_by_period(
                self.benchmark_returns, period
            )
            vals.append(
                [
                    round(
                        100 * port_rets.std() * (len(port_rets) ** 0.5),
                        3,
                    ),
                    round(
                        100 * bench_rets.std() * (len(bench_rets) ** 0.5),
                        3,
                    ),
                ]
            )
        return pd.DataFrame(
            vals,
            index=portfolio_helper.PERIODS,
            columns=["Portfolio [%]", "Benchmark [%]"],
        )

    @log_start_end(log=logger)
    def get_sharpe_ratio(self, risk_free_rate: float) -> pd.DataFrame:
        """Class method that retrieves sharpe ratio for portfolio and benchmark selected

        Parameters
        ----------
        risk_free_rate: float
            Risk free rate value

        Returns
        -------
        pd.DataFrame
            DataFrame with sharpe ratio for portfolio and benchmark for different periods
        """
        vals = list()
        for period in portfolio_helper.PERIODS:
            vals.append(
                [
                    round(
                        portfolio_helper.sharpe_ratio(
                            portfolio_helper.filter_df_by_period(self.returns, period),
                            risk_free_rate,
                        ),
                        3,
                    ),
                    round(
                        portfolio_helper.sharpe_ratio(
                            portfolio_helper.filter_df_by_period(
                                self.benchmark_returns, period
                            ),
                            risk_free_rate,
                        ),
                        3,
                    ),
                ]
            )
        return pd.DataFrame(
            vals, index=portfolio_helper.PERIODS, columns=["Portfolio", "Benchmark"]
        )

    @log_start_end(log=logger)
    def get_sortino_ratio(self, risk_free_rate: float) -> pd.DataFrame:
        """Class method that retrieves sortino ratio for portfolio and benchmark selected

        Parameters
        ----------
        risk_free_rate: float
            Risk free rate value

        Returns
        -------
        pd.DataFrame
            DataFrame with sortino ratio for portfolio and benchmark for different periods
        """
        vals = list()
        for period in portfolio_helper.PERIODS:
            vals.append(
                [
                    round(
                        portfolio_helper.sortino_ratio(
                            portfolio_helper.filter_df_by_period(self.returns, period),
                            risk_free_rate,
                        ),
                        3,
                    ),
                    round(
                        portfolio_helper.sortino_ratio(
                            portfolio_helper.filter_df_by_period(
                                self.benchmark_returns, period
                            ),
                            risk_free_rate,
                        ),
                        3,
                    ),
                ]
            )
        return pd.DataFrame(
            vals, index=portfolio_helper.PERIODS, columns=["Portfolio", "Benchmark"]
        )

    @log_start_end(log=logger)
    def get_maximum_drawdown_ratio(self) -> pd.DataFrame:
        """Class method that retrieves maximum drawdown ratio for portfolio and benchmark selected

        Returns
        -------
        pd.DataFrame
            DataFrame with maximum drawdown for portfolio and benchmark for different periods
        """
        vals = list()
        for period in portfolio_helper.PERIODS:
            vals.append(
                [
                    round(
                        portfolio_helper.get_maximum_drawdown(
                            portfolio_helper.filter_df_by_period(self.returns, period)
                        ),
                        3,
                    ),
                    round(
                        portfolio_helper.get_maximum_drawdown(
                            portfolio_helper.filter_df_by_period(
                                self.benchmark_returns, period
                            )
                        ),
                        3,
                    ),
                ]
            )
        return pd.DataFrame(
            vals, index=portfolio_helper.PERIODS, columns=["Portfolio", "Benchmark"]
        )
