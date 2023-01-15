"""Portfolio View"""
__docformat__ = "numpy"

import logging
import os
from datetime import datetime
from typing import List, Optional

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from openbb_terminal.common.quantitative_analysis import qa_view
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.config_terminal import theme
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, plot_autoscale, print_rich_table
from openbb_terminal.plots_core.plotly_helper import OpenBBFigure
from openbb_terminal.portfolio.portfolio_model import (
    PortfolioEngine,
    get_assets_allocation,
    get_calmar_ratio,
    get_common_sense_ratio,
    get_countries_allocation,
    get_daily_returns,
    get_distribution_returns,
    get_gaintopain_ratio,
    get_holdings_percentage,
    get_holdings_value,
    get_information_ratio,
    get_jensens_alpha,
    get_kelly_criterion,
    get_kurtosis,
    get_maximum_drawdown,
    get_maximum_drawdown_ratio,
    get_monthly_returns,
    get_payoff_ratio,
    get_performance_vs_benchmark,
    get_profit_factor,
    get_r2_score,
    get_regions_allocation,
    get_rolling_beta,
    get_rolling_sharpe,
    get_rolling_sortino,
    get_rolling_volatility,
    get_sectors_allocation,
    get_sharpe_ratio,
    get_skewness,
    get_sortino_ratio,
    get_stats,
    get_summary,
    get_tail_ratio,
    get_tracking_error,
    get_transactions,
    get_volatility,
    get_yearly_returns,
)
from openbb_terminal.rich_config import console

# pylint: disable=C0302,redefined-outer-name

