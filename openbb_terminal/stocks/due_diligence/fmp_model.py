""" Financial Modeling Prep Model """
__docformat__ = "numpy"

import logging

import fundamentalanalysis as fa
import pandas as pd

from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
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
            l_recoms = [col for col in df.columns if "Recommendation" in col]
            l_recoms_show = [
                recom.replace("rating", "")
                .replace("Details", "")
                .replace("Recommendation", "")
                for recom in l_recoms
            ]
            l_recoms_show[0] = "Rating"
            df = df[l_recoms]
            df.columns = l_recoms_show
        except ValueError as e:
            console.print(f"[red]{e}[/red]\n")
            logger.exception(str(e))
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()
    return df
