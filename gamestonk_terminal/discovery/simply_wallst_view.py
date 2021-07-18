""" Simply Wallst View """
__docformat__ = "numpy"

import argparse
from typing import List
import webbrowser
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn


def simply_wallst_view(other_args: List[str]):
    """Opens simplywall.st for a specific industry in a browser

    Parameters
    ----------
    other_args : List[str]
        argparse other args - ["-i", "banks"]
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="simply_wallst",
        description="""
            Simply Wall Street Research. Opens web browser. Although this does not require
            an API key, it requires a subscription to the website by the user
            (there's a 14 days free trial).[Source: Simply Wall St.]
        """,
    )
    parser.add_argument(
        "-i",
        "--industry",
        action="store",
        dest="s_industry",
        type=str,
        default="any",
        help="Industry of interest.",
        choices=[
            "any",
            "automobiles",
            "banks",
            "capital-goods",
            "commercial-services",
            "consumer-durables",
            "consumer-services",
            "diversified-financials",
            "energy",
            "consumer-retailing",
            "food-beverage-tobacco",
            "healthcare",
            "household",
            "insurance",
            "materials",
            "media",
            "pharmaceuticals-biotech",
            "real-estate",
            "retail",
            "semiconductors",
            "software",
            "tech",
            "telecom",
            "transportation",
            "utilities",
        ],
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        webbrowser.open(
            f"https://simplywall.st/stocks/us/{ns_parser.s_industry}?page=1"
        )
        print("")

    except Exception as e:
        print(e, "\n")