# from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
# from reportlab.lib.utils import ImageReader
# from openbb_terminal.portfolio import reportlab_helpers

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def load_info():
    """Print instructions to load a CSV

    Returns
    -------
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
def display_transactions(
    portfolio_engine: PortfolioEngine,
    show_index=False,
    limit: int = 10,
    export: str = "",
):
    """Display portfolio transactions

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        Instance of PortfolioEngine class
    show_index: bool
        Defaults to False.
    limit: int
        Number of rows to display
    export : str
        Export certain type of data
    """

    if portfolio_engine.empty:
        logger.warning("No transactions file loaded.")
        console.print("[red]No transactions file loaded.[/red]\n")

    else:
        df = get_transactions(portfolio_engine)
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
    portfolio_engine: PortfolioEngine,
    limit: int = 10,
    tables: bool = False,
):
    """Display portfolio asset allocation compared to the benchmark

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        Instance of PortfolioEngine class
    tables: bool
        Whether to include separate asset allocation tables
    limit: int
        The amount of assets you wish to show, by default this is set to 10
    """

    combined, portfolio_allocation, benchmark_allocation = get_assets_allocation(
        portfolio_engine=portfolio_engine,
        limit=limit,
        tables=True,
    )

    display_category(
        category="assets",
        df0=combined,
        df1=portfolio_allocation,
        df2=benchmark_allocation,
        tables=tables,
        limit=limit,
    )


@log_start_end(log=logger)
def display_sectors_allocation(
    portfolio_engine: PortfolioEngine,
    limit: int = 10,
    tables: bool = False,
):
    """Display portfolio sector allocation compared to the benchmark

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        Instance of PortfolioEngine class
    limit: int
        The amount of assets you wish to show, by default this is set to 10
    tables: bool
        Whether to include separate asset allocation tables
    """

    combined, portfolio_allocation, benchmark_allocation = get_sectors_allocation(
        portfolio_engine=portfolio_engine,
        limit=limit,
        tables=True,
    )

    display_category(
        category="sectors",
        df0=combined,
        df1=portfolio_allocation,
        df2=benchmark_allocation,
        tables=tables,
        limit=limit,
    )


@log_start_end(log=logger)
def display_countries_allocation(
    portfolio_engine: PortfolioEngine,
    limit: int = 10,
    tables: bool = False,
):
    """Display portfolio country allocation compared to the benchmark

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        Instance of PortfolioEngine class
    limit: int
        The amount of assets you wish to show, by default this is set to 10
    tables: bool
        Whether to include separate asset allocation tables
    """

    combined, portfolio_allocation, benchmark_allocation = get_countries_allocation(
        portfolio_engine=portfolio_engine,
        limit=limit,
        tables=True,
    )

    display_category(
        category="countries",
        df0=combined,
        df1=portfolio_allocation,
        df2=benchmark_allocation,
        tables=tables,
        limit=limit,
    )


@log_start_end(log=logger)
def display_regions_allocation(
    portfolio_engine: PortfolioEngine,
    limit: int = 10,
    tables: bool = False,
):
    """Display portfolio region allocation compared to the benchmark

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        Instance of PortfolioEngine class
    limit: int
        The amount of assets you wish to show, by default this is set to 10
    tables: bool
        Whether to include separate asset allocation tables
    """

    combined, portfolio_allocation, benchmark_allocation = get_regions_allocation(
        portfolio_engine=portfolio_engine,
        limit=limit,
        tables=True,
    )

    display_category(
        category="regions",
        df0=combined,
        df1=portfolio_allocation,
        df2=benchmark_allocation,
        tables=tables,
        limit=limit,
    )


def display_category(**kwargs):
    """Display category tables

    Parameters
    ----------
    **kwargs
    """

    category = kwargs["category"]
    combined = kwargs["df0"]
    portfolio_allocation = kwargs["df1"]
    benchmark_allocation = kwargs["df2"]
    tables = kwargs["tables"]
    limit = kwargs["limit"]

    if benchmark_allocation.empty:
        console.print(f"[red]Benchmark data for {category} is empty.[/red]")
        return

    if portfolio_allocation.empty:
        console.print(f"[red]Portfolio data for {category} is empty.[/red]")
        return

    if tables:
        print_rich_table(
            combined.replace(0, "-"),
            headers=list(combined.columns),
            title=f"Portfolio vs. Benchmark - Top {len(combined) if len(combined) < limit else limit} "
            f"{category.capitalize()} Allocation",
            floatfmt=[".2f", ".2%", ".2%", ".2%"],
            show_index=False,
        )
        console.print("")
        print_rich_table(
            pd.DataFrame(portfolio_allocation),
            headers=["Symbol", "Allocation"],
            title=f"Portfolio - Top {len(portfolio_allocation) if len(portfolio_allocation) < limit else limit} "
            f"{category.capitalize()} Allocation",
            floatfmt=["", ".2%"],
            show_index=False,
        )
        console.print("")
        print_rich_table(
            pd.DataFrame(benchmark_allocation),
            headers=["Symbol", "Allocation"],
            title=f"Benchmark - Top {len(benchmark_allocation) if len(benchmark_allocation) < limit else limit} "
            f"{category.capitalize()} Allocation",
            floatfmt=["", ".2%"],
            show_index=False,
        )
    else:
        print_rich_table(
            combined.replace(0, "-"),
            headers=list(combined.columns),
            title=f"Portfolio vs. Benchmark - Top {len(combined) if len(combined) < limit else limit} "
            f"{category.capitalize()} Allocation",
            floatfmt=[".2f", ".2%", ".2%", ".2%"],
            show_index=False,
        )


@log_start_end(log=logger)
def display_performance_vs_benchmark(
    portfolio_engine: PortfolioEngine,
    show_all_trades: bool = False,
):
    """Display portfolio performance vs the benchmark

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    show_all_trades: bool
        Whether to also show all trades made and their performance (default is False)
    """

    df = get_performance_vs_benchmark(portfolio_engine, show_all_trades)

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
    portfolio_engine: PortfolioEngine,
    window: str = "all",
    raw: bool = False,
    export: str = "",
    external_axes: bool = False,
):
    """Display yearly returns

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window : str
        interval to compare cumulative returns and benchmark
    raw : False
        Display raw data from cumulative return
    export : str
        Export certain type of data
    external_axes: plt.Axes
        Optional axes to display plot on
    """

    df = get_yearly_returns(portfolio_engine, window)

    if raw:
        print_rich_table(
            df,
            title="Yearly Portfolio and Benchmark returns",
            headers=["Portfolio [%]", "Benchmark [%]", "Difference [%]"],
            show_index=True,
        )

    else:

        fig = OpenBBFigure()

        creturns_year_idx = list()
        breturns_year_idx = list()

        for year in df.index.values:
            creturns_year_idx.append(datetime.strptime(f"{year}-04-15", "%Y-%m-%d"))
            breturns_year_idx.append(datetime.strptime(f"{year}-08-15", "%Y-%m-%d"))

        fig.add_bar(
            x=creturns_year_idx,
            y=df["Portfolio"],
            name="Portfolio",
        )
        fig.add_bar(
            x=breturns_year_idx,
            y=df["Benchmark"],
            name="Benchmark",
        )

        fig.update_layout(
            title=f"Yearly Returns [%] in period {window}",
            xaxis=dict(title="Year", type="date"),
            yaxis=dict(title="Yearly Returns [%]"),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "yret",
        df,
    )

    return fig.show() if not external_axes else fig


@log_start_end(log=logger)
def display_monthly_returns(
    portfolio_engine: PortfolioEngine,
    window: str = "all",
    raw: bool = False,
    show_vals: bool = False,
    export: str = "",
    external_axes: Optional[plt.Axes] = None,
):
    """Display monthly returns

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
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

    portfolio_returns, benchmark_returns = get_monthly_returns(portfolio_engine, window)

    if raw:
        print_rich_table(
            portfolio_returns,
            title="Monthly returns - portfolio [%]",
            headers=portfolio_returns.columns,
            show_index=True,
        )
        console.print("\n")

        print_rich_table(
            benchmark_returns,
            title="Monthly returns - benchmark [%]",
            headers=benchmark_returns.columns,
            show_index=True,
        )

    else:
        fig = OpenBBFigure.create_subplots(
            rows=2,
            cols=1,
            subplot_titles=("Portfolio", "Benchmark"),
            specs=[[{"type": "heatmap"}], [{"type": "heatmap"}]],
            vertical_spacing=0.15,
            shared_xaxes=False,
            row_width=[0.8, 0.8],
        )
        texttemplate = "%{z:.2f}%" if show_vals else ""
        hovertemplate = "%{x} %{y:.0f}:<br>%{z:.2f}%<extra></extra>"

        try:
            zero = 0 - float(
                min(portfolio_returns.min().min(), benchmark_returns.min().min())
            ) / (
                float(max(portfolio_returns.max().max(), benchmark_returns.max().max()))
                - float(
                    min(portfolio_returns.min().min(), benchmark_returns.min().min())
                )
            )
        except ZeroDivisionError:
            zero = (
                2
                if float(
                    max(portfolio_returns.max().max(), benchmark_returns.max().max())
                )
                < 0
                else -2
            )

        increasing_color = [
            "rgba(0, 150, 255, 1)",
            "rgba(0, 170, 255, 0.92)",
            "rgba(0, 170, 255, 0.90)",
            "rgba(0, 170, 255, 0.80)",
            "rgba(0, 170, 255, 0.70)",
            "rgba(0, 170, 255, 0.60)",
            "rgba(0, 170, 255, 0.50)",
            "rgba(0, 170, 255, 0.40)",
            "rgba(0, 170, 255, 0.34)",
            "rgba(0, 170, 255, 0.22)",
            "rgba(0, 170, 255, 0.10)",
            "rgba(0, 170, 255, 0.05)",
        ]

        decreasing_color = [
            "rgba(230, 0, 57, 1)",
            "rgba(230, 0, 57, 0.92)",
            "rgba(230, 0, 57, 0.90)",
            "rgba(230, 0, 57, 0.80)",
            "rgba(230, 0, 57, 0.70)",
            "rgba(230, 0, 57, 0.60)",
            "rgba(230, 0, 57, 0.50)",
            "rgba(230, 0, 57, 0.40)",
            "rgba(230, 0, 57, 0.34)",
            "rgba(230, 0, 57, 0.22)",
            "rgba(230, 0, 57, 0.10)",
            "rgba(230, 0, 57, 0.05)",
        ]
        colorscale = [
            [0.0, decreasing_color[3]],
            [zero, decreasing_color[-3]],
            [zero + 0.01, increasing_color[-2]],
            [1.0, increasing_color[0]],
        ]

        if zero < 0:
            colorscale = [
                [0.0, increasing_color[-1]],
                [1.0, increasing_color[4]],
            ]
        elif zero > 1:
            zero = [
                [0.0, decreasing_color[4]],
                [1.0, decreasing_color[6]],
            ]

        row = 1
        for df, name in zip(
            [portfolio_returns, benchmark_returns], ["Portfolio", "Benchmark"]
        ):
            fig.add_heatmap(
                z=df,
                x=df.columns,
                y=df.index,
                zmin=min(portfolio_returns.min().min(), benchmark_returns.min().min()),
                zmax=max(portfolio_returns.max().max(), benchmark_returns.max().max()),
                zmid=zero,
                name=name,
                texttemplate=texttemplate,
                hovertemplate=hovertemplate,
                textfont=dict(color="white"),
                text=df,
                colorscale=colorscale,
                colorbar=dict(
                    thickness=10,
                    thicknessmode="pixels",
                    x=1.1,
                    y=1,
                    xanchor="right",
                    yanchor="top",
                    xpad=10,
                ),
                row=row,
                col=1,
            )
            row += 1

        fig.update_layout(
            margin=dict(l=0, r=60, t=0, b=0),
            title=f"Monthly Returns [%] in period {window}",
            xaxis=dict(title="Month"),
            yaxis=dict(title="Year", autorange="reversed"),
            xaxis2=dict(title="Month"),
            yaxis2=dict(title="Year", autorange="reversed"),
            font=dict(size=12),
            showlegend=False,
        )

        fig.show()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "mret",
        portfolio_returns,
    )


