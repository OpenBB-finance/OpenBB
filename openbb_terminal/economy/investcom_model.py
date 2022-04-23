""" Invest.com Model """
__docformat__ = "numpy"

import logging

import pandas as pd
import investpy

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_yieldcurve(country) -> pd.DataFrame:
    """Get country yields [Source: Invest.com]

    Returns
    -------
    pd.DataFrame
        Country yields
    """

    data = investpy.bonds.get_bonds_overview(country)
    
    return data