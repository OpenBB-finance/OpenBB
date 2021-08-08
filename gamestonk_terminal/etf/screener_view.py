"""ETF Screener view"""
__docformat__ = "numpy"

import os

from tabulate import tabulate

from gamestonk_terminal.etf import screener_model
from gamestonk_terminal.helper_funcs import export_data

# pylint:disable=no-member


def view_screener(num_to_show: int, preset: str, export: str):
    """Display screener output

    Parameters
    ----------
    num_to_show: int
        Number of etfs to show
    preset: str
        Preset to use
    export: str
        Output format of export

    """
    screened_data = screener_model.etf_screener(preset)
    if screened_data.shape[0] > int(num_to_show):
        screened_data = screened_data.sample(num_to_show)
    print(
        tabulate(
            screened_data.fillna(""),
            tablefmt="fancy_grid",
            headers=screened_data.columns,
            showindex=True,
            disable_numparse=True,
        )
    )
    print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "screener",
        screened_data,
    )
