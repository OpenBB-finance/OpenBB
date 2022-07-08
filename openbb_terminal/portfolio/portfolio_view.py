"""Portfolio View"""
__docformat__ = "numpy"

import logging
from typing import List, Optional
import os

from datetime import datetime
import numpy as np
import scipy
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from sklearn.metrics import r2_score

from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.portfolio import (
    portfolio_helper,
    portfolio_model,
)

from openbb_terminal.helper_funcs import (
    export_data,
    plot_autoscale,
    print_rich_table,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

# pylint: disable=C0302,redefined-outer-name

# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from reportlab.lib.utils import ImageReader
# from openbb_terminal.portfolio import reportlab_helpers

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def load_info():
    """Prints instructions to load a CSV

    Returns
    ----------
    text : str
        Information on how to load a csv
    """
    text = """
In order to load a CSV do the following:

1. Add headers to the first row, below is data for each column:\n
\t1. Identifier for the asset (such as a stock ticker)
\t2. Type of asset (stock, bond, option, crypto)
\t3. The volume of the asset transacted
\t4. The buy date in yyyy/mm/dd
\t5. The Price paid for the asset
\t6. Any fees paid during the transaction
\t7. A premium paid or received if this was an option
\t8. Whether the asset was bought (covered) or sold (shorted)\n
2. Place this file in openbb_terminal/portfolio/portfolios\n
        """
    console.print(text)


@log_start_end(log=logger)
def display_orderbook(portfolio=None, show_index=False):
    """Display portfolio orderbook

    Parameters
    ----------
    portfolio: Portfolio
        Instance of Portfolio class
    show_index: bool
        Defaults to False.
    """

    if portfolio is None:
        logger.warning("No orderbook loaded")
        console.print("[red]No orderbook loaded.[/red]\n")
    else:
        print_rich_table(portfolio.get_orderbook(), show_index)


@log_start_end(log=logger)
def display_assets_allocation(
    portfolio_allocation: pd.DataFrame,
    benchmark_allocation: pd.DataFrame,
    limit: int = 10,
    include_separate_tables: bool = False,
):
    """Display portfolio asset allocation compared to the benchmark

    Parameters
    ----------
    portfolio_allocation: pd.DataFrame
        The asset allocation of the portfolio
    benchmark_allocation: pd.DataFrame
        The asset allocation of the benchmark
    limit: int
        The amount of assets you wish to show, by default this is set to 10.
    include_separate_tables: bool
        Whether to include separate asset allocation tables
    """
    benchmark_allocation = benchmark_allocation.iloc[:limit]
    portfolio_allocation = portfolio_allocation.iloc[:limit]

    combined = pd.DataFrame()

    for ticker, allocation in portfolio_allocation.items():
        if ticker in benchmark_allocation["symbol"].values:
            benchmark_allocation_value = float(
                benchmark_allocation[benchmark_allocation["symbol"] == ticker][
                    "holdingPercent"
                ]
            )
        else:
            benchmark_allocation_value = 0

        combined = combined.append(
            [
                [
                    ticker,
                    allocation,
                    benchmark_allocation_value,
                    allocation - benchmark_allocation_value,
                ]
            ]
        )

    combined.columns = ["Symbol", "Portfolio", "Benchmark", "Difference"]

    print_rich_table(
        combined.replace(0, "-"),
        headers=list(combined.columns),
        title=f"Portfolio vs. Benchmark - Top {len(combined) if len(combined) < limit else limit} Assets Allocation",
        floatfmt=[".2f", ".2%", ".2%", ".2%"],
        show_index=False,
    )

    if include_separate_tables:
        print_rich_table(
            pd.DataFrame(portfolio_allocation),
            headers=list(["Allocation"]),
            title=f"Portfolio - Top {len(portfolio_allocation) if len(benchmark_allocation) < limit else limit} "
            f"Assets Allocation",
            floatfmt=[".2%"],
            show_index=True,
        )
        print_rich_table(
            benchmark_allocation,
            headers=list(["Symbol", "Name", "Allocation"]),
            title=f"Benchmark - Top {len(benchmark_allocation) if len(benchmark_allocation) < limit else limit} "
            f"Assets Allocation",
            floatfmt=[".2f", ".2f", ".2%"],
            show_index=False,
        )


@log_start_end(log=logger)
def display_category_allocation(
    category: str,
    portfolio_allocation: pd.DataFrame,
    benchmark_allocation: pd.DataFrame,
    limit: int = 10,
    include_separate_tables: bool = False,
):
    """Display portfolio sector, country or region allocation compared to the benchmark

    Parameters
    ----------
    category: str
        Whether you want to show sectors, countries or regions
    portfolio_allocation: pd.DataFrame
        The allocation to the set category of the portfolio
    benchmark_allocation: pd.DataFrame
        The allocation to the set category of the benchmark
    limit: int
        The amount of assets you wish to show, by default this is set to 10.
    include_separate_tables: bool
        Whether to include separate asset allocation tables
    """
    benchmark_allocation = benchmark_allocation.iloc[:limit]
    portfolio_allocation = portfolio_allocation.iloc[:limit]

    combined = pd.DataFrame()

    for category_name, allocation in portfolio_allocation.items():
        if category_name in benchmark_allocation.index:
            benchmark_allocation_value = float(
                benchmark_allocation[benchmark_allocation.index == category_name]
            )
        else:
            benchmark_allocation_value = 0

        combined = combined.append(
            [
                [
                    category_name,
                    allocation,
                    benchmark_allocation_value,
                    allocation - benchmark_allocation_value,
                ]
            ]
        )

    combined.columns = [category.capitalize(), "Portfolio", "Benchmark", "Difference"]

    print_rich_table(
        combined.replace(0, "-"),
        headers=list(combined.columns),
        title=f"Portfolio vs. Benchmark - Top {len(combined) if len(combined) < limit else limit} "
        f"{category.capitalize()} Allocation",
        floatfmt=[".2f", ".2%", ".2%", ".2%"],
        show_index=False,
    )

    if include_separate_tables:
        print_rich_table(
            pd.DataFrame(portfolio_allocation),
            headers=list(["Allocation"]),
            title=f"Portfolio - Top {len(portfolio_allocation) if len(portfolio_allocation) < limit else limit} "
            f"{category.capitalize()} Allocation",
            floatfmt=[".2%"],
            show_index=True,
        )
        print_rich_table(
            pd.DataFrame(benchmark_allocation),
            headers=list(["Allocation"]),
            title=f"Benchmark - Top {len(benchmark_allocation) if len(benchmark_allocation) < limit else limit} "
            f"{category.capitalize()} Allocation",
            floatfmt=[".2%"],
            show_index=True,
        )


@log_start_end(log=logger)
def display_performance_vs_benchmark(
    portfolio_trades: pd.DataFrame,
    benchmark_trades: pd.DataFrame,
    period: str,
    show_all_trades: bool = False,
):
    """Display portfolio performance vs the benchmark

    Parameters
    ----------
    portfolio_trades: pd.DataFrame
        Object containing trades made within the portfolio.
    benchmark_trades: pd.DataFrame
        Object containing trades made within the benchmark.
    period : str
        Period to consider performance. From: mtd, qtd, ytd, 3m, 6m, 1y, 3y, 5y, 10y, all
    show_all_trades: bool
        Whether to also show all trades made and their performance (default is False)
    """

    portfolio_trades.index = pd.to_datetime(portfolio_trades["Date"].values)
    portfolio_trades = portfolio_helper.filter_df_by_period(portfolio_trades, period)

    benchmark_trades.index = pd.to_datetime(benchmark_trades["Date"].values)
    benchmark_trades = portfolio_helper.filter_df_by_period(benchmark_trades, period)

    if show_all_trades:
        # Combine DataFrames
        combined = pd.concat(
            [
                portfolio_trades[
                    ["Date", "Ticker", "Portfolio Value", "% Portfolio Return"]
                ],
                benchmark_trades[["Benchmark Value", "Benchmark % Return"]],
            ],
            axis=1,
        )

        # Calculate alpha
        combined["Alpha"] = (
            combined["% Portfolio Return"] - combined["Benchmark % Return"]
        )

        combined["Date"] = pd.to_datetime(combined["Date"]).dt.date

        print_rich_table(
            combined,
            title=f"Portfolio vs. Benchmark - Individual Trades in period: {period}",
            headers=list(combined.columns),
            show_index=False,
            floatfmt=[".2f", ".2f", ".2f", ".2%", ".2f", ".2%", ".2%"],
        )
    else:
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
        print_rich_table(
            totals.replace(0, "-"),
            title=f"Portfolio vs. Benchmark - Totals in period: {period}",
            headers=list(totals.columns),
            show_index=True,
        )


@log_start_end(log=logger)
def display_cumulative_returns(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    period: str = "all",
    raw: bool = False,
    limit: int = 10,
    export: str = "",
    external_axes: Optional[plt.Axes] = None,
):
    """Display portfolio returns vs benchmark

    Parameters
    ----------
    portfolio_returns : pd.Series
        Returns of the portfolio
    benchmark_returns : pd.Series
        Returns of the benchmark
    period : str
        Period to compare cumulative returns and benchmark
    raw : False
        Display raw data from cumulative return
    limit : int
        Last cumulative returns to display
    export : str
        Export certain type of data
    external_axes: plt.Axes
        Optional axes to display plot on
    """

    portfolio_returns = portfolio_helper.filter_df_by_period(portfolio_returns, period)
    benchmark_returns = portfolio_helper.filter_df_by_period(benchmark_returns, period)

    cumulative_returns = 100 * portfolio_model.cumulative_returns(portfolio_returns)
    benchmark_c_returns = 100 * portfolio_model.cumulative_returns(benchmark_returns)

    if raw:
        last_cumulative_returns = cumulative_returns.to_frame()
        last_cumulative_returns = last_cumulative_returns.join(benchmark_c_returns)
        last_cumulative_returns.index = last_cumulative_returns.index.date
        print_rich_table(
            last_cumulative_returns.tail(limit),
            title="Cumulative Portfolio and Benchmark returns",
            headers=["Portfolio [%]", "Benchmark [%]"],
            show_index=True,
        )
    else:
        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            ax = external_axes

        ax.plot(cumulative_returns.index, cumulative_returns, label="Portfolio")
        ax.plot(benchmark_c_returns.index, benchmark_c_returns, label="Benchmark")

        ax.legend(loc="upper left")
        ax.set_ylabel("Cumulative Returns [%]")
        theme.style_primary_axis(ax)

        if not external_axes:
            theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cret",
        cumulative_returns.to_frame().join(benchmark_c_returns),
    )


