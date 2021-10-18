"""Chartexchange view"""
__docformat__ = "numpy"

import os

from tabulate import tabulate

from gamestonk_terminal.options.chartexchange_model import get_option_history
from gamestonk_terminal.helper_funcs import export_data
import gamestonk_terminal.feature_flags as gtff


def get_option_hist(
    ticker: str, date: str, call: bool, strike: str, export: str, sort: str, des: bool
) -> None:
    """Shows the historical prices for an option [chartexchange]

    Parameters
    ----------
    ticker : str
        Ticker to get historical data from
    date : str
        Date as a string YYYY-MM-DD
    call : bool
        Whether the option is a call or a put
    strike : str
        Strike price for a specific option
    export : str
        What format you want the export in
    sort : str
        Which column data will be sorted by
    des : bool
        Whether data will be sorted descending
    """

    date = date.replace("-", "")
    strike = f"{float(strike):g}"
    history = get_option_history(ticker, date, call, strike)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "history",
        history,
    )

    history = history.sort_values(by=sort, ascending=des)

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                history,
                headers=[x.title() if x != "" else "Date" for x in history.columns],
                tablefmt="fancy_grid",
                showindex=True,
                floatfmt=".2f",
            )
        )
    else:
        print(history.to_string(index=False))

    print("")
