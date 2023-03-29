"""AlphaQuery View"""
__docforma__ = "numpy"

import logging
import os
from datetime import datetime, timedelta
from typing import Optional, Union

from openbb_terminal import OpenBBFigure
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.options import alphaquery_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_put_call_ratio(
    symbol: str,
    window: int = 30,
    start_date: str = (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
    export: str = "",
    sheet_name: Optional[str] = None,
    external_axes: bool = False,
) -> Union[OpenBBFigure, None]:
    """Display put call ratio [Source: AlphaQuery.com]

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    window : int, optional
        Window length to look at, by default 30
    start_date : str, optional
        Starting date for data, by default (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d")
    export : str, optional
        Format to export data, by default ""
    external_axes : bool, optional
        Whether to return the figure object or not, by default False
    """
    pcr = alphaquery_model.get_put_call_ratio(symbol, window, start_date)
    if pcr.empty:
        return console.print("No data found.\n")

    fig = OpenBBFigure().set_title(f"Put Call Ratio for {symbol.upper()}")
    fig.add_scatter(x=pcr.index, y=pcr["PCR"], name="Put Call Ratio")

    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "pcr", pcr, sheet_name, fig
    )

    return fig.show(external=external_axes)