@log_start_end(log=logger)
def display_yearly_returns(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    period: str = "all",
    raw: bool = False,
    export: str = "",
    external_axes: Optional[plt.Axes] = None,
):
    """Display yearly returns

    Parameters
    ----------
    portfolio_returns : pd.Series
        Returns of the portfolio
    benchmark_returns : pd.Series
        Returns of the benchmark
    period : str
        Period to compare cumulative returns and benchmark
    raw : False
        Display raw data from cumulative return
    export : str
        Export certain type of data
    external_axes: plt.Axes
        Optional axes to display plot on
    """
    portfolio_returns = portfolio_helper.filter_df_by_period(portfolio_returns, period)
    benchmark_returns = portfolio_helper.filter_df_by_period(benchmark_returns, period)

    creturns_year_idx = list()
    creturns_year_val = list()
    breturns_year_idx = list()
    breturns_year_val = list()

    for year in sorted(set(portfolio_returns.index.year)):
        creturns_year = portfolio_returns[portfolio_returns.index.year == year]
        cumulative_returns = 100 * portfolio_model.cumulative_returns(creturns_year)

        creturns_year_idx.append(datetime.strptime(f"{year}-04-15", "%Y-%m-%d"))
        creturns_year_val.append(cumulative_returns.values[-1])

        breturns_year = benchmark_returns[benchmark_returns.index.year == year]
        benchmark_c_returns = 100 * portfolio_model.cumulative_returns(breturns_year)

        breturns_year_idx.append(datetime.strptime(f"{year}-08-15", "%Y-%m-%d"))
        breturns_year_val.append(benchmark_c_returns.values[-1])

    if raw:
        yreturns = pd.DataFrame(
            {
                "Portfolio [%]": pd.Series(
                    creturns_year_val, index=list(set(portfolio_returns.index.year))
                ),
                "Benchmark [%]": pd.Series(
                    breturns_year_val, index=list(set(portfolio_returns.index.year))
                ),
                "Difference [%]": pd.Series(
                    np.array(creturns_year_val) - np.array(breturns_year_val),
                    index=list(set(portfolio_returns.index.year)),
                ),
            }
        )
        print_rich_table(
            yreturns.sort_index(),
            title="Yearly Portfolio and Benchmark returns",
            headers=["Portfolio [%]", "Benchmark [%]", "Difference [%]"],
            show_index=True,
        )

    else:
        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            ax = external_axes

        ax.bar(
            creturns_year_idx,
            creturns_year_val,
            width=100,
            label="Portfolio",
        )
        ax.bar(
            breturns_year_idx,
            breturns_year_val,
            width=100,
            label="Benchmark",
        )

        ax.legend(loc="upper left")
        ax.set_ylabel("Yearly Returns [%]")
        ax.set_title(f"Yearly Returns [%] in period {period}")
        theme.style_primary_axis(ax)

        if not external_axes:
            theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "yret",
        cumulative_returns.to_frame().join(benchmark_c_returns),
    )


