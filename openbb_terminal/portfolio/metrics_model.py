"""Metrics Model"""
__docformat__ = "numpy"

import logging
from datetime import datetime
from typing import Tuple

import numpy as np
import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.portfolio.portfolio_helper import filter_df_by_period
from openbb_terminal.portfolio.statics import PERIODS
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


# pylint: disable=too-many-return-statements, too-many-lines, too-many-statements
# pylint: disable=C0302


now = datetime.now()
PERIODS_DAYS = {
    "mtd": (now - datetime(now.year, now.month, 1)).days,
    "qtd": (
        now
        - datetime(
            now.year,
            1 if now.month < 4 else 4 if now.month < 7 else 7 if now.month < 10 else 10,
            1,
        )
    ).days,
    "ytd": (now - datetime(now.year, 1, 1)).days,
    "all": 1,
    "3m": 3 * 21,
    "6m": 6 * 21,
    "1y": 12 * 21,
    "3y": 3 * 12 * 21,
    "5y": 5 * 12 * 21,
    "10y": 10 * 12 * 21,
}

DEFAULT_HOLDINGS_PATH = (
    get_current_user().preferences.USER_PORTFOLIO_DATA_DIRECTORY / "holdings"
)


@log_start_end(log=logger)
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

    length = PERIODS_DAYS[window]
    sample_length = len(portfolio_returns)

    if length > sample_length:
        console.print(
            f"[red]Window length ({window}->{length}) is larger than returns length ({sample_length}).\
            \nTry a smaller window.[/red]"
        )
        return pd.DataFrame()

    # max(2, length) -> std needs at least 2 observations
    return portfolio_returns.rolling(max(2, length)).std()


@log_start_end(log=logger)
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


@log_start_end(log=logger)
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

    length = PERIODS_DAYS[window]
    sample_length = len(portfolio_returns)

    if length > sample_length:
        console.print(
            f"[red]Window length ({window}->{length}) is larger than returns length ({sample_length}).\
            \nTry a smaller window.[/red]"
        )
        return pd.DataFrame()

    # max(2, length) -> std needs at least 2 observations
    rolling_sharpe_df = portfolio_returns.rolling(max(2, length)).apply(
        lambda x: (x.mean() - risk_free_rate) / x.std()
    )
    return rolling_sharpe_df


@log_start_end(log=logger)
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


@log_start_end(log=logger)
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
    length = PERIODS_DAYS[window]

    sample_length = len(portfolio_returns)

    if length > sample_length:
        console.print(
            f"[red]Window length ({window}->{length}) is larger than returns length ({sample_length}).\
            \nTry a smaller window.[/red]"
        )
        return pd.DataFrame()

    # max(2, length) -> std needs at least 2 observations
    rolling_sortino_df = portfolio_returns.rolling(max(2, length)).apply(
        lambda x: (x.mean() - risk_free_rate) / x[x < 0].std()
    )

    return rolling_sortino_df


@log_start_end(log=logger)
def rolling_beta(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    window: str = "1y",
) -> pd.DataFrame:
    """Get rolling beta using portfolio and benchmark returns

    Parameters
    ----------
    returns: pd.Series
        Series of portfolio returns
    benchmark_returns: pd.Series
        Series of benchmark returns
    window: string
        Interval used for rolling values.
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y.

    Returns
    -------
    pd.DataFrame
        DataFrame of the portfolio's rolling beta
    """

    length = PERIODS_DAYS[window]

    sample_length = len(portfolio_returns)

    if length > sample_length:
        console.print(
            f"[red]Window length ({window}->{length}) is larger than returns length ({sample_length}).\
            \nTry a smaller window.[/red]"
        )
        return pd.DataFrame()

    covs = (
        pd.DataFrame({"Portfolio": portfolio_returns, "Benchmark": benchmark_returns})
        .dropna(axis=0)
        .rolling(max(2, length))  # needs at least 2 observations.
        .cov()
        .unstack()
        .dropna()
    )

    rolling_beta_num = covs["Portfolio"]["Benchmark"] / covs["Benchmark"]["Benchmark"]

    return rolling_beta_num


@log_start_end(log=logger)
def maximum_drawdown(portfolio_returns: pd.Series) -> float:
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


