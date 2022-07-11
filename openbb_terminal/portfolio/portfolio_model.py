"""Portfolio Model"""
__docformat__ = "numpy"

import logging
from typing import Dict, Any

import numpy as np
import scipy
import pandas as pd
import yfinance as yf
from sklearn.metrics import r2_score
from pycoingecko import CoinGeckoAPI

from openbb_terminal.decorators import log_start_end
from openbb_terminal.portfolio import portfolio_helper, allocation_model
from openbb_terminal.rich_config import console

# pylint: disable=E1136,W0201,R0902,C0302
# pylint: disable=unsupported-assignment-operation,redefined-outer-name,too-many-public-methods

logger = logging.getLogger(__name__)
cg = CoinGeckoAPI()

pd.options.mode.chained_assignment = None


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


def cumulative_returns(returns: pd.Series) -> pd.Series:
    """Calculate cumulative returns filtered by period

    Parameters
    ----------
    returns : pd.Series
        Returns series

    Returns
    ----------
    pd.Series
        Cumulative returns series
    -------
    """
    cumulative_returns = (1 + returns.shift(periods=1, fill_value=0)).cumprod() - 1
    return cumulative_returns


@log_start_end(log=logger)
def get_gaintopain_ratio(returns: pd.DataFrame, benchmark_returns: pd.DataFrame):
    """Gets Pain-to-Gain ratio

    Parameters
    ----------
    returns: pd.Series
        Series of portfolio returns
    benchmark_returns: pd.Series
        Series of benchmark returns

    Returns
    -------
    pd.DataFrame
            DataFrame of the portfolio's gain-to-pain ratio
    """
    vals = list()
    for period in portfolio_helper.PERIODS:
        period_return = portfolio_helper.filter_df_by_period(returns, period)
        period_bench_return = portfolio_helper.filter_df_by_period(
            benchmark_returns, period
        )
        if not period_return.empty:
            vals.append(
                [
                    round(
                        (
                            (1 + period_return.shift(periods=1, fill_value=0)).cumprod()
                            - 1
                        ).iloc[-1]
                        / get_maximum_drawdown(period_return),
                        3,
                    ),
                    round(
                        (
                            (
                                1 + period_bench_return.shift(periods=1, fill_value=0)
                            ).cumprod()
                            - 1
                        ).iloc[-1]
                        / get_maximum_drawdown(period_bench_return),
                        3,
                    ),
                ]
            )
        else:
            vals.append(["-", "-"])
    gtr_period_df = pd.DataFrame(
        vals, index=portfolio_helper.PERIODS, columns=["Portfolio", "Benchmark"]
    )

    return gtr_period_df


@log_start_end(log=logger)
def get_rolling_beta(
    returns: pd.Series, benchmark_returns: pd.Series, period: float = 252
):
    """Get rolling beta

    Parameters
    ----------
    returns: pd.Series
        Series of portfolio returns
    benchmark_returns: pd.Series
        Series of benchmark returns
    period: float
        Interval used for rolling values

    Returns
    -------
    pd.DataFrame
        DataFrame of the portfolio's rolling beta
    """
    # Rolling beta is defined as Cov(Port,Bench)/var(Bench)
    covs = (
        pd.DataFrame({"Portfolio": returns, "Benchmark": benchmark_returns})
        .dropna(axis=0)
        .rolling(max(1, period))
        .cov()
        .unstack()
        .dropna()
    )
    rolling_beta = covs["Portfolio"]["Benchmark"] / covs["Benchmark"]["Benchmark"]

    return rolling_beta


@log_start_end(log=logger)
def get_tracking_error(
    returns: pd.Series, benchmark_returns: pd.Series, period: float = 252
):
    """Get tracking error

    Parameters
    ----------
    returns: pd.Series
        Series of portfolio returns
    benchmark_returns: pd.Series
        Series of benchmark returns
    period: float
        Interval used for rolling values

    Returns
    -------
    pd.DataFrame
        DataFrame of tracking errors during different time periods
    pd.Series
        Series of rolling tracking error
    """
    diff_returns = returns - benchmark_returns

    trackr_rolling = diff_returns.rolling(period, min_periods=period).std()

    vals = list()
    for periods in portfolio_helper.PERIODS:
        period_return = portfolio_helper.filter_df_by_period(diff_returns, periods)
        if not period_return.empty:
            vals.append([round(period_return.std(), 3)])
        else:
            vals.append(["-"])
    trackr_period_df = pd.DataFrame(
        vals, index=portfolio_helper.PERIODS, columns=["Tracking Error"]
    )

    return trackr_period_df, trackr_rolling