@log_start_end(log=logger)
def display_monthly_returns(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    period: str = "all",
    raw: bool = False,
    show_vals: bool = False,
    export: str = "",
    external_axes: Optional[plt.Axes] = None,
):
    """Display monthly returns

    Parameters
    ----------
    portfolio_returns : pd.Series
        Returns of the portfolio
    benchmark_returns : pd.Series
        Returns of the benchmark
    period : str
        Period to compare cumulative returns and benchmark
    raw : False
        Display raw data from cumulative return
    show_vals : False
        Show values on heatmap
    export : str
        Export certain type of data
    external_axes: plt.Axes
        Optional axes to display plot on
    """
    portfolio_returns = portfolio_helper.filter_df_by_period(portfolio_returns, period)
    benchmark_returns = portfolio_helper.filter_df_by_period(benchmark_returns, period)

    creturns_month_val = list()
    breturns_month_val = list()

    for year in sorted(list(set(portfolio_returns.index.year))):
        creturns_year = portfolio_returns[portfolio_returns.index.year == year]
        creturns_val = list()
        for i in range(1, 13):
            creturns_year_month = creturns_year[creturns_year.index.month == i]
            creturns_year_month_val = 100 * portfolio_model.cumulative_returns(
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
            breturns_year_month_val = 100 * portfolio_model.cumulative_returns(
                breturns_year_month
            )

            if breturns_year_month.empty:
                breturns_val.append(0)
            else:
                breturns_val.append(breturns_year_month_val.values[-1])
        breturns_month_val.append(breturns_val)

    monthly_returns = pd.DataFrame(
        creturns_month_val,
        index=sorted(list(set(portfolio_returns.index.year))),
        columns=[
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
        ],
    )
    bench_monthly_returns = pd.DataFrame(
        breturns_month_val,
        index=sorted(list(set(benchmark_returns.index.year))),
        columns=[
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
        ],
    )

    if raw:
        print_rich_table(
            monthly_returns,
            title="Portfolio monthly returns",
            headers=monthly_returns.columns,
            show_index=True,
        )
        print_rich_table(
            bench_monthly_returns,
            title="Benchmark monthly returns",
            headers=bench_monthly_returns.columns,
            show_index=True,
        )

    else:
        if external_axes is None:
            _, ax = plt.subplots(
                2,
                1,
                figsize=plot_autoscale(),
                dpi=PLOT_DPI,
            )
        else:
            ax = external_axes

        ax[0].set_title(f"Portfolio in period {period}")
        sns.heatmap(
            monthly_returns,
            cmap="bwr_r",
            vmax=max(monthly_returns.max().max(), bench_monthly_returns.max().max()),
            vmin=min(monthly_returns.min().min(), bench_monthly_returns.min().min()),
            center=0,
            annot=show_vals,
            fmt=".1f",
            mask=monthly_returns.applymap(lambda x: x == 0),
            ax=ax[0],
        )
        theme.style_primary_axis(ax[0])

        ax[1].set_title(f"Benchmark in period {period}")
        sns.heatmap(
            bench_monthly_returns,
            cmap="bwr_r",
            vmax=max(monthly_returns.max().max(), bench_monthly_returns.max().max()),
            vmin=min(monthly_returns.min().min(), bench_monthly_returns.min().min()),
            center=0,
            annot=show_vals,
            fmt=".1f",
            mask=bench_monthly_returns.applymap(lambda x: x == 0),
            ax=ax[1],
        )
        theme.style_primary_axis(ax[1])

        if not external_axes:
            theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "mret",
    )


