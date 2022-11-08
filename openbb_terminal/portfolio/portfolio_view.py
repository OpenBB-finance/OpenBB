"""Portfolio View"""
__docformat__ = "numpy"

import logging
from typing import List, Optional
import os

from datetime import datetime
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

from openbb_terminal.common.quantitative_analysis import qa_view
from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.portfolio import portfolio_model

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
def display_orderbook(
    portfolio=None,
    show_index=False,
    limit: int = 10,
    export: str = "",
):
    """Display portfolio orderbook

    Parameters
    ----------
    portfolio: Portfolio
        Instance of Portfolio class
    show_index: bool
        Defaults to False.
    limit: int
        Number of rows to display
    export : str
        Export certain type of data
    """

    if portfolio.empty:
        logger.warning("No orderbook loaded")
        console.print("[red]No orderbook loaded.[/red]\n")
    else:
        df = portfolio.get_orderbook()
        print_rich_table(
            df=df[:limit],
            show_index=show_index,
            title=f"Last {limit if limit < len(df) else len(df)} transactions",
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "transactions",
            df.set_index("Date"),
        )


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

    combined = pd.merge(
        portfolio_allocation, benchmark_allocation, on="Symbol", how="left"
    )
    combined["Difference"] = combined["Portfolio"] - combined["Benchmark"]
    combined = combined.replace(np.nan, "-")
    combined = combined.replace(0, "-")

    print_rich_table(
        combined,
        headers=list(combined.columns),
        title=f"Portfolio vs. Benchmark - Top {len(combined) if len(combined) < limit else limit} Assets Allocation",
        floatfmt=["", ".2%", ".2%", ".2%"],
        show_index=False,
    )

    if include_separate_tables:
        print_rich_table(
            portfolio_allocation,
            headers=list(portfolio_allocation.columns),
            title=f"Portfolio - Top {len(portfolio_allocation) if len(benchmark_allocation) < limit else limit} "
            f"Assets Allocation",
            floatfmt=[".2%", ".2%"],
            show_index=False,
        )
        print_rich_table(
            benchmark_allocation,
            headers=list(benchmark_allocation.columns),
            title=f"Benchmark - Top {len(benchmark_allocation) if len(benchmark_allocation) < limit else limit} "
            f"Assets Allocation",
            floatfmt=[".2%", ".2%"],
            show_index=False,
        )


@log_start_end(log=logger)
def display_category_allocation(
    portfolio_allocation: pd.DataFrame,
    benchmark_allocation: pd.DataFrame,
    category: str = "sectors",
    limit: int = 10,
    include_separate_tables: bool = False,
):
    """Display portfolio sector, country or region allocation compared to the benchmark

    Parameters
    ----------
    portfolio_allocation: pd.DataFrame
        The allocation to the set category of the portfolio
    benchmark_allocation: pd.DataFrame
        The allocation to the set category of the benchmark
    category: str
        Whether you want to show sectors, countries or regions
    limit: int
        The amount of assets you wish to show, by default this is set to 10.
    include_separate_tables: bool
        Whether to include separate asset allocation tables
    """

    if benchmark_allocation.empty:
        console.print(f"[red]Benchmark data for {category} is empty.\n[/red]")
        return

    if portfolio_allocation.empty:
        console.print(f"[red]Portfolio data for {category} is empty.\n[/red]")
        return

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
    portfolio: portfolio_model.PortfolioModel,
    show_all_trades: bool = False,
):
    """Display portfolio performance vs the benchmark

    Parameters
    ----------
    portfolio_trades: pd.DataFrame
        Object containing trades made within the portfolio.
    benchmark_trades: pd.DataFrame
        Object containing trades made within the benchmark.
    show_all_trades: bool
        Whether to also show all trades made and their performance (default is False)
    """

    df = portfolio_model.get_performance_vs_benchmark(portfolio, show_all_trades)

    if show_all_trades:
        print_rich_table(
            df,
            title="Portfolio vs. Benchmark - Individual Trades in period",
            headers=list(df.columns),
            show_index=False,
            floatfmt=[".2f", ".2f", ".2f", ".2%", ".2f", ".2%", ".2%"],
        )
    else:
        print_rich_table(
            df,
            title="Portfolio vs. Benchmark",
            headers=list(df.columns),
            show_index=True,
        )