@log_start_end(log=logger)
def display_daily_returns(
    portfolio_engine: PortfolioEngine,
    window: str = "all",
    raw: bool = False,
    limit: int = 10,
    export: str = "",
    external_axes: Optional[plt.Axes] = None,
):
    """Display daily returns

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
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

    df = get_daily_returns(portfolio_engine, window)

    if raw:
        print_rich_table(
            df.tail(limit),
            title="Portfolio and Benchmark daily returns",
            headers=["Portfolio [%]", "Benchmark [%]"],
            show_index=True,
        )
    else:
        clrs_portfolio = [
            theme.down_color if (x < 0) else theme.up_color for x in df["portfolio"]
        ]
        clrs_benchmark = [
            theme.down_color if (x < 0) else theme.up_color for x in df["benchmark"]
        ]

        fig = OpenBBFigure()

        fig.add_bar(
            x=df.index,
            y=df["portfolio"],
            name="Portfolio",
            marker_color=clrs_portfolio,
        )

        fig.add_bar(
            x=df.index,
            y=df["benchmark"],
            name="Benchmark",
            marker_color=clrs_benchmark,
        )

        fig.update_layout(
            title=f"Daily Returns [%] in period {window}",
            xaxis=dict(title="Date"),
            yaxis=dict(title="Returns [%]"),
        )

        fig.show()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dret",
        df,
    )


@log_start_end(log=logger)
def display_distribution_returns(
    portfolio_engine: PortfolioEngine,
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

    df = get_distribution_returns(portfolio_engine, window)
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
        fig = OpenBBFigure()

        fig.add_histogram(
            x=df_portfolio,
            name="Portfolio",
            histnorm="probability density",
            marker_color=theme.up_color,
        )

        fig.add_histogram(
            x=df_benchmark,
            name="Benchmark",
            histnorm="probability density",
            marker_color=theme.down_color,
        )

        fig.update_layout(
            title=f"Returns distribution in period {window}",
            xaxis=dict(title="Returns [%]"),
            yaxis=dict(title="Density"),
        )

        fig.show()

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "distr",
        stats,
    )


@log_start_end(log=logger)
def display_holdings_value(
    portfolio_engine: PortfolioEngine,
    unstack: bool = False,
    raw: bool = False,
    limit: int = 10,
    export: str = "",
    external_axes: bool = False,
):
    """Display holdings of assets (absolute value)

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    unstack: bool
        Individual assets over time
    raw : bool
        To display raw data
    limit : int
        Number of past market days to display holdings
    export: str
        Format to export plot
    external_axes: plt.Axes
        Optional axes to display plot on
    """

    all_holdings = get_holdings_value(portfolio_engine)

    if raw:
        print_rich_table(
            all_holdings.tail(limit),
            title="Holdings of assets (absolute value)",
            headers=all_holdings.columns,
            show_index=True,
        )
    else:
        if not unstack and "Total Value" in all_holdings.columns:
            all_holdings.drop(columns=["Total Value"], inplace=True)

        fig = OpenBBFigure()

        for col in all_holdings.columns:
            fig.add_scatter(
                x=all_holdings.index,
                y=all_holdings[col].values,
                name=col,
                stackgroup="one",
            )

        fig.update_layout(
            title="Total Holdings (value)",
            xaxis=dict(title="Date"),
            yaxis=dict(title="Holdings ($)"),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "holdv",
        all_holdings,
    )

    return fig.show() if not external_axes else fig


@log_start_end(log=logger)
def display_holdings_percentage(
    portfolio_engine: PortfolioEngine,
    unstack: bool = False,
    raw: bool = False,
    limit: int = 10,
    export: str = "",
    external_axes: bool = False,
):
    """Display holdings of assets (in percentage)

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    unstack: bool
        Individual assets over time
    raw : bool
        To display raw data
    limit : int
        Number of past market days to display holdings
    export: str
        Format to export plot
    external_axes: plt.Axes
        Optional axes to display plot on
    """

    all_holdings = get_holdings_percentage(portfolio_engine)

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
        if not unstack and "Total Value" in all_holdings.columns:
            all_holdings.drop(columns=["Total Value"], inplace=True)

        fig = OpenBBFigure()

        for col in all_holdings.columns:
            fig.add_scatter(
                x=all_holdings.index,
                y=all_holdings[col].values,
                name=col,
                stackgroup="one",
            )

        fig.update_layout(
            title="Total Holdings (percentage)",
            xaxis=dict(title="Date"),
            yaxis=dict(title="Holdings (%)"),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "holdp",
        all_holdings,
    )

    return fig.show() if not external_axes else fig


@log_start_end(log=logger)
def display_rolling_volatility(
    portfolio_engine: PortfolioEngine,
    window: str = "1y",
    export: str = "",
    external_axes: bool = False,
):
    """Display rolling volatility

    Parameters
    ----------
    portfolio : PortfolioEngine
        PortfolioEngine object
    interval: str
        interval for window to consider
    export: str
        Export to file
    external_axes: Optional[List[plt.Axes]]
        Optional axes to display plot on
    """

    metric = "volatility"
    df = get_rolling_volatility(portfolio_engine, window)
    if df.empty:
        return

    df_portfolio = df["portfolio"]
    df_benchmark = df["benchmark"]

    fig = OpenBBFigure()

    fig.add_scatter(
        x=df_portfolio.index,
        y=df_portfolio,
        name="Portfolio",
        marker_color=theme.up_color,
    )

    fig.add_scatter(
        x=df_benchmark.index,
        y=df_benchmark,
        name="Benchmark",
        marker_color=theme.down_color,
    )

    fig.update_layout(
        title=f"Rolling {metric.title()} using {window} window",
        xaxis=dict(title="Date"),
        yaxis=dict(title=f"{metric.title()}"),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        metric,
        df_portfolio.to_frame().join(df_benchmark),
    )

    return fig.show() if not external_axes else fig


@log_start_end(log=logger)
def display_rolling_sharpe(
    portfolio_engine: PortfolioEngine,
    risk_free_rate: float = 0,
    window: str = "1y",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display rolling sharpe

    Parameters
    ----------
    portfolio : PortfolioEngine
        PortfolioEngine object
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
    df = get_rolling_sharpe(portfolio_engine, risk_free_rate, window)
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
    portfolio_engine: PortfolioEngine,
    risk_free_rate: float = 0,
    window: str = "1y",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display rolling sortino

    Parameters
    ----------
    portfolio : PortfolioEngine
        PortfolioEngine object
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
    df = get_rolling_sortino(portfolio_engine, risk_free_rate, window)
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
    portfolio_engine: PortfolioEngine,
    window: str = "1y",
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display rolling beta

    Parameters
    ----------
    portfolio : PortfolioEngine
        PortfolioEngine object
    window: str
        interval for window to consider
        Possible options: mtd, qtd, ytd, 1d, 5d, 10d, 1m, 3m, 6m, 1y, 3y, 5y, 10y.
    export: str
        Export to file
    external_axes: Optional[List[plt.Axes]]
        Optional axes to display plot on
    """

    rolling_beta = get_rolling_beta(portfolio_engine, window)
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
    portfolio_engine: PortfolioEngine,
    export: str = "",
    external_axes: Optional[List[plt.Axes]] = None,
):
    """Display maximum drawdown curve

    Parameters
    ----------
    portfolio : PortfolioEngine
        PortfolioEngine object
    export: str
        Format to export data
    external_axes: plt.Axes
        Optional axes to display plot on
    """
    holdings, drawdown = get_maximum_drawdown(portfolio_engine)
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
    portfolio_engine: PortfolioEngine,
    export: str = "",
):
    """Display R-square

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    export : str
        Export data format
    """

    df = get_r2_score(portfolio_engine).fillna("-")

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
    portfolio_engine: PortfolioEngine,
    export: str = "",
):
    """Display skewness

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    export : str
        Export data format
    """

    df = get_skewness(portfolio_engine).fillna("-")

    print_rich_table(
        df,
        title="Skewness for Portfolio and Benchmark",
        show_index=True,
        floatfmt=".2f",
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "skew",
    )


