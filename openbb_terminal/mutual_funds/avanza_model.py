"""Avanza Model"""
__docformat__ = "numpy"

# pylint: disable=E1101

import logging
import os

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_data(isin: str) -> dict:
    """Gets the data from Avanza

    Parameters
    ----------
    isin: str
        ISIN of the fund

    Returns
    -------
    dict
        Fund data
    """
    ava_fund = pd.read_csv(
        os.path.join("openbb_terminal", "mutual_funds", "avanza_fund_ID.csv"),
        index_col=0,
    )
    fund_id = ava_fund.loc[ava_fund["ISIN"] == isin]["ID"].tolist()[0]
    url = f"https://www.avanza.se/_api/fund-guide/guide/{fund_id}"
    response = request(url)
    fund_data = response.json()
    return fund_data
