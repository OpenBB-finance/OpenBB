"""Portfolio Model"""
__docformat__ = "numpy"

import logging
from typing import Dict, Any, Tuple

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
def get_main_text(data: pd.DataFrame) -> str:
    """Get main performance summary from a dataframe with market returns

    Parameters
    ----------
    data : pd.DataFrame
        Stock holdings and returns with market returns

    Returns
    ----------
    text : str
        The main summary of performance
    """
    d_debt = np.where(data[("Cash", "Cash")] > 0, 0, 1)
    bcash = 0 if data[("Cash", "Cash")][0] > 0 else abs(data[("Cash", "Cash")][0])
    ecash = 0 if data[("Cash", "Cash")][-1] > 0 else abs(data[("Cash", "Cash")][-1])
    bdte = bcash / (data["holdings"][0] - bcash)
    edte = ecash / (data["holdings"][-1] - ecash)
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
        f"Your portfolio's performance for the period was {data['return'][-1]:.2%}. This was"
        f" {'greater' if data['return'][-1] > data[('Market', 'Return')][-1] else 'less'} than"
        f" the market return of {data[('Market', 'Return')][-1]:.2%}. The variance for the"
        f" portfolio is {np.var(data['return']):.2%}, while the variance for the market was"
        f" {np.var(data[('Market', 'Return')]):.2%}. {t_debt} The following report details"
        f" various analytics from the portfolio. Read below to see the moving beta for a"
        f" stock."
    )
    return text