@log_start_end(log=logger)
def display_kurtosis(
    portfolio_engine: PortfolioEngine,
    export: str = "",
):
    """Display kurtosis

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    export : str
        Export data format
    """

    df = get_kurtosis(portfolio_engine).fillna("-")

    print_rich_table(
        df,
        title="Kurtosis for Portfolio and Benchmark",
        show_index=True,
        floatfmt=".2f",
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "kurt",
    )


@log_start_end(log=logger)
def display_stats(
    portfolio_engine: PortfolioEngine,
    window: str = "all",
    export: str = "",
):
    """Display stats

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window : str
        interval to consider. Choices are: mtd, qtd, ytd, 3m, 6m, 1y, 3y, 5y, 10y, all
    export : str
        Export data format
    """

    df = get_stats(portfolio_engine, window)

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
    portfolio_engine: PortfolioEngine,
    export: str = "",
):
    """Display volatility for multiple intervals

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    export : str
        Export data format
    """

    df = get_volatility(portfolio_engine).fillna("-")
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
    portfolio_engine: PortfolioEngine,
    risk_free_rate: float = 0,
    export: str = "",
):
    """Display sharpe ratio for multiple intervals

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    risk_free_rate: float
        Risk free rate value
    export : str
        Export data format
    """

    df = get_sharpe_ratio(portfolio_engine, risk_free_rate).fillna("-")
    print_rich_table(
        df,
        title="Sharpe ratio for Portfolio and Benchmark",
        show_index=True,
        floatfmt=".2f",
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "metric_sharpe",
        df,
    )


