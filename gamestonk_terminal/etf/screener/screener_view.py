"""ETF Screener view"""
__docformat__ = "numpy"

import os

from tabulate import tabulate

from gamestonk_terminal.etf.screener import screener_model
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal import feature_flags as gtff

# pylint:disable=no-member


def view_screener(
    preset: str, num_to_show: int, sortby: str, ascend: bool, export: str = ""
):
    """Display screener output

    Parameters
    ----------
    preset: str
        Preset to use
    num_to_show: int
        Number of etfs to show
    sortby: str
        Column to sort by
    ascend: bool
        Ascend when sorted
    export: str
        Output format of export

    """
    screened_data = screener_model.etf_screener(preset)

    screened_data = screened_data.sort_values(by=sortby, ascending=ascend)

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                screened_data.head(num_to_show).fillna(""),
                tablefmt="fancy_grid",
                headers=screened_data.columns,
                showindex=True,
                disable_numparse=True,
            )
        )
    else:
        print(screened_data.head(num_to_show).fillna("").to_string())
    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "screen",
        screened_data,
    )