@log_start_end(log=logger)
def display_daily_returns(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    period: str = "all",
    raw: bool = False,
    limit: int = 10,
    export: str = "",
    external_axes: Optional[plt.Axes] = None,
):
    """Display daily returns

    Parameters
    ----------
    portfolio_returns : pd.Series
        Returns of the portfolio
    benchmark_returns : pd.Series
        Returns of the benchmark
    period : str
        Period to compare cumulative returns and benchmark
    raw : False
        Display raw data from cumulative return
    limit : int
        Last daily returns to display
    export : str
        Export certain type of data
    external_axes: plt.Axes
        Optional axes to display plot on
    """
    portfolio_returns = portfolio_helper.filter_df_by_period(portfolio_returns, period)
    benchmark_returns = portfolio_helper.filter_df_by_period(benchmark_returns, period)

    if raw:
        last_returns = portfolio_returns.to_frame()
        last_returns = last_returns.join(benchmark_returns)
        last_returns.index = last_returns.index.date
        print_rich_table(
            last_returns.tail(limit),
            title="Portfolio and Benchmark daily returns",
            headers=["Portfolio [%]", "Benchmark [%]"],
            show_index=True,
        )
    else:
        if external_axes is None:
            _, ax = plt.subplots(
                2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI, sharex=True
            )
        else:
            ax = external_axes

        ax[0].set_title(f"Portfolio in period {period}")
        ax[0].plot(portfolio_returns.index, portfolio_returns, label="Portfolio")
        ax[0].set_ylabel("Returns [%]")
        theme.style_primary_axis(ax[0])
        ax[1].set_title(f"Benchmark in period {period}")
        ax[1].plot(benchmark_returns.index, benchmark_returns, label="Benchmark")
        ax[1].set_ylabel("Returns [%]")
        theme.style_primary_axis(ax[1])

        if not external_axes:
            theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dret",
        portfolio_returns.to_frame().join(benchmark_returns),
    )


@log_start_end(log=logger)
def display_distribution_returns(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    period: str = "all",
    raw: bool = False,
    export: str = "",
    external_axes: Optional[plt.Axes] = None,
):
    """Display daily returns

    Parameters
    ----------
    portfolio_returns : pd.Series
        Returns of the portfolio
    benchmark_returns : pd.Series
        Returns of the benchmark
    period : str
        Period to compare cumulative returns and benchmark
    raw : False
        Display raw data from cumulative return
    export : str
        Export certain type of data
    external_axes: plt.Axes
        Optional axes to display plot on
    """
    portfolio_returns = portfolio_helper.filter_df_by_period(portfolio_returns, period)
    benchmark_returns = portfolio_helper.filter_df_by_period(benchmark_returns, period)

    stats = portfolio_returns.describe().to_frame().join(benchmark_returns.describe())

    if raw:
        print_rich_table(
            stats,
            title=f"Stats for Portfolio and Benchmark in period {period}",
            show_index=True,
            headers=["Portfolio", "Benchmark"],
        )

    else:
        if external_axes is None:
            _, ax = plt.subplots(
                1,
                2,
                figsize=plot_autoscale(),
                dpi=PLOT_DPI,
            )
        else:
            ax = external_axes

        ax[0].set_title("Portfolio distribution")
        sns.kdeplot(portfolio_returns.values, ax=ax[0])
        ax[0].set_ylabel("Density")
        ax[0].set_xlabel("Daily return [%]")
        theme.style_primary_axis(ax[0])

        ax[1].set_title("Benchmark distribution")
        sns.kdeplot(benchmark_returns.values, ax=ax[1])
        ax[1].set_ylabel("Density")
        ax[1].set_xlabel("Daily return [%]")
        theme.style_primary_axis(ax[1])

        if not external_axes:
            theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "distr",
        stats,
    )


