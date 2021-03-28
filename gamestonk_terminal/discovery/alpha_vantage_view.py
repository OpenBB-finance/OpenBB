import argparse
import matplotlib.pyplot as plt
from alpha_vantage.sectorperformance import SectorPerformances
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn


def sectors(l_args):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="sectors",
        description="""Real-time and historical sector performances calculated from
        S&P500 incumbents. Pops plot in terminal. [Source: Alpha Vantage]""",
    )

    ns_parser = parse_known_args_and_warn(parser, l_args)
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
    plt.show()
    print("")
