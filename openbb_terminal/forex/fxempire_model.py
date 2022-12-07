"""FXEmpire Model"""

import logging
import requests
import pandas as pd

from openbb_terminal.helper_funcs import get_user_agent
from openbb_terminal.decorators import log_start_end
from openbb_terminal.core.exceptions.exceptions import OpenBBUserError

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_forward_rates(to_symbol: str = "USD", from_symbol: str = "EUR") -> pd.DataFrame:
    """Gets forward rates from fxempire

    Parameters
    ----------
    to_symbol: str
        To currency
    from_symbol: str
        From currency

    Returns
    -------
    df: pd.DataFrame
        Dataframe containing forward rates

    """
    r = requests.get(
        f"https://www.fxempire.com/currencies/{from_symbol}-{to_symbol}/forward-rates",
        headers={"User-Agent": get_user_agent()},
    )
    if r.status_code == 200:
        forwards = pd.read_html(r.text)[0].set_index("Expiration")
        return forwards

    logger.info("Currency not found.")
    raise OpenBBUserError(f"Forward rates not found for '{to_symbol}/{from_symbol}'.")
