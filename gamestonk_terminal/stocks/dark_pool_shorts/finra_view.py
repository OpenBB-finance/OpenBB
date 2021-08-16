""" FINRA View """
__docformat__ = "numpy"

from typing import List
import pandas as pd
from matplotlib import pyplot as plt
from gamestonk_terminal.stocks.dark_pool_shorts import finra_model
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import plot_autoscale


def plot_dark_pools(ticker: str, ats: pd.DataFrame, otc: pd.DataFrame):
    """Plots ATS and NON-ATS data

    Parameters
    ----------
    ticker : str
        Stock ticker to get data from
    ats : pd.DataFrame
        Dark Pools (ATS) Data
    otc : pd.DataFrame
        OTC (Non-ATS) Data
    """
    _, _ = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    plt.subplot(3, 1, (1, 2))
    if not ats.empty and not otc.empty:
        plt.bar(
            ats.index,
            (ats["totalWeeklyShareQuantity"] + otc["totalWeeklyShareQuantity"])
            / 1_000_000,
            color="tab:orange",
        )
        plt.bar(
            otc.index, otc["totalWeeklyShareQuantity"] / 1_000_000, color="tab:blue"
        )
        plt.legend(["ATS", "OTC"])

    elif not ats.empty:
        plt.bar(
            ats.index,
            ats["totalWeeklyShareQuantity"] / 1_000_000,
            color="tab:orange",
        )
        plt.legend(["ATS"])

    elif not otc.empty:
        plt.bar(
            otc.index, otc["totalWeeklyShareQuantity"] / 1_000_000, color="tab:blue"
        )
        plt.legend(["OTC"])

    plt.ylabel("Total Weekly Shares [Million]")
    plt.grid(b=True, which="major", color="#666666", linestyle="-", alpha=0.2)
    plt.title(f"Dark Pools (ATS) vs OTC (Non-ATS) Data for {ticker}")

    plt.subplot(313)
    if not ats.empty:
        plt.plot(
            ats.index,
            ats["totalWeeklyShareQuantity"] / ats["totalWeeklyTradeCount"],
            color="tab:orange",
        )
        plt.legend(["ATS"])

        if not otc.empty:
            plt.plot(
                otc.index,
                otc["totalWeeklyShareQuantity"] / otc["totalWeeklyTradeCount"],
                color="tab:blue",
            )
            plt.legend(["ATS", "OTC"])

    else:
        plt.plot(
            otc.index,
            otc["totalWeeklyShareQuantity"] / otc["totalWeeklyTradeCount"],
            color="tab:blue",
        )
        plt.legend(["OTC"])

    plt.ylabel("Shares per Trade")
    plt.grid(b=True, which="major", color="#666666", linestyle="-", alpha=0.2)
    plt.gcf().autofmt_xdate()
    plt.xlabel("Weeks")

    if gtff.USE_ION:
        plt.ion()

    plt.show()


def darkpool_ats_otc(ticker: str):
    """Display barchart of dark pool (ATS) and OTC (Non ATS) data

    Parameters
    ----------
    ticker : str
        Stock ticker
    """
    df_ats, df_otc = finra_model.getTickerFINRAdata(ticker)

    if df_ats.empty and df_otc.empty:
        print("No ticker data found!")

    plot_dark_pools(ticker, df_ats, df_otc)
    print("")


def plot_dark_pools_ats(ats: pd.DataFrame, top_ats_tickers: List):
    """Plots promising tickers based on growing ATS data

    Parameters
    ----------
    ats : pd.DataFrame
        Dark Pools (ATS) Data
    top_ats_tickers : List
        List of tickers from most promising with better linear regression slope
    """
    plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

    for symbol in top_ats_tickers:
        plt.plot(
            pd.to_datetime(
                ats[ats["issueSymbolIdentifier"] == symbol]["weekStartDate"]
            ),
            ats[ats["issueSymbolIdentifier"] == symbol]["totalWeeklyShareQuantity"]
            / 1_000_000,
        )

    plt.legend(top_ats_tickers)
    plt.ylabel("Total Weekly Shares [Million]")
    plt.grid(b=True, which="major", color="#666666", linestyle="-", alpha=0.2)
    plt.title("Dark Pool (ATS) growing tickers")
    plt.gcf().autofmt_xdate()
    plt.xlabel("Weeks")

    if gtff.USE_ION:
        plt.ion()

    plt.show()


def darkpool_otc(num: int, promising: int):
    """Display dark pool (ATS) data of tickers with growing trades activity

    Parameters
    ----------
    num : int
        Number of tickers to filter from entire ATS data based on
        the sum of the total weekly shares quantity
    promising : int
        Number of tickers to display from most promising with
        better linear regression slope
    """
    df_ats, d_ats_reg = finra_model.getATSdata(num)

    top_ats_tickers = list(
        dict(sorted(d_ats_reg.items(), key=lambda item: item[1], reverse=True)).keys()
    )[:promising]

    plot_dark_pools_ats(df_ats, top_ats_tickers)
    print("")
