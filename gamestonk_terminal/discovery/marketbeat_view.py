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
from gamestonk_terminal.discovery import marketbeat_model


def ratings_view(other_args: List[str]):
    """Prints top ratings updates

    Parameters
    ----------
    other_args : List[str]
        argparse other args - ["-t", "100"]
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="ratings",
        description="""Top ratings updates. [Source: MarketBeat]""",
    )
    parser.add_argument(
        "-t",
        "--threshold",
        action="store",
        dest="n_threshold",
        type=check_positive,
        default=100,
        help="Minimum threshold in percentage change between current and target price to show ratings",
    )

    if other_args:
        if "-" not in other_args[0]:
            other_args.insert(0, "-t")

    ns_parser = parse_known_args_and_warn(parser, other_args)
    if not ns_parser:
        return

    try:
        ratings = marketbeat_model.get_ratings()

        df_ratings = pd.DataFrame(ratings)
        df_ratings = df_ratings[df_ratings["target_price"] != ""]
        df_ratings["old_target"] = df_ratings["target_price"].apply(
            lambda x: x.split(" ➝ ")[0] if "➝" in x else ""
        )
        df_ratings["new_target"] = df_ratings["target_price"].apply(
            lambda x: x.split(" ➝ ")[1] if "➝" in x else x
        )

        df_ratings["clean_current_price"] = df_ratings["current_price"].apply(
            lambda x: "".join(c if c.isdigit() or c == "." else "" for c in str(x))
        )
        df_ratings["clean_current_price"] = df_ratings["clean_current_price"].astype(
            float
        )
        df_ratings["clean_target_price"] = df_ratings["new_target"].apply(
            lambda x: "".join(c if c.isdigit() or c == "." else "" for c in str(x))
        )
        df_ratings["clean_target_price"] = df_ratings["clean_target_price"].astype(
            float
        )

        df_ratings["pct_increase"] = (
            100
            * (df_ratings["clean_target_price"] - df_ratings["clean_current_price"])
            / df_ratings["clean_current_price"]
        )
        df_ratings["pct_increase"] = df_ratings["pct_increase"].round(2)

        df_ratings["pct_abs"] = np.abs(df_ratings["pct_increase"])
        df_ratings["pct_abs"] = df_ratings["pct_abs"].round(2)

        df_ratings = df_ratings.sort_values("pct_abs", ascending=False)

        df_ratings_top = df_ratings[df_ratings["pct_abs"] > ns_parser.n_threshold][
            [
                "ticker",
                "brokerage",
                "rating",
                "current_price",
                "old_target",
                "new_target",
                "pct_increase",
            ]
        ]

        df_ratings_top["pct_increase"] = df_ratings_top["pct_increase"].apply(
            lambda x: str(x) + " %"
        )

        print(
            df_ratings_top.rename(
                columns={
                    "ticker": "Ticker",
                    "brokerage": "Brokerage",
                    "rating": "Rating",
                    "current_price": "Current Price",
                    "old_target": "Old Target",
                    "new_target": "New Target",
                    "pct_increase": "Percentage Increase",
                }
            ).to_string(index=False)
        )

        print("")
    except Exception as e:
        print(e, "\n")
