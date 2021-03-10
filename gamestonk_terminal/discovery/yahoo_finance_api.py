import argparse
import pandas as pd
from gamestonk_terminal.helper_funcs import parse_known_args_and_warn


def gainers(l_args):
    parser = argparse.ArgumentParser(
        prog="gainers",
        description="Print up to 25 top ticker gainers in terminal. [Source: Yahoo Finance]",
    )

    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_gainers",
        type=int,
        default=5,
        choices=range(1, 25),
        help="Number of the top gainers stocks to retrieve.",
    )

    ns_parser = parse_known_args_and_warn(parser, l_args)
    if not ns_parser:
        return

    df_gainers = pd.read_html(
        "https://finance.yahoo.com/screener/predefined/day_gainers"
    )[0]
    print(df_gainers.head(ns_parser.n_gainers).to_string(index=False))
    print("")
