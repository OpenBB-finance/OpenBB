""" MarketBeat View """
__docformat__ = "numpy"

import argparse
from typing import List
import numpy as np
import pandas as pd

from gamestonk_terminal.helper_funcs import (
    check_positive,
    parse_known_args_and_warn,
)
from gamestonk_terminal.stocks.discovery import marketbeat_model


def ratings_view(other_args: List[str]):
    """Prints top ratings updates [Source: MarketBeat]

    MarketBeat has changed the access to their data. Now, a user needs to have 'MarketBeat All Access'
    to make the most out of this command.

    Parameters
    ----------
    other_args : List[str]
        argparse other args - ["-t", "100"]
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="ratings",
        description="""Top ratings updates. MarketBeat has changed the access to their data.
        Now, a user needs to have 'MarketBeat All Access' to make the most out of this command.
        [Source: MarketBeat]""",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        action="store",
        dest="n_threshold",
        type=check_positive,
        default=0,  # Change to 0 because of the preview shown by MarketBeat
        help="Minimum threshold in percentage change between current and target price to show ratings",
    )

    if other_args:
        if "-" not in other_args[0]:
            other_args.insert(0, "-t")

    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    ratings = marketbeat_model.get_ratings()

    df_ratings = pd.DataFrame(ratings)

    df_ratings = df_ratings[df_ratings["target_price"] != ""]
    df_ratings["old_target"] = (
        df_ratings["target_price"]
        .apply(lambda x: x.split(" ➝ ")[0].replace("$", "") if "➝" in x else "")
        .astype(float)
    )
    df_ratings["new_target"] = (
        df_ratings["target_price"]
        .apply(lambda x: x.split(" ➝ ")[1].replace("$", "") if "➝" in x else x)
        .astype(float)
    )

    df_ratings["clean_current_price"] = (
        df_ratings["current_price"]
        .apply(lambda x: x.replace("0.0%", "").replace("+", "").replace("$", ""))
        .astype(float)
    )

    df_ratings.drop(columns=["analyst", "current_price", "target_price"], inplace=True)

    df_ratings["pct_increase"] = round(
        100
        * (df_ratings["new_target"] - df_ratings["clean_current_price"])
        / df_ratings["clean_current_price"],
        2,
    )

    df_ratings = df_ratings.sort_values(by=["pct_increase"], ascending=False)

    df_ratings["pct_abs"] = np.abs(df_ratings["pct_increase"])

    df_ratings_top = df_ratings[df_ratings["pct_abs"] > ns_parser.n_threshold][
        [
            "ticker",
            "action",
            "brokerage",
            "rate",
            "old_target",
            "new_target",
            "clean_current_price",
            "pct_increase",
        ]
    ]

    df_ratings_top["old_target"] = df_ratings_top["old_target"].apply(
        lambda x: str(x) + " $"
    )

    df_ratings_top["new_target"] = df_ratings_top["new_target"].apply(
        lambda x: str(x) + " $"
    )

    df_ratings_top["clean_current_price"] = df_ratings_top["clean_current_price"].apply(
        lambda x: str(x) + " $"
    )

    df_ratings_top["pct_increase"] = df_ratings_top["pct_increase"].apply(
        lambda x: str(x) + " %"
    )

    df_ratings_top = df_ratings_top.rename(
        columns={
            "old_target": "Old Target",
            "new_target": "New Target",
            "clean_current_price": "Current Price",
            "pct_increase": "Increase",
        }
    )

    print(df_ratings_top.to_string(index=False))
    print("")
