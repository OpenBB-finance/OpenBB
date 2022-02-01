"""ETF Screener view"""
__docformat__ = "numpy"

import logging
import os

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.etf.screener import screener_model
from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.rich_config import console

# pylint:disable=no-member


logger = logging.getLogger(__name__)


@log_start_end(log=logger)
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

    print_rich_table(
        screened_data.head(num_to_show).fillna(""),
        headers=screened_data.columns,
        show_index=True,
        title="Display Screener Output",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "screen",
        screened_data,
    )
