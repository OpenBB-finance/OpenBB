""" Financial Modeling Prep Model """
__docformat__ = "numpy"

import logging

import fundamentalanalysis as fa
import pandas as pd

from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_rating(symbol: str) -> pd.DataFrame:
    """Get ratings for a given ticker. [Source: Financial Modeling Prep]

    Parameters
    ----------
    symbol : str
        Stock ticker symbol

    Returns
    -------
    pd.DataFrame
        Rating data
    """
    if cfg.API_KEY_FINANCIALMODELINGPREP:
        try:
            df = fa.rating(symbol, cfg.API_KEY_FINANCIALMODELINGPREP)
        except ValueError as e:
            console.print(f"[red]{e}[/red]\n")
            logger.exception(str(e))
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()
    return df