@log_start_end(log=logger)
def display_yearly_returns(
    portfolio: portfolio_model.PortfolioModel,
    window: str = "all",
    raw: bool = False,
    export: str = "",
    external_axes: Optional[plt.Axes] = None,
):
    """Display yearly returns

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    window : str
        interval to compare cumulative returns and benchmark
    raw : False
        Display raw data from cumulative return
    export : str
        Export certain type of data
    external_axes: plt.Axes
        Optional axes to display plot on
    """

    df = portfolio_model.get_yearly_returns(portfolio, window)

    if raw:
        print_rich_table(
            df,
            title="Yearly Portfolio and Benchmark returns",
            headers=["Portfolio [%]", "Benchmark [%]", "Difference [%]"],
            show_index=True,
        )

    else:
        if external_axes is None:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        else:
            if len(external_axes) != 1:
                logger.error("Expected list of 1 axis items")
                console.print("[red]Expected list of 1 axis items.\n[/red]")
                return
            ax = external_axes[0]

        creturns_year_idx = list()
        breturns_year_idx = list()

        for year in df.index.values:
            creturns_year_idx.append(datetime.strptime(f"{year}-04-15", "%Y-%m-%d"))
            breturns_year_idx.append(datetime.strptime(f"{year}-08-15", "%Y-%m-%d"))

        ax.bar(
            creturns_year_idx,
            df["Portfolio"],
            width=100,
            label="Portfolio",
        )
        ax.bar(
            breturns_year_idx,
            df["Benchmark"],
            width=100,
            label="Benchmark",
        )

        ax.legend(loc="upper left")
        ax.set_ylabel("Yearly Returns [%]")
        ax.set_title(f"Yearly Returns [%] in period {window}")
        theme.style_primary_axis(ax)

        if not external_axes:
            theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "yret",
        df,
    )


@log_start_end(log=logger)
def display_monthly_returns(
    portfolio: portfolio_model.PortfolioModel,
    window: str = "all",
    raw: bool = False,
    show_vals: bool = False,
    export: str = "",
    external_axes: Optional[plt.Axes] = None,
):
    """Display monthly returns

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    window : str
        interval to compare cumulative returns and benchmark
    raw : False
        Display raw data from cumulative return
    show_vals : False
        Show values on heatmap
    export : str
        Export certain type of data
    external_axes: plt.Axes
        Optional axes to display plot on
    """

    portfolio_returns, benchmark_returns = portfolio_model.get_monthly_returns(
        portfolio, window
    )

    if raw:
        print_rich_table(
            portfolio_returns,
            title="Monthly returns",
            headers=portfolio_returns.columns,
            show_index=True,
        )
        print_rich_table(
            benchmark_returns,
            title="Monthly returns",
            headers=benchmark_returns.columns,
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
            if len(external_axes) != 2:
                logger.error("Expected list of 2 axis items")
                console.print("[red]Expected list of 2 axis items.\n[/red]")
                return
            ax = external_axes

        ax[0].set_title(f"Portfolio in period {window}")
        sns.heatmap(
            portfolio_returns,
            cmap="bwr_r",
            vmax=max(portfolio_returns.max().max(), benchmark_returns.max().max()),
            vmin=min(portfolio_returns.min().min(), benchmark_returns.min().min()),
            center=0,
            annot=show_vals,
            fmt=".1f",
            mask=portfolio_returns.applymap(lambda x: x == 0),
            ax=ax[0],
        )
        theme.style_primary_axis(ax[0])

        ax[1].set_title(f"Benchmark in period {window}")
        sns.heatmap(
            portfolio_returns,
            cmap="bwr_r",
            vmax=max(portfolio_returns.max().max(), benchmark_returns.max().max()),
            vmin=min(portfolio_returns.min().min(), benchmark_returns.min().min()),
            center=0,
            annot=show_vals,
            fmt=".1f",
            mask=benchmark_returns.applymap(lambda x: x == 0),
            ax=ax[1],
        )
        theme.style_primary_axis(ax[1])

        if external_axes is None:
            theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "mret",
        portfolio_returns,
    )


