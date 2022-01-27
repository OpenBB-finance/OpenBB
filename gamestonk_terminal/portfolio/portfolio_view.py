"""Portfolio View"""
__docformat__ = "numpy"

from typing import List
from datetime import datetime
from io import BytesIO
from os import path
import os

import numpy as np
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from matplotlib.lines import Line2D
from matplotlib import pyplot as plt
import matplotlib.ticker as mtick
from pypfopt import plotting

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.portfolio import (
    portfolio_model,
    yfinance_model,
)
from gamestonk_terminal.portfolio import reportlab_helpers
from gamestonk_terminal.helper_funcs import (
    get_rf,
    plot_autoscale,
    export_data,
    print_rich_table,
)
from gamestonk_terminal.portfolio.portfolio_optimization import optimizer_model
from gamestonk_terminal.rich_config import console


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
2. Place this file in gamestonk_terminal/portfolio/portfolios\n
        """
    console.print(text)


def show_df(df: pd.DataFrame, show: bool) -> None:
    """Shows the given dataframe

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to be shown
    show : bool
        Whether to show the dataframe index
    """

    df = df.dropna(how="all", axis=1).fillna("")

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=show,
    )
    console.print("")


def plot_overall_return(
    comb: pd.DataFrame, m_tick: str, plot: bool = False
) -> ImageReader:
    """Generates overall return graph

    Parameters
    ----------
    comb : pd.DataFrame
        Dataframe with returns
    m_tick : str
        The ticker for the market asset
    plot : bool
        Whether to plot the graph or return it for PDF

    Returns
    ----------
    img : ImageReader
        Overal return graph
    """
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(comb.index, comb["return"], color="tab:blue", label="Portfolio")
    ax.plot(comb.index, comb[("Market", "Return")], color="orange", label=m_tick)

    ax.set_ylabel("", fontweight="bold", fontsize=12, color="black")
    ax.set_xlabel("")
    ax.yaxis.set_label_coords(-0.1, 0.5)
    ax.grid(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    fig.suptitle(
        "Cumulative Performance", y=0.99, fontweight="bold", fontsize=14, color="black"
    )
    ax.axhline(0, ls="-", lw=1, color="gray", zorder=1)
    ax.axhline(0, ls="--", lw=1, color="black", zorder=2)
    fig.set_facecolor("white")
    ax.set_title(
        f'{comb.index[:1][0].strftime("%Y/%m/%d")} - {comb.index[-1:][0].strftime("%Y/%m/%d")}',
        fontsize=12,
        color="gray",
    )
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.set_facecolor("white")
    ax.legend()
    fig.autofmt_xdate()
    if plot:
        plt.show()
        console.print("")
        return None
    imgdata = BytesIO()
    fig.savefig(imgdata, format="png")
    plt.close("all")
    imgdata.seek(0)
    return ImageReader(imgdata)


def plot_rolling_beta(df: pd.DataFrame) -> ImageReader:
    """Returns a chart with the portfolio's rolling beta

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to be analyzed

    Returns
    ----------
    img : ImageReader
        Rolling beta graph
    """

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        df.index,
        df["total"],
        color="tab:blue",
    )

    ax.set_ylabel("", fontweight="bold", fontsize=12, color="black")
    ax.set_xlabel("")
    ax.yaxis.set_label_coords(-0.1, 0.5)
    ax.grid(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    fig.suptitle(
        "Rolling Beta of Stocks", y=0.99, fontweight="bold", fontsize=14, color="black"
    )
    ax.axhline(0, ls="-", lw=1, color="gray", zorder=1)
    ax.axhline(0, ls="--", lw=1, color="black", zorder=2)
    fig.set_facecolor("white")
    ax.set_title(
        f'{df.index[:1][0].strftime("%Y-%m-%d")} - {df.index[-1:][0].strftime("%Y-%m-%d")}',
        color="gray",
    )
    ax.set_facecolor("white")
    fig.autofmt_xdate()
    imgdata = BytesIO()
    fig.savefig(imgdata, format="png")
    plt.close("all")
    imgdata.seek(0)
    return ImageReader(imgdata)


def plot_ef(
    stocks: List[str],
    variance: float,
    per_ret: float,
    rf_rate: float,
    period: str = "3mo",
    n_portfolios: int = 300,
    risk_free: bool = False,
):
    """Display efficient frontier

    Parameters
    ----------
    stocks : List[str]
        List of the stocks to be included in the weights
    variance : float
        The variance for the portfolio
    per_ret : float
        The portfolio's return for the portfolio
    rf_rate : float
        The risk free rate
    period : str
        The period to track
    n_portfolios : int
        The number of portfolios to generate
    risk_free : bool
        Include the risk-free asset
    """
    fig, ax = plt.subplots(figsize=(10, 5), dpi=PLOT_DPI)
    ef, rets, stds = optimizer_model.generate_random_portfolios(
        [x.upper() for x in stocks], period, n_portfolios
    )
    sharpes = rets / stds
    ax.scatter(stds, rets, marker=".", c=sharpes, cmap="viridis_r")
    plotting.plot_efficient_frontier(ef, ax=ax, show_assets=True)
    # Find the tangency portfolio
    ret_sharpe, std_sharpe, _ = ef.portfolio_performance(risk_free_rate=rf_rate)
    ax.scatter(std_sharpe, ret_sharpe, marker="*", s=100, c="r", label="Max Sharpe")
    plt.plot(variance, per_ret, "ro", label="Portfolio")
    # Add risk free line
    if risk_free:
        y = ret_sharpe * 1.2
        m = (ret_sharpe - rf_rate) / std_sharpe
        x2 = (y - rf_rate) / m
        x = [0, x2]
        y = [rf_rate, y]
        line = Line2D(x, y, color="#FF0000", label="Capital Allocation Line")
        ax.set_xlim(xmin=min(stds) * 0.8)
        ax.add_line(line)
    ax.set_title(f"Efficient Frontier simulating {n_portfolios} portfolios")
    ax.legend()
    fig.tight_layout()
    ax.grid(b=True, which="major", color="#666666", linestyle="-")

    if gtff.USE_ION:
        plt.ion()

    imgdata = BytesIO()
    fig.savefig(imgdata, format="png")
    plt.close("all")
    imgdata.seek(0)
    return ImageReader(imgdata)


def display_allocation(data: pd.DataFrame, graph: bool):
    """Displays allocation
    Parameters
    ----------
    data: pd.DataFrame
        The portfolio allocation dataframe
    graph: bool
        If pie chart shall be displayed with table"""

    print_rich_table(data, headers=list(data.columns), title="Allocation")
    console.print("")

    if graph:
        graph_data = data[data["pct_allocation"] >= 5].copy()
        if not graph_data.empty:
            graph_data.loc["Other"] = [
                "NA",
                data["value"].sum() - graph_data["value"].sum(),
                100 - graph_data["value"].sum(),
            ]
            labels = graph_data.index.values
            sizes = graph_data["value"].to_list()
        else:
            labels = data.index.values
            sizes = data["value"].to_list()
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        ax.set_title("Portfolio Allocation")
        fig.set_tight_layout(True)

        plt.show()


def display_drawdown(holdings: pd.DataFrame, export: str = ""):
    """Display drawdown curve

    Parameters
    ----------
    holdings: pd.DataFrame
        Dataframe of holdings vs time
    export: str
        Format to export data

    """
    drawdown = portfolio_model.calculate_drawdown(holdings)
    fig, ax = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax[0].plot(holdings.index, holdings)
    ax[0].set_title("Cumulative Returns")

    ax[1].plot(holdings.index, drawdown)
    ax[1].fill_between(holdings.index, np.asarray(drawdown["return"]), alpha=0.4)
    ax[1].set_title("Portfolio Drawdown")
    ax[0].grid()
    ax[1].grid()
    fig.autofmt_xdate()
    fig.tight_layout()
    if gtff.USE_ION:
        plt.ion()
    console.print()
    plt.show()
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "mdd",
    )


class Report:
    def __init__(self, df: pd.DataFrame, hist: pd.DataFrame, m_tick: str, n: int):
        """Generate financial reports.
        Financial reports allow users to show the how they have been performing in
        trades. This allows for a simple way to show progress and analyze metrics
        that track portfolio performance

        Parameters
        ----------
        df : pd.DataFrame
            The dataframe with previous holdings information
        hist : pd.DataFrame
            The dataframe with previous prices for stocks in the portfolio
        m_tick : str
            The market asset to be identified
        n : int
            The number of days to analyze

        Attributes
        ----------
        generate_report : None
            Generates a report with the given parameters
        generate_pg1 : None
            Creates the first page of the PDF report
        generate_pg2 : None
            Creates the second page of the PDF report

        """
        self.df = df
        self.hist = hist
        self.m_tick = m_tick
        self.df_m = yfinance_model.get_market(self.df.index[0], self.m_tick)
        self.returns, self.variance = portfolio_model.get_return(df, self.df_m, n)
        self.rf = get_rf()
        self.betas = portfolio_model.get_rolling_beta(
            self.df, self.hist, self.df_m, 365
        )

    def generate_report(self) -> None:
        d = path.dirname(path.abspath(__file__)).replace(
            "gamestonk_terminal", "exports"
        )
        loc = path.abspath(
            path.join(
                d,
                f"ar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            )
        )
        report = canvas.Canvas(loc, pagesize=letter)
        reportlab_helpers.base_format(report, "Overview")
        self.generate_pg1(report)
        self.generate_pg2(report)
        report.save()
        console.print("File save in:\n", loc, "\n")

    def generate_pg1(self, report: canvas.Canvas) -> None:
        report.drawImage(
            plot_overall_return(self.returns, self.m_tick, False), 15, 400, 600, 300
        )
        main_text = portfolio_model.get_main_text(self.returns)
        reportlab_helpers.draw_paragraph(report, main_text, 30, 410, 550, 200)
        current_return = self.returns["return"][-1]
        beta = self.betas["total"][-1]
        market_return = self.returns[("Market", "Return")][-1]
        sharpe = f"{(current_return - self.rf)/ np.std(self.returns['return']):.2f}"
        treynor = f"{(current_return - self.rf)/ beta:.2f}" if beta > 0 else "N/A"
        alpha = f"{current_return - (self.rf + beta * (market_return - self.rf)):.2f}"
        information = (
            f"{float(alpha)/ (np.std(self.returns['return'] - market_return)):.2f}"
        )
        perf = [
            ["Sharpe", sharpe],
            ["Treynor", treynor],
            ["Alpha", alpha],
            ["Information", information],
        ]
        reportlab_helpers.draw_table(report, "Performance", 540, 300, 30, perf)
        reportlab_helpers.draw_paragraph(
            report, portfolio_model.performance_text, 140, 290, 460, 200
        )
        report.showPage()

    def generate_pg2(self, report: canvas.Canvas) -> None:
        reportlab_helpers.base_format(report, "Portfolio Analysis")
        if "Holding" in self.df.columns:
            report.drawImage(plot_rolling_beta(self.betas), 15, 400, 600, 300)
            main_t = portfolio_model.get_beta_text(self.betas)
            reportlab_helpers.draw_paragraph(report, main_t, 30, 410, 550, 200)
            # report.drawImage(plot_ef(uniques, self.variance, self.returns["return"][-1], self.rf), 15, 65, 600, 300)