@log_start_end(log=logger)
def get_information_ratio(
    returns: pd.Series, benchmark_returns: pd.Series, period: float = 252
):
    """

    Parameters
    ----------
    returns: pd.Series
        Series of portfolio returns
    benchmark_returns: pd.Series
        Series of benchmark returns
    period: float
        Interval used for rolling values

    Returns
    -------
    pd.DataFrame
        DataFrame of the information ratio during different time periods
    pd.Series
        Series of rolling information ratio
    """
    tracking_err_df, tracking_err_rol = get_tracking_error(
        returns, benchmark_returns, period
    )

    ir_rolling = (
        (1.0 + returns).rolling(window=period).agg(lambda x: x.prod())
        - 1
        - ((1.0 + benchmark_returns).rolling(window=period).agg(lambda x: x.prod()) - 1)
    ) / tracking_err_rol

    vals = list()
    for periods in portfolio_helper.PERIODS:
        period_return = portfolio_helper.filter_df_by_period(returns, periods)
        period_bench_return = portfolio_helper.filter_df_by_period(
            benchmark_returns, periods
        )
        if not period_return.empty:
            vals.append(
                [
                    round(
                        (
                            (
                                (
                                    1 + period_return.shift(periods=1, fill_value=0)
                                ).cumprod()
                                - 1
                            ).iloc[-1]
                            - (
                                (
                                    (
                                        1
                                        + period_bench_return.shift(
                                            periods=1, fill_value=0
                                        )
                                    ).cumprod()
                                    - 1
                                ).iloc[-1]
                            )
                        )
                        / tracking_err_df.loc[periods, "Tracking Error"],
                        3,
                    )
                ]
            )
        else:
            vals.append(["-"])

    ir_period_df = pd.DataFrame(
        vals, index=portfolio_helper.PERIODS, columns=["Information Ratio"]
    )

    return ir_period_df, ir_rolling


@log_start_end(log=logger)
def get_tail_ratio(
    returns: pd.Series, benchmark_returns: pd.Series, period: float = 252
):
    """

    Parameters
    ----------
    returns: pd.Series
        Series of portfolio returns
    benchmark_returns: pd.Series
        Series of benchmark returns
    period: float
        Interval used for rolling values

    Returns
    -------
    pd.DataFrame
        DataFrame of the portfolios and the benchmarks tail ratio during different time periods
    pd.Series
        Series of the portfolios rolling tail ratio
    pd.Series
        Series of the benchmarks rolling tail ratio
    """
    returns_r = returns.rolling(period, min_periods=period)
    benchmark_returns_r = benchmark_returns.rolling(period, min_periods=period)

    portfolio_tr = returns_r.quantile(0.95) / abs(returns_r.quantile(0.05))
    benchmark_tr = benchmark_returns_r.quantile(0.95) / abs(
        benchmark_returns_r.quantile(0.05)
    )

    vals = list()
    for periods in portfolio_helper.PERIODS:
        period_return = portfolio_helper.filter_df_by_period(returns, periods)
        period_bench_return = portfolio_helper.filter_df_by_period(
            benchmark_returns, periods
        )
        if not period_return.empty:
            vals.append(
                [
                    round(
                        period_return.quantile(0.95)
                        / abs(period_return.quantile(0.05)),
                        3,
                    ),
                    round(
                        period_bench_return.quantile(0.95)
                        / abs(period_bench_return.quantile(0.05)),
                        3,
                    ),
                ]
            )
        else:
            vals.append(["-", "-"])

    tailr_period_df = pd.DataFrame(
        vals, index=portfolio_helper.PERIODS, columns=["Portfolio", "Benchmark"]
    )

    return tailr_period_df, portfolio_tr, benchmark_tr