@log_start_end(log=logger)
def display_sortino_ratio(
    portfolio_engine: PortfolioEngine,
    risk_free_rate: float = 0,
    export: str = "",
):
    """Display sortino ratio for multiple intervals

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    risk_free_rate: float
        Risk free rate value
    export : str
        Export data format
    """

    df = get_sortino_ratio(portfolio_engine, risk_free_rate).fillna("-")
    print_rich_table(
        df,
        title="Sortino ratio for Portfolio and Benchmark",
        show_index=True,
        floatfmt=".2f",
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "metric_sortino",
        df,
    )


@log_start_end(log=logger)
def display_maximum_drawdown_ratio(
    portfolio_engine: PortfolioEngine,
    export: str = "",
):
    """Display maximum drawdown for multiple intervals

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    export : str
        Export data format
    """

    df = get_maximum_drawdown_ratio(portfolio_engine).fillna("-")
    print_rich_table(
        df,
        title="Maximum drawdown for Portfolio and Benchmark",
        show_index=True,
        floatfmt=".2f",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_maxdrawdown", df
    )


@log_start_end(log=logger)
def display_gaintopain_ratio(
    portfolio_engine: PortfolioEngine,
    export: str = "",
):
    """Display gain-to-pain ratio for multiple intervals

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine object with returns and benchmark loaded
    export : str
        Export data format
    """

    df = get_gaintopain_ratio(portfolio_engine).fillna("-")
    print_rich_table(
        df,
        title="Gain-to-pain ratio for portfolio and benchmark",
        show_index=True,
        floatfmt=".2f",
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "metric_gaintopain_ratio",
        df,
    )


