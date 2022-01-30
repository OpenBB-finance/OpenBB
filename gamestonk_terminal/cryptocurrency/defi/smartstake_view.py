"""SentimentInvestor View"""
__docformat__ = "numpy"

import os
import matplotlib.dates as mdates
from matplotlib import pyplot as plt

from gamestonk_terminal.cryptocurrency.defi import smartstake_model
from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal import feature_flags as gtff

# pylint: disable=E1101

LUNA_CIR_SUPPLY_CHANGE = "lunaSupplyChallengeStats"


def display_luna_circ_supply_change(
    days: int,
    export: str,
    supply_type: str = LUNA_CIR_SUPPLY_CHANGE,
    limit: int = 5,
):
    """Display Luna circulating supply stats

    Parameters
    ----------
    days: int
        Number of days
    supply_type: str
        Supply type to unpack json
    export: str
        Export type
    limit: int
        Number of results display on the terminal
        Default: 5
    Returns
        None
    -------
    """

    df = smartstake_model.get_luna_supply_stats(supply_type, days)

    if df.empty:
        print("Error in SmartStake request")
    else:
        _, ax1 = plt.subplots(figsize=(25, 7))
        ax1.plot(
            df.index, df["circulatingSupplyInMil"], c="k", label="Circulating Supply"
        )
        ax1.plot(
            df.index,
            df["liquidCircSupplyInMil"],
            c="r",
            label="Liquid Circulating Supply",
        )
        ax1.plot(
            df.index, df["stakeFromCircSupplyInMil"], c="g", label="Stake of Supply"
        )
        ax1.plot(
            df.index,
            df["recentTotalLunaBurntInMil"],
            c="b",
            label="Supply Reduction (Luna Burnt)",
        )

        ax1.grid()
        ax1.set_ylabel("Millions")
        ax1.set_xlabel("Time")
        ax1.set_title("Luna Circulating Supply Changes (In Millions)")
        ax1.set_xlim(df.index[0], df.index[-1])
        ax1.legend(loc="upper left")

        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.gcf().autofmt_xdate()

        if gtff.USE_ION:
            plt.ion()

        plt.show()

        RAW_COLS = [
            "circulatingSupplyInMil",
            "liquidCircSupplyInMil",
            "circSupplyChangeInMil",
            "recentTotalLunaBurntInMil",
        ]

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "lcsc",
            df[RAW_COLS],
        )

        df.index = df.index.strftime("%Y-%m-%d")
        df = df.sort_index(ascending=False)

        print_rich_table(
            df[RAW_COLS].head(limit),
            headers=[
                "Circ Supply",
                "Liquid Circ Supply",
                "Supply Change",
                "Supply Reduction (Luna Burnt)",
            ],
            show_index=True,
            index_name="Time",
            title="Luna Circulating Supply Changes (in Millions)",
        )
