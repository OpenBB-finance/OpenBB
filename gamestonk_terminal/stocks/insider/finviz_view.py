""" FinViz View """
__docformat__ = "numpy"

import argparse
from typing import List
import finviz
import pandas as pd
from gamestonk_terminal.helper_funcs import (
    check_positive,
    parse_known_args_and_warn,
)


def last_insider_activity(other_args: List[str], ticker: str):
    """Display insider activity for a given stock ticker

    Parameters
    ----------
    other_args : List[str]
        argparse other args - ["-n", "10"]
    ticker : str
        Stock ticker
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="insider",
        description="""
            Prints information about inside traders. The following fields are expected: Date, Relationship,
            Transaction, #Shares, Cost, Value ($), #Shares Total, Insider Trading, SEC Form 4. [Source: Finviz]
        """,
    )

    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n_num",
        type=check_positive,
        default=10,
        help="number of latest inside traders.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        d_finviz_insider = finviz.get_insider(ticker)
        df_fa = pd.DataFrame.from_dict(d_finviz_insider)
        df_fa.set_index("Date", inplace=True)
        df_fa = df_fa[
            [
                "Relationship",
                "Transaction",
                "#Shares",
                "Cost",
                "Value ($)",
                "#Shares Total",
                "Insider Trading",
                "SEC Form 4",
            ]
        ]
        print(df_fa.head(n=ns_parser.n_num))

        print("")

    except Exception as e:
        print(e)
        print("")
        return