@log_start_end(log=logger)
def display_daily_returns(
    portfolio: portfolio_model.PortfolioModel,
    window: str = "all",
    raw: bool = False,
    limit: int = 10,
    export: str = "",
    external_axes: Optional[plt.Axes] = None,
):
    """Display daily returns

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    window : str
        interval to compare cumulative returns and benchmark
    raw : False
        Display raw data from cumulative return
    limit : int
        Last daily returns to display
    export : str
        Export certain type of data
    external_axes: plt.Axes
        Optional axes to display plot on
    """

    df = portfolio_model.get_daily_returns(portfolio, window)

    if raw:
        print_rich_table(
            df.tail(limit),
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
            if len(external_axes) != 2:
                logger.error("Expected list of 2 axis items")
                console.print("[red]Expected list of 2 axis items.\n[/red]")
                return
            ax = external_axes

        ax[0].set_title(f"Portfolio in period {window}")
        ax[0].plot(df.index, df["portfolio"], label="Portfolio")
        ax[0].set_ylabel("Returns [%]")
        theme.style_primary_axis(ax[0])
        ax[1].set_title(f"Benchmark in period {window}")
        ax[1].plot(df.index, df["benchmark"], label="Benchmark")
        ax[1].set_ylabel("Returns [%]")
        theme.style_primary_axis(ax[1])

        if external_axes is None:
            theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dret",
        df,
    )


@log_start_end(log=logger)
def display_distribution_returns(
    portfolio: portfolio_model.PortfolioModel,
    window: str = "all",
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
    interval : str
        interval to compare cumulative returns and benchmark
    raw : False
        Display raw data from cumulative return
    export : str
        Export certain type of data
    external_axes: plt.Axes
        Optional axes to display plot on
    """

    df = portfolio_model.get_distribution_returns(portfolio, window)
    df_portfolio = df["portfolio"]
    df_benchmark = df["benchmark"]

    stats = df.describe()

    if raw:
        print_rich_table(
            stats,
            title=f"Stats for Portfolio and Benchmark in period {window}",
            show_index=True,
            headers=["Portfolio", "Benchmark"],
        )

    else:
        if external_axes is None:
            _, ax = plt.subplots(
                figsize=plot_autoscale(),
                dpi=PLOT_DPI,
            )
        else:
            if len(external_axes) != 1:
                logger.error("Expected list of 1 axis items")
                console.print("[red]Expected list of 1 axis items.\n[/red]")
                return
            ax = external_axes[0]

        ax.set_title("Returns distribution")
        ax.set_ylabel("Density")
        ax.set_xlabel("Daily return [%]")

        ax = sns.kdeplot(df_portfolio.values, label="portfolio")
        kdeline = ax.lines[0]
        mean = df_portfolio.values.mean()
        xs = kdeline.get_xdata()
        ys = kdeline.get_ydata()
        height = np.interp(mean, xs, ys)
        ax.vlines(mean, 0, height, color="yellow", ls=":")

        ax = sns.kdeplot(df_benchmark.values, label="benchmark")
        kdeline = ax.lines[1]
        mean = df_benchmark.values.mean()
        xs = kdeline.get_xdata()
        ys = kdeline.get_ydata()
        height = np.interp(mean, xs, ys)
        ax.vlines(mean, 0, height, color="orange", ls=":")

        theme.style_primary_axis(ax)
        ax.legend()

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

    all_holdings = portfolio_model.get_holdings_value(portfolio)

    if raw:
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
            if len(external_axes) != 1:
                logger.error("Expected list of 1 axis items")
                console.print("[red]Expected list of 1 axis items.\n[/red]")
                return
            ax = external_axes[0]

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

    all_holdings = portfolio_model.get_holdings_percentage(portfolio)

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
            if len(external_axes) != 1:
                logger.error("Expected list of 1 axis items")
                console.print("[red]Expected list of 1 axis items.\n[/red]")
                return
            ax = external_axes[0]

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
    portfolio: portfolio_model.PortfolioModel,
    window: str = "1y",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display rolling volatility

    Parameters
    ----------
    portfolio : PortfolioModel
        Portfolio object
    interval: str
        interval for window to consider
    export: str
        Export to file
    external_axes: Optional[List[plt.Axes]]
        Optional axes to display plot on
    """

    metric = "volatility"
    df = portfolio_model.get_rolling_volatility(portfolio, window)
    if df.empty:
        return

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis items.")
            console.print("[red]1 axes expected.\n[/red]")
            return
        ax = external_axes[0]

    df_portfolio = df["portfolio"]
    df_benchmark = df["benchmark"]

    df_portfolio.plot(ax=ax)
    df_benchmark.plot(ax=ax)
    ax.set_title(f"Rolling {metric.title()} using {window} window")
    ax.set_xlabel("Date")
    ax.legend(["Portfolio", "Benchmark"], loc="upper left")
    ax.set_xlim(df_portfolio.index[0], df_portfolio.index[-1])

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        metric,
        df_portfolio.to_frame().join(df_benchmark),
    )


