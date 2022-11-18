"""Tools Model"""
__docformat__ = "numpy"

import logging
from typing import Tuple

import pandas as pd

from openbb_terminal.cryptocurrency.tools.tools_helpers import (
    calculate_hold_value,
    calculate_pool_value,
)
from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def calculate_apy(apr: float, compounding_times: int) -> Tuple[pd.DataFrame, str]:
    """Converts apr into apy

    Parameters
    ----------
    apr: float
        value in percentage
    compounding_times: int
        number of compounded periods in a year

    Returns
    -------
    Tuple[pd.DataFrame, str]
        - pd.DataFrame: dataframe with results
        - str: narrative version of results
    """
    apy = (pow((1 + (apr / 100) / compounding_times), compounding_times) - 1) * 100
    apy_str = f"""
An APR of {apr}% compounded {compounding_times} times per year equals to an APY of {round(apy,3)}%
    """
    df = pd.DataFrame(
        {
            "Metric": [
                "APR",
                "Compounding Times",
                "APY",
            ],
            "Value": [
                f"{apr}%",
                compounding_times,
                f"{round(apy, 3)}%",
            ],
        }
    )
    return df, apy_str


@log_start_end(log=logger)
def calculate_il(
    price_changeA: float,
    price_changeB: float,
    proportion: float,
    initial_pool_value: float,
) -> Tuple[pd.DataFrame, str]:
    """Calculates Impermanent Loss in a custom liquidity pool

    Parameters
    ----------
    price_changeA: float
        price change of crypto A in percentage
    price_changeB: float
        price change of crypto B in percentage
    proportion: float
        percentage of first token in pool
    initial_pool_value: float
        initial value that pool contains

    Returns
    -------
    Tuple[pd.DataFrame, str]
        - pd.DataFrame: dataframe with results
        - str: narrative version of results
    """
    pool_value = calculate_pool_value(price_changeA, price_changeB, proportion)
    hold_value = calculate_hold_value(price_changeA, price_changeB, proportion)
    il = abs(((pool_value / hold_value) - 1) * 100)
    hold_value = hold_value * initial_pool_value
    pool_value = pool_value * initial_pool_value
    il_str = f"""
Ignoring fees/rewards and only accounting for impermanent loss:

A change of {price_changeA}% in token A and {price_changeB}% in token B in
a pool with a proportion of {proportion}/{100-proportion} and with an initial
value of ${initial_pool_value} would result in an impermant loss of {round(il,2)}%
If you just hold the tokens you would have ${round(hold_value,2)} whereas
in the pool you would have ${round(pool_value,2)}
    """
    df = pd.DataFrame(
        {
            "Metric": [
                "Price Change Token A",
                "Price Change Token B",
                "Initial Pool Value",
                "Proportion",
                "Impermanent Loss",
                "Hold Value",
                "Pool Value",
            ],
            "Value": [
                f"{price_changeA}%",
                f"{price_changeB}%",
                f"${initial_pool_value}",
                f"{proportion}/{100-proportion}",
                f"{round(il,2)}%",
                f"${round(hold_value,2)}",
                f"${round(pool_value,2)}",
            ],
        }
    )
    return df, il_str
