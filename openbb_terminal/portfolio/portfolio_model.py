"""Portfolio Model"""
__docformat__ = "numpy"

import logging
from typing import Tuple, Union

import numpy as np
import pandas as pd
import scipy
from sklearn.metrics import r2_score

from openbb_terminal.common.quantitative_analysis import qa_model
from openbb_terminal.decorators import log_start_end
from openbb_terminal.portfolio import metrics_model, portfolio_helper
from openbb_terminal.portfolio.portfolio_engine import PortfolioEngine
from openbb_terminal.portfolio.statics import PERIODS

# pylint: disable=E1136,W0201,R0902,C0302, consider-using-f-string, consider-iterating-dictionary
# pylint: disable=unsupported-assignment-operation,redefined-outer-name,too-many-public-methods

logger = logging.getLogger(__name__)

pd.options.mode.chained_assignment = None


@log_start_end(log=logger)
def generate_portfolio(
    transactions_file_path: str,
    benchmark_symbol: str = "SPY",
    full_shares: bool = False,
    risk_free_rate: float = 0,
) -> PortfolioEngine:
    """Get PortfolioEngine object

    Parameters
    ----------
    transactions_file_path : str
        Path to transactions file
    benchmark_symbol : str
        Benchmark ticker to download data
    full_shares : bool
        Whether to mimic the portfolio trades exactly (partial shares) or round down the
        quantity to the nearest number
    risk_free_rate : float
        Risk free rate in float format

    Returns
    -------
    PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    """

    transactions = PortfolioEngine.read_transactions(transactions_file_path)
    portfolio_engine = PortfolioEngine(transactions)
    portfolio_engine.generate_portfolio_data()
    portfolio_engine.set_risk_free_rate(risk_free_rate)
    portfolio_engine.set_benchmark(symbol=benchmark_symbol, full_shares=full_shares)

    return portfolio_engine


@log_start_end(log=logger)
def get_transactions(portfolio_engine: PortfolioEngine) -> pd.DataFrame:
    """Get portfolio transactions

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        Portfolio transactions

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.show(p)
    """

    return portfolio_engine.get_transactions()


@log_start_end(log=logger)
def set_benchmark(
    portfolio_engine: PortfolioEngine, symbol: str, full_shares: bool = False
) -> bool:
    """Load benchmark into portfolio

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    symbol: str
        Benchmark symbol to download data
    full_shares: bool
        Whether to mimic the portfolio trades exactly (partial shares) or round down the
        quantity to the nearest number

    Returns
    -------
    bool
        True if successful, False otherwise

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.bench(p, symbol="SPY")
    """

    return portfolio_engine.set_benchmark(symbol=symbol, full_shares=full_shares)


@log_start_end(log=logger)
def set_risk_free_rate(portfolio_engine: PortfolioEngine, risk_free_rate: float):
    """Set risk-free rate

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    risk_free_rate: float
        Risk free rate in float format
    """

    portfolio_engine.set_risk_free_rate(risk_free_rate=risk_free_rate)


def get_holdings_value(portfolio_engine: PortfolioEngine) -> pd.DataFrame:
    """Get holdings of assets (absolute value)

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame of holdings value

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.holdv(p)
    """

    all_holdings = portfolio_engine.historical_trade_data["End Value"][
        portfolio_engine.tickers_list
    ]

    all_holdings["Total Value"] = all_holdings.sum(axis=1)
    # No need to account for time since this is daily data
    all_holdings.index = all_holdings.index.date

    return all_holdings


def get_holdings_percentage(
    portfolio_engine: PortfolioEngine,
) -> pd.DataFrame:
    """Get holdings of assets (in percentage)

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame of holdings percentage

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.holdp(p)
    """

    all_holdings = portfolio_engine.historical_trade_data["End Value"][
        portfolio_engine.tickers_list
    ]

    all_holdings = all_holdings.divide(all_holdings.sum(axis=1), axis=0) * 100

    # order it a bit more in terms of magnitude
    all_holdings = all_holdings[all_holdings.sum().sort_values(ascending=False).index]

    return all_holdings


@log_start_end(log=logger)
def get_yearly_returns(
    portfolio_engine: PortfolioEngine,
    window: str = "all",
) -> pd.DataFrame:
    """Get yearly returns

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window : str
        interval to compare cumulative returns and benchmark

    Returns
    -------
    pd.DataFrame
        DataFrame with yearly returns

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.yret(p)
    """

    portfolio_returns = portfolio_helper.filter_df_by_period(
        portfolio_engine.portfolio_returns, window
    )
    benchmark_returns = portfolio_helper.filter_df_by_period(
        portfolio_engine.benchmark_returns, window
    )

    creturns_year_val = list()
    breturns_year_val = list()

    for year in sorted(set(portfolio_returns.index.year)):
        creturns_year = portfolio_returns[portfolio_returns.index.year == year]
        cumulative_returns = 100 * metrics_model.cumulative_returns(creturns_year)
        creturns_year_val.append(cumulative_returns.values[-1])

        breturns_year = benchmark_returns[benchmark_returns.index.year == year]
        benchmark_c_returns = 100 * metrics_model.cumulative_returns(breturns_year)
        breturns_year_val.append(benchmark_c_returns.values[-1])

    df = pd.DataFrame(
        {
            "Portfolio": pd.Series(
                creturns_year_val, index=list(set(portfolio_returns.index.year))
            ),
            "Benchmark": pd.Series(
                breturns_year_val, index=list(set(portfolio_returns.index.year))
            ),
            "Difference": pd.Series(
                np.array(creturns_year_val) - np.array(breturns_year_val),
                index=list(set(portfolio_returns.index.year)),
            ),
        }
    )

    return df