@log_start_end(log=logger)
def display_holdings_value(
    portfolio: portfolio_model.PortfolioModel,
    sum_assets: bool = False,
    raw: bool = False,
    limit: int = 10,
    export: str = "",
    external_axes: Optional[plt.Axes] = None,
):
    """Display holdings of assets (absolute value)

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    sum_assets: bool
        Sum assets over time
    raw : bool
        To display raw data
    limit : int
        Number of past market days to display holdings
    export: str
        Format to export plot
    external_axes: plt.Axes
        Optional axes to display plot on
    """

    all_holdings = portfolio.historical_trade_data["End Value"][portfolio.tickers_list]

    if raw:
        all_holdings["Total Value"] = all_holdings.sum(axis=1)
        # No need to account for time since this is daily data
        all_holdings.index = all_holdings.index.date

        print_rich_table(
            all_holdings.tail(limit),
            title="Holdings of assets (absolute value)",
            headers=all_holdings.columns,
            show_index=True,
        )

    else:
        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            ax = external_axes

        if sum_assets:
            ax.stackplot(
                all_holdings.index,
                [all_holdings[col] for col in all_holdings.columns],
                labels=all_holdings.columns,
            )
            ax.set_title("Asset Holdings (value)")
        else:
            all_holdings.plot(ax=ax)
            ax.set_title("Individual Asset Holdings (value)")

        if len(all_holdings.columns) > 10:
            legend_columns = round(len(all_holdings.columns) / 5)
        elif len(all_holdings.columns) > 40:
            legend_columns = round(len(all_holdings.columns) / 10)
        else:
            legend_columns = 1
        ax.legend(loc="upper left", ncol=legend_columns)
        ax.set_ylabel("Holdings ($)")
        theme.style_primary_axis(ax)
        if external_axes is None:
            theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "holdv",
        all_holdings,
    )


@log_start_end(log=logger)
def display_holdings_percentage(
    portfolio: portfolio_model.PortfolioModel,
    sum_assets: bool = False,
    raw: bool = False,
    limit: int = 10,
    export: str = "",
    external_axes: Optional[plt.Axes] = None,
):
    """Display holdings of assets (in percentage)

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    sum_assets: bool
        Sum assets over time
    raw : bool
        To display raw data
    limit : int
        Number of past market days to display holdings
    export: str
        Format to export plot
    external_axes: plt.Axes
        Optional axes to display plot on
    """

    all_holdings = portfolio.historical_trade_data["End Value"][portfolio.tickers_list]

    all_holdings = all_holdings.divide(all_holdings.sum(axis=1), axis=0) * 100

    # order it a bit more in terms of magnitude
    all_holdings = all_holdings[all_holdings.sum().sort_values(ascending=False).index]

    if raw:
        # No need to account for time since this is daily data
        all_holdings.index = all_holdings.index.date

        all_holdings.columns = [f"{col} [%]" for col in all_holdings.columns]

        print_rich_table(
            all_holdings.tail(limit),
            title="Holdings of assets (in percentage)",
            headers=all_holdings.columns,
            show_index=True,
        )

    else:
        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            ax = external_axes

        if sum_assets:
            ax.stackplot(
                all_holdings.index,
                all_holdings.values.T,
                labels=all_holdings.columns,
            )
            ax.set_title("Asset Holdings (percentage)")
        else:
            all_holdings.plot(ax=ax)
            ax.set_title("Individual Asset Holdings (percentage)")

        if len(all_holdings.columns) > 10:
            legend_columns = round(len(all_holdings.columns) / 5)
        elif len(all_holdings.columns) > 40:
            legend_columns = round(len(all_holdings.columns) / 10)
        else:
            legend_columns = 1
        ax.legend(loc="upper left", ncol=legend_columns)
        ax.set_ylabel("Portfolio holdings (%)")
        theme.style_primary_axis(ax)
        if external_axes is None:
            theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "holdp",
        all_holdings,
    )