@log_start_end(log=logger)
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
    return (1 + data.shift(periods=1, fill_value=0)).cumprod() - 1


@log_start_end(log=logger)
def get_gaintopain_ratio(
    historical_trade_data: pd.DataFrame,
    benchmark_trades: pd.DataFrame,
    benchmark_returns: pd.DataFrame,
) -> pd.DataFrame:
    """Get Pain-to-Gain ratio

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
    for period in PERIODS:
        period_historical_trade_data = filter_df_by_period(
            historical_trade_data, period
        )
        period_bench_trades = filter_df_by_period(benchmark_trades, period)
        period_bench_return = filter_df_by_period(benchmark_returns, period)
        if not period_historical_trade_data.empty:
            if not period_bench_trades.empty:
                benchmark_values = (
                    period_bench_trades["Benchmark Value"].sum()
                    / period_bench_trades["Benchmark Investment"].sum()
                    - 1
                ) / maximum_drawdown(period_bench_return)
            else:
                benchmark_values = ((1 + period_bench_return).cumprod() - 1).iloc[
                    -1
                ] / maximum_drawdown(period_bench_return)

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
                        / maximum_drawdown(
                            period_historical_trade_data["Period percentage return"][
                                "Total"
                            ]
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
        vals, index=PERIODS, columns=["Portfolio", "Benchmark"]
    )

    return gtr_period_df


@log_start_end(log=logger)
def calculate_beta(portfolio_returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """Calculate the beta using portfolio and benchmark return values

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
    for periods in PERIODS:
        period_return = filter_df_by_period(diff_returns, periods)
        if not period_return.empty:
            vals.append([round(period_return.std(), 3)])
        else:
            vals.append(["-"])
    tracker_period_df = pd.DataFrame(vals, index=PERIODS, columns=["Tracking Error"])

    return tracker_period_df, tracker_rolling


