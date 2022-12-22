"""Factors view"""
__docformat__ = "numpy"

import logging

from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.quantitative_analysis.factors_model import capm_information

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def capm_view(symbol: str) -> None:
    """Displays information for the CAPM model.

    Parameters
    ----------
    symbol : str
        Selected ticker symbol
    """
    beta, sy = capm_information(symbol)
    console.print(f"Beta:\t\t\t{beta:.2f}")
    console.print(f"Systematic Risk:\t{sy*100:.2f}%")
    console.print(f"Unsystematic Risk:\t{(1-sy)*100:.2f}%\n")