@log_start_end(log=logger)
def get_monthly_returns(
    portfolio_engine: PortfolioEngine,
    window: str = "all",
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Get monthly returns

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window : str
        interval to compare cumulative returns and benchmark

    Returns
    -------
    pd.DataFrame
        DataFrame with monthly returns

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.mret(p)
    """

    portfolio_returns = portfolio_helper.filter_df_by_period(
        portfolio_engine.portfolio_returns, window
    )
    benchmark_returns = portfolio_helper.filter_df_by_period(
        portfolio_engine.benchmark_returns, window
    )

    creturns_month_val = list()
    breturns_month_val = list()

    for year in sorted(list(set(portfolio_returns.index.year))):
        creturns_year = portfolio_returns[portfolio_returns.index.year == year]
        creturns_val = list()
        for i in range(1, 13):
            creturns_year_month = creturns_year[creturns_year.index.month == i]
            creturns_year_month_val = 100 * metrics_model.cumulative_returns(
                creturns_year_month
            )

            if creturns_year_month.empty:
                creturns_val.append(0)
            else:
                creturns_val.append(creturns_year_month_val.values[-1])
        creturns_month_val.append(creturns_val)

        breturns_year = benchmark_returns[benchmark_returns.index.year == year]
        breturns_val = list()
        for i in range(1, 13):
            breturns_year_month = breturns_year[breturns_year.index.month == i]
            breturns_year_month_val = 100 * metrics_model.cumulative_returns(
                breturns_year_month
            )

            if breturns_year_month.empty:
                breturns_val.append(0)
            else:
                breturns_val.append(breturns_year_month_val.values[-1])
        breturns_month_val.append(breturns_val)

    columns = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]
    monthly_returns = pd.DataFrame(
        creturns_month_val,
        index=sorted(list(set(portfolio_returns.index.year))),
        columns=columns,
    )
    bench_monthly_returns = pd.DataFrame(
        breturns_month_val,
        index=sorted(list(set(benchmark_returns.index.year))),
        columns=columns,
    )

    years = [
        (year, instrument)
        for year in monthly_returns.index
        for instrument in ["Portfolio", "Benchmark", "Alpha"]
    ]
    total_monthly_returns = pd.DataFrame(
        np.nan,
        columns=monthly_returns.columns,
        index=pd.MultiIndex.from_tuples(years, names=["Year", "Instrument"]),
    )

    for year in monthly_returns.index:
        for instrument in ["Portfolio", "Benchmark", "Alpha"]:
            if instrument == "Portfolio":
                total_monthly_returns.loc[
                    (year, instrument), monthly_returns.columns
                ] = monthly_returns.loc[year].values
            elif instrument == "Benchmark":
                total_monthly_returns.loc[
                    (year, instrument), monthly_returns.columns
                ] = bench_monthly_returns.loc[year].values
            elif instrument == "Alpha":
                total_monthly_returns.loc[
                    (year, instrument), monthly_returns.columns
                ] = (
                    monthly_returns.loc[year].values
                    - bench_monthly_returns.loc[year].values
                )

    return monthly_returns, bench_monthly_returns, total_monthly_returns


@log_start_end(log=logger)
def get_daily_returns(
    portfolio_engine: PortfolioEngine,
    window: str = "all",
) -> pd.DataFrame:
    """Get daily returns

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window : str
        interval to compare cumulative returns and benchmark

    Returns
    -------
    pd.DataFrame
        DataFrame with daily returns

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.dret(p)
    """

    portfolio_returns = portfolio_helper.filter_df_by_period(
        portfolio_engine.portfolio_returns, window
    )
    benchmark_returns = portfolio_helper.filter_df_by_period(
        portfolio_engine.benchmark_returns, window
    )

    df = portfolio_returns.to_frame()
    df = df.join(benchmark_returns)
    df.index = df.index.date
    df.columns = ["portfolio", "benchmark"]

    return df


def join_allocation(
    portfolio: pd.DataFrame, benchmark: pd.DataFrame, column: str
) -> pd.DataFrame:
    """Help method to join portfolio and benchmark allocation by column

    Parameters
    ----------
    portfolio: pd.DataFrame
        Portfolio allocation
    benchmark: pd.DataFrame
        Benchmark allocation
    column: str
        Column to join DataFrames

    Returns
    -------
    pd.DataFrame
        DataFrame with portfolio and benchmark allocations
    """

    if portfolio.empty:
        portfolio = pd.DataFrame(columns=[column, "Portfolio"])

    if benchmark.empty:
        benchmark = pd.DataFrame(columns=[column, "Benchmark"])

    combined = pd.merge(portfolio, benchmark, on=column, how="left")
    combined["Difference"] = combined["Portfolio"] - combined["Benchmark"]
    combined = combined.replace(np.nan, "-")
    combined = combined.replace(0, "-")

    return combined


def get_distribution_returns(
    portfolio_engine: PortfolioEngine,
    window: str = "all",
) -> pd.DataFrame:
    """Display daily returns

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window : str
        interval to compare cumulative returns and benchmark

    Returns
    -------
    pd.DataFrame
        DataFrame of returns distribution

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.distr(p)
    """

    portfolio_returns = portfolio_helper.filter_df_by_period(
        portfolio_engine.portfolio_returns, window
    )
    benchmark_returns = portfolio_helper.filter_df_by_period(
        portfolio_engine.benchmark_returns, window
    )

    df = pd.DataFrame(portfolio_returns).join(pd.DataFrame(benchmark_returns))
    df.columns.values[0] = "portfolio"
    df.columns.values[1] = "benchmark"

    return df


@log_start_end(log=logger)
def get_maximum_drawdown(
    portfolio_engine: PortfolioEngine, is_returns: bool = False
) -> Tuple[pd.DataFrame, pd.Series]:
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
    -------
    pd.Series
        Holdings series
    pd.Series
        Drawdown series

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.maxdd(p)
    """

    holdings: pd.Series = portfolio_engine.historical_trade_data["End Value"]["Total"]
    if is_returns:
        holdings = (1 + holdings).cumprod()

    rolling_max = holdings.cummax()
    drawdown = (holdings - rolling_max) / rolling_max

    return holdings, drawdown


def get_rolling_volatility(
    portfolio_engine: PortfolioEngine, window: str = "1y"
) -> pd.DataFrame:
    """Get rolling volatility

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window : str
        Rolling window size to use
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y

    Returns
    -------
    pd.DataFrame
        Rolling volatility DataFrame

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.rvol(p)
    """

    portfolio_rvol = metrics_model.rolling_volatility(
        portfolio_engine.portfolio_returns, window
    )
    if portfolio_rvol.empty:
        return pd.DataFrame()

    benchmark_rvol = metrics_model.rolling_volatility(
        portfolio_engine.benchmark_returns, window
    )
    if benchmark_rvol.empty:
        return pd.DataFrame()

    df = pd.DataFrame(portfolio_rvol).join(pd.DataFrame(benchmark_rvol))
    df.columns.values[0] = "portfolio"
    df.columns.values[1] = "benchmark"

    return df


def get_rolling_sharpe(
    portfolio_engine: pd.DataFrame, risk_free_rate: float = 0, window: str = "1y"
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

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.rsharpe(p)
    """

    portfolio_rsharpe = metrics_model.rolling_sharpe(
        portfolio_engine.portfolio_returns, risk_free_rate, window
    )
    if portfolio_rsharpe.empty:
        return pd.DataFrame()

    benchmark_rsharpe = metrics_model.rolling_sharpe(
        portfolio_engine.benchmark_returns, risk_free_rate, window
    )
    if benchmark_rsharpe.empty:
        return pd.DataFrame()

    df = pd.DataFrame(portfolio_rsharpe).join(pd.DataFrame(benchmark_rsharpe))
    df.columns.values[0] = "portfolio"
    df.columns.values[1] = "benchmark"

    return df


def get_rolling_sortino(
    portfolio_engine: PortfolioEngine,
    risk_free_rate: float = 0,
    window: str = "1y",
) -> pd.DataFrame:
    """Get rolling sortino

    Parameters
    ----------
    portfolio : PortfolioEngine
        PortfolioEngine object
    window: str
        interval for window to consider
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y
    risk_free_rate: float
        Value to use for risk free rate in sharpe/other calculations

    Returns
    -------
    pd.DataFrame
        Rolling sortino ratio DataFrame

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.rsort(p)
    """

    portfolio_rsortino = metrics_model.rolling_sortino(
        portfolio_engine.portfolio_returns, risk_free_rate, window
    )
    if portfolio_rsortino.empty:
        return pd.DataFrame()

    benchmark_rsortino = metrics_model.rolling_sortino(
        portfolio_engine.benchmark_returns, risk_free_rate, window
    )
    if benchmark_rsortino.empty:
        return pd.DataFrame()

    df = pd.DataFrame(portfolio_rsortino).join(pd.DataFrame(benchmark_rsortino))
    df.columns.values[0] = "portfolio"
    df.columns.values[1] = "benchmark"

    return df


@log_start_end(log=logger)
def get_rolling_beta(
    portfolio_engine: PortfolioEngine,
    window: str = "1y",
) -> pd.DataFrame:
    """Get rolling beta using portfolio and benchmark returns

    Parameters
    ----------
    portfolio : PortfolioEngine
        PortfolioEngine object
    window: string
        Interval used for rolling values.
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y.

    Returns
    -------
    pd.DataFrame
        DataFrame of the portfolio's rolling beta

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.rbeta(p)
    """

    df = metrics_model.rolling_beta(
        portfolio_engine.portfolio_returns, portfolio_engine.benchmark_returns, window
    )

    return df


def get_summary(
    portfolio_engine: PortfolioEngine,
    window: str = "all",
    risk_free_rate: float = 0,
) -> pd.DataFrame:
    """Get portfolio and benchmark returns summary

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window : str
        interval to compare cumulative returns and benchmark
    risk_free_rate : float
        Risk free rate for calculations

    Returns
    -------
    pd.DataFrame
        DataFrame with portfolio and benchmark returns summary

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.summary(p)
    """

    portfolio_returns = portfolio_helper.filter_df_by_period(
        portfolio_engine.portfolio_returns, window
    )
    benchmark_returns = portfolio_helper.filter_df_by_period(
        portfolio_engine.benchmark_returns, window
    )

    r2_portfolio_returns = portfolio_returns.copy()
    r2_benchmark_returns = benchmark_returns.copy()
    if len(portfolio_returns) > len(benchmark_returns):
        r2_portfolio_returns = r2_portfolio_returns[
            r2_portfolio_returns.index.isin(r2_benchmark_returns.index)
        ]
    elif len(portfolio_returns) < len(benchmark_returns):
        r2_benchmark_returns = r2_benchmark_returns[
            r2_benchmark_returns.index.isin(r2_portfolio_returns.index)
        ]

    metrics = {
        "Volatility": [portfolio_returns.std(), benchmark_returns.std()],
        "Skew": [
            scipy.stats.skew(portfolio_returns),
            scipy.stats.skew(benchmark_returns),
        ],
        "Kurtosis": [
            scipy.stats.kurtosis(portfolio_returns),
            scipy.stats.kurtosis(benchmark_returns),
        ],
        "Maximum Drawdown": [
            metrics_model.maximum_drawdown(portfolio_returns),
            metrics_model.maximum_drawdown(benchmark_returns),
        ],
        "Sharpe ratio": [
            metrics_model.sharpe_ratio(portfolio_returns, risk_free_rate),
            metrics_model.sharpe_ratio(benchmark_returns, risk_free_rate),
        ],
        "Sortino ratio": [
            metrics_model.sortino_ratio(portfolio_returns, risk_free_rate),
            metrics_model.sortino_ratio(benchmark_returns, risk_free_rate),
        ],
        "R2 Score": [
            r2_score(r2_portfolio_returns, r2_benchmark_returns),
            r2_score(r2_portfolio_returns, r2_benchmark_returns),
        ],
    }

    summary = pd.DataFrame(
        metrics.values(), index=metrics.keys(), columns=["Portfolio", "Benchmark"]
    )
    summary["Difference"] = summary["Portfolio"] - summary["Benchmark"]
    summary.loc["Volatility"] = summary.loc["Volatility"].apply("{:.2%}".format)
    summary.loc["Maximum Drawdown"] = summary.loc["Maximum Drawdown"].apply(
        "{:.2%}".format
    )
    summary.loc["R2 Score"] = summary.loc["R2 Score"].apply("{:.2%}".format)

    return summary


@log_start_end(log=logger)
def get_assets_allocation(
    portfolio_engine: PortfolioEngine,
    tables: bool = False,
    limit: int = 10,
    recalculate: bool = False,
) -> Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]]:
    """Display portfolio asset allocation compared to the benchmark

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    tables: bool
        Whether to include separate allocation tables
    limit: int
        The amount of assets you wish to show, by default this is set to 10
    recalculate: bool
        Flag to force recalculate allocation if already exists

    Returns
    -------
    Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]]
        DataFrame with combined allocation plus individual allocation if tables is `True`.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.alloc.assets(p)
    """

    portfolio_engine.calculate_allocation(category="Asset", recalculate=recalculate)

    benchmark_allocation = portfolio_engine.benchmark_assets_allocation.iloc[:limit]
    portfolio_allocation = portfolio_engine.portfolio_assets_allocation.iloc[:limit]

    combined = join_allocation(portfolio_allocation, benchmark_allocation, "Symbol")

    if tables:
        return combined, portfolio_allocation, benchmark_allocation
    return combined


def get_sectors_allocation(
    portfolio_engine: PortfolioEngine,
    limit: int = 10,
    tables: bool = False,
    recalculate: bool = False,
):
    """Display portfolio sector allocation compared to the benchmark

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    tables: bool
        Whether to include separate allocation tables
    limit: int
        The amount of assets you wish to show, by default this is set to 10
    recalculate: bool
        Flag to force recalculate allocation if already exists

    Returns
    -------
    Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]]
        DataFrame with combined allocation plus individual allocation if tables is `True`.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.alloc.sectors(p)
    """

    portfolio_engine.calculate_allocation(category="Sector", recalculate=recalculate)

    benchmark_allocation = portfolio_engine.benchmark_sectors_allocation.iloc[:limit]
    portfolio_allocation = portfolio_engine.portfolio_sectors_allocation.iloc[:limit]

    combined = join_allocation(portfolio_allocation, benchmark_allocation, "Sector")

    if tables:
        return combined, portfolio_allocation, benchmark_allocation
    return combined


def get_countries_allocation(
    portfolio_engine: PortfolioEngine,
    limit: int = 10,
    tables: bool = False,
    recalculate: bool = False,
):
    """Display portfolio country allocation compared to the benchmark

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    tables: bool
        Whether to include separate allocation tables
    limit: int
        The amount of assets you wish to show, by default this is set to 10
    recalculate: bool
        Flag to force recalculate allocation if already exists

    Returns
    -------
    Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]]
        DataFrame with combined allocation plus individual allocation if tables is `True`.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.alloc.countries(p)
    """

    portfolio_engine.calculate_allocation(category="Country", recalculate=recalculate)

    benchmark_allocation = portfolio_engine.benchmark_countries_allocation.iloc[:limit]
    portfolio_allocation = portfolio_engine.portfolio_countries_allocation.iloc[:limit]

    combined = join_allocation(portfolio_allocation, benchmark_allocation, "Country")

    if tables:
        return combined, portfolio_allocation, benchmark_allocation
    return combined


def get_regions_allocation(
    portfolio_engine: PortfolioEngine,
    limit: int = 10,
    tables: bool = False,
    recalculate: bool = False,
):
    """Display portfolio region allocation compared to the benchmark

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    tables: bool
        Whether to include separate allocation tables
    limit: int
        The amount of assets you wish to show, by default this is set to 10
    recalculate: bool
        Flag to force recalculate allocation if already exists

    Returns
    -------
    Union[pd.DataFrame, Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]]
        DataFrame with combined allocation plus individual allocation if tables is `True`.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.alloc.regions(p)
    """

    portfolio_engine.calculate_allocation(category="Region", recalculate=recalculate)

    benchmark_allocation = portfolio_engine.benchmark_regions_allocation.iloc[:limit]
    portfolio_allocation = portfolio_engine.portfolio_regions_allocation.iloc[:limit]

    combined = join_allocation(portfolio_allocation, benchmark_allocation, "Region")

    if tables:
        return combined, portfolio_allocation, benchmark_allocation
    return combined


@log_start_end(log=logger)
def get_r2_score(portfolio_engine: PortfolioEngine) -> pd.DataFrame:
    """Get R2 Score for portfolio and benchmark selected

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame with R2 Score between portfolio and benchmark for different periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.metric.rsquare(p)
    """

    vals = list()
    for period in PERIODS:
        vals.append(
            round(
                r2_score(
                    portfolio_helper.filter_df_by_period(
                        portfolio_engine.portfolio_returns, period
                    ),
                    portfolio_helper.filter_df_by_period(
                        portfolio_engine.benchmark_returns, period
                    ),
                ),
                3,
            )
        )
    return pd.DataFrame(vals, index=PERIODS, columns=["R2 Score"])


@log_start_end(log=logger)
def get_skewness(portfolio_engine: PortfolioEngine) -> pd.DataFrame:
    """Get skewness for portfolio and benchmark selected

    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame with skewness for portfolio and benchmark for different periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.metric.skew(p)
    """

    vals = list()
    for period in PERIODS:
        vals.append(
            [
                round(
                    scipy.stats.skew(
                        portfolio_helper.filter_df_by_period(
                            portfolio_engine.portfolio_returns, period
                        )
                    ),
                    3,
                ),
                round(
                    scipy.stats.skew(
                        portfolio_helper.filter_df_by_period(
                            portfolio_engine.benchmark_returns, period
                        )
                    ),
                    3,
                ),
            ]
        )
    return pd.DataFrame(vals, index=PERIODS, columns=["Portfolio", "Benchmark"])


@log_start_end(log=logger)
def get_kurtosis(portfolio_engine: PortfolioEngine) -> pd.DataFrame:
    """Get kurtosis for portfolio and benchmark selected

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame with kurtosis for portfolio and benchmark for different periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.metric.kurtosis(p)
    """

    vals = list()
    for period in PERIODS:
        vals.append(
            [
                round(
                    scipy.stats.kurtosis(
                        portfolio_helper.filter_df_by_period(
                            portfolio_engine.portfolio_returns, period
                        )
                    ),
                    3,
                ),
                round(
                    scipy.stats.skew(
                        portfolio_helper.filter_df_by_period(
                            portfolio_engine.benchmark_returns, period
                        )
                    ),
                    3,
                ),
            ]
        )
    return pd.DataFrame(vals, index=PERIODS, columns=["Portfolio", "Benchmark"])


@log_start_end(log=logger)
def get_stats(portfolio_engine: PortfolioEngine, window: str = "all") -> pd.DataFrame:
    """Get stats for portfolio and benchmark selected based on a certain interval

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window : str
        interval to consider. Choices are: mtd, qtd, ytd, 3m, 6m, 1y, 3y, 5y, 10y, all

    Returns
    -------
    pd.DataFrame
        DataFrame with overall stats for portfolio and benchmark for a certain period
    """

    df = (
        portfolio_helper.filter_df_by_period(portfolio_engine.portfolio_returns, window)
        .describe()
        .to_frame()
        .join(
            portfolio_helper.filter_df_by_period(
                portfolio_engine.benchmark_returns, window
            ).describe()
        )
    )
    df.columns = ["Portfolio", "Benchmark"]
    return df


@log_start_end(log=logger)
def get_volatility(portfolio_engine: PortfolioEngine) -> pd.DataFrame:
    """Get volatility for portfolio and benchmark selected

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame with volatility for portfolio and benchmark for different periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.metric.volatility(p)
    """

    vals = list()
    for period in PERIODS:
        port_rets = portfolio_helper.filter_df_by_period(
            portfolio_engine.portfolio_returns, period
        )
        bench_rets = portfolio_helper.filter_df_by_period(
            portfolio_engine.benchmark_returns, period
        )
        vals.append(
            [
                round(
                    port_rets.std() * (len(port_rets) ** 0.5),
                    3,
                ),
                round(
                    bench_rets.std() * (len(bench_rets) ** 0.5),
                    3,
                ),
            ]
        )
    return pd.DataFrame(
        vals,
        index=PERIODS,
        columns=["Portfolio [%]", "Benchmark [%]"],
    )


@log_start_end(log=logger)
def get_sharpe_ratio(
    portfolio_engine: PortfolioEngine, risk_free_rate: float = 0
) -> pd.DataFrame:
    """Get sharpe ratio for portfolio and benchmark selected

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    risk_free_rate: float
        Risk free rate value

    Returns
    -------
    pd.DataFrame
        DataFrame with sharpe ratio for portfolio and benchmark for different periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.metric.sharpe(p)
    """

    vals = list()
    for period in PERIODS:
        vals.append(
            [
                round(
                    metrics_model.sharpe_ratio(
                        portfolio_helper.filter_df_by_period(
                            portfolio_engine.portfolio_returns, period
                        ),
                        risk_free_rate,
                    ),
                    3,
                ),
                round(
                    metrics_model.sharpe_ratio(
                        portfolio_helper.filter_df_by_period(
                            portfolio_engine.benchmark_returns, period
                        ),
                        risk_free_rate,
                    ),
                    3,
                ),
            ]
        )
    return pd.DataFrame(vals, index=PERIODS, columns=["Portfolio", "Benchmark"])


@log_start_end(log=logger)
def get_sortino_ratio(
    portfolio_engine: PortfolioEngine, risk_free_rate: float = 0
) -> pd.DataFrame:
    """Get sortino ratio for portfolio and benchmark selected

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    risk_free_rate: float
        Risk free rate value

    Returns
    -------
    pd.DataFrame
        DataFrame with sortino ratio for portfolio and benchmark for different periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.metric.sortino(p)
    """

    vals = list()
    for period in PERIODS:
        vals.append(
            [
                round(
                    metrics_model.sortino_ratio(
                        portfolio_helper.filter_df_by_period(
                            portfolio_engine.portfolio_returns, period
                        ),
                        risk_free_rate,
                    ),
                    3,
                ),
                round(
                    metrics_model.sortino_ratio(
                        portfolio_helper.filter_df_by_period(
                            portfolio_engine.benchmark_returns, period
                        ),
                        risk_free_rate,
                    ),
                    3,
                ),
            ]
        )
    return pd.DataFrame(vals, index=PERIODS, columns=["Portfolio", "Benchmark"])


@log_start_end(log=logger)
def get_maximum_drawdown_ratio(portfolio_engine: PortfolioEngine) -> pd.DataFrame:
    """Get maximum drawdown ratio for portfolio and benchmark selected

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame with maximum drawdown for portfolio and benchmark for different periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.metric.maxdrawdown(p)
    """

    vals = list()
    for period in PERIODS:
        vals.append(
            [
                round(
                    metrics_model.maximum_drawdown(
                        portfolio_helper.filter_df_by_period(
                            portfolio_engine.portfolio_returns, period
                        )
                    ),
                    3,
                ),
                round(
                    metrics_model.maximum_drawdown(
                        portfolio_helper.filter_df_by_period(
                            portfolio_engine.benchmark_returns, period
                        )
                    ),
                    3,
                ),
            ]
        )
    return pd.DataFrame(vals, index=PERIODS, columns=["Portfolio", "Benchmark"])


@log_start_end(log=logger)
def get_gaintopain_ratio(portfolio_engine: PortfolioEngine) -> pd.DataFrame:
    """Get Pain-to-Gain ratio based on historical data

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame of the portfolio's gain-to-pain ratio

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.metric.gaintopain(p)
    """

    gtp_period_df = metrics_model.get_gaintopain_ratio(
        portfolio_engine.historical_trade_data,
        portfolio_engine.benchmark_trades,
        portfolio_engine.benchmark_returns,
    )

    return gtp_period_df


@log_start_end(log=logger)
def get_tracking_error(
    portfolio_engine: PortfolioEngine, window: int = 252
) -> Tuple[pd.DataFrame, pd.Series]:
    """Get tracking error

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window: int
        Interval used for rolling values

    Returns
    -------
    pd.DataFrame
        DataFrame of tracking errors during different time windows
    pd.Series
        Series of rolling tracking error

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.metric.trackerr(p)
    """

    trackr_period_df, trackr_rolling = metrics_model.get_tracking_error(
        portfolio_engine.portfolio_returns, portfolio_engine.benchmark_returns, window
    )

    return trackr_period_df, trackr_rolling


@log_start_end(log=logger)
def get_information_ratio(portfolio_engine: PortfolioEngine) -> pd.DataFrame:
    """Get information ratio

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame of the information ratio during different time periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.metric.information(p)
    """

    ir_period_df = metrics_model.get_information_ratio(
        portfolio_engine.portfolio_returns,
        portfolio_engine.historical_trade_data,
        portfolio_engine.benchmark_trades,
        portfolio_engine.benchmark_returns,
    )

    return ir_period_df


@log_start_end(log=logger)
def get_tail_ratio(
    portfolio_engine: PortfolioEngine, window: int = 252
) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Get tail ratio

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window: int
        Interval used for rolling values

    Returns
    -------
    pd.DataFrame
        DataFrame of the portfolios and the benchmarks tail ratio during different time windows
    pd.Series
        Series of the portfolios rolling tail ratio
    pd.Series
        Series of the benchmarks rolling tail ratio

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.metric.tail(p)
    """

    tailr_period_df, portfolio_tr, benchmark_tr = metrics_model.get_tail_ratio(
        portfolio_engine.portfolio_returns, portfolio_engine.benchmark_returns, window
    )

    return tailr_period_df, portfolio_tr, benchmark_tr