@log_start_end(log=logger)
def get_beta_text(data: pd.DataFrame) -> str:
    """Get beta summary for a stock from a dataframe

    Parameters
    ----------
    data : pd.DataFrame
        The beta history of the stock

    Returns
    ----------
    text : str
        The beta history for a ticker
    """
    betas = data[list(filter(lambda score: "beta" in score, list(data.columns)))]
    high = betas.idxmax(axis=1)
    low = betas.idxmin(axis=1)
    text = (
        "Beta is how strongly a portfolio's movements correlate with the market's movements."
        " A stock with a high beta is considered to be riskier. The beginning beta for the period"
        f" was {portfolio_helper.beta_word(data['total'][0])} at {data['total'][0]:.2f}. This went"
        f" {'up' if data['total'][-1] > data['total'][0] else 'down'} to"
        f" {portfolio_helper.beta_word(data['total'][-1])} at {data['total'][-1]:.2f} by the end"
        f" of the period. The ending beta was pulled {'up' if data['total'][-1] > 1 else 'down'} by"
        f" {portfolio_helper.clean_name(high[-1] if data['total'][-1] > 1 else low[-1])}, which had"
        f" an ending beta of {data[high[-1]][-1] if data['total'][-1] > 1 else data[low[-1]][-1]:.2f}."
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
def calculate_drawdown(data: pd.Series, is_returns: bool = False) -> pd.Series:
    """Calculate the drawdown (MDD) of historical series.  Note that the calculation is done
     on cumulative returns (or prices).  The definition of drawdown is

     DD = (current value - rolling maximum) / rolling maximum

    Parameters
    ----------
    data: pd.Series
        Series of input values
    is_returns: bool
        Flag to indicate inputs are returns

    Returns
    ----------
    pd.Series
        Drawdown series
    -------
    """
    if is_returns:
        data = (1 + data).cumprod()

    rolling_max = data.cummax()
    drawdown = (data - rolling_max) / rolling_max

    return drawdown


def cumulative_returns(data: pd.Series) -> pd.Series:
    """Calculate cumulative returns filtered by period

    Parameters
    ----------
    data : pd.Series
        Series of portfolio returns

    Returns
    ----------
    pd.Series
        Cumulative investment returns series
    -------
    """
    cumulative_returns = (1 + data.shift(periods=1, fill_value=0)).cumprod() - 1
    return cumulative_returns


@log_start_end(log=logger)
def get_gaintopain_ratio(
    historical_trade_data: pd.DataFrame,
    benchmark_trades: pd.DataFrame,
    benchmark_returns: pd.DataFrame,
) -> pd.DataFrame:
    """Gets Pain-to-Gain ratio

    Parameters
    ----------
    historical_trade_data: pd.DataFrame
        Dataframe of historical data for the portfolios trade
    benchmark_trades: pd.DataFrame
        Dataframe of the benchmark's trades
    benchmark_returns: pd.DataFrame
        Dataframe of benchmark returns

    Returns
    -------
    pd.DataFrame
            DataFrame of the portfolio's gain-to-pain ratio
    """
    benchmark_trades = benchmark_trades.set_index("Date")
    vals = list()
    for period in portfolio_helper.PERIODS:
        period_historical_trade_data = portfolio_helper.filter_df_by_period(
            historical_trade_data, period
        )
        period_bench_trades = portfolio_helper.filter_df_by_period(
            benchmark_trades, period
        )
        period_bench_return = portfolio_helper.filter_df_by_period(
            benchmark_returns, period
        )
        if not period_historical_trade_data.empty:
            if not period_bench_trades.empty:
                benchmark_values = (
                    period_bench_trades["Benchmark Value"].sum()
                    / period_bench_trades["Benchmark Investment"].sum()
                    - 1
                ) / get_maximum_drawdown(period_bench_return)
            else:
                benchmark_values = ((1 + period_bench_return).cumprod() - 1).iloc[
                    -1
                ] / get_maximum_drawdown(period_bench_return)
            vals.append(
                [
                    round(
                        (
                            period_historical_trade_data["End Value"]["Total"].iloc[-1]
                            / (
                                period_historical_trade_data["Initial Value"][
                                    "Total"
                                ].iloc[0]
                                + period_historical_trade_data["Investment"][
                                    "Total"
                                ].iloc[-1]
                                - period_historical_trade_data["Investment"][
                                    "Total"
                                ].iloc[0]
                            )
                            - 1
                        )
                        / get_maximum_drawdown(
                            period_historical_trade_data["Returns"]["Total"]
                        ),
                        3,
                    ),
                    round(
                        benchmark_values,
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
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    period: str = "1y",
) -> pd.DataFrame:
    """Get rolling beta using portfolio and benchmark returns

    Parameters
    ----------
    returns: pd.Series
        Series of portfolio returns
    benchmark_returns: pd.Series
        Series of benchmark returns
    period: string
        Interval used for rolling values.
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y.

    Returns
    -------
    pd.DataFrame
        DataFrame of the portfolio's rolling beta
    """

    length = portfolio_helper.PERIODS_DAYS[period]

    covs = (
        pd.DataFrame({"Portfolio": portfolio_returns, "Benchmark": benchmark_returns})
        .dropna(axis=0)
        .rolling(max(1, length))
        .cov()
        .unstack()
        .dropna()
    )

    rolling_beta = covs["Portfolio"]["Benchmark"] / covs["Benchmark"]["Benchmark"]

    return rolling_beta


@log_start_end(log=logger)
def calculate_beta(portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """Calculates the beta using portfolio and benchmark return values

    Parameters
    ----------
    portfolio_returns: pd.Series
        Series of portfolio returns
    benchmark_returns: pd.Series
        Series of benchmark returns

    Returns
    -------
    float
        The calculated beta value
    """
    axis_diff = len(portfolio_returns) - len(benchmark_returns)
    axis_diff_bench = 0
    if axis_diff < 0:
        axis_diff_bench = -axis_diff
        axis_diff = 0

    covariance = np.cov(
        portfolio_returns[axis_diff:], benchmark_returns[axis_diff_bench:]
    )[0][1]
    variance = portfolio_returns.var()

    return covariance / variance


@log_start_end(log=logger)
def get_tracking_error(
    portfolio_returns: pd.Series, benchmark_returns: pd.Series, window: str = "252d"
) -> Tuple[pd.DataFrame, pd.Series]:
    """Get tracking error, or active risk, using portfolio and benchmark returns

    Parameters
    ----------
    portfolio_returns: pd.Series
        Series of portfolio returns
    benchmark_returns: pd.Series
        Series of benchmark returns
    window: string
        Interval used for rolling values in days.
        Examples: 1d, 5d, 10d

    Returns
    -------
    pd.DataFrame
        DataFrame of tracking errors during different time periods
    pd.Series
        Series of rolling tracking error
    """
    diff_returns = portfolio_returns - benchmark_returns

    tracker_rolling = diff_returns.rolling(window).std()

    vals = list()
    for periods in portfolio_helper.PERIODS:
        period_return = portfolio_helper.filter_df_by_period(diff_returns, periods)
        if not period_return.empty:
            vals.append([round(period_return.std(), 3)])
        else:
            vals.append(["-"])
    tracker_period_df = pd.DataFrame(
        vals, index=portfolio_helper.PERIODS, columns=["Tracking Error"]
    )

    return tracker_period_df, tracker_rolling


@log_start_end(log=logger)
def get_information_ratio(
    portfolio_returns: pd.Series,
    historical_trade_data: pd.DataFrame,
    benchmark_trades: pd.DataFrame,
    benchmark_returns: pd.Series,
) -> pd.DataFrame:
    """Calculates information ratio, which measures the active return of an investment
    compared to the benchmark relative to the volatility of the active return

    Parameters
    ----------
    portfolio_returns: pd.Series
        Series of portfolio returns
    historical_trade_data: pd.DataFrame
        Dataframe of historical data for the portfolio's trade
    benchmark_trades: pd.DataFrame
        Dataframe of the benchmark's trades
    benchmark_returns: pd.Series
        Series of benchmark returns

    Returns
    -------
    pd.DataFrame
        DataFrame of the information ratio during different time periods
    """
    tracking_err_df, _ = get_tracking_error(portfolio_returns, benchmark_returns)
    benchmark_trades = benchmark_trades.set_index("Date")
    vals = list()
    for periods in portfolio_helper.PERIODS:
        period_historical_trade_data = portfolio_helper.filter_df_by_period(
            historical_trade_data, periods
        )
        period_bench_trades = portfolio_helper.filter_df_by_period(
            benchmark_trades, periods
        )
        period_bench_return = portfolio_helper.filter_df_by_period(
            benchmark_returns, periods
        )
        if not period_historical_trade_data.empty:
            if not period_bench_trades.empty:
                period_bench_total_return = (
                    period_bench_trades["Benchmark Value"].sum()
                    / period_bench_trades["Benchmark Investment"].sum()
                    - 1
                )
            else:
                period_bench_total_return = (
                    (1 + period_bench_return).cumprod() - 1
                ).iloc[-1]
            vals.append(
                [
                    round(
                        (
                            (
                                period_historical_trade_data["End Value"]["Total"].iloc[
                                    -1
                                ]
                                / (
                                    period_historical_trade_data["Initial Value"][
                                        "Total"
                                    ].iloc[0]
                                    + period_historical_trade_data["Investment"][
                                        "Total"
                                    ].iloc[-1]
                                    - period_historical_trade_data["Investment"][
                                        "Total"
                                    ].iloc[0]
                                )
                                - 1
                            )
                            - period_bench_total_return
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

    return ir_period_df


@log_start_end(log=logger)
def get_tail_ratio(
    portfolio_returns: pd.Series, benchmark_returns: pd.Series, window: str = "252d"
) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Returns the portfolios tail ratio

    Parameters
    ----------
    portfolio_returns: pd.Series
        Series of portfolio returns
    benchmark_returns: pd.Series
        Series of benchmark returns
    window: string
        Interval used for rolling values in days.
        Examples: 1d, 5d, 10d

    Returns
    -------
    pd.DataFrame
        DataFrame of the portfolios and the benchmarks tail ratio during different time periods
    pd.Series
        Series of the portfolios rolling tail ratio
    pd.Series
        Series of the benchmarks rolling tail ratio
    """
    returns_r = portfolio_returns.rolling(window)
    benchmark_returns_r = benchmark_returns.rolling(window)

    portfolio_tr = returns_r.quantile(0.95) / abs(returns_r.quantile(0.05))
    benchmark_tr = benchmark_returns_r.quantile(0.95) / abs(
        benchmark_returns_r.quantile(0.05)
    )

    vals = list()
    for periods in portfolio_helper.PERIODS:
        period_return = portfolio_helper.filter_df_by_period(portfolio_returns, periods)
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
def get_common_sense_ratio(
    portfolio_returns: pd.Series,
    historical_trade_data: pd.DataFrame,
    benchmark_trades: pd.DataFrame,
    benchmark_returns: pd.Series,
) -> pd.DataFrame:
    """Get common sense ratio

    Parameters
    ----------
    portfolio_returns: pd.Series
        Series of portfolio returns
    historical_trade_data: pd.DataFrame
        Dataframe of historical data for the portfolios trade
    benchmark_trades: pd.DataFrame
        Dataframe of the benchmarks trades
    benchmark_returns: pd.Series
        Series of benchmark returns

    Returns
    -------
    pd.DataFrame
        DataFrame of the portfolios and the benchmarks common sense ratio during different time periods
    """
    tail_ratio_df, _, _ = get_tail_ratio(portfolio_returns, benchmark_returns)
    gaintopain_ratio_df = get_gaintopain_ratio(
        historical_trade_data, benchmark_trades, benchmark_returns
    )

    vals = list()
    for period in portfolio_helper.PERIODS:
        vals.append(
            [
                round(
                    tail_ratio_df.loc[period, "Portfolio"]
                    * gaintopain_ratio_df.loc[period, "Portfolio"],
                    3,
                ),
                round(
                    tail_ratio_df.loc[period, "Benchmark"]
                    * gaintopain_ratio_df.loc[period, "Benchmark"],
                    3,
                ),
            ]
        )

    csr_period_df = pd.DataFrame(
        vals, index=portfolio_helper.PERIODS, columns=["Portfolio", "Benchmark"]
    )

    return csr_period_df


@log_start_end(log=logger)
def get_jensens_alpha(
    portfolio_returns: pd.Series,
    historical_trade_data: pd.DataFrame,
    benchmark_trades: pd.DataFrame,
    benchmark_returns: pd.Series,
    rf: float = 0,
    window: str = "1y",
) -> Tuple[pd.DataFrame, pd.Series]:
    """Get jensen's alpha

    Parameters
    ----------
    portfolio_returns: pd.Series
        Series of portfolio returns
    historical_trade_data: pd.DataFrame
        Dataframe of historical data for the portfolios trade
    benchmark_trades: pd.DataFrame
        Dataframe of the benchmarks trades
    benchmark_returns: pd.Series
        Series of benchmark returns
    rf: float
        Risk free rate
    window: str
        Interval used for rolling values.
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y.

    Returns
    -------
    pd.DataFrame
        DataFrame of jensens's alpha during different time periods
    pd.Series
        Series of jensens's alpha data
    """
    length = portfolio_helper.PERIODS_DAYS[window]
    periods_d = portfolio_helper.PERIODS_DAYS

    period_cum_returns = (1.0 + portfolio_returns).rolling(window=window).agg(
        lambda x: x.prod()
    ) - 1
    period_cum_bench_returns = (1.0 + benchmark_returns).rolling(window=window).agg(
        lambda x: x.prod()
    ) - 1
    rfr_cum_returns = rf * length / 252
    beta = get_rolling_beta(portfolio_returns, benchmark_returns, length)
    ja_rolling = period_cum_returns - (
        rfr_cum_returns + beta * (period_cum_bench_returns - rfr_cum_returns)
    )

    benchmark_trades = benchmark_trades.set_index("Date")
    vals = list()
    for periods in portfolio_helper.PERIODS:
        period_return = portfolio_helper.filter_df_by_period(portfolio_returns, periods)
        period_bench_return = portfolio_helper.filter_df_by_period(
            benchmark_returns, periods
        )
        period_historical_trade_data = portfolio_helper.filter_df_by_period(
            historical_trade_data, periods
        )
        period_bench_trades = portfolio_helper.filter_df_by_period(
            benchmark_trades, periods
        )
        if not period_return.empty:
            beta = calculate_beta(period_return, period_bench_return)
            period_cum_returns = (
                period_historical_trade_data["End Value"]["Total"].iloc[-1]
                / (
                    period_historical_trade_data["Initial Value"]["Total"].iloc[0]
                    + period_historical_trade_data["Investment"]["Total"].iloc[-1]
                    - period_historical_trade_data["Investment"]["Total"].iloc[0]
                )
                - 1
            )
            if not period_bench_trades.empty:
                period_bench_total_return = (
                    period_bench_trades["Benchmark Value"].sum()
                    / period_bench_trades["Benchmark Investment"].sum()
                    - 1
                )
            else:
                period_bench_total_return = (
                    (1 + period_bench_return).cumprod() - 1
                ).iloc[-1]
            rfr_cum_returns = rf * periods_d[periods] / 252
            vals.append(
                [
                    round(
                        period_cum_returns
                        - (
                            rfr_cum_returns
                            + beta * (period_bench_total_return - rfr_cum_returns)
                        ),
                        3,
                    )
                ]
            )
        else:
            vals.append(["-"])

    ja_period_df = pd.DataFrame(
        vals, index=portfolio_helper.PERIODS, columns=["Portfolio"]
    )

    return ja_period_df, ja_rolling


@log_start_end(log=logger)
def get_calmar_ratio(
    portfolio_returns: pd.Series,
    historical_trade_data: pd.DataFrame,
    benchmark_trades: pd.DataFrame,
    benchmark_returns: pd.Series,
    window: str = "3y",
) -> Tuple[pd.DataFrame, pd.Series]:
    """Get calmar ratio

    Parameters
    ----------
    portfolio_returns: pd.Serires
        Series of portfolio returns
    historical_trade_data: pd.DataFrame
        Dataframe of historical data for the portfolios trade
    benchmark_trades: pd.DataFrame
        Dataframe of the benchmarks trades
    benchmark_returns: pd.DataFrame
        Series of benchmark returns
    window: str
        Interval used for rolling values.
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y.

    Returns
    -------
    pd.DataFrame
        DataFrame of calmar ratio of the benchmark and portfolio during different time periods
    pd.Series
        Series of calmar ratio data
    """
    periods_d = portfolio_helper.PERIODS_DAYS
    period_cum_returns = (1.0 + portfolio_returns).rolling(window=window).agg(
        lambda x: x.prod()
    ) - 1

    # Calculate annual return
    annual_return = period_cum_returns ** (1 / (int(window) / 252)) - 1

    cr_rolling = annual_return / get_maximum_drawdown(portfolio_returns)

    benchmark_trades = benchmark_trades.set_index("Date")
    vals = list()
    for periods in portfolio_helper.PERIODS:
        period_return = portfolio_helper.filter_df_by_period(portfolio_returns, periods)
        period_historical_trade_data = portfolio_helper.filter_df_by_period(
            historical_trade_data, periods
        )
        period_bench_trades = portfolio_helper.filter_df_by_period(
            benchmark_trades, periods
        )
        period_bench_return = portfolio_helper.filter_df_by_period(
            benchmark_returns, periods
        )
        if (not period_return.empty) and (periods_d[periods] != 0):
            period_cum_returns = (
                period_historical_trade_data["End Value"]["Total"].iloc[-1]
                / (
                    period_historical_trade_data["Initial Value"]["Total"].iloc[0]
                    + period_historical_trade_data["Investment"]["Total"].iloc[-1]
                    - period_historical_trade_data["Investment"]["Total"].iloc[0]
                )
                - 1
            )
            if not period_bench_trades.empty:
                period_bench_total_return = (
                    period_bench_trades["Benchmark Value"].sum()
                    / period_bench_trades["Benchmark Investment"].sum()
                    - 1
                )
            else:
                period_bench_total_return = (
                    (1 + period_bench_return).cumprod() - 1
                ).iloc[-1]
            annual_return = (1 + period_cum_returns) ** (
                1 / (len(period_return) / 252)
            ) - 1
            annual_bench_return = (1 + period_bench_total_return) ** (
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
def get_kelly_criterion(
    portfolio_returns: pd.Series, portfolio_trades: pd.DataFrame
) -> pd.DataFrame:
    """Gets kelly criterion

    Parameters
    ----------
    portfolio_returns: pd.Series
        DataFrame of portfolio returns
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
        period_return = portfolio_helper.filter_df_by_period(portfolio_returns, period)
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
def get_payoff_ratio(portfolio_trades: pd.DataFrame) -> pd.DataFrame:
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

    no_losses = False

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
            if portfolio_loses.empty:
                vals.append(["-"])
                no_losses = True
                continue
            avg_w = portfolio_wins["Abs Portfolio Return"].mean()
            avg_l = portfolio_loses["Abs Portfolio Return"].mean()
            vals.append(
                [round(avg_w / abs(avg_l), 3)] if avg_w is not np.nan else ["0"]
            )
        else:
            vals.append(["-"])

    if no_losses:
        console.print(
            "During some time periods there were no losing trades. Thus some values could not be calculated."
        )

    pr_period_ratio = pd.DataFrame(
        vals, index=portfolio_helper.PERIODS, columns=["Payoff Ratio"]
    ).fillna("-")

    return pr_period_ratio


@log_start_end(log=logger)
def get_profit_factor(portfolio_trades: pd.DataFrame) -> pd.DataFrame:
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

    no_losses = False

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
            if portfolio_loses.empty:
                vals.append(["-"])
                no_losses = True
                continue
            gross_profit = portfolio_wins["Abs Portfolio Return"].sum()
            gross_loss = portfolio_loses["Abs Portfolio Return"].sum()
            vals.append([round(gross_profit / abs(gross_loss), 3)])
        else:
            vals.append(["-"])

    if no_losses:
        console.print(
            "During some time periods there were no losing trades. Thus some values could not be calculated."
        )

    pf_period_df = pd.DataFrame(
        vals, index=portfolio_helper.PERIODS, columns=["Profit Factor"]
    ).fillna("-")

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
        self.portfolio_historical_prices = pd.DataFrame()
        self.empty = True

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
        if not orderbook.empty:
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

        # descrbibe outputs

        try:
            console.print(" Preprocessing orderbook: ", end="")
            # Convert Date to datetime
            self.__orderbook["Date"] = pd.to_datetime(self.__orderbook["Date"])
            console.print(".", end="")

            # Sort orderbook by date
            self.__orderbook = self.__orderbook.sort_values(by="Date")
            console.print(".", end="")

            # Capitalize Ticker and Type [of instrument...]
            self.__orderbook["Ticker"] = self.__orderbook["Ticker"].map(
                lambda x: x.upper()
            )
            self.__orderbook["Type"] = self.__orderbook["Type"].map(lambda x: x.upper())
            console.print(".", end="")

            # Translate side: ["deposit", "buy"] -> 1 and ["withdrawal", "sell"] -> -1
            self.__orderbook["Side"] = self.__orderbook["Side"].map(
                lambda x: 1
                if x.lower() in ["deposit", "buy"]
                else (-1 if x.lower() in ["withdrawal", "sell"] else 0)
            )
            console.print(".", end="")

            # Convert quantity to signed integer
            self.__orderbook["Quantity"] = (
                abs(self.__orderbook["Quantity"]) * self.__orderbook["Side"]
            )
            console.print(".", end="")

            # Determining the investment/divestment value
            self.__orderbook["Investment"] = (
                self.__orderbook["Quantity"] * self.__orderbook["Price"]
                - self.__orderbook["Fees"]
            )
            console.print(".", end="")

            # Reformat crypto tickers to yfinance format (e.g. BTC -> BTC-USD)
            crypto_trades = self.__orderbook[self.__orderbook.Type == "CRYPTO"]
            self.__orderbook.loc[(self.__orderbook.Type == "CRYPTO"), "Ticker"] = [
                f"{crypto}-{currency}"
                for crypto, currency in zip(
                    crypto_trades.Ticker, crypto_trades.Currency
                )
            ]
            console.print(".", end="")

            # Create tickers dictionary with structure {'Type': [Ticker]}
            for ticker_type in set(self.__orderbook["Type"]):
                self.tickers[ticker_type] = list(
                    set(
                        self.__orderbook[self.__orderbook["Type"].isin([ticker_type])][
                            "Ticker"
                        ]
                    )
                )
            console.print(".", end="")

            # Create list with tickers except cash
            self.tickers_list = list(set(self.__orderbook["Ticker"]))
            console.print(".", end="")

            # Save orderbook inception date
            self.inception_date = self.__orderbook["Date"][0]
            console.print(".", end="")

            # Populate fields Sector, Industry and Country
            if not (
                {"Sector", "Industry", "Country", "Region"}.issubset(
                    set(self.__orderbook.columns)
                )
            ):
                # if fields not in the orderbook add missing
                if "Sector" not in self.__orderbook.columns:
                    self.__orderbook["Sector"] = np.nan
                if "Industry" not in self.__orderbook.columns:
                    self.__orderbook["Industry"] = np.nan
                if "Country" not in self.__orderbook.columns:
                    self.__orderbook["Country"] = np.nan
                if "Region" not in self.__orderbook.columns:
                    self.__orderbook["Region"] = np.nan

                self.load_company_data()
            elif (
                self.__orderbook.loc[
                    self.__orderbook["Type"] == "STOCK",
                    ["Sector", "Industry", "Country", "Region"],
                ]
                .isnull()
                .values.any()
            ):
                # if any fields is empty for Stocks (overwrites any info there)
                self.load_company_data()

        except Exception:
            console.print("\nCould not preprocess orderbook.")

    def load_company_data(self):

        console.print("\n    Loading company data: ", end="")

        for ticker_type, ticker_list in self.tickers.items():

            # yfinance only has sector, industry and country for stocks
            if ticker_type == "STOCK":
                for ticker in ticker_list:

                    # Only gets fields for tickers with missing data
                    # TODO: Should only get field missing for tickers with missing data
                    # now it's taking the 4 of them
                    if (
                        self.__orderbook.loc[
                            self.__orderbook["Ticker"] == ticker,
                            ["Sector", "Industry", "Country", "Region"],
                        ]
                        .isnull()
                        .values.any()
                    ):
                        ticker_info_list = portfolio_helper.get_info_from_ticker(ticker)

                        # replace fields in orderbook
                        self.__orderbook.loc[
                            self.__orderbook.Ticker == ticker,
                            ["Sector", "Industry", "Country", "Region"],
                        ] = ticker_info_list
                        # Display progress
                        console.print(".", end="")

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

        console.print("\n      Loading price data: ", end="")

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
                console.print(f"Type {ticker_type} not supported.")

            console.print(".", end="")

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

        console.print("\n     Calculating returns: ", end="")

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

        trade_data[
            pd.MultiIndex.from_product(
                [["Initial Value"], self.tickers_list + ["Total"]]
            )
        ] = 0

        # Initial Value = Previous End Value + Investment changes
        trade_data["Initial Value"] = trade_data["End Value"].shift(1) + trade_data[
            "Investment"
        ].diff(periods=1)

        # Set first day Initial Value as the Investment (NaNs break first period)
        for t in self.tickers_list + ["Total"]:
            trade_data.at[trade_data.index[0], ("Initial Value", t)] = trade_data.iloc[
                0
            ]["Investment"][t]

        console.print(".", end="")

        self.historical_trade_data = trade_data

        console.print("\n")

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
        gtp_period_df = get_gaintopain_ratio(
            self.historical_trade_data, self.benchmark_trades, self.benchmark_returns
        )

        return gtp_period_df

    @log_start_end(log=logger)
    def get_rolling_beta(self, period: int = 252):
        """Get rolling beta

        Parameters
        ----------
        period: int
            Interval used for rolling values

        Returns
        -------
        pd.DataFrame
            DataFrame of the portfolio's rolling beta
        """
        rolling_beta = get_rolling_beta(self.returns, self.benchmark_returns, period)

        return rolling_beta

    @log_start_end(log=logger)
    def get_tracking_error(self, period: int = 252):
        """Get tracking error

        Parameters
        ----------
        period: int
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
    def get_information_ratio(self):
        """Get information ratio

        Returns
        -------
        pd.DataFrame
            DataFrame of the information ratio during different time periods
        """
        ir_period_df = get_information_ratio(
            self.returns,
            self.historical_trade_data,
            self.benchmark_trades,
            self.benchmark_returns,
        )

        return ir_period_df

    @log_start_end(log=logger)
    def get_tail_ratio(self, period: int = 252):
        """Get tail ratio

        Parameters
        ----------
        period: int
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
        csr_period_df = get_common_sense_ratio(
            self.returns,
            self.historical_trade_data,
            self.benchmark_trades,
            self.benchmark_returns,
        )

        return csr_period_df

    @log_start_end(log=logger)
    def get_jensens_alpha(self, rf: float = 0, period: int = 252):
        """Get jensen's alpha

        Parameters
        ----------
        period: int
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
            self.returns,
            self.historical_trade_data,
            self.benchmark_trades,
            self.benchmark_returns,
            rf,
            period,
        )

        return ja_period_df, ja_rolling

    @log_start_end(log=logger)
    def get_calmar_ratio(self, period: int = 756):
        """Get calmar ratio

        Parameters
        ----------
        period: int
            Interval used for rolling values

        Returns
        -------
        pd.DataFrame
            DataFrame of calmar ratio of the benchmark and portfolio during different time periods
        pd.Series
            Series of calmar ratio data
        """
        cr_period_df, cr_rolling = get_calmar_ratio(
            self.returns,
            self.historical_trade_data,
            self.benchmark_trades,
            self.benchmark_returns,
            period,
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


def rolling_volatility(
    portfolio_returns: pd.Series, window: str = "1y"
) -> pd.DataFrame:
    """Get rolling volatility

    Parameters
    ----------
    portfolio_returns : pd.Series
        Series of portfolio returns
    window : str
        Rolling window size to use

    Returns
    -------
    pd.DataFrame
        Rolling volatility DataFrame
    """
    length = portfolio_helper.PERIODS_DAYS[window]
    return portfolio_returns.rolling(length).std()


def sharpe_ratio(portfolio_returns: pd.Series, risk_free_rate: float) -> float:
    """Get sharpe ratio

    Parameters
    ----------
    return_series : pd.Series
        Series of portfolio returns
    risk_free_rate: float
        Value to use for risk free rate

    Returns
    -------
    float
        Sharpe ratio
    """
    mean = portfolio_returns.mean() - risk_free_rate
    sigma = portfolio_returns.std()

    return mean / sigma


def rolling_sharpe(
    portfolio_returns: pd.DataFrame, risk_free_rate: float, window: str = "1y"
) -> pd.DataFrame:
    """Get rolling sharpe ratio

    Parameters
    ----------
    portfolio_returns : pd.Series
        Series of portfolio returns
    risk_free_rate : float
        Risk free rate
    window : str
        Rolling window to use
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y

    Returns
    -------
    pd.DataFrame
        Rolling sharpe ratio DataFrame
    """

    length = portfolio_helper.PERIODS_DAYS[window]

    rolling_sharpe_df = portfolio_returns.rolling(length).apply(
        lambda x: (x.mean() - risk_free_rate) / x.std()
    )
    return rolling_sharpe_df


def sortino_ratio(portfolio_returns: pd.Series, risk_free_rate: float) -> float:
    """Get sortino ratio

    Parameters
    ----------
    portfolio_returns : pd.Series
        Series of portfolio returns
    risk_free_rate: float
        Value to use for risk free rate

    Returns
    -------
    float
        Sortino ratio
    """
    mean = portfolio_returns.mean() - risk_free_rate
    std_neg = portfolio_returns[portfolio_returns < 0].std()

    return mean / std_neg


def rolling_sortino(
    portfolio_returns: pd.Series, risk_free_rate: float, window: str = "1y"
) -> pd.DataFrame:
    """Get rolling sortino ratio

    Parameters
    ----------
    portfolio_returns : pd.Series
        Series of portfolio returns
    risk_free_rate : float
        Risk free rate
    window : str
        Rolling window to use

    Returns
    -------
    pd.DataFrame
        Rolling sortino ratio DataFrame
    """
    length = portfolio_helper.PERIODS_DAYS[window]
    rolling_sortino_df = portfolio_returns.rolling(length).apply(
        lambda x: (x.mean() - risk_free_rate) / x[x < 0].std()
    )

    return rolling_sortino_df


def get_maximum_drawdown(portfolio_returns: pd.Series) -> float:
    """Get maximum drawdown

    Parameters
    ----------
    portfolio_returns : pd.Series
        Series of portfolio returns

    Returns
    -------
    float
        Maximum drawdown
    """
    comp_ret = (portfolio_returns + 1).cumprod()
    peak = comp_ret.expanding(min_periods=1).max()
    dd = (comp_ret / peak) - 1

    return dd.min()