@log_start_end(log=logger)
def get_common_sense_ratio(returns: pd.Series, benchmark_returns: pd.Series):
    """Get common sense ratio

    Parameters
    ----------
    returns: pd.Series
        Series of portfolio returns
    benchmark_returns: pd.Series
        Series of benchmark returns

    Returns
    -------
    pd.DataFrame
        DataFrame of the portfolios and the benchmarks common sense ratio during different time periods
    """
    tail_ratio_df, _, _ = get_tail_ratio(returns, benchmark_returns)

    vals = list()
    for period in portfolio_helper.PERIODS:
        period_return = portfolio_helper.filter_df_by_period(returns, period)
        period_bench_return = portfolio_helper.filter_df_by_period(
            benchmark_returns, period
        )
        if not period_return.empty:
            vals.append(
                [
                    round(
                        tail_ratio_df.loc[period, "Portfolio"]
                        * (
                            (1 + period_return.shift(periods=1, fill_value=0)).cumprod()
                            - 1
                        ).iloc[-1]
                        / get_maximum_drawdown(period_return),
                        3,
                    ),
                    round(
                        tail_ratio_df.loc[period, "Benchmark"]
                        * (
                            (
                                1 + period_bench_return.shift(periods=1, fill_value=0)
                            ).cumprod()
                            - 1
                        ).iloc[-1]
                        / get_maximum_drawdown(period_bench_return),
                        3,
                    ),
                ]
            )
        else:
            vals.append(["-", "-"])

    csr_period_df = pd.DataFrame(
        vals, index=portfolio_helper.PERIODS, columns=["Portfolio", "Benchmark"]
    )

    return csr_period_df


@log_start_end(log=logger)
def get_jensens_alpha(
    returns: pd.Series, benchmark_returns: pd.Series, rf: float = 0, period: float = 252
):
    """Get jensen's alpha

    Parameters
    ----------
    returns: pd.Series
        Series of portfolio returns
    benchmark_returns: pd.Series
        Series of benchmark returns
    rf: float
        Risk free rate
    period: float
        Interval used for rolling values

    Returns
    -------
    pd.DataFrame
        DataFrame of jensens's alpha during different time periods
    pd.Series
        Series of jensens's alpha data
    """
    periods_d = portfolio_helper.PERIODS_DAYS

    period_cum_returns = (1.0 + returns).rolling(window=period).agg(
        lambda x: x.prod()
    ) - 1
    period_cum_bench_returns = (1.0 + benchmark_returns).rolling(window=period).agg(
        lambda x: x.prod()
    ) - 1
    rfr_cum_returns = rf * period / 252
    beta = get_rolling_beta(returns, benchmark_returns, period)
    ja_rolling = period_cum_returns - (
        rfr_cum_returns + beta * (period_cum_bench_returns - rfr_cum_returns)
    )

    vals = list()
    for periods in portfolio_helper.PERIODS:
        period_return = portfolio_helper.filter_df_by_period(returns, periods)
        period_bench_return = portfolio_helper.filter_df_by_period(
            benchmark_returns, periods
        )
        if not period_return.empty:
            beta = get_rolling_beta(returns, benchmark_returns, periods_d[periods])
            if not beta.empty:
                beta = beta.iloc[-1]
                period_cum_returns = (
                    (1 + period_return.shift(periods=1, fill_value=0)).cumprod() - 1
                ).iloc[-1]
                period_cum_bench_returns = (
                    (1 + period_bench_return.shift(periods=1, fill_value=0)).cumprod()
                    - 1
                ).iloc[-1]
                rfr_cum_returns = rf * periods_d[periods] / 252
                vals.append(
                    [
                        round(
                            period_cum_returns
                            - (
                                rfr_cum_returns
                                + beta * (period_cum_bench_returns - rfr_cum_returns)
                            ),
                            3,
                        )
                    ]
                )
            else:
                vals.append(["-"])
        else:
            vals.append(["-"])

    ja_period_df = pd.DataFrame(
        vals, index=portfolio_helper.PERIODS, columns=["Portfolio"]
    )

    return ja_period_df, ja_rolling


