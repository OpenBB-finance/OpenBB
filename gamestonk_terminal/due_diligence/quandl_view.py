""" Quandl View """
__docformat__ = "numpy"

import argparse
from typing import List
import quandl
from matplotlib import pyplot as plt
import matplotlib.ticker
import pandas as pd
from gamestonk_terminal.helper_funcs import (
    check_positive,
    long_number_format,
    parse_known_args_and_warn,
)
from gamestonk_terminal import config_terminal as cfg


def short_interest(other_args: List[str], ticker: str, start: str):
    """Display short interest for a given ticker and a given start date

    Parameters
    ----------
    other_args : List[str]
        argparse other args - ["-d", "10"]
    ticker : str
        Stock ticker
    start : str
        Start date of the stock data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="short",
        description="""
            Plots the short interest of a stock. This corresponds to the number of shares that
            have been sold short but have not yet been covered or closed out. Either NASDAQ or NYSE [Source: Quandl]
        """,
    )
    parser.add_argument(
        "-n",
        "--nyse",
        action="store_true",
        default=False,
        dest="b_nyse",
        help="data from NYSE flag.",
    )
    parser.add_argument(
        "-d",
        "--days",
        action="store",
        dest="n_days",
        type=check_positive,
        default=10,
        help="number of latest days to print data.",
    )
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        quandl.ApiConfig.api_key = cfg.API_KEY_QUANDL

        if ns_parser.b_nyse:
            df_short_interest = quandl.get(f"FINRA/FNYX_{ticker}")
        else:
            df_short_interest = quandl.get(f"FINRA/FNSQ_{ticker}")

        df_short_interest = df_short_interest[start:]  # type: ignore
        df_short_interest.columns = [
            "".join(
                " " + char if char.isupper() else char.strip() for char in idx
            ).strip()
            for idx in df_short_interest.columns.tolist()
        ]
        df_short_interest["% of Volume Shorted"] = round(
            100 * df_short_interest["Short Volume"] / df_short_interest["Total Volume"],
            2,
        )

        _, ax = plt.subplots()
        ax.bar(
            df_short_interest.index, df_short_interest["Short Volume"], 0.3, color="r"
        )
        ax.bar(
            df_short_interest.index,
            df_short_interest["Total Volume"] - df_short_interest["Short Volume"],
            0.3,
            bottom=df_short_interest["Short Volume"],
            color="b",
        )
        ax.set_ylabel("Shares")
        ax.set_xlabel("Date")

        if start:
            ax.set_title(
                f"{('NASDAQ', 'NYSE')[ns_parser.b_nyse]} Short Interest on {ticker} from {start.date()}"  # type: ignore
            )
        else:
            ax.set_title(
                f"{('NASDAQ', 'NYSE')[ns_parser.b_nyse]} Short Interest on {ticker}"
            )

        ax.legend(labels=["Short Volume", "Total Volume"])
        ax.tick_params(axis="both", which="major")
        ax.yaxis.set_major_formatter(matplotlib.ticker.EngFormatter())
        ax_twin = ax.twinx()
        ax_twin.tick_params(axis="y", colors="green")
        ax_twin.set_ylabel("Percentage of Volume Shorted", color="green")
        ax_twin.plot(
            df_short_interest.index,
            df_short_interest["% of Volume Shorted"],
            color="green",
        )
        ax_twin.tick_params(axis="y", which="major", color="green")
        ax_twin.yaxis.set_major_formatter(
            matplotlib.ticker.FormatStrFormatter("%.0f%%")
        )
        plt.xlim([df_short_interest.index[0], df_short_interest.index[-1]])

        df_short_interest["% of Volume Shorted"] = df_short_interest[
            "% of Volume Shorted"
        ].apply(lambda x: f"{x/100:.2%}")
        df_short_interest = df_short_interest.applymap(
            lambda x: long_number_format(x)
        ).sort_index(ascending=False)

        pd.set_option("display.max_colwidth", 70)
        print(df_short_interest.head(n=ns_parser.n_days).to_string())
        print("")
        plt.show()

    except Exception as e:
        print(e, "\n")
        return
