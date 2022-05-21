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

# pylint: disable=C0302

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

    if show_all_trades:
        # Combine DataFrames
        combined = pd.concat(
            [
                portfolio_trades[
                    ["Date", "Name", "Portfolio Value", "% Portfolio Return"]
                ],
                benchmark_trades[["Benchmark Value", "% Benchmark Return"]],
            ],
            axis=1,
        )

        # Calculate alpha
        combined["Alpha"] = (
            combined["% Portfolio Return"] - combined["% Benchmark Return"]
        )

        combined["Date"] = pd.to_datetime(combined["Date"]).dt.date

        print_rich_table(
            combined,
            title=f"Portfolio vs. Benchmark - Individual Trades in period: {period}",
            headers=list(combined.columns),
            show_index=False,
            floatfmt=[".2f", ".2f", ".2f", ".2%", ".2f", ".2%", ".2%"],
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

    cumulative_returns = 100 * (
        (1 + portfolio_returns.shift(periods=1, fill_value=0)).cumprod() - 1
    )
    benchmark_c_returns = 100 * (
        (1 + benchmark_returns.shift(periods=1, fill_value=0)).cumprod() - 1
    )

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
        cumulative_returns = 100 * (
            (1 + creturns_year.shift(periods=1, fill_value=0)).cumprod() - 1
        )

        creturns_year_idx.append(datetime.strptime(f"{year}-04-15", "%Y-%m-%d"))
        creturns_year_val.append(cumulative_returns.values[-1])

        breturns_year = benchmark_returns[benchmark_returns.index.year == year]
        benchmark_c_returns = 100 * (
            (1 + breturns_year.shift(periods=1, fill_value=0)).cumprod() - 1
        )

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
            creturns_year_month_val = 100 * (
                (1 + creturns_year_month.shift(periods=1, fill_value=0)).cumprod() - 1
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
            breturns_year_month_val = 100 * (
                (1 + breturns_year_month.shift(periods=1, fill_value=0)).cumprod() - 1
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
    portfolio: portfolio_model.Portfolio,
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
    all_holdings = pd.concat(
        [
            portfolio.portfolio["StockHoldings"],
            portfolio.portfolio["ETFHoldings"],
            portfolio.portfolio["CryptoHoldings"],
        ],
        axis=1,
    )
    all_holdings = all_holdings.drop(columns=["temp"])

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
    portfolio: portfolio_model.Portfolio,
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
    all_holdings = pd.concat(
        [
            portfolio.portfolio["StockHoldings"],
            portfolio.portfolio["ETFHoldings"],
            portfolio.portfolio["CryptoHoldings"],
        ],
        axis=1,
    )
    all_holdings = all_holdings.drop(columns=["temp"])

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

    rolling_volatility = portfolio_returns.rolling(length).std()
    rolling_volatility_bench = benchmark_returns.rolling(length).std()

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

    rolling_sharpe = portfolio_returns.rolling(length).apply(
        lambda x: (x.mean() - risk_free_rate) / x.std()
    )
    rolling_sharpe_bench = benchmark_returns.rolling(length).apply(
        lambda x: (x.mean() - risk_free_rate) / x.std()
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

    rolling_sortino = portfolio_returns.rolling(length).apply(
        lambda x: (x.mean() - risk_free_rate) / x[x < 0].std()
    )
    rolling_sortino_bench = benchmark_returns.rolling(length).apply(
        lambda x: (x.mean() - risk_free_rate) / x[x < 0].std()
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
    portfolio: portfolio_model.Portfolio,
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
    portfolio: portfolio_model.Portfolio,
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
    portfolio: portfolio_model.Portfolio,
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
    portfolio: portfolio_model.Portfolio,
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
    portfolio: portfolio_model.Portfolio,
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
    portfolio: portfolio_model.Portfolio,
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
    portfolio: portfolio_model.Portfolio,
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
    portfolio: portfolio_model.Portfolio,
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

    metrics = {}
    metrics["Volatility"] = [portfolio_returns.std(), benchmark_returns.std()]
    metrics["Skew"] = [
        scipy.stats.skew(portfolio_returns),
        scipy.stats.skew(benchmark_returns),
    ]
    metrics["Kurtosis"] = [
        scipy.stats.kurtosis(portfolio_returns),
        scipy.stats.kurtosis(benchmark_returns),
    ]
    metrics["Maximum Drawdowwn"] = [
        portfolio_helper.get_maximum_drawdown(portfolio_returns),
        portfolio_helper.get_maximum_drawdown(benchmark_returns),
    ]
    metrics["Sharpe ratio"] = [
        portfolio_helper.sharpe_ratio(portfolio_returns, risk_free_rate),
        portfolio_helper.sharpe_ratio(benchmark_returns, risk_free_rate),
    ]
    metrics["Sortino ratio"] = [
        portfolio_helper.sortino_ratio(portfolio_returns, risk_free_rate),
        portfolio_helper.sortino_ratio(benchmark_returns, risk_free_rate),
    ]
    metrics["R2 Score"] = [
        r2_score(portfolio_returns, benchmark_returns),
        r2_score(portfolio_returns, benchmark_returns),
    ]

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


#
# @log_start_end(log=logger)
# def plot_overall_return(
#     comb: pd.DataFrame, m_tick: str, plot: bool = False
# ) -> ImageReader:
#     """Generates overall return graph
#
#     Parameters
#     ----------
#     comb : pd.DataFrame
#         Dataframe with returns
#     m_tick : str
#         The ticker for the market asset
#     plot : bool
#         Whether to plot the graph or return it for PDF
#
#     Returns
#     ----------
#     img : ImageReader
#         Overal return graph
#     """
#     fig, ax = plt.subplots(figsize=(10, 5))
#     ax.plot(comb.index, comb["return"], color="tab:blue", label="Portfolio")
#     ax.plot(comb.index, comb[("Market", "Return")], color="orange", label=m_tick)
#
#     ax.set_ylabel("", fontweight="bold", fontsize=12, color="black")
#     ax.set_xlabel("")
#     ax.yaxis.set_label_coords(-0.1, 0.5)
#     ax.grid(True)
#     ax.spines["top"].set_visible(False)
#     ax.spines["right"].set_visible(False)
#     ax.spines["bottom"].set_visible(False)
#     ax.spines["left"].set_visible(False)
#     fig.suptitle(
#         "Cumulative Performance", y=0.99, fontweight="bold", fontsize=14, color="black"
#     )
#     ax.axhline(0, ls="-", lw=1, color="gray", zorder=1)
#     ax.axhline(0, ls="--", lw=1, color="black", zorder=2)
#     fig.set_facecolor("white")
#     ax.set_title(
#         f'{comb.index[:1][0].strftime("%Y/%m/%d")} - {comb.index[-1:][0].strftime("%Y/%m/%d")}',
#         fontsize=12,
#         color="gray",
#     )
#     ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
#     ax.set_facecolor("white")
#     ax.legend()
#     fig.autofmt_xdate()
#     if plot:
#         plt.show()
#         console.print("")
#         return None
#     imgdata = BytesIO()
#     fig.savefig(imgdata, format="png")
#     plt.close("all")
#     imgdata.seek(0)
#     return ImageReader(imgdata)
#
#
# @log_start_end(log=logger)
# def plot_rolling_beta(df: pd.DataFrame) -> ImageReader:
#     """Returns a chart with the portfolio's rolling beta
#
#     Parameters
#     ----------
#     df : pd.DataFrame
#         The dataframe to be analyzed
#
#     Returns
#     ----------
#     img : ImageReader
#         Rolling beta graph
#     """
#
#     fig, ax = plt.subplots(figsize=(10, 5))
#     ax.plot(
#         df.index,
#         df["total"],
#         color="tab:blue",
#     )
#
#     ax.set_ylabel("", fontweight="bold", fontsize=12, color="black")
#     ax.set_xlabel("")
#     ax.yaxis.set_label_coords(-0.1, 0.5)
#     ax.grid(True)
#     ax.spines["top"].set_visible(False)
#     ax.spines["right"].set_visible(False)
#     ax.spines["bottom"].set_visible(False)
#     ax.spines["left"].set_visible(False)
#     fig.suptitle(
#         "Rolling Beta of Stocks", y=0.99, fontweight="bold", fontsize=14, color="black"
#     )
#     ax.axhline(0, ls="-", lw=1, color="gray", zorder=1)
#     ax.axhline(0, ls="--", lw=1, color="black", zorder=2)
#     fig.set_facecolor("white")
#     ax.set_title(
#         f'{df.index[:1][0].strftime("%Y-%m-%d")} - {df.index[-1:][0].strftime("%Y-%m-%d")}',
#         color="gray",
#     )
#     ax.set_facecolor("white")
#     fig.autofmt_xdate()
#     imgdata = BytesIO()
#     fig.savefig(imgdata, format="png")
#     plt.close("all")
#     imgdata.seek(0)
#     return ImageReader(imgdata)
#
#
# @log_start_end(log=logger)
# def plot_ef(
#     stocks: List[str],
#     variance: float,
#     per_ret: float,
#     rf_rate: float,
#     period: str = "3mo",
#     n_portfolios: int = 300,
#     risk_free: bool = False,
# ):
#     """Display efficient frontier
#
#     Parameters
#     ----------
#     stocks : List[str]
#         List of the stocks to be included in the weights
#     variance : float
#         The variance for the portfolio
#     per_ret : float
#         The portfolio's return for the portfolio
#     rf_rate : float
#         The risk free rate
#     period : str
#         The period to track
#     n_portfolios : int
#         The number of portfolios to generate
#     risk_free : bool
#         Include the risk-free asset
#     """
#     fig, ax = plt.subplots(figsize=(10, 5), dpi=PLOT_DPI)
#     ef, rets, stds = optimizer_model.generate_random_portfolios(
#         [x.upper() for x in stocks], period, n_portfolios
#     )
#     sharpes = rets / stds
#     ax.scatter(stds, rets, marker=".", c=sharpes, cmap="viridis_r")
#     plotting.plot_efficient_frontier(ef, ax=ax, show_assets=True)
#     # Find the tangency portfolio
#     ret_sharpe, std_sharpe, _ = ef.portfolio_performance(risk_free_rate=rf_rate)
#     ax.scatter(std_sharpe, ret_sharpe, marker="*", s=100, c="r", label="Max Sharpe")
#     plt.plot(variance, per_ret, "ro", label="Portfolio")
#     # Add risk free line
#     if risk_free:
#         y = ret_sharpe * 1.2
#         m = (ret_sharpe - rf_rate) / std_sharpe
#         x2 = (y - rf_rate) / m
#         x = [0, x2]
#         y = [rf_rate, y]
#         line = Line2D(x, y, color="#FF0000", label="Capital Allocation Line")
#         ax.set_xlim(xmin=min(stds) * 0.8)
#         ax.add_line(line)
#     ax.set_title(f"Efficient Frontier simulating {n_portfolios} portfolios")
#     ax.legend()
#     fig.tight_layout()
#     ax.grid(b=True, which="major", color="#666666", linestyle="-")
#
#     if obbff.USE_ION:
#         plt.ion()
#
#     imgdata = BytesIO()
#     fig.savefig(imgdata, format="png")
#     plt.close("all")
#     imgdata.seek(0)
#     return ImageReader(imgdata)


# @log_start_end(log=logger)
# def display_allocation2(data: pd.DataFrame, graph: bool):
#     """Displays allocation
#     Parameters
#     ----------
#     data: pd.DataFrame
#         The portfolio allocation dataframe
#     graph: bool
#         If pie chart shall be displayed with table"""
#
#     print_rich_table(data, headers=list(data.columns), title="Allocation")
#     console.print("")
#
#     if graph:
#         graph_data = data[data["pct_allocation"] >= 5].copy()
#         if not graph_data.empty:
#             graph_data.loc["Other"] = [
#                 "NA",
#                 data["value"].sum() - graph_data["value"].sum(),
#                 100 - graph_data["value"].sum(),
#             ]
#             labels = graph_data.index.values
#             sizes = graph_data["value"].to_list()
#         else:
#             labels = data.index.values
#             sizes = data["value"].to_list()
#         fig, ax = plt.subplots()
#         ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
#         ax.axis("equal")
#         ax.set_title("Portfolio Allocation")
#         fig.set_tight_layout(True)
#
#         plt.show()

#
# class Report:
#     @log_start_end(log=logger)
#     def __init__(self, df: pd.DataFrame, hist: pd.DataFrame, m_tick: str):
#         """Generate financial reports.
#         Financial reports allow users to show the how they have been performing in
#         trades. This allows for a simple way to show progress and analyze metrics
#         that track portfolio performance
#
#         Parameters
#         ----------
#         df : pd.DataFrame
#             The dataframe with previous holdings information
#         hist : pd.DataFrame
#             The dataframe with previous prices for stocks in the portfolio
#         df_m : pd.DataFrame
#             Dataframe of benchmark
#         n : int
#             The number of days to analyze
#
#         Attributes
#         ----------
#         generate_report : None
#             Generates a report with the given parameters
#         generate_pg1 : None
#             Creates the first page of the PDF report
#         generate_pg2 : None
#             Creates the second page of the PDF report
#
#         """
#         self.df = df
#         self.hist = hist
#         self.m_tick = m_tick
#         self.df_m = yfinance_model.get_market(self.df.index[0], self.m_tick)
#         # self.returns, self.variance = portfolio_model.get_return(df, self.df_m, n)
#         self.returns = pd.DataFrame()
#         self.rf = get_rf()
#         self.betas = portfolio_model.get_rolling_beta(
#             self.df, self.hist, self.df_m, 365
#         )
#
#     @log_start_end(log=logger)
#     def generate_report(self) -> None:
#         d = path.dirname(path.abspath(__file__)).replace(
#             "openbb_terminal", "exports"
#         )
#         loc = path.abspath(
#             path.join(
#                 d,
#                 f"ar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
#             )
#         )
#         report = canvas.Canvas(loc, pagesize=letter)
#         reportlab_helpers.base_format(report, "Overview")
#         self.generate_pg1(report)
#         self.generate_pg2(report)
#         report.save()
#         console.print("File save in:\n", loc, "\n")
#
#     @log_start_end(log=logger)
#     def generate_pg1(self, report: canvas.Canvas) -> None:
#         report.drawImage(
#             plot_overall_return(self.returns, self.m_tick, False), 15, 400, 600, 300
#         )
#         main_text = portfolio_model.get_main_text(self.returns)
#         reportlab_helpers.draw_paragraph(report, main_text, 30, 410, 550, 200)
#         current_return = self.returns["return"][-1]
#         beta = self.betas["total"][-1]
#         market_return = self.returns[("Market", "Return")][-1]
#         sharpe = f"{(current_return - self.rf)/ np.std(self.returns['return']):.2f}"
#         treynor = f"{(current_return - self.rf)/ beta:.2f}" if beta > 0 else "N/A"
#         alpha = f"{current_return - (self.rf + beta * (market_return - self.rf)):.2f}"
#         information = (
#             f"{float(alpha)/ (np.std(self.returns['return'] - market_return)):.2f}"
#         )
#         perf = [
#             ["Sharpe", sharpe],
#             ["Treynor", treynor],
#             ["Alpha", alpha],
#             ["Information", information],
#         ]
#         reportlab_helpers.draw_table(report, "Performance", 540, 300, 30, perf)
#         reportlab_helpers.draw_paragraph(
#             report, portfolio_model.performance_text, 140, 290, 460, 200
#         )
#         report.showPage()
#
#     @log_start_end(log=logger)
#     def generate_pg2(self, report: canvas.Canvas) -> None:
#         reportlab_helpers.base_format(report, "Portfolio Analysis")
#         if "Holding" in self.df.columns:
#             report.drawImage(plot_rolling_beta(self.betas), 15, 400, 600, 300)
#             main_t = portfolio_model.get_beta_text(self.betas)
#             reportlab_helpers.draw_paragraph(report, main_t, 30, 410, 550, 200)
#             # report.drawImage(plot_ef(uniques, self.variance, self.returns["return"][-1], self.rf), 15, 65, 600, 300)