@log_start_end(log=logger)
def get_calmar_ratio(
    returns: pd.Series, benchmark_returns: pd.Series, period: float = 756
):
    """Get calmar ratio

    Parameters
    ----------
    returns: pd.Series
        Series of portfolio returns
    benchmark_returns: pd.Series
        Series of benchmark returns
    period: float
        Interval used for rolling values

    Returns
    -------
    pd.DataFrame
        DataFrame of calmar ratio of the benchmark and portfolio during different time periods
    pd.Series
        Series of calmar ratio data
    """
    periods_d = portfolio_helper.PERIODS_DAYS

    period_cum_returns = (1.0 + returns).rolling(window=period).agg(
        lambda x: x.prod()
    ) - 1

    # Calculate annual return
    annual_return = period_cum_returns ** (1 / (period / 252)) - 1

    cr_rolling = annual_return / get_maximum_drawdown(returns)

    vals = list()
    for periods in portfolio_helper.PERIODS:
        period_return = portfolio_helper.filter_df_by_period(returns, periods)
        period_bench_return = portfolio_helper.filter_df_by_period(
            benchmark_returns, periods
        )
        if (not period_return.empty) and (periods_d[periods] != 0):
            period_cum_returns = (
                (1 + period_return.shift(periods=1, fill_value=0)).cumprod() - 1
            ).iloc[-1]
            period_cum_bench_returns = (
                (1 + period_bench_return.shift(periods=1, fill_value=0)).cumprod() - 1
            ).iloc[-1]
            annual_return = (1 + period_cum_returns) ** (
                1 / (len(period_return) / 252)
            ) - 1
            annual_bench_return = (1 + period_cum_bench_returns) ** (
                1 / (len(period_bench_return) / 252)
            ) - 1
            drawdown = get_maximum_drawdown(period_return)
            bench_drawdown = get_maximum_drawdown(period_bench_return)
            if (drawdown != 0) and (bench_drawdown != 0):
                vals.append(
                    [
                        round(annual_return / drawdown, 3),
                        round(annual_bench_return / bench_drawdown, 3),
                    ]
                )
            else:
                vals.append(["-", "-"])
        else:
            vals.append(["-", "-"])

    cr_period_df = pd.DataFrame(
        vals, index=portfolio_helper.PERIODS, columns=["Portfolio", "Benchmark"]
    )

    return cr_period_df, cr_rolling


@log_start_end(log=logger)
def get_kelly_criterion(returns: pd.Series, portfolio_trades: pd.DataFrame):
    """Gets kelly criterion

    Parameters
    ----------
    returns: pd.Series
        Series of portfolio returns
    portfolio_trades: pd.DataFrame
        DataFrame of the portfolio trades with trade return in %

    Returns
    -------
    pd.DataFrame
        DataFrame of kelly criterion of the portfolio during different time periods
    """
    portfolio_trades["Date"] = pd.to_datetime(portfolio_trades["Date"])
    portfolio_trades = portfolio_trades.set_index("Date")

    vals: list = list()
    for period in portfolio_helper.PERIODS:
        period_return = portfolio_helper.filter_df_by_period(returns, period)
        period_portfolio_tr = portfolio_helper.filter_df_by_period(
            portfolio_trades, period
        )
        if (not period_return.empty) and (not period_portfolio_tr.empty):
            w = len(period_return[period_return > 0]) / len(period_return)
            r = len(
                period_portfolio_tr[period_portfolio_tr["% Portfolio Return"] > 0]
            ) / len(
                period_portfolio_tr[period_portfolio_tr["Type"].str.upper() != "CASH"]
            )
            if r != 0:
                vals.append([round(w - (1 - w) / r, 3)])
            else:
                vals.append(["-"])
        else:
            vals.append(["-"])

    kc_period_df = pd.DataFrame(
        vals, index=portfolio_helper.PERIODS, columns=["Kelly %"]
    )

    return kc_period_df


@log_start_end(log=logger)
def get_payoff_ratio(portfolio_trades: pd.DataFrame):
    """Gets payoff ratio

    Parameters
    ----------
    portfolio_trades: pd.DataFrame
        DataFrame of the portfolio trades with trade return in % and abs values

    Returns
    -------
    pd.DataFrame
        DataFrame of payoff ratio of the portfolio during different time periods
    """
    portfolio_trades["Date"] = pd.to_datetime(portfolio_trades["Date"])
    portfolio_trades = portfolio_trades.set_index("Date")

    vals = list()
    for period in portfolio_helper.PERIODS:
        period_portfolio_tr = portfolio_helper.filter_df_by_period(
            portfolio_trades, period
        )
        if not portfolio_trades.empty:
            portfolio_wins = period_portfolio_tr[
                period_portfolio_tr["% Portfolio Return"] > 0
            ]
            portfolio_loses = period_portfolio_tr[
                period_portfolio_tr["% Portfolio Return"] < 0
            ]
            avg_w = portfolio_wins["Abs Portfolio Return"].mean()
            avg_l = portfolio_loses["Abs Portfolio Return"].mean()
            vals.append([round(avg_w / abs(avg_l), 3)] if avg_w is not np.nan else [0])
        else:
            vals.append(["-"])

    pr_period_ratio = pd.DataFrame(
        vals, index=portfolio_helper.PERIODS, columns=["Payoff Ratio"]
    )

    return pr_period_ratio


