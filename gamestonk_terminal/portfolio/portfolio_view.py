"""Portfolio View"""
__docformat__ = "numpy"

from datetime import datetime
from io import BytesIO
import os

import pandas as pd
import numpy as np
from tabulate import tabulate
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from matplotlib import pyplot as plt
import matplotlib.ticker as mtick

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.portfolio import yfinance_model


def load_info():
    """Prints instructions to load a CSV"""
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
    """
    Shows the given dataframe

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to be shown
    show : bool
        Whether to show the dataframe index
    """

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


def plot_overall_return(df: pd.DataFrame):
    """Generates overall return graph

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to be analyzed

    Returns
    ----------
    img : ImageReader
        Overal return graph
    """
    df_m = yfinance_model.get_market()
    comb = pd.merge(df, df_m, how="left", left_index=True, right_index=True)
    comb = comb.fillna(method="ffill")
    comb[("Market", "Return")] = (
        comb[("Market", "Close")] - comb[("Market", "Close")][0]
    ) / comb[("Market", "Close")][0]

    pos = df["return"].copy()
    neg = df["return"].copy()
    mark = comb[("Market", "Return")].copy()

    pos[pos <= 0] = np.nan
    neg[neg > 0] = np.nan

    # plt.plot(pos, color="r")
    # plt.plot(neg, color="b")
    # plt.plot(mark, color="y", label="SPY")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(pos.index.to_list(), pos.to_list(), color="tab:blue")
    ax.plot(neg.index.to_list(), neg.to_list(), color="tab:red")
    ax.plot(mark.index.to_list(), mark.to_list(), color="orange", label="SPY")

    ax.set_ylabel("", fontweight="bold", fontsize=12, color="black")
    ax.set_xlabel("")
    ax.yaxis.set_label_coords(-0.1, 0.5)
    ax.grid(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    fig.suptitle("Performance", y=0.99, fontweight="bold", fontsize=14, color="black")
    ax.axhline(0, ls="-", lw=1, color="gray", zorder=1)
    ax.axhline(0, ls="--", lw=1, color="black", zorder=2)
    fig.set_facecolor("white")
    ax.set_title(
        "%s - %s"
        % (df.index[:1][0].strftime("%Y/%m/%d"), df.index[-1:][0].strftime("%Y/%m/%d")),
        fontsize=12,
        color="gray",
    )
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.set_facecolor("white")
    ax.fill_between(
        df.index,
        0,
        df["return"],
        where=df["return"] >= 0,
        interpolate=True,
        color="#348dc1",
        alpha=0.25,
    )
    ax.fill_between(
        df.index,
        0,
        df["return"],
        where=df["return"] <= 0,
        interpolate=True,
        color="red",
        alpha=0.25,
    )
    ax.legend()
    fig.autofmt_xdate()
    imgdata = BytesIO()
    fig.savefig(imgdata, format="png")
    imgdata.seek(0)
    return ImageReader(imgdata)


def annual_report(df: pd.DataFrame) -> None:
    """Generates an annual report

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to be analyzed
    """
    dire = os.path.dirname(os.path.abspath(__file__)).replace(
        "gamestonk_terminal", "exports"
    )

    now = datetime.now()
    path = os.path.abspath(
        os.path.join(
            dire,
            f"ar_{now.strftime('%Y%m%d_%H%M%S')}.pdf",
        )
    )
    report = canvas.Canvas(path, pagesize=letter)
    report.setLineWidth(0.3)
    report.setFont("Helvetica", 12)
    report.drawString(30, 750, "Gamestonk Terminal")
    report.drawString(500, 750, now.strftime("%Y/%m/%d"))
    report.drawString(275, 725, "Annual Report")
    report.setFillColorRGB(255, 0, 0)
    report.drawString(200, 710, "Warning: currently only analyzes stocks")
    report.setFillColorRGB(0, 0, 0)
    report.line(50, 700, 580, 700)
    image = plot_overall_return(df)
    report.drawImage(image, 15, 380, 600, 300)
    report.save()

    print("File save in:\n", path, "\n")