@log_start_end(log=logger)
def display_tracking_error(
    portfolio_engine: PortfolioEngine,
    export: str = "",
):
    """Display tracking error for multiple intervals

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine object with returns and benchmark loaded
    export : str
        Export data format
    """

    df, _ = get_tracking_error(portfolio_engine)
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
    portfolio_engine: PortfolioEngine,
    export: str = "",
):
    """Display information ratio for multiple intervals

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine object with returns and benchmark loaded
    export : str
        Export data format
    """

    df = get_information_ratio(portfolio_engine).fillna("-")
    print_rich_table(
        df,
        title="Information ratio for portfolio",
        show_index=True,
        floatfmt=".2f",
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "metric_information_ratio",
        df,
    )


@log_start_end(log=logger)
def display_tail_ratio(
    portfolio_engine: PortfolioEngine,
    export: str = "",
):
    """Display tail ratio for multiple intervals

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine object with returns and benchmark loaded
    window: str
        interval for window to consider
    export : str
        Export data format
    """

    df, _, _ = get_tail_ratio(portfolio_engine)
    df = df.fillna("-")
    print_rich_table(
        df,
        title="Tail ratio for portfolio and benchmark",
        show_index=True,
        floatfmt=".2f",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_tail_ratio", df
    )


@log_start_end(log=logger)
def display_common_sense_ratio(
    portfolio_engine: PortfolioEngine,
    export: str = "",
):
    """Display common sense ratio for multiple intervals

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine object with returns and benchmark loaded
    export : str
        Export data format
    """

    df = get_common_sense_ratio(portfolio_engine).fillna("-")
    print_rich_table(
        df,
        title="Common sense ratio for portfolio and benchmark",
        show_index=True,
        floatfmt=".2f",
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "metric_common_sense_ratio",
        df,
    )