@log_start_end(log=logger)
def get_information_ratio(
    portfolio_returns: pd.Series,
    historical_trade_data: pd.DataFrame,
    benchmark_trades: pd.DataFrame,
    benchmark_returns: pd.Series,
) -> pd.DataFrame:
    """Calculate information ratio, which measures the active return of an investment
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
    for periods in PERIODS:
        period_historical_trade_data = filter_df_by_period(
            historical_trade_data, periods
        )
        period_bench_trades = filter_df_by_period(benchmark_trades, periods)
        period_bench_return = filter_df_by_period(benchmark_returns, periods)
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

    ir_period_df = pd.DataFrame(vals, index=PERIODS, columns=["Information Ratio"])

    return ir_period_df


@log_start_end(log=logger)
def get_tail_ratio(
    portfolio_returns: pd.Series, benchmark_returns: pd.Series, window: str = "252d"
) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Return the portfolios tail ratio

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
    for periods in PERIODS:
        period_return = filter_df_by_period(portfolio_returns, periods)
        period_bench_return = filter_df_by_period(benchmark_returns, periods)
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
        vals, index=PERIODS, columns=["Portfolio", "Benchmark"]
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
    for period in PERIODS:
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
        vals, index=PERIODS, columns=["Portfolio", "Benchmark"]
    )

    return csr_period_df


@log_start_end(log=logger)
def jensens_alpha(
    portfolio_returns: pd.Series,
    historical_trade_data: pd.DataFrame,
    benchmark_trades: pd.DataFrame,
    benchmark_returns: pd.Series,
    risk_free_rate: float = 0,
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
    risk_free_rate: float
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
    length = PERIODS_DAYS[window]
    periods_d = PERIODS_DAYS

    period_cum_returns = (1.0 + portfolio_returns).rolling(window=length).agg(
        lambda x: x.prod()
    ) - 1
    period_cum_bench_returns = (1.0 + benchmark_returns).rolling(window=length).agg(
        lambda x: x.prod()
    ) - 1
    rfr_cum_returns = risk_free_rate * length / 252
    beta = rolling_beta(portfolio_returns, benchmark_returns, window)
    ja_rolling = period_cum_returns - (
        rfr_cum_returns + beta * (period_cum_bench_returns - rfr_cum_returns)
    )

    benchmark_trades = benchmark_trades.set_index("Date")
    vals = list()
    for periods in PERIODS:
        period_return = filter_df_by_period(portfolio_returns, periods)
        period_bench_return = filter_df_by_period(benchmark_returns, periods)
        period_historical_trade_data = filter_df_by_period(
            historical_trade_data, periods
        )
        period_bench_trades = filter_df_by_period(benchmark_trades, periods)
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
            rfr_cum_returns = risk_free_rate * periods_d[periods] / 252
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

    ja_period_df = pd.DataFrame(vals, index=PERIODS, columns=["Portfolio"])

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
    periods_d = PERIODS_DAYS
    period_cum_returns = (1.0 + portfolio_returns).rolling(window=window).agg(
        lambda x: x.prod()
    ) - 1

    # Calculate annual return
    annual_return = period_cum_returns ** (1 / (int(window) / 252)) - 1

    cr_rolling = annual_return / maximum_drawdown(portfolio_returns)

    benchmark_trades = benchmark_trades.set_index("Date")
    vals = list()
    for periods in PERIODS:
        period_return = filter_df_by_period(portfolio_returns, periods)
        period_historical_trade_data = filter_df_by_period(
            historical_trade_data, periods
        )
        period_bench_trades = filter_df_by_period(benchmark_trades, periods)
        period_bench_return = filter_df_by_period(benchmark_returns, periods)
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
            drawdown = maximum_drawdown(period_return)
            bench_drawdown = maximum_drawdown(period_bench_return)
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

    cr_period_df = pd.DataFrame(vals, index=PERIODS, columns=["Portfolio", "Benchmark"])

    return cr_period_df, cr_rolling


@log_start_end(log=logger)
def get_kelly_criterion(
    portfolio_returns: pd.Series, portfolio_trades: pd.DataFrame
) -> pd.DataFrame:
    """Get kelly criterion

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
    for period in PERIODS:
        period_return = filter_df_by_period(portfolio_returns, period)
        period_portfolio_tr = filter_df_by_period(portfolio_trades, period)
        if (not period_return.empty) and (not period_portfolio_tr.empty):
            w = len(period_return[period_return > 0]) / len(period_return)
            r = len(
                period_portfolio_tr[period_portfolio_tr["Portfolio % Return"] > 0]
            ) / len(
                period_portfolio_tr[period_portfolio_tr["Type"].str.upper() != "CASH"]
            )
            if r != 0:
                vals.append([round(w - (1 - w) / r, 3)])
            else:
                vals.append(["-"])
        else:
            vals.append(["-"])

    kc_period_df = pd.DataFrame(vals, index=PERIODS, columns=["Kelly %"])

    return kc_period_df


@log_start_end(log=logger)
def get_payoff_ratio(portfolio_trades: pd.DataFrame) -> pd.DataFrame:
    """Get payoff ratio

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
    for period in PERIODS:
        period_portfolio_tr = filter_df_by_period(portfolio_trades, period)
        if not portfolio_trades.empty:
            portfolio_wins = period_portfolio_tr[
                period_portfolio_tr["Portfolio % Return"] > 0
            ]
            portfolio_loses = period_portfolio_tr[
                period_portfolio_tr["Portfolio % Return"] < 0
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
            "During some time periods there were no losing trades.",
            "Thus some values could not be calculated.",
        )

    pr_period_ratio = pd.DataFrame(
        vals, index=PERIODS, columns=["Payoff Ratio"]
    ).fillna("-")

    return pr_period_ratio


@log_start_end(log=logger)
def get_profit_factor(portfolio_trades: pd.DataFrame) -> pd.DataFrame:
    """Get profit factor

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
    for period in PERIODS:
        period_portfolio_tr = filter_df_by_period(portfolio_trades, period)
        if not portfolio_trades.empty:
            portfolio_wins = period_portfolio_tr[
                period_portfolio_tr["Portfolio % Return"] > 0
            ]
            portfolio_loses = period_portfolio_tr[
                period_portfolio_tr["Portfolio % Return"] < 0
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
            "During some time periods there were no losing trades.",
            "Thus some values could not be calculated.",
        )

    pf_period_df = pd.DataFrame(vals, index=PERIODS, columns=["Profit Factor"]).fillna(
        "-"
    )

    return pf_period_df