@log_start_end(log=logger)
def get_common_sense_ratio(portfolio_engine: PortfolioEngine) -> pd.DataFrame:
    """Get common sense ratio

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame of the portfolios and the benchmarks common sense ratio during different time periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.metric.commonsense(p)
    """

    csr_period_df = metrics_model.get_common_sense_ratio(
        portfolio_engine.portfolio_returns,
        portfolio_engine.historical_trade_data,
        portfolio_engine.benchmark_trades,
        portfolio_engine.benchmark_returns,
    )

    return csr_period_df


@log_start_end(log=logger)
def get_jensens_alpha(
    portfolio_engine: PortfolioEngine, risk_free_rate: float = 0, window: str = "1y"
) -> Tuple[pd.DataFrame, pd.Series]:
    """Get jensen's alpha

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window: str
        Interval used for rolling values
    risk_free_rate: float
        Risk free rate

    Returns
    -------
    pd.DataFrame
        DataFrame of jensens's alpha during different time windows
    pd.Series
        Series of jensens's alpha data

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.metric.jensens(p)
    """

    ja_period_df, ja_rolling = metrics_model.jensens_alpha(
        portfolio_engine.portfolio_returns,
        portfolio_engine.historical_trade_data,
        portfolio_engine.benchmark_trades,
        portfolio_engine.benchmark_returns,
        risk_free_rate,
        window,
    )

    return ja_period_df, ja_rolling