@log_start_end(log=logger)
def display_jensens_alpha(
    portfolio_engine: PortfolioEngine,
    risk_free_rate: float = 0,
    export: str = "",
):
    """Display jensens alpha for multiple intervals

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine object with returns and benchmark loaded
    risk_free_rate: float
            Risk free rate
    export : str
        Export data format
    """

    df, _ = get_jensens_alpha(portfolio_engine, risk_free_rate)
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
    portfolio_engine: PortfolioEngine,
    export: str = "",
):
    """Display calmar ratio for multiple intervals

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine object with returns and benchmark loaded
    export : str
        Export data format
    """

    df, _ = get_calmar_ratio(portfolio_engine)
    df = df.fillna("-")
    print_rich_table(
        df,
        title="Calmar ratio for portfolio and benchmark",
        show_index=True,
        floatfmt=".2f",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_calmar_ratio", df
    )


@log_start_end(log=logger)
def display_kelly_criterion(
    portfolio_engine: PortfolioEngine,
    export: str = "",
):
    """Display kelly criterion for multiple intervals

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine object with trades and returns loaded
    export : str
        Export data format
    """

    df = get_kelly_criterion(portfolio_engine).fillna("-")
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
    portfolio_engine: PortfolioEngine,
    export: str = "",
):
    """Display payoff ratio for multiple intervals

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    export : str
        Export data format
    """

    df = get_payoff_ratio(portfolio_engine).fillna("-")
    print_rich_table(
        df,
        title="Portfolio's payoff ratio",
        show_index=True,
        floatfmt=".2f",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_payoff_ratio", df
    )


