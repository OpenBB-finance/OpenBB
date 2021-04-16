""" MarketBeat View """
__docformat__ = "numpy"

import argparse
from typing import List
from gamestonk_terminal.helper_funcs import (
    check_positive,
    parse_known_args_and_warn,
)

from gamestonk_terminal.discovery import marketbeat_model


def ratings_view(other_args: List[str]):
    """Prints a list with ratings

    Parameters
    ----------
    other_args : List[str]
        argparse other args - ["-n", "5"]
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        prog="ratings",
        description="""Latest ratings. [Source: MarketBeat]""",
    )

    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=10,
        help="number of ratings to print",
    )

    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    ratings = marketbeat_model.get_ratings()
    for idx, rating in enumerate(ratings):
        print(
            rating["ticker"],
            rating["action"].replace(" by", ""),
            rating["impact"],
            rating["current_price"],
            "->",
            rating["target_price"],
        )
        if idx >= ns_parser.n_num - 1:
            break
