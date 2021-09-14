""" Alpha Vantage View """
__docformat__ = "numpy"

import os

import matplotlib.pyplot as plt
from tabulate import tabulate

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.economy import alphavantage_model
from gamestonk_terminal.helper_funcs import export_data


def realtime_performance_sector(raw: bool, export: str):
    """Display Real-Time Performance sector. [Source: AlphaVantage]

    Parameters
    ----------
    raw : bool
        Output only raw data
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_sectors = alphavantage_model.get_sector_data()

    # pylint: disable=invalid-sequence-index
    df_rtp = df_sectors["Rank A: Real-Time Performance"]

    if raw:
        if gtff.USE_TABULATE_DF:
            print(
                tabulate(
                    df_rtp.to_frame(),
                    showindex=True,
                    headers=["Sector", "Real-Time Performance"],
                    floatfmt=".5f",
                    tablefmt="fancy_grid",
                )
            )
        else:
            print(df_rtp.to_string())

    else:
        df_rtp.plot(kind="bar")
        plt.title("Real Time Performance (%) per Sector")
        plt.tight_layout()
        plt.grid()

    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "rtps",
        df_sectors,
    )

    if not raw:
        if gtff.USE_ION:
            plt.ion()
        plt.show()