@log_start_end(log=logger)
def display_rolling_sharpe(
    portfolio: portfolio_model.PortfolioModel,
    risk_free_rate: float = 0,
    window: str = "1y",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display rolling sharpe

    Parameters
    ----------
    portfolio : PortfolioModel
        Portfolio object
    risk_free_rate: float
        Value to use for risk free rate in sharpe/other calculations
    window: str
        interval for window to consider
    export: str
        Export to file
    external_axes: Optional[List[plt.Axes]]
        Optional axes to display plot on
    """

    metric = "sharpe"
    df = portfolio_model.get_rolling_sharpe(portfolio, risk_free_rate, window)
    if df.empty:
        return

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis items.")
            console.print("[red]1 axes expected.\n[/red]")
            return
        ax = external_axes[0]

    df_portfolio = df["portfolio"]
    df_benchmark = df["benchmark"]

    df_portfolio.plot(ax=ax)
    df_benchmark.plot(ax=ax)
    ax.set_title(f"Rolling {metric.title()} using {window} window")
    ax.set_xlabel("Date")
    ax.legend(["Portfolio", "Benchmark"], loc="upper left")
    ax.set_xlim(df_portfolio.index[0], df_portfolio.index[-1])

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        metric,
        df_portfolio.to_frame().join(df_benchmark),
    )


@log_start_end(log=logger)
def display_rolling_sortino(
    portfolio: portfolio_model.PortfolioModel,
    risk_free_rate: float = 0,
    window: str = "1y",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display rolling sortino

    Parameters
    ----------
    portfolio : PortfolioModel
        Portfolio object
    risk_free_rate: float
        Value to use for risk free rate in sharpe/other calculations
    window: str
        interval for window to consider
    export: str
        Export to file
    external_axes: Optional[List[plt.Axes]]
        Optional axes to display plot on
    """

    metric = "sortino"
    df = portfolio_model.get_rolling_sortino(portfolio, risk_free_rate, window)
    if df.empty:
        return

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis items.")
            console.print("[red]1 axes expected.\n[/red]")
            return
        ax = external_axes[0]

    df_portfolio = df["portfolio"]
    df_benchmark = df["benchmark"]

    df_portfolio.plot(ax=ax)
    df_benchmark.plot(ax=ax)
    ax.set_title(f"Rolling {metric.title()} using {window} window")
    ax.set_xlabel("Date")
    ax.legend(["Portfolio", "Benchmark"], loc="upper left")
    ax.set_xlim(df_portfolio.index[0], df_portfolio.index[-1])

    if external_axes is None:
        theme.visualize_output()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        metric,
        df_portfolio.to_frame().join(df_benchmark),
    )


