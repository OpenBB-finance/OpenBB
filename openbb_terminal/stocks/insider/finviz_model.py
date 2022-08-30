""" Finviz Model """
__docformat__ = "numpy"

import logging
from typing import Dict

import finviz

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_last_insider_activity(symbol: str) -> Dict:
    """Get last insider activity for a given stock ticker. [Source: Finviz]

    Parameters
    ----------
    symbol : str
        Stock ticker symbol

    Dict
        Latest insider trading activity
    """
    return finviz.get_insider(symbol)
