""" Invest.com Model """
__docformat__ = "numpy"

import logging

import pandas as pd
import investpy

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

countries = [
    country.replace(" ", "_") for country in investpy.bonds.get_bond_countries()
]


@log_start_end(log=logger)
def get_yieldcurve(country) -> pd.DataFrame:
    """Get country yield curve [Source: Investing.com]

    Returns
    -------
    pd.DataFrame
        Country yield curve
    """

    data = investpy.bonds.get_bonds_overview(country)

    return data