@log_start_end(log=logger)
def display_rolling_beta(
    portfolio: portfolio_model.PortfolioModel,
    window: str = "1y",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display rolling beta

    Parameters
    ----------
    portfolio : PortfolioModel
        Portfolio object
    window: str
        interval for window to consider
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y.
    export: str
        Export to file
    external_axes: Optional[List[plt.Axes]]
        Optional axes to display plot on
    """

    rolling_beta = portfolio_model.get_rolling_beta(portfolio, window)
    if rolling_beta.empty:
        return

    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis items.")
            console.print("[red]1 axes expected.\n[/red]")
            return
        ax = external_axes[0]

    metric = "beta"
    rolling_beta.plot(ax=ax)

    ax.set_title(f"Rolling {metric.title()} using {window} window")
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
        metric,
        rolling_beta,
    )


@log_start_end(log=logger)
def display_maximum_drawdown(
    portfolio: portfolio_model.PortfolioModel,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display maximum drawdown curve

    Parameters
    ----------
    portfolio : PortfolioModel
        Portfolio object
    export: str
        Format to export data
    external_axes: plt.Axes
        Optional axes to display plot on
    """
    holdings, drawdown = portfolio_model.get_maximum_drawdown(portfolio)
    if external_axes is None:
        _, ax = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI, sharex=True)
    else:
        if len(external_axes) != 2:
            logger.error("Expected list of 2 axis items")
            console.print("[red]Expected list of 2 axis items.\n[/red]")
            return
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
        drawdown,
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

    df = portfolio_model.get_r2_score(portfolio).fillna("-")

    print_rich_table(
        df,
        title="R-Square Score between Portfolio and Benchmark",
        headers=["R-Square Score"],
        show_index=True,
        floatfmt=".2%",
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "rsquare",
        df,
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

    df = portfolio_model.get_skewness(portfolio).fillna("-")

    print_rich_table(
        df,
        title="Skewness for Portfolio and Benchmark",
        show_index=True,
        floatfmt=".2%",
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

    df = portfolio_model.get_kurtosis(portfolio).fillna("-")

    print_rich_table(
        df,
        title="Kurtosis for Portfolio and Benchmark",
        show_index=True,
        floatfmt=".2%",
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "kurt",
    )


@log_start_end(log=logger)
def display_stats(
    portfolio: portfolio_model.PortfolioModel,
    window: str = "all",
    export: str = "",
):
    """Display stats

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    window : str
        interval to consider. Choices are: mtd, qtd, ytd, 3m, 6m, 1y, 3y, 5y, 10y, all
    export : str
        Export data format
    """

    df = portfolio_model.get_stats(portfolio, window)

    print_rich_table(
        df,
        title=f"Stats for Portfolio and Benchmark in period {window}",
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
    """Display volatility for multiple intervals

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    export : str
        Export data format
    """
    df = portfolio_model.get_volatility(portfolio).fillna("-")
    print_rich_table(
        df,
        title="Volatility for Portfolio and Benchmark",
        show_index=True,
        floatfmt=".2%",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_volatility", df
    )


@log_start_end(log=logger)
def display_sharpe_ratio(
    portfolio: portfolio_model.PortfolioModel,
    risk_free_rate: float = 0,
    export: str = "",
):
    """Display sharpe ratio for multiple intervals

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    risk_free_rate: float
        Risk free rate value
    export : str
        Export data format
    """
    df = portfolio_model.get_sharpe_ratio(portfolio, risk_free_rate).fillna("-")
    print_rich_table(
        df,
        title="Sharpe ratio for Portfolio and Benchmark",
        show_index=True,
        floatfmt=".2%",
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
    risk_free_rate: float = 0,
    export: str = "",
):
    """Display sortino ratio for multiple intervals

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    risk_free_rate: float
        Risk free rate value
    export : str
        Export data format
    """
    df = portfolio_model.get_sortino_ratio(portfolio, risk_free_rate).fillna("-")
    print_rich_table(
        df,
        title="Sortino ratio for Portfolio and Benchmark",
        show_index=True,
        floatfmt=".2%",
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
    """Display maximum drawdown for multiple intervals

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    export : str
        Export data format
    """
    df = portfolio_model.get_maximum_drawdown_ratio(portfolio).fillna("-")
    print_rich_table(
        df,
        title="Maximum drawdown for Portfolio and Benchmark",
        show_index=True,
        floatfmt=".2%",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_maxdrawdown", df
    )


@log_start_end(log=logger)
def display_gaintopain_ratio(
    portfolio: portfolio_model.PortfolioModel,
    export: str = "",
):
    """Display gain-to-pain ratio for multiple intervals

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with returns and benchmark loaded
    export : str
        Export data format
    """
    df = portfolio_model.get_gaintopain_ratio(portfolio).fillna("-")
    print_rich_table(
        df,
        title="Gain-to-pain ratio for portfolio and benchmark",
        show_index=True,
        floatfmt=".2%",
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
    """Display tracking error for multiple intervals

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with returns and benchmark loaded
    export : str
        Export data format
    """
    df, _ = portfolio_model.get_tracking_error(portfolio)
    df = df.fillna("-")
    print_rich_table(
        df,
        title="Benchmark Tracking Error",
        show_index=True,
        floatfmt=".2%",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_tracking_error", df
    )


@log_start_end(log=logger)
def display_information_ratio(
    portfolio: portfolio_model.PortfolioModel,
    export: str = "",
):
    """Display information ratio for multiple intervals

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with returns and benchmark loaded
    export : str
        Export data format
    """
    df = portfolio_model.get_information_ratio(portfolio).fillna("-")
    print_rich_table(
        df,
        title="Information ratio for portfolio",
        show_index=True,
        floatfmt=".2%",
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
    """Display tail ratio for multiple intervals

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with returns and benchmark loaded
    window: str
        interval for window to consider
    export : str
        Export data format
    """
    df, _, _ = portfolio_model.get_tail_ratio(portfolio)
    df = df.fillna("-")
    print_rich_table(
        df,
        title="Tail ratio for portfolio and benchmark",
        show_index=True,
        floatfmt=".2%",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_tail_ratio", df
    )


@log_start_end(log=logger)
def display_common_sense_ratio(
    portfolio: portfolio_model.PortfolioModel,
    export: str = "",
):
    """Display common sense ratio for multiple intervals

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with returns and benchmark loaded
    export : str
        Export data format
    """
    df = portfolio_model.get_common_sense_ratio(portfolio).fillna("-")
    print_rich_table(
        df,
        title="Common sense ratio for portfolio and benchmark",
        show_index=True,
        floatfmt=".2%",
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
    risk_free_rate: float = 0,
    export: str = "",
):
    """Display jensens alpha for multiple intervals

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with returns and benchmark loaded
    risk_free_rate: float
            Risk free rate
    export : str
        Export data format
    """
    df, _ = portfolio_model.get_jensens_alpha(portfolio, risk_free_rate)
    df = df.fillna("-")
    print_rich_table(
        df,
        title="Portfolio's jensen's alpha",
        show_index=True,
        floatfmt=".2%",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_jensens_alpha", df
    )


@log_start_end(log=logger)
def display_calmar_ratio(
    portfolio: portfolio_model.PortfolioModel,
    export: str = "",
):
    """Display calmar ratio for multiple intervals

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with returns and benchmark loaded
    export : str
        Export data format
    """
    df, _ = portfolio_model.get_calmar_ratio(portfolio)
    df = df.fillna("-")
    print_rich_table(
        df,
        title="Calmar ratio for portfolio and benchmark",
        show_index=True,
        floatfmt=".2%",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_calmar_ratio", df
    )


@log_start_end(log=logger)
def display_kelly_criterion(
    portfolio: portfolio_model.PortfolioModel,
    export: str = "",
):
    """Display kelly criterion for multiple intervals

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades and returns loaded
    export : str
        Export data format
    """
    df = portfolio_model.get_kelly_criterion(portfolio).fillna("-")
    print_rich_table(
        df,
        title="Kelly criterion of the portfolio",
        show_index=True,
        floatfmt=".2%",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_kelly_criterion", df
    )


def display_payoff_ratio(
    portfolio: portfolio_model.PortfolioModel,
    export: str = "",
):
    """Display payoff ratio for multiple intervals

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    export : str
        Export data format
    """
    df = portfolio_model.get_payoff_ratio(portfolio).fillna("-")
    print_rich_table(
        df,
        title="Portfolio's payoff ratio",
        show_index=True,
        floatfmt=".2%",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_payoff_ratio", df
    )


def display_profit_factor(
    portfolio: portfolio_model.PortfolioModel,
    export: str = "",
):
    """Display profit factor for multiple intervals

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    export : str
        Export data format
    """
    df = portfolio_model.get_profit_factor(portfolio).fillna("-")
    print_rich_table(
        df,
        title="Portfolio's profit factor",
        show_index=True,
        floatfmt=".2%",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_profit_factor", df
    )


@log_start_end(log=logger)
def display_summary(
    portfolio: portfolio_model.PortfolioModel,
    window: str = "all",
    risk_free_rate: float = 0,
    export: str = "",
):
    """Display summary portfolio and benchmark returns

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    window : str
        interval to compare cumulative returns and benchmark
    risk_free_rate : float
        Risk free rate for calculations
    export : str
        Export certain type of data
    """
    summary = portfolio_model.get_summary(portfolio, window, risk_free_rate)

    print_rich_table(
        summary,
        title=f"Summary of Portfolio vs Benchmark for {window} period",
        show_index=True,
        headers=summary.columns,
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "summary",
        summary,
    )


@log_start_end(log=logger)
def display_var(
    portfolio: portfolio_model.PortfolioModel,
    use_mean: bool = False,
    adjusted_var: bool = False,
    student_t: bool = False,
    percentile: float = 99.9,
):
    """Display portfolio VaR

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    use_mean: bool
        if one should use the data mean return
    adjusted_var: bool
        if one should have VaR adjusted for skew and kurtosis (Cornish-Fisher-Expansion)
    student_t: bool
        If one should use the student-t distribution
    percentile: float
        var percentile (%)
    """
    qa_view.display_var(
        data=portfolio.returns,
        symbol="Portfolio",
        use_mean=use_mean,
        adjusted_var=adjusted_var,
        student_t=student_t,
        percentile=percentile,
        portfolio=True,
    )


@log_start_end(log=logger)
def display_es(
    portfolio: portfolio_model.PortfolioModel,
    use_mean: bool = False,
    distribution: str = "normal",
    percentile: float = 99.9,
):
    """Displays expected shortfall

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    use_mean:
        if one should use the data mean return
    distribution: str
        choose distribution to use: logistic, laplace, normal
    percentile: float
        es percentile (%)
    """

    qa_view.display_es(
        data=portfolio.returns,
        symbol="Portfolio",
        use_mean=use_mean,
        distribution=distribution,
        percentile=percentile,
        portfolio=True,
    )


@log_start_end(log=logger)
def display_omega(
    portfolio: portfolio_model.PortfolioModel,
    threshold_start: float = 0,
    threshold_end: float = 1.5,
):
    """Display omega ratio

    Parameters
    ----------
    portfolio: Portfolio
        Portfolio object with trades loaded
    threshold_start: float
        annualized target return threshold start of plotted threshold range
    threshold_end: float
        annualized target return threshold end of plotted threshold range
    """

    qa_view.display_omega(
        data=portfolio.returns,
        threshold_start=threshold_start,
        threshold_end=threshold_end,
    )
