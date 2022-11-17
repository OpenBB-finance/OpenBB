"""Finbrain view"""
__docformat__ = "numpy"

import logging

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.technical_analysis import finbrain_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def technical_summary_report(symbol: str):
    """Print technical summary report provided by FinBrain's API

    Parameters
    ----------
    symbol: str
        Ticker symbol to get the technical summary
    """

    report = finbrain_model.get_technical_summary_report(symbol)
    if report:
        console.print(report.replace(". ", ".\n"))