@log_start_end(log=logger)
def display_rolling_volatility(
    benchmark_returns: pd.Series,
    portfolio_returns: pd.Series,
    period: str = "1y",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display rolling volatility

    Parameters
    ----------
    portfolio_returns : pd.Series
        Returns of the portfolio
    benchmark_returns : pd.Series
        Returns of the benchmark
    period: str
        Period for window to consider
    export: str
        Export to file
    external_axes: Optional[List[plt.Axes]]
        Optional axes to display plot on
    """
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis items.")
            console.print("[red]1 axes expected.\n[/red]")
            return
        ax = external_axes

    length = portfolio_helper.PERIODS_DAYS[period]

    rolling_volatility = portfolio_model.rolling_volatility(portfolio_returns, length)
    rolling_volatility_bench = portfolio_model.rolling_volatility(
        benchmark_returns, length
    )

    rolling_volatility.plot(ax=ax)
    rolling_volatility_bench.plot(ax=ax)
    ax.set_title(f"Rolling Volatility using {period} window")
    ax.set_xlabel("Date")
    ax.legend(["Portfolio", "Benchmark"], loc="upper left")
    ax.set_xlim(rolling_volatility.index[0], rolling_volatility.index[-1])

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "rvol",
        rolling_volatility.to_frame().join(rolling_volatility_bench),
    )


@log_start_end(log=logger)
def display_rolling_sharpe(
    benchmark_returns: pd.Series,
    portfolio_returns: pd.Series,
    period: str = "1y",
    risk_free_rate: float = 0,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display rolling sharpe

    Parameters
    ----------
    portfolio_returns : pd.Series
        Returns of the portfolio
    benchmark_returns : pd.Series
        Returns of the benchmark
    period: str
        Period for window to consider
    risk_free_rate: float
        Value to use for risk free rate in sharpe/other calculations
    export: str
        Export to file
    external_axes: Optional[List[plt.Axes]]
        Optional axes to display plot on
    """
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis items.")
            console.print("[red]1 axes expected.\n[/red]")
            return
        ax = external_axes

    length = portfolio_helper.PERIODS_DAYS[period]

    rolling_sharpe = portfolio_model.rolling_sharpe(
        portfolio_returns, risk_free_rate, length
    )
    rolling_sharpe_bench = portfolio_model.rolling_sharpe(
        benchmark_returns, risk_free_rate, length
    )

    rolling_sharpe.plot(ax=ax)
    rolling_sharpe_bench.plot(ax=ax)
    ax.set_title(f"Rolling Sharpe using {period} window")
    ax.set_xlabel("Date")
    ax.legend(["Portfolio", "Benchmark"], loc="upper left")
    ax.set_xlim(rolling_sharpe.index[0], rolling_sharpe.index[-1])

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "rsharpe",
        rolling_sharpe.to_frame().join(rolling_sharpe_bench),
    )


@log_start_end(log=logger)
def display_rolling_sortino(
    benchmark_returns: pd.Series,
    portfolio_returns: pd.Series,
    period: str = "1y",
    risk_free_rate: float = 0,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display rolling sortino

    Parameters
    ----------
    portfolio_returns : pd.Series
        Returns of the portfolio
    benchmark_returns : pd.Series
        Returns of the benchmark
    period: str
        Period for window to consider
    risk_free_rate: float
        Value to use for risk free rate in sharpe/other calculations
    export: str
        Export to file
    external_axes: Optional[List[plt.Axes]]
        Optional axes to display plot on
    """
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis items.")
            console.print("[red]1 axes expected.\n[/red]")
            return
        ax = external_axes

    length = portfolio_helper.PERIODS_DAYS[period]

    rolling_sortino = portfolio_model.rolling_sortino(
        portfolio_returns, risk_free_rate, length
    )
    rolling_sortino_bench = portfolio_model.rolling_sortino(
        benchmark_returns, risk_free_rate, length
    )

    rolling_sortino.plot(ax=ax)
    rolling_sortino_bench.plot(ax=ax)
    ax.set_title(f"Rolling Sortino using {period} window")
    ax.set_xlabel("Date")
    ax.legend(["Portfolio", "Benchmark"], loc="upper left")
    ax.set_xlim(rolling_sortino.index[0], rolling_sortino.index[-1])

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "rsortino",
        rolling_sortino.to_frame().join(rolling_sortino_bench),
    )


@log_start_end(log=logger)
def display_rolling_beta(
    benchmark_returns: pd.Series,
    portfolio_returns: pd.Series,
    period: str = "1y",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display rolling beta

    Parameters
    ----------
    portfolio_returns : pd.Series
        Returns of the portfolio
    benchmark_returns : pd.Series
        Returns of the benchmark
    period: str
        Period for window to consider
    export: str
        Export to file
    external_axes: Optional[List[plt.Axes]]
        Optional axes to display plot on
    """
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis items.")
            console.print("[red]1 axes expected.\n[/red]")
            return
        ax = external_axes

    length = portfolio_helper.PERIODS_DAYS[period]

    # Rolling beta is defined as Cov(Port,Bench)/var(Bench)
    covs = (
        pd.DataFrame({"Portfolio": portfolio_returns, "Benchmark": benchmark_returns})
        .dropna(axis=0)
        .rolling(length)
        .cov()
        .unstack()
        .dropna()
    )
    rolling_beta = covs["Portfolio"]["Benchmark"] / covs["Benchmark"]["Benchmark"]
    rolling_beta.plot(ax=ax)

    ax.set_title(f"Rolling Beta using {period} window")
    ax.set_xlabel("Date")
    ax.hlines(
        [1],
        xmin=rolling_beta.index[0],
        xmax=rolling_beta.index[-1],
        ls="--",
        color="red",
    )
    ax.legend(["Portfolio", "Benchmark"], loc="upper left")
    ax.set_xlim(rolling_beta.index[0], rolling_beta.index[-1])

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "rbeta",
        rolling_beta,
    )


