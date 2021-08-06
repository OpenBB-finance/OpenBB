""" Alpha Vantage View """
__docformat__ = "numpy"

import argparse
from typing import List
import matplotlib.pyplot as plt
from alpha_vantage.sectorperformance import SectorPerformances
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn
from gamestonk_terminal import feature_flags as gtff


def sectors_view(other_args: List[str]):
    """Opens a bar chart with sector performance

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="sectors",
        description="""
            Real-time and historical sector performances calculated from
            S&P500 incumbents. Pops plot in terminal. [Source: Alpha Vantage]
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        sector_perf = SectorPerformances(
            key=cfg.API_KEY_ALPHAVANTAGE, output_format="pandas"
        )
        # pylint: disable=unbalanced-tuple-unpacking
        df_sectors, _ = sector_perf.get_sector()
        # pylint: disable=invalid-sequence-index
        df_sectors["Rank A: Real-Time Performance"].plot(kind="bar")
        plt.title("Real Time Performance (%) per Sector")
        plt.tight_layout()
        plt.grid()

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")
