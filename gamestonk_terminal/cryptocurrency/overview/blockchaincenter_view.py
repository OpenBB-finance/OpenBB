"""Blockchain Center View"""
import logging
import os

from matplotlib import dates as mdates
from matplotlib import pyplot as plt

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.cryptocurrency.overview.blockchaincenter_model import (
    DAYS,
    get_altcoin_index,
)
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_altcoin_index(
    period: int, since: int, until: int, export: str = ""
) -> None:
    """Displays altcoin index overtime
     [Source: https://blockchaincenter.net]

    Parameters
    ----------
    since : int
        Initial date timestamp (e.g., 1_609_459_200)
    until : int
        End date timestamp (e.g., 1_641_588_030)
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
            console.print("\nError scraping blockchain central\n")
        else:
            _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            ax.set_ylabel("Altcoin Index")
            ax.axhline(y=75, color="b", label="Altcoin Season (75)")
            ax.axhline(y=25, color="orange", label="Bitcoin Season (25)")
            ax.set_title(f"Altcoin Index (Performance based on {period} days)")
            ax.plot(df.index, df["Value"], label="Altcoin Index", color="k")
            ax.grid()
            ax.legend()
            ax.set_xlabel("Time")
            ax.set_xlim(df.index[0], df.index[-1])
            dateFmt = mdates.DateFormatter("%m/%d/%Y")

            ax.xaxis.set_major_formatter(dateFmt)
            ax.tick_params(axis="x", labelrotation=45)
            if gtff.USE_ION:
                plt.ion()
            plt.show()
            console.print("")

            export_data(
                export,
                os.path.dirname(os.path.abspath(__file__)),
                "altindex",
                df,
            )