@log_start_end(log=logger)
def get_profit_factor(portfolio_trades: pd.DataFrame):
    """Gets profit factor

    Parameters
    ----------
    portfolio_trades: pd.DataFrame
        DataFrame of the portfolio trades with trade return in % and abs values

    Returns
    -------
    pd.DataFrame
        DataFrame of profit factor of the portfolio during different time periods
    """
    portfolio_trades["Date"] = pd.to_datetime(portfolio_trades["Date"])
    portfolio_trades = portfolio_trades.set_index("Date")

    vals = list()
    for period in portfolio_helper.PERIODS:
        period_portfolio_tr = portfolio_helper.filter_df_by_period(
            portfolio_trades, period
        )
        if not portfolio_trades.empty:
            portfolio_wins = period_portfolio_tr[
                period_portfolio_tr["% Portfolio Return"] > 0
            ]
            portfolio_loses = period_portfolio_tr[
                period_portfolio_tr["% Portfolio Return"] < 0
            ]
            gross_profit = portfolio_wins["Abs Portfolio Return"].sum()
            gross_loss = portfolio_loses["Abs Portfolio Return"].sum()
            vals.append([round(gross_profit / abs(gross_loss), 3)])
        else:
            vals.append(["-"])

    pf_period_df = pd.DataFrame(
        vals, index=portfolio_helper.PERIODS, columns=["Profit Factor"]
    )

    return pf_period_df