@log_start_end(log=logger)
def get_calmar_ratio(
    portfolio_engine: PortfolioEngine, window: int = 756
) -> Tuple[pd.DataFrame, pd.Series]:
    """Get calmar ratio

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window: int
        Interval used for rolling values

    Returns
    -------
    pd.DataFrame
        DataFrame of calmar ratio of the benchmark and portfolio during different time periods
    pd.Series
        Series of calmar ratio data

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.metric.calmar(p)
    """

    cr_period_df, cr_rolling = metrics_model.get_calmar_ratio(
        portfolio_engine.portfolio_returns,
        portfolio_engine.historical_trade_data,
        portfolio_engine.benchmark_trades,
        portfolio_engine.benchmark_returns,
        window,
    )

    return cr_period_df, cr_rolling


@log_start_end(log=logger)
def get_kelly_criterion(portfolio_engine: PortfolioEngine) -> pd.DataFrame:
    """Get kelly criterion

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame of kelly criterion of the portfolio during different time periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.metric.kelly(p)
    """

    kc_period_df = metrics_model.get_kelly_criterion(
        portfolio_engine.portfolio_returns, portfolio_engine.portfolio_trades
    )

    return kc_period_df


@log_start_end(log=logger)
def get_payoff_ratio(portfolio_engine: PortfolioEngine) -> pd.DataFrame:
    """Get payoff ratio

    Returns
    -------
    pd.DataFrame
        DataFrame of payoff ratio of the portfolio during different time periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.metric.payoff(p)
    During some time periods there were no losing trades. Thus some values could not be calculated.
    """

    pr_period_ratio = metrics_model.get_payoff_ratio(portfolio_engine.portfolio_trades)

    return pr_period_ratio


