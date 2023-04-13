""" Market Watch View """
__docformat__ = "numpy"

import logging

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.fundamental_analysis import marketwatch_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@log_start_end(log=logger)
def display_sean_seah_warnings(symbol: str, debug: bool = False):
    """Display Sean Seah warnings

    Parameters
    ----------
    symbol : str
        Stock ticker
    debug : bool, optional
        Whether or not to return debug messages.
        Defaults to False.
    """

    financials, warnings, debugged_warnings = marketwatch_model.get_sean_seah_warnings(
        symbol, debug
    )

    if financials.empty:
        console.print(f"No financials found for {symbol}\n")
        return

    print_rich_table(
        financials,
        headers=list(financials.columns),
        title="Sean Seah Warnings",
        show_index=True,
    )

    if not warnings:
        console.print("No warnings found. Good stonk")
        return

    messages = (
        [item for pair in zip(warnings, debugged_warnings) for item in pair]
        if debug
        else warnings
    )

    console.print("Warnings:\n")
    console.print("\n".join(messages))
