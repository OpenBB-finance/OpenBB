""" Investing.com Model """
__docformat__ = "numpy"

import logging
import argparse

import pandas as pd
import investpy

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import log_and_raise

logger = logging.getLogger(__name__)

COUNTRIES = investpy.bonds.get_bond_countries()


def check_correct_country(country):
    """Argparse type to check that correct country is inserted"""
    if country not in investpy.bonds.get_bond_countries():
        log_and_raise(
            argparse.ArgumentTypeError(
                f"{country} is an invalid country. Choose from {', '.join(investpy.bonds.get_bond_countries())}"
            )
        )
    return country


@log_start_end(log=logger)
def get_yieldcurve(country) -> pd.DataFrame:
    """Get country yield curve [Source: Investing.com]

    Returns
    -------
    pd.DataFrame
        Country yield curve
    """

    data = investpy.bonds.get_bonds_overview(country)
    data.drop(columns=data.columns[0], axis=1, inplace=True)
    data.rename(
        columns={
            "name": "Tenor",
            "last": "Current",
            "last_close": "Previous",
            "high": "High",
            "low": "Low",
            "change": "Change",
            "change_percentage": "% Change",
        },
        inplace=True,
    )
    return data
