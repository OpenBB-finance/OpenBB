"""Eclect.us view"""
__docformat__ = "numpy"

import logging

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.fundamental_analysis import eclect_us_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_analysis(
    ticker: str,
) -> None:
    """Display analysis of SEC filings based on NLP model. [Source: https://eclect.us]

    Parameters
    ----------
    ticker: str
        Ticker to do SEC filings analysis from
    """

    analysis = eclect_us_model.get_filings_analysis(ticker)

    if analysis:
        console.print(analysis)
    else:
        console.print("Filings not found from eclect.us")
    console.print("")