@log_start_end(log=logger)
def display_maximum_drawdown(
    holdings: pd.Series,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display maximum drawdown curve

    Parameters
    ----------
    holdings: pd.DataFrame
        Dataframe of holdings vs time
    export: str
        Format to export data
    external_axes: plt.Axes
        Optional axes to display plot on
    """
    drawdown = portfolio_model.calculate_drawdown(holdings)
    if external_axes is None:
        _, ax = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI, sharex=True)
    else:
        ax = external_axes

    ax[0].plot(holdings.index, holdings)
    ax[0].set_title("Holdings")
    ax[1].plot(holdings.index, drawdown)
    ax[1].fill_between(holdings.index, np.asarray(drawdown), alpha=0.4)
    ax[1].set_title("Portfolio Drawdown")

    theme.style_primary_axis(ax[1])
    if external_axes is None:
        theme.visualize_output()
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "maxdd",
    )


@log_start_end(log=logger)
def display_rsquare(
    portfolio: portfolio_model.PortfolioModel,
    export: str = "",
):
    """Display R-square

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    export : str
        Export data format
    """
    print_rich_table(
        portfolio.get_r2_score(),
        title="R-Square Score between Portfolio and Benchmark",
        headers=["R-Square Score"],
        show_index=True,
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "rsquare",
    )


@log_start_end(log=logger)
def display_skewness(
    portfolio: portfolio_model.PortfolioModel,
    export: str = "",
):
    """Display skewness

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    export : str
        Export data format
    """
    print_rich_table(
        portfolio.get_skewness(),
        title="Skewness for Portfolio and Benchmark",
        show_index=True,
        floatfmt=".3f",
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "skew",
    )


@log_start_end(log=logger)
def display_kurtosis(
    portfolio: portfolio_model.PortfolioModel,
    export: str = "",
):
    """Display kurtosis

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    export : str
        Export data format
    """
    print_rich_table(
        portfolio.get_kurtosis(),
        title="Kurtosis for Portfolio and Benchmark",
        show_index=True,
        floatfmt=".3f",
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "kurt",
    )


@log_start_end(log=logger)
def display_stats(
    portfolio: portfolio_model.PortfolioModel,
    period: str = "all",
    export: str = "",
):
    """Display stats

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    period : str
        Period to consider. Choices are: mtd, qtd, ytd, 3m, 6m, 1y, 3y, 5y, 10y, all
    export : str
        Export data format
    """
    print_rich_table(
        portfolio.get_stats(period),
        title=f"Stats for Portfolio and Benchmark in period {period}",
        show_index=True,
        floatfmt=".3f",
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "stats",
    )


@log_start_end(log=logger)
def display_volatility(
    portfolio: portfolio_model.PortfolioModel,
    export: str = "",
):
    """Display volatility for multiple periods

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    export : str
        Export data format
    """
    df = portfolio.get_volatility()
    print_rich_table(
        df,
        title="Volatility for Portfolio and Benchmark",
        show_index=True,
        floatfmt=".3f",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_volatility", df
    )


@log_start_end(log=logger)
def display_sharpe_ratio(
    portfolio: portfolio_model.PortfolioModel,
    risk_free_rate: float,
    export: str = "",
):
    """Display sharpe ratio for multiple periods

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    risk_free_rate: float
        Risk free rate value
    export : str
        Export data format
    """
    df = portfolio.get_sharpe_ratio(risk_free_rate)
    print_rich_table(
        df,
        title="Sharpe ratio for Portfolio and Benchmark",
        show_index=True,
        floatfmt=".3f",
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "metric_sharpe",
        df,
    )


@log_start_end(log=logger)
def display_sortino_ratio(
    portfolio: portfolio_model.PortfolioModel,
    risk_free_rate: float,
    export: str = "",
):
    """Display sortino ratio for multiple periods

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    risk_free_rate: float
        Risk free rate value
    export : str
        Export data format
    """
    df = portfolio.get_sortino_ratio(risk_free_rate)
    print_rich_table(
        df,
        title="Sortino ratio for Portfolio and Benchmark",
        show_index=True,
        floatfmt=".3f",
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "metric_sortino",
        df,
    )


@log_start_end(log=logger)
def display_maximum_drawdown_ratio(
    portfolio: portfolio_model.PortfolioModel,
    export: str = "",
):
    """Display maximum drawdown for multiple periods

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    export : str
        Export data format
    """
    df = portfolio.get_maximum_drawdown_ratio()
    print_rich_table(
        df,
        title="Maximum drawdown for Portfolio and Benchmark",
        show_index=True,
        floatfmt=".3f",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_maxdrawdown", df
    )


@log_start_end(log=logger)
def display_gaintopain_ratio(
    portfolio: portfolio_model.PortfolioModel,
    export: str = "",
):
    """Display gain-to-pain ratio for multiple periods

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with returns and benchmark loaded
    export : str
        Export data format
    """
    df = portfolio.get_gaintopain_ratio()
    print_rich_table(
        df,
        title="Gain-to-pain ratio for portfolio and benchmark",
        show_index=True,
        floatfmt=".3f",
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "metric_gaintopain_ratio",
        df,
    )


@log_start_end(log=logger)
def display_tracking_error(
    portfolio: portfolio_model.PortfolioModel,
    export: str = "",
):
    """Display tracking error for multiple periods

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with returns and benchmark loaded
    export : str
        Export data format
    """
    df, _ = portfolio.get_tracking_error()
    print_rich_table(
        df,
        title="Benchmark Tracking Error",
        show_index=True,
        floatfmt=".3f",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_tracking_error", df
    )


@log_start_end(log=logger)
def display_information_ratio(
    portfolio: portfolio_model.PortfolioModel,
    export: str = "",
):
    """Display information ratio for multiple periods

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with returns and benchmark loaded
    export : str
        Export data format
    """
    df, _ = portfolio.get_information_ratio()
    print_rich_table(
        df,
        title="Information ratio for portfolio",
        show_index=True,
        floatfmt=".3f",
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "metric_information_ratio",
        df,
    )


@log_start_end(log=logger)
def display_tail_ratio(
    portfolio: portfolio_model.PortfolioModel,
    export: str = "",
):
    """Display tail ratio for multiple periods

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with returns and benchmark loaded
    export : str
        Export data format
    """
    df, _, _ = portfolio.get_tail_ratio()
    print_rich_table(
        df,
        title="Tail ratio for portfolio and benchmark",
        show_index=True,
        floatfmt=".3f",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_tail_ratio", df
    )


@log_start_end(log=logger)
def display_common_sense_ratio(
    portfolio: portfolio_model.PortfolioModel,
    export: str = "",
):
    """Display common sense ratio for multiple periods

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with returns and benchmark loaded
    export : str
        Export data format
    """
    df = portfolio.get_common_sense_ratio()
    print_rich_table(
        df,
        title="Common sense ratio for portfolio and benchmark",
        show_index=True,
        floatfmt=".3f",
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "metric_common_sense_ratio",
        df,
    )


@log_start_end(log=logger)
def display_jensens_alpha(
    portfolio: portfolio_model.PortfolioModel,
    rf: float = 0,
    export: str = "",
):
    """Display jensens alpha for multiple periods

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with returns and benchmark loaded
    rf: float
            Risk free rate
    export : str
        Export data format
    """
    df, _ = portfolio.get_jensens_alpha(rf=rf)
    print_rich_table(
        df,
        title="Portfolio's jensen's alpha",
        show_index=True,
        floatfmt=".3f",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_jensens_alpha", df
    )


@log_start_end(log=logger)
def display_calmar_ratio(
    portfolio: portfolio_model.PortfolioModel,
    export: str = "",
):
    """Display calmar ratio for multiple periods

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with returns and benchmark loaded
    export : str
        Export data format
    """
    df, _ = portfolio.get_calmar_ratio()
    print_rich_table(
        df,
        title="Calmar ratio for portfolio and benchmark",
        show_index=True,
        floatfmt=".3f",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_calmar_ratio", df
    )


@log_start_end(log=logger)
def display_kelly_criterion(
    portfolio: portfolio_model.PortfolioModel,
    export: str = "",
):
    """Display kelly criterion for multiple periods

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades and returns loaded
    export : str
        Export data format
    """
    df = portfolio.get_kelly_criterion()
    print_rich_table(
        df,
        title="Kelly criterion of the portfolio",
        show_index=True,
        floatfmt=".3f",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_kelly_criterion", df
    )


def display_payoff_ratio(
    portfolio: portfolio_model.PortfolioModel,
    export: str = "",
):
    """Display payoff ratio for multiple periods

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    export : str
        Export data format
    """
    df = portfolio.get_payoff_ratio()
    print_rich_table(
        df,
        title="Portfolio's payoff ratio",
        show_index=True,
        floatfmt=".3f",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_payoff_ratio", df
    )


def display_profit_factor(
    portfolio: portfolio_model.PortfolioModel,
    export: str = "",
):
    """Display profit factor for multiple periods

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    export : str
        Export data format
    """
    df = portfolio.get_profit_factor()
    print_rich_table(
        df,
        title="Portfolio's profit factor",
        show_index=True,
        floatfmt=".3f",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_profit_factor", df
    )


@log_start_end(log=logger)
def display_summary_portfolio_benchmark(
    portfolio_returns: pd.Series,
    benchmark_returns: pd.Series,
    period: str = "all",
    risk_free_rate: float = 0,
    export: str = "",
):
    """Display summary portfolio and benchmark returns

    Parameters
    ----------
    portfolio_returns : pd.Series
        Returns of the portfolio
    benchmark_returns : pd.Series
        Returns of the benchmark
    period : str
        Period to compare cumulative returns and benchmark
    risk_free_rate : float
        Risk free rate for calculations
    export : str
        Export certain type of data
    """
    portfolio_returns = portfolio_helper.filter_df_by_period(portfolio_returns, period)
    benchmark_returns = portfolio_helper.filter_df_by_period(benchmark_returns, period)

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
        "Maximum Drawdowwn": [
            portfolio_model.get_maximum_drawdown(portfolio_returns),
            portfolio_model.get_maximum_drawdown(benchmark_returns),
        ],
        "Sharpe ratio": [
            portfolio_model.sharpe_ratio(portfolio_returns, risk_free_rate),
            portfolio_model.sharpe_ratio(benchmark_returns, risk_free_rate),
        ],
        "Sortino ratio": [
            portfolio_model.sortino_ratio(portfolio_returns, risk_free_rate),
            portfolio_model.sortino_ratio(benchmark_returns, risk_free_rate),
        ],
        "R2 Score": [
            r2_score(portfolio_returns, benchmark_returns),
            r2_score(portfolio_returns, benchmark_returns),
        ],
    }

    summary = pd.DataFrame(
        metrics.values(), index=metrics.keys(), columns=["Portfolio", "Benchmark"]
    )

    print_rich_table(
        summary,
        title=f"Summary of Portfolio vs Benchmark for {period} period",
        show_index=True,
        headers=summary.columns,
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "summary",
        summary,
    )