def display_profit_factor(
    portfolio_engine: PortfolioEngine,
    export: str = "",
):
    """Display profit factor for multiple intervals

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    export : str
        Export data format
    """

    df = get_profit_factor(portfolio_engine).fillna("-")
    print_rich_table(
        df,
        title="Portfolio's profit factor",
        show_index=True,
        floatfmt=".2f",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "metric_profit_factor", df
    )


@log_start_end(log=logger)
def display_summary(
    portfolio_engine: PortfolioEngine,
    window: str = "all",
    risk_free_rate: float = 0,
    export: str = "",
):
    """Display summary portfolio and benchmark returns

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    window : str
        interval to compare cumulative returns and benchmark
    risk_free_rate : float
        Risk free rate for calculations
    export : str
        Export certain type of data
    """

    summary = get_summary(portfolio_engine, window, risk_free_rate)
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
    portfolio_engine: PortfolioEngine,
    use_mean: bool = True,
    adjusted_var: bool = False,
    student_t: bool = False,
    percentile: float = 99.9,
):
    """Display portfolio VaR

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
    """

    qa_view.display_var(
        data=portfolio_engine.portfolio_returns,
        symbol="Portfolio",
        use_mean=use_mean,
        adjusted_var=adjusted_var,
        student_t=student_t,
        percentile=percentile,
        portfolio=True,
    )


@log_start_end(log=logger)
def display_es(
    portfolio_engine: PortfolioEngine,
    use_mean: bool = True,
    distribution: str = "normal",
    percentile: float = 99.9,
):
    """Display expected shortfall

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
    """

    qa_view.display_es(
        data=portfolio_engine.portfolio_returns,
        symbol="Portfolio",
        use_mean=use_mean,
        distribution=distribution,
        percentile=percentile,
        portfolio=True,
    )


@log_start_end(log=logger)
def display_omega(
    portfolio_engine: PortfolioEngine,
    threshold_start: float = 0,
    threshold_end: float = 1.5,
):
    """Display omega ratio

    Parameters
    ----------
    portfolio_engine: PortfolioEngine
        PortfolioEngine class instance, this will hold transactions and perform calculations.
        Use `portfolio.load` to create a PortfolioEngine.
    threshold_start: float
        annualized target return threshold start of plotted threshold range
    threshold_end: float
        annualized target return threshold end of plotted threshold range
    """

    qa_view.display_omega(
        data=portfolio_engine.portfolio_returns,
        threshold_start=threshold_start,
        threshold_end=threshold_end,
    )


@log_start_end(log=logger)
def display_attribution_categorization(
    display: pd.DataFrame,
    time_period: str,
    attrib_type: str,
    plot_fields: list,
    show_table: bool = False,
):
    """Display attribution for sector comparison to portfolio

    Parameters
    ----------
    display: dataframe to be displayed
    """
    if show_table:
        print_rich_table(
            display,
            title=f"{attrib_type}: Portfolio vs. Benchmark Attribution categorization {time_period}",
            show_index=True,
            floatfmt=".2f",
        )

    _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    plot_out = display[plot_fields]
    plot_out.plot.barh(ax=ax, align="center", width=0.8, color=["#1f77b4", "#ff7f0e"])
    ax.set_title(f"{attrib_type} By Sector")
    plt.tight_layout()
