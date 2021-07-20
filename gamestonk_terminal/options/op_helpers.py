"""Option mneu helpers"""
__docformat__ = "numpy"

import argparse
from typing import List

from gamestonk_terminal.helper_funcs import parse_known_args_and_warn

# pylint: disable=R1710


def load(other_args: List[str]):

    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="opload",
        description="Load a ticker into option menu",
    )

    parser.add_argument(
        "-t",
        "--ticker",
        action="store",
        dest="ticker",
        required="-h" not in other_args,
        help="Stock ticker",
    )

    try:
        if other_args:
            if "-t" not in other_args and "-h" not in other_args:
                other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        return ns_parser.ticker
    except Exception as e:
        print(e, "\n")
    except SystemExit:
        print("")
        return
