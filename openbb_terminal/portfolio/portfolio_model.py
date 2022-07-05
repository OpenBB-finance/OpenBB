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

# pylint: disable=E1136,W0201,R0902,C0302
# pylint: disable=unsupported-assignment-operation
logger = logging.getLogger(__name__)
cg = CoinGeckoAPI()

pd.options.mode.chained_assignment = None


@log_start_end(log=logger)
def get_rolling_beta2(
    df: pd.DataFrame, hist: pd.DataFrame, mark: pd.DataFrame, n: pd.DataFrame
) -> pd.DataFrame:
    """Turns the holdings of a portfolio into a rolling beta dataframe

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
        A Dataframe with rolling beta
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
                        / portfolio_helper.get_maximum_drawdown(period_return),
                        3,
                    ),
                    round(
                        (
                            (
                                1 + period_bench_return.shift(periods=1, fill_value=0)
                            ).cumprod()
                            - 1
                        ).iloc[-1]
                        / portfolio_helper.get_maximum_drawdown(period_bench_return),
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
                        / portfolio_helper.get_maximum_drawdown(period_return),
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
                        / portfolio_helper.get_maximum_drawdown(period_bench_return),
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

    cr_rolling = annual_return / portfolio_helper.get_maximum_drawdown(returns)

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
            drawdown = portfolio_helper.get_maximum_drawdown(period_return)
            bench_drawdown = portfolio_helper.get_maximum_drawdown(period_bench_return)
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


class Portfolio:
    """
    Class for portfolio analysis in OpenBB

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
    def __init__(self, trades: pd.DataFrame = pd.DataFrame(), rf: float = 0.0):
        """Initialize Portfolio class"""
        # Allow for empty initialization
        self.benchmark_ticker: str = ""
        self.benchmark_info = None
        self.benchmark: pd.DataFrame = pd.DataFrame()
        self._historical_crypto: pd.DataFrame = pd.DataFrame()
        self._historical_prices: pd.DataFrame = pd.DataFrame()
        self.returns: pd.Series = pd.Series(dtype=object)
        self.portfolio_value = None
        self.ItemizedHoldings = None
        self.benchmark_returns: pd.Series = pd.Series(dtype=object)
        self.portfolio_sectors_allocation = pd.DataFrame()
        self.portfolio_assets_allocation = pd.DataFrame()
        self.benchmark_sectors_allocation = pd.DataFrame()
        self.benchmark_assets_allocation = pd.DataFrame()
        self.benchmark_trades = pd.DataFrame()
        self.portfolio_trades = pd.DataFrame()
        self.last_price = pd.DataFrame()
        self.empty = True
        self.rf = rf

        if not trades.empty:
            trades.Name = trades.Name.map(lambda x: x.upper())
            trades.Type = trades.Type.map(lambda x: x.upper())

            # Load in trades df and do some quick editing
            trades["Side"] = trades["Side"].map(
                lambda x: 1
                if x.lower() in ["deposit", "buy"]
                else (-1 if x.lower() in ["withdrawal", "sell"] else 0)
            )

            # Determining the investment value
            trades["Investment"] = trades.Quantity * trades.Price * trades.Side

            if "CASH" not in trades.Name.to_list():
                logger.warning(
                    "No initial cash deposit. Calculations may be off as this assumes trading from a "
                    "funded account"
                )
                console.print(
                    "[red]No initial cash deposit. Calculations may be off as this assumes trading from a "
                    "funded account[/red]."
                )

            # Make selling negative for cumulative sum of quantity later
            trades["Quantity"] = trades["Quantity"] * trades["Side"]

            # Should be simply extended for crypto/bonds etc
            # Treat etf as stock for yfinance historical.
            self._stock_tickers = list(
                set(trades[trades.Type == "STOCK"].Name.to_list())
            )
            self._etf_tickers = list(set(trades[trades.Type == "ETF"].Name.to_list()))

            crypto_trades = trades[trades.Type == "CRYPTO"]
            self._crypto_tickers = [
                f"{crypto}-{currency}"
                for crypto, currency in zip(crypto_trades.Name, crypto_trades.Currency)
            ]
            trades.loc[(trades.Type == "CRYPTO"), "Name"] = self._crypto_tickers
            self._start_date = trades.Date[0]

            # Copy pandas notation
            self.empty = False

            # Adjust date of trades
            trades["Date"] = pd.DatetimeIndex(trades["Date"])

        self.trades = trades
        self.portfolio = pd.DataFrame()

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

        # Add holdings for each 'type'. Will check for tickers matching type.

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

        # Find amount of cash held in account. If CASH does not exist within the Orderbook,
        # the cash hold will equal the invested amount. Otherwise, the cash hold is defined as deposited cash -
        # stocks bought + stocks sold
        if "CASH" not in portfolio["Investment"]:
            portfolio["CashHold"] = (
                portfolio["Investment"][
                    self._stock_tickers + self._etf_tickers + self._crypto_tickers
                ].sum(axis=1)
                + portfolio["Fees"].sum(axis=1)
                + portfolio["Premium"].sum(axis=1)
            )
        else:
            portfolio["CashHold"] = portfolio["Investment"]["CASH"] - portfolio[
                "Investment"
            ][self._stock_tickers + self._etf_tickers + self._crypto_tickers].sum(
                axis=1
            )

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

        # Determine the returns, replace inf values with NaN and then drop any missing values
        returns = portfolio["TotalHoldings"].pct_change()
        returns.replace([np.inf, -np.inf], np.nan, inplace=True)
        self.returns = returns.dropna()

        # Update all period
        portfolio_helper.PERIODS_DAYS["all"] = len(self.returns)

        self.ItemizedHoldings = pd.DataFrame(
            {
                "Stocks": portfolio["StockHoldings"][self._stock_tickers].sum(axis=1),
                "ETFs": portfolio["ETFHoldings"][self._etf_tickers].sum(axis=1),
                "Crypto": portfolio["CryptoHoldings"][self._crypto_tickers].sum(axis=1),
                "Cash": portfolio["CashHold"],
            }
        )

        # Determine invested amount, relative and absolute return based on last close
        self.last_price = portfolio["Close"].iloc[-1]
        self.portfolio_trades = self.trades.copy()
        self.portfolio_trades[
            [
                "Portfolio Investment",
                "Close",
                "Portfolio Value",
                "% Portfolio Return",
                "Abs Portfolio Return",
            ]
        ] = float(0)

        for index, trade in self.trades.iterrows():
            if trade["Type"] != "CASH":
                self.portfolio_trades["Close"][index] = self.last_price[trade["Name"]]
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
        """Gets historical coin data from yfinance"""
        if self._crypto_tickers:
            self._historical_crypto = yf.download(
                self._crypto_tickers, start=self._start_date, progress=False
            )["Close"]

            if len(self._crypto_tickers) == 1:
                self._historical_crypto = pd.DataFrame(self._historical_crypto)
                self._historical_crypto.columns = self._crypto_tickers

            self._historical_crypto.columns = pd.MultiIndex.from_product(
                [["Close"], self._crypto_tickers]
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

        self.benchmark_info = yf.Ticker(benchmark).info

        self.benchmark_ticker = benchmark

    @log_start_end(log=logger)
    def mimic_portfolio_trades_for_benchmark(self, full_shares: bool = False):
        """Mimic trades from the orderbook as good as possible based on chosen benchmark. The assumption is that the
        benchmark is always tradable and allows for partial shares. This eliminates the need to keep track of a cash
        position due to a mismatch in trades"""

        if full_shares:
            console.print(
                "[red]Note that without the partial shares assumption, the absolute return will be incorrect "
                "due to the model not taking into account the remaining cash position.[/red]"
            )

        self.benchmark_trades = self.trades[["Date", "Type", "Investment"]].copy()
        self.benchmark_trades["Close"] = self.benchmark[-1]
        self.benchmark_trades[
            [
                "Benchmark Quantity",
                "Price",
                "Benchmark Investment",
                "Benchmark Value",
                "% Benchmark Return",
                "Abs Benchmark Return",
            ]
        ] = float(0)

        for index, trade in self.trades.iterrows():
            if trade["Type"] != "CASH":
                if trade["Date"] not in self.benchmark.index:
                    date = self.benchmark.index.searchsorted(trade["Date"])
                else:
                    date = trade["Date"]

                self.benchmark_trades["Price"][index] = self.benchmark[date]

                if not full_shares:
                    self.benchmark_trades["Benchmark Quantity"][index] = (
                        trade["Investment"] / self.benchmark_trades["Price"][index]
                    )
                else:
                    self.benchmark_trades["Benchmark Quantity"][index] = np.floor(
                        trade["Investment"] / self.benchmark_trades["Price"][index]
                    )

                self.benchmark_trades["Benchmark Investment"][index] = (
                    self.benchmark_trades["Price"][index]
                    * self.benchmark_trades["Benchmark Quantity"][index]
                )
                self.benchmark_trades["Benchmark Value"][index] = (
                    self.benchmark_trades["Close"][index]
                    * self.benchmark_trades["Benchmark Quantity"][index]
                )
                self.benchmark_trades["% Benchmark Return"][index] = (
                    self.benchmark_trades["Benchmark Value"][index]
                    / self.benchmark_trades["Benchmark Investment"][index]
                ) - 1
                self.benchmark_trades["Abs Benchmark Return"][index] = (
                    self.benchmark_trades["Benchmark Value"][index]
                    - self.benchmark_trades["Benchmark Investment"][index]
                )

    # pylint:disable=no-member
    @log_start_end(log=logger)
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

    # pylint:disable=no-member
    @classmethod
    @log_start_end(log=logger)
    def from_xlsx(cls, xlsx_path: str):
        """Class method that generates a portfolio object from a xlsx file

        Parameters
        ----------
        xlsx_path: str
            Path to xlsx of trade data

        Returns
        -------
        Portfolio
            Initialized portfolio object
        """
        # Load in a list of trades
        trades = pd.read_excel(xlsx_path)

        # Convert the date to what pandas understands
        trades.Date = pd.to_datetime(trades.Date)

        # Sort by date to make more sense of trades
        trades = trades.sort_values(by="Date")

        # Build the portfolio object
        return cls(trades)

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
