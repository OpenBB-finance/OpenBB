"""Portfolio View"""
__docformat__ = "numpy"

from datetime import datetime
from io import BytesIO
from os import path

import pandas as pd
from tabulate import tabulate
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from matplotlib import pyplot as plt
import matplotlib.ticker as mtick

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.portfolio import portfolio_model, yfinance_model
from gamestonk_terminal.portfolio import reportlab_helpers


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
    print(text)


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

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                df,
                headers=df.columns,
                floatfmt=".2f",
                showindex=show,
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(df.to_string, "\n")


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
    plt.close("all")
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
        "%s - %s"
        % (
            comb.index[:1][0].strftime("%Y/%m/%d"),
            comb.index[-1:][0].strftime("%Y/%m/%d"),
        ),
        fontsize=12,
        color="gray",
    )
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.set_facecolor("white")
    ax.legend()
    fig.autofmt_xdate()
    if plot:
        plt.show()
        print("")
        return None

    imgdata = BytesIO()
    fig.savefig(imgdata, format="png")
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
    plt.close("all")

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
        "%s - %s"
        % (df.index[:1][0].strftime("%Y-%m-%d"), df.index[-1:][0].strftime("%Y-%m-%d")),
        fontsize=12,
        color="gray",
    )
    ax.set_facecolor("white")
    fig.autofmt_xdate()
    imgdata = BytesIO()
    fig.savefig(imgdata, format="png")
    imgdata.seek(0)
    return ImageReader(imgdata)


class Report:
    def __init__(self, df: pd.DataFrame, hist: pd.DataFrame, m_tick: str, n: int):
        self.df = df
        self.hist = hist
        self.m_tick = m_tick
        self.df_m = yfinance_model.get_market(self.df.index[0], self.m_tick)
        self.returns = portfolio_model.get_return(df, self.df_m, n)

    def generate_report(self):
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
        self.generate_pg2(report, self.df_m)
        report.save()
        print("File save in:\n", loc, "\n")

    def generate_pg1(self, report: canvas.Canvas):
        report.drawImage(
            plot_overall_return(self.returns, self.m_tick, False), 15, 360, 600, 300
        )
        main_t = portfolio_model.get_main_text(self.returns)
        reportlab_helpers.draw_paragraph(report, main_t, 30, 380, 550, 200)
        report.showPage()

    def generate_pg2(self, report: canvas.Canvas, df_m: pd.DataFrame):
        reportlab_helpers.base_format(report, "Portfolio Analysis")
        if "Holding" in self.df.columns:
            rolling_beta = portfolio_model.get_rolling_beta(
                self.df, self.hist, df_m, 365
            )
            report.drawImage(plot_rolling_beta(rolling_beta), 15, 360, 600, 300)
            main_t = portfolio_model.get_beta_text(rolling_beta)
            reportlab_helpers.draw_paragraph(report, main_t, 30, 380, 550, 200)
