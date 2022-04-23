"""FXEmpire Model"""

import logging
import requests
import pandas as pd

from openbb_terminal.helper_funcs import get_user_agent
from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_forward_rates(to_cur: str, from_cur: str):
    """Gets forward rates from fxempire

    Parameters
    ----------
    to_cur:str
        To currenct
    from_cur:str

    Returns
    -------

    """
    r = requests.get(
        f"https://www.fxempire.com/currencies/{to_cur}-{from_cur}/forward-rates",
        headers={"User-Agent": get_user_agent()},
    )
    if r.status_code == 200:
        forwards = pd.read_html(r.text)[0].set_index("Expiration")
        return forwards

    logger.info("Currency not found.")
    return pd.DataFrame()
