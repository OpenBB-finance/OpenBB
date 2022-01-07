"""Blockchain Center View"""
import os
from matplotlib import pyplot as plt

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.cryptocurrency.overview.blockchaincenter_model import get_altcoin_index, DAYS
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal import feature_flags as gtff


def display_altcoin_index(period: int, since: int, until: int, export: str = "") -> None:
    """Displays altcoin index overtime
     [Source: https://blockchaincenter.net]

    Parameters
    ----------
    since : int
        Initial date timestamp (e.g., 1_614_556_800)
    until : int
        End date timestamp (e.g., 1_614_556_800)
    period: int
        Number of days to check the performance of coins and calculate the altcoin index.
        E.g., 365 will check yearly performance (365 days), 90 will check seasonal performance (90 days),
        30 will check monthly performance (30 days).

    export : str
        Export dataframe data to csv,json,xlsx file
    """
    if period in DAYS:
        df = get_altcoin_index(period, since, until)

        if df.empty:
            print("\nError scraping blockchain central\n")
        else:
            plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

            plt.plot(df.index, df["Value"], label="Altcoin Index", color="k")
            plt.xlabel("Time")
            plt.xlim(df.index.iloc[0], df.index.iloc[-1])
            plt.gcf().autofmt_xdate()
            plt.ylabel(f"Altcoin Index (comparing with {period}-day performance)")
            plt.axhline(y=75, color='b', label="Altcoin Season")
            plt.axhline(y=25, color='orange', label="Bitcoin Season")
            plt.title("Altcoin Index")
            if gtff.USE_ION:
                plt.ion()
            plt.show()
            print("")

            export_data(
                export,
                os.path.dirname(os.path.abspath(__file__)),
                "altindex",
                df,
            )
