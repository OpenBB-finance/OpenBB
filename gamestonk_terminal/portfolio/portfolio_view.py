"""Portfolio View"""
__docformat__ = "numpy"

from datetime import datetime, timedelta
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
from gamestonk_terminal.portfolio import reportlab_helpers


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


def plot_overall_return(
    df: pd.DataFrame, df_m: pd.DataFrame, n: int, m_tick: str
) -> ImageReader:
    """Generates overall return graph

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to be analyzed
    df_m : pd.DataFrame
        The dataframe for historical market performance
    n : int
        The number of days to include in chart
    m_tick : str
        The ticker for the market asset

    Returns
    ----------
    img : ImageReader
        Overal return graph
    """
    df = df.copy()
    df = df[df.index >= datetime.now() - timedelta(days=n + 1)]
    comb = pd.merge(df, df_m, how="left", left_index=True, right_index=True)
    comb = comb.fillna(method="ffill")
    comb = comb.dropna()

    comb["return"] = (
        comb["holdings"]
        + comb["Cash"]["Cash"]
        - comb["holdings"][0]
        - comb["Cash"]["Cash"][0]
    ) / (comb["Cash"]["Cash"][0] + comb["holdings"][0] + comb["total_cost"][0])

    comb[("Market", "Return")] = (
        comb[("Market", "Close")] - comb[("Market", "Close")][0]
    ) / comb[("Market", "Close")][0]

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
        % (df.index[:1][0].strftime("%Y/%m/%d"), df.index[-1:][0].strftime("%Y/%m/%d")),
        fontsize=12,
        color="gray",
    )
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    ax.set_facecolor("white")
    ax.legend()
    fig.autofmt_xdate()
    imgdata = BytesIO()
    fig.savefig(imgdata, format="png")
    imgdata.seek(0)
    return ImageReader(imgdata)


def plot_rolling_beta(
    df: pd.DataFrame, hist: pd.DataFrame, mark: pd.DataFrame, n: int
) -> ImageReader:
    """Returns a chart with the portfolio's rolling beta

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to be analyzed
    hist : pd.DataFrame
        A dataframe of historical returns
    market : pd.DataFrame
        A dataframe of SPY returns
    n : int
        The number of days to include in chart

    Returns
    ----------
    img : ImageReader
        Rolling beta graph
    """
    df = df["Holding"]
    uniques = df.columns.tolist()
    res = df.div(df.sum(axis=1), axis=0)
    comb = pd.merge(
        hist["Close"], mark["Market"], how="left", left_index=True, right_index=True
    )
    comb = comb.fillna(method="ffill")
    df_var = comb.rolling(600).var().unstack()["Close"].to_frame(name="var")

    for col in hist["Close"].columns:
        df1 = (
            comb.rolling(600).cov().unstack()[col]["Close"].to_frame(name=f"cov_{col}")
        )
        df_var = pd.merge(df_var, df1, how="left", left_index=True, right_index=True)
        df_var[f"beta_{col}"] = df_var[f"cov_{col}"] / df_var["var"]

    final = pd.merge(res, df_var, how="left", left_index=True, right_index=True)
    final = final.fillna(method="ffill")
    final = final.drop(columns=["var"] + [f"cov_{x}" for x in uniques])
    for uni in uniques:
        final[f"prod_{uni}"] = final[uni] * final[f"beta_{uni}"]

    final = final.drop(columns=[f"beta_{x}" for x in uniques] + uniques)
    final["total"] = final.sum(axis=1)
    final = final[final.index >= datetime.now() - timedelta(days=n + 1)]

    final[final == 0] = np.nan

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        final.index,
        final["total"],
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
    fig.suptitle("Rolling Beta", y=0.99, fontweight="bold", fontsize=14, color="black")
    ax.axhline(0, ls="-", lw=1, color="gray", zorder=1)
    ax.axhline(0, ls="--", lw=1, color="black", zorder=2)
    fig.set_facecolor("white")
    ax.set_title(
        "%s - %s"
        % (df.index[:1][0].strftime("%Y/%m/%d"), df.index[-1:][0].strftime("%Y/%m/%d")),
        fontsize=12,
        color="gray",
    )
    ax.set_facecolor("white")
    fig.autofmt_xdate()
    imgdata = BytesIO()
    fig.savefig(imgdata, format="png")
    imgdata.seek(0)
    return ImageReader(imgdata)


def annual_report(df: pd.DataFrame, hist: pd.DataFrame, m_tick: str) -> None:
    """Generates an annual report

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to be analyzed
    m_tick : str
        The ticker for the market asset

    hist : pd.DataFrame
        A dataframe of historical returns
    """
    df_m = yfinance_model.get_market(m_tick)
    dire = os.path.dirname(os.path.abspath(__file__)).replace(
        "gamestonk_terminal", "exports"
    )

    path = os.path.abspath(
        os.path.join(
            dire,
            f"ar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        )
    )
    report = canvas.Canvas(path, pagesize=letter)
    reportlab_helpers.base_format(report, "Overview")
    report.drawImage(plot_overall_return(df, df_m, 365, m_tick), 15, 360, 600, 300)
    report.showPage()
    reportlab_helpers.base_format(report, "Portfolio Analysis")
    report.drawImage(plot_rolling_beta(df, hist, df_m, 365), 15, 360, 600, 300)
    report.save()

    print("File save in:\n", path, "\n")