@log_start_end(log=logger)
def get_profit_factor(portfolio_engine: PortfolioEngine) -> pd.DataFrame:
    """Get profit factor

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.

    Returns
    -------
    pd.DataFrame
        DataFrame of profit factor of the portfolio during different time periods

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.metric.profitfactor(p)
    During some time periods there were no losing trades. Thus some values could not be calculated.
    """

    pf_period_df = metrics_model.get_profit_factor(portfolio_engine.portfolio_trades)

    return pf_period_df


@log_start_end(log=logger)
def get_performance_vs_benchmark(
    portfolio_engine: PortfolioEngine,
    show_all_trades: bool = False,
) -> pd.DataFrame:
    """Get portfolio performance vs the benchmark

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    show_all_trades: bool
        Whether to also show all trades made and their performance (default is False)

    Returns
    -------
    pd.DataFrame
        DataFrame with portfolio performance vs the benchmark

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.perf(p)
    """

    portfolio_trades = portfolio_engine.portfolio_trades
    benchmark_trades = portfolio_engine.benchmark_trades

    portfolio_trades.index = pd.to_datetime(portfolio_trades["Date"].values)
    benchmark_trades.index = pd.to_datetime(benchmark_trades["Date"].values)

    if show_all_trades:
        # Combine DataFrames
        combined = pd.concat(
            [
                portfolio_trades[
                    ["Date", "Ticker", "Portfolio Value", "Portfolio % Return"]
                ],
                benchmark_trades[["Benchmark Value", "Benchmark % Return"]],
            ],
            axis=1,
        )

        # Calculate alpha
        combined["Alpha"] = (
            combined["Portfolio % Return"] - combined["Benchmark % Return"]
        )

        combined["Date"] = pd.to_datetime(combined["Date"]).dt.date

        return combined

    # Calculate total value and return
    total_investment_difference = (
        portfolio_trades["Portfolio Investment"].sum()
        - benchmark_trades["Benchmark Investment"].sum()
    )
    total_value_difference = (
        portfolio_trades["Portfolio Value"].sum()
        - benchmark_trades["Benchmark Value"].sum()
    )
    total_portfolio_return = (
        portfolio_trades["Portfolio Value"].sum()
        / portfolio_trades["Portfolio Investment"].sum()
    ) - 1
    total_benchmark_return = (
        benchmark_trades["Benchmark Value"].sum()
        / benchmark_trades["Benchmark Investment"].sum()
    ) - 1
    total_abs_return_difference = (
        portfolio_trades["Portfolio Value"].sum()
        - portfolio_trades["Portfolio Investment"].sum()
    ) - (
        benchmark_trades["Benchmark Value"].sum()
        - benchmark_trades["Benchmark Investment"].sum()
    )

    totals = pd.DataFrame.from_dict(
        {
            "Total Investment": [
                portfolio_trades["Portfolio Investment"].sum(),
                benchmark_trades["Benchmark Investment"].sum(),
                total_investment_difference,
            ],
            "Total Value": [
                portfolio_trades["Portfolio Value"].sum(),
                benchmark_trades["Benchmark Value"].sum(),
                total_value_difference,
            ],
            "Total % Return": [
                f"{total_portfolio_return:.2%}",
                f"{total_benchmark_return:.2%}",
                f"{total_portfolio_return - total_benchmark_return:.2%}",
            ],
            "Total Abs Return": [
                portfolio_trades["Portfolio Value"].sum()
                - portfolio_trades["Portfolio Investment"].sum(),
                benchmark_trades["Benchmark Value"].sum()
                - benchmark_trades["Benchmark Investment"].sum(),
                total_abs_return_difference,
            ],
        },
        orient="index",
        columns=["Portfolio", "Benchmark", "Difference"],
    )

    return totals.replace(0, "-")