class PortfolioModel:
    """
    Class for portfolio analysis in OpenBB
    Implements a Portfolio and related methods.

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
        calculate_value: Calculate value from historical data

    calculate_reserves:

    calculate_allocations:

    set_risk_free_rate: Sets risk free rate

    calculate_metrics:

    """

    def __init__(self, orderbook: pd.DataFrame = pd.DataFrame()):
        """Initialize Portfolio class"""
        # Portfolio
        self.tickers_list = None
        self.tickers: Dict[Any, Any] = {}
        self.inception_date = None
        self.static_data = pd.DataFrame()
        self.historical_trade_data = pd.DataFrame()
        self.returns = pd.DataFrame()
        self.itemized_value = pd.DataFrame()
        self.portfolio_trades = pd.DataFrame()
        self.portfolio_value = None
        self.portfolio_assets_allocation = pd.DataFrame()
        self.portfolio_regional_allocation = pd.DataFrame()
        self.portfolio_country_allocation = pd.DataFrame()

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

        # Set and preprocess orderbook
        self.__set_orderbook(orderbook)

    def __set_orderbook(self, orderbook):
        self.__orderbook = orderbook
        self.preprocess_orderbook()

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

        # descrbibe outputs

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
                - self.__orderbook["Fees"]
            )

            # Reformat crypto tickers to yfinance format (e.g. BTC -> BTC-USD)
            crypto_trades = self.__orderbook[self.__orderbook.Type == "CRYPTO"]
            self.__orderbook.loc[(self.__orderbook.Type == "CRYPTO"), "Ticker"] = [
                f"{crypto}-{currency}"
                for crypto, currency in zip(
                    crypto_trades.Ticker, crypto_trades.Currency
                )
            ]

            # Create tickers dictionary with structure {'Type': [Ticker]}
            for ticker_type in set(self.__orderbook["Type"]):
                self.tickers[ticker_type] = list(
                    set(
                        self.__orderbook[self.__orderbook["Type"].isin([ticker_type])][
                            "Ticker"
                        ]
                    )
                )

            # Create list with tickers except cash
            self.tickers_list = list(set(self.__orderbook["Ticker"]))

            # Save orderbook inception date
            self.inception_date = self.__orderbook["Date"][0]

            # Save trades static data
            self.static_data = self.__orderbook.pivot(
                index="Ticker",
                columns=[],
                values=["Type", "Sector", "Industry", "Country"],
            )

        except Exception:
            console.print("Could not preprocess orderbook.")

    def load_benchmark(self, ticker: str = "SPY", full_shares: bool = False):
        """Adds benchmark dataframe

        Args:
            ticker (str): benchmark ticker to download data
            full_shares (bool): whether to mimic the portfolio trades exactly (partial shares) or round down the
            quantity to the nearest number.
        """
        self.benchmark_ticker = ticker
        self.benchmark_historical_prices = yf.download(
            ticker, start=self.inception_date, threads=False, progress=False
        )["Adj Close"]
        self.benchmark_returns = self.benchmark_historical_prices.pct_change().dropna()
        self.benchmark_info = yf.Ticker(ticker).info
        self.mimic_trades_for_benchmark(full_shares)

    def mimic_trades_for_benchmark(self, full_shares: bool = False):
        """Mimic trades from the orderbook based on chosen benchmark assuming partial shares"""
        # Create dataframe to store benchmark trades
        self.benchmark_trades = self.__orderbook[["Date", "Type", "Investment"]].copy()

        # Set current price of benchmark
        self.benchmark_trades["Last price"] = self.benchmark_historical_prices[-1]
        self.benchmark_trades[["Benchmark Quantity", "Trade price"]] = float(0)

        # Iterate over orderbook to replicate trades on benchmark
        for index, trade in self.__orderbook.iterrows():
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

            # Whether full shares are desired (thus no partial shares).
            if full_shares:
                self.benchmark_trades["Benchmark Quantity"][index] = np.floor(
                    trade["Investment"] / self.benchmark_trades["Trade price"][index]
                )
            else:
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

        if full_shares:
            console.print(
                "Note that with full shares (-s) enabled, there will be a mismatch between how much you invested in the"
                f" portfolio ({round(sum(self.portfolio_trades['Portfolio Investment']), 2)}) and how much you invested"
                f" in the benchmark ({round(sum(self.benchmark_trades['Benchmark Investment']), 2)})."
            )

    def generate_portfolio_data(self):
        """Generates portfolio data from orderbook"""
        self.load_portfolio_historical_prices()
        self.populate_historical_trade_data()
        self.calculate_value()

        # Determine the returns, replace inf values with NaN and then drop any missing values
        for _, data in self.tickers.items():
            self.historical_trade_data[
                pd.MultiIndex.from_product([["Returns"], data])
            ] = (
                self.historical_trade_data["End Value"][data]
                / self.historical_trade_data["Initial Value"][data]
                - 1
            )

        self.historical_trade_data.loc[:, ("Returns", "Total")] = (
            self.historical_trade_data["End Value"]["Total"]
            / self.historical_trade_data["Initial Value"]["Total"]
            - 1
        )

        self.returns = self.historical_trade_data["Returns"]["Total"]
        self.returns.replace([np.inf, -np.inf], np.nan, inplace=True)
        self.returns = self.returns.dropna()

        # Determine invested amount, relative and absolute return based on last close
        last_price = self.historical_trade_data["Close"].iloc[-1]

        self.portfolio_returns = pd.DataFrame(self.__orderbook["Date"])

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
            self.portfolio_trades["Close"][index] = last_price[trade["Ticker"]]
            self.portfolio_trades["Portfolio Investment"][index] = trade["Investment"]
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

        for ticker_type, data in self.tickers.items():
            if ticker_type in ["STOCK", "ETF", "CRYPTO"]:
                # Download yfinance data
                price_data = yf.download(
                    data, start=self.inception_date, progress=False
                )["Close" if use_close or ticker_type == "CRYPTO" else "Adj Close"]

                # Set up column name if only 1 ticker (pd.DataFrame only does this if >1 ticker)
                if len(data) == 1:
                    price_data = pd.DataFrame(price_data)
                    price_data.columns = data

                # Add to historical_prices dataframe
                self.portfolio_historical_prices = pd.concat(
                    [self.portfolio_historical_prices, price_data], axis=1
                )
            else:
                console.print("Type not supported in the orderbook.")

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

        trade_data["Investment"] = trade_data["Investment"].cumsum()

        trade_data.loc[:, ("Investment", "Total")] = trade_data["Investment"][
            self.tickers_list
        ].sum(axis=1)

        self.historical_trade_data = trade_data

    def calculate_value(self):
        """Calculate value from historical data"""
        trade_data = self.historical_trade_data

        # For each type [STOCK, ETF, etc] calculate value value by trade date
        # and add it to historical_trade_data

        # End Value
        for ticker_type, data in self.tickers.items():
            trade_data[pd.MultiIndex.from_product([["End Value"], data])] = (
                trade_data["Quantity"][data] * trade_data["Close"][data]
            )

        trade_data.loc[:, ("End Value", "Total")] = trade_data["End Value"][
            self.tickers_list
        ].sum(axis=1)

        self.portfolio_value = trade_data["End Value"]["Total"]

        for ticker_type, data in self.tickers.items():
            self.itemized_value[ticker_type] = trade_data["End Value"][data].sum(axis=1)

        # Initial Value = Cumulative Investment - (Previous End Value - Previous Initial Value)
        trade_data[
            pd.MultiIndex.from_product([["Initial Value"], self.tickers_list])
        ] = 0

        for i, date in enumerate(trade_data.index):
            if i == 0:
                for t in self.tickers_list:
                    trade_data.at[date, ("Initial Value", t)] = trade_data.iloc[i][
                        "Investment"
                    ][t]
            else:
                for t in self.tickers_list:
                    trade_data.at[date, ("Initial Value", t)] = (
                        +trade_data.iloc[i - 1]["End Value"][t]
                        + trade_data.iloc[i]["Investment"][t]
                        - trade_data.iloc[i - 1]["Investment"][t]
                    )

        trade_data.loc[:, ("Initial Value", "Total")] = trade_data["Initial Value"][
            self.tickers_list
        ].sum(axis=1)

        self.historical_trade_data = trade_data

    def calculate_reserves(self):
        """_summary_"""
        # TODO: Add back cash dividends and deduct exchange costs
        console.print("Still has to be build.")

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

        Parameters
        ----------
        risk_free (float): risk free rate in decimal format
        """
        self.risk_free_rate = risk_free_rate

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
                        sharpe_ratio(
                            portfolio_helper.filter_df_by_period(self.returns, period),
                            risk_free_rate,
                        ),
                        3,
                    ),
                    round(
                        sharpe_ratio(
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
                        sortino_ratio(
                            portfolio_helper.filter_df_by_period(self.returns, period),
                            risk_free_rate,
                        ),
                        3,
                    ),
                    round(
                        sortino_ratio(
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
                        get_maximum_drawdown(
                            portfolio_helper.filter_df_by_period(self.returns, period)
                        ),
                        3,
                    ),
                    round(
                        get_maximum_drawdown(
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
    def get_gaintopain_ratio(self):
        """Gets Pain-to-Gain ratio based on historical data

        Returns
        -------
        pd.DataFrame
            DataFrame of the portfolio's gain-to-pain ratio
        """
        gtp_period_df = get_gaintopain_ratio(self.returns, self.benchmark_returns)

        return gtp_period_df

    @log_start_end(log=logger)
    def get_rolling_beta(self, period: float = 252):
        """Get rolling beta

        Parameters
        ----------
        period: float
            Interval used for rolling values

        Returns
        -------
        pd.DataFrame
            DataFrame of the portfolio's rolling beta
        """
        rolling_beta = get_rolling_beta(self.returns, self.benchmark_returns, period)

        return rolling_beta

    @log_start_end(log=logger)
    def get_tracking_error(self, period: float = 252):
        """Get tracking error

        Parameters
        ----------
        period: float
            Interval used for rolling values

        Returns
        -------
        pd.DataFrame
            DataFrame of tracking errors during different time periods
        pd.Series
            Series of rolling tracking error
        """
        trackr_period_df, trackr_rolling = get_tracking_error(
            self.returns, self.benchmark_returns, period
        )

        return trackr_period_df, trackr_rolling

    @log_start_end(log=logger)
    def get_information_ratio(self, period: float = 252):
        """

        Parameters
        ----------
        period: float
            Interval used for rolling values

        Returns
        -------
        pd.DataFrame
            DataFrame of the information ratio during different time periods
        pd.Series
            Series of rolling information ratio
        """
        ir_period_df, ir_rolling = get_information_ratio(
            self.returns, self.benchmark_returns, period
        )

        return ir_period_df, ir_rolling

    @log_start_end(log=logger)
    def get_tail_ratio(self, period: float = 252):
        """

        Parameters
        ----------
        period: float
            Interval used for rolling values

        Returns
        -------
        pd.DataFrame
            DataFrame of the portfolios and the benchmarks tail ratio during different time periods
        pd.Series
            Series of the portfolios rolling tail ratio
        pd.Series
            Series of the benchmarks rolling tail ratio
        """
        tailr_period_df, portfolio_tr, benchmark_tr = get_tail_ratio(
            self.returns, self.benchmark_returns, period
        )

        return tailr_period_df, portfolio_tr, benchmark_tr

    @log_start_end(log=logger)
    def get_common_sense_ratio(self):
        """Get common sense ratio

        Returns
        -------
        pd.DataFrame
            DataFrame of the portfolios and the benchmarks common sense ratio during different time periods
        """
        csr_period_df = get_common_sense_ratio(self.returns, self.benchmark_returns)

        return csr_period_df

    @log_start_end(log=logger)
    def get_jensens_alpha(self, rf: float = 0, period: float = 252):
        """Get jensen's alpha

        Parameters
        ----------
        period: float
            Interval used for rolling values
        rf: float
            Risk free rate

        Returns
        -------
        pd.DataFrame
            DataFrame of jensens's alpha during different time periods
        pd.Series
            Series of jensens's alpha data
        """
        ja_period_df, ja_rolling = get_jensens_alpha(
            self.returns, self.benchmark_returns, rf, period
        )

        return ja_period_df, ja_rolling

    @log_start_end(log=logger)
    def get_calmar_ratio(self, period: float = 756):
        """Get calmar ratio

        Parameters
        ----------
        period: float
            Interval used for rolling values

        Returns
        -------
        pd.DataFrame
            DataFrame of calmar ratio of the benchmark and portfolio during different time periods
        pd.Series
            Series of calmar ratio data
        """
        cr_period_df, cr_rolling = get_calmar_ratio(
            self.returns, self.benchmark_returns, period
        )

        return cr_period_df, cr_rolling

    @log_start_end(log=logger)
    def get_kelly_criterion(self):
        """Gets kelly criterion

        Returns
        -------
        pd.DataFrame
            DataFrame of kelly criterion of the portfolio during different time periods
        """
        kc_period_df = get_kelly_criterion(self.returns, self.portfolio_trades)

        return kc_period_df

    @log_start_end(log=logger)
    def get_payoff_ratio(self):
        """Gets payoff ratio

        Returns
        -------
        pd.DataFrame
            DataFrame of payoff ratio of the portfolio during different time periods
        """
        pr_period_ratio = get_payoff_ratio(self.portfolio_trades)

        return pr_period_ratio

    @log_start_end(log=logger)
    def get_profit_factor(self):
        """Gets profit factor

        Returns
        -------
        pd.DataFrame
            DataFrame of profit factor of the portfolio during different time periods
        """
        pf_period_df = get_profit_factor(self.portfolio_trades)

        return pf_period_df


def rolling_volatility(returns: pd.DataFrame, length: int) -> pd.DataFrame:
    """Get rolling volatility

    Parameters
    ----------
    returns : pd.DataFrame
        Returns series
    length : int
        Rolling window to use

    Returns
    -------
    pd.DataFrame
        Rolling volatility DataFrame
    """
    return returns.rolling(length).std()


def sharpe_ratio(return_series: pd.Series, risk_free_rate: float) -> float:
    """Get sharpe ratio

    Parameters
    ----------
    return_series : pd.Series
        Returns of the portfolio
    risk_free_rate: float
        Value to use for risk free rate

    Returns
    -------
    float
        Sharpe ratio
    """
    mean = return_series.mean() - risk_free_rate
    sigma = return_series.std()

    return mean / sigma


def rolling_sharpe(
    returns: pd.DataFrame, risk_free_rate: float, length: int
) -> pd.DataFrame:
    """Get rolling sharpe ratio

    Parameters
    ----------
    returns : pd.DataFrame
        Returns series
    risk_free_rate : float
        Risk free rate
    length : int
        Rolling window to use

    Returns
    -------
    pd.DataFrame
        Rolling sharpe ratio DataFrame
    """
    rolling_sharpe_df = returns.rolling(length).apply(
        lambda x: (x.mean() - risk_free_rate) / x.std()
    )
    return rolling_sharpe_df


def sortino_ratio(return_series: pd.Series, risk_free_rate: float) -> float:
    """Get sortino ratio

    Parameters
    ----------
    return_series : pd.Series
        Returns of the portfolio
    risk_free_rate: float
        Value to use for risk free rate

    Returns
    -------
    float
        Sortino ratio
    """
    mean = return_series.mean() - risk_free_rate
    std_neg = return_series[return_series < 0].std()

    return mean / std_neg


def rolling_sortino(
    returns: pd.DataFrame, risk_free_rate: float, length: int
) -> pd.DataFrame:
    """Get rolling sortino ratio

    Parameters
    ----------
    returns : pd.DataFrame
        Returns series
    risk_free_rate : float
        Risk free rate
    length : int
        Rolling window to use

    Returns
    -------
    pd.DataFrame
        Rolling sortino ratio DataFrame
    """
    rolling_sortino_df = returns.rolling(length).apply(
        lambda x: (x.mean() - risk_free_rate) / x[x < 0].std()
    )

    return rolling_sortino_df


def get_maximum_drawdown(return_series: pd.Series) -> float:
    """Get maximum drawdown

    Parameters
    ----------
    return_series : pd.Series
        Returns of the portfolio

    Returns
    -------
    float
        maximum drawdown
    """
    comp_ret = (return_series + 1).cumprod()
    peak = comp_ret.expanding(min_periods=1).max()
    dd = (comp_ret / peak) - 1

    return dd.min()
