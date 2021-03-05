import argparse
import pandas as pd

# ---------------------------------------------------- GAINERS ----------------------------------------------------
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

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return

    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    df_gainers = pd.read_html(
        "https://finance.yahoo.com/screener/predefined/day_gainers"
    )[0]
    print(df_gainers.head(ns_parser.n_gainers).to_string(index=False))
    print("")
