"""ETF Screener view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.decorators import log_start_end
from openbb_terminal.etf.screener import screener_model
from openbb_terminal.helper_funcs import export_data, print_rich_table

# pylint:disable=no-member


logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def view_screener(
    preset: str,
    num_to_show: int,
    sortby: str,
    ascend: bool,
    export: str = "",
    sheet_name: Optional[str] = None,
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
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Output format of export

    """
    screened_data = screener_model.etf_screener(preset)

    screened_data = screened_data.sort_values(by=sortby, ascending=ascend)

    print_rich_table(
        screened_data.head(num_to_show).fillna(""),
        headers=list(screened_data.columns),
        show_index=True,
        title="Display Screener Output",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "screen",
        screened_data,
        sheet_name,
    )