@log_start_end(log=logger)
def get_var(
    portfolio_engine: PortfolioEngine,
    use_mean: bool = False,
    adjusted_var: bool = False,
    student_t: bool = False,
    percentile: float = 99.9,
) -> pd.DataFrame:
    """Get portfolio VaR

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    use_mean: bool
        if one should use the data mean return
    adjusted_var: bool
        if one should have VaR adjusted for skew and kurtosis (Cornish-Fisher-Expansion)
    student_t: bool
        If one should use the student-t distribution
    percentile: float
        var percentile (%)

    Returns
    -------
    pd.DataFrame
        DataFrame with portfolio VaR

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.var(p)
    """

    return qa_model.get_var(
        data=portfolio_engine.portfolio_returns,
        use_mean=use_mean,
        adjusted_var=adjusted_var,
        student_t=student_t,
        percentile=percentile,
        portfolio=True,
    )


@log_start_end(log=logger)
def get_es(
    portfolio_engine: PortfolioEngine,
    use_mean: bool = False,
    distribution: str = "normal",
    percentile: float = 99.9,
) -> pd.DataFrame:
    """Get portfolio expected shortfall

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    use_mean:
        if one should use the data mean return
    distribution: str
        choose distribution to use: logistic, laplace, normal
    percentile: float
        es percentile (%)

    Returns
    -------
    pd.DataFrame
        DataFrame with portfolio expected shortfall

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.es(p)
    """

    return qa_model.get_es(
        data=portfolio_engine.portfolio_returns,
        use_mean=use_mean,
        distribution=distribution,
        percentile=percentile,
        portfolio=True,
    )


@log_start_end(log=logger)
def get_omega(
    portfolio_engine: PortfolioEngine,
    threshold_start: float = 0,
    threshold_end: float = 1.5,
) -> pd.DataFrame:
    """Get omega ratio

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    threshold_start: float
        annualized target return threshold start of plotted threshold range
    threshold_end: float
        annualized target return threshold end of plotted threshold range

    Returns
    -------
    pd.DataFrame
        DataFrame with portfolio omega ratio

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> p = openbb.portfolio.load("openbb_terminal/miscellaneous/portfolio/holdings_example.xlsx")
    >>> output = openbb.portfolio.om(p)
    """

    return qa_model.get_omega(
        data=portfolio_engine.portfolio_returns,
        threshold_start=threshold_start,
        threshold_end=threshold_end,
    )
