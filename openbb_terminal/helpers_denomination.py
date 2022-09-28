"""Denomination Helper functions"""

from typing import Literal, Tuple
import pandas as pd

DENOMINATION = Literal["Trillions", "Billions", "Millions", "Thousands", "Units", ""]


def transform(
    df: pd.DataFrame,
    sourceDenomination: DENOMINATION = "Units",
    targetDenomination: DENOMINATION = None,
    maxValue: float = None,
) -> Tuple[pd.DataFrame, DENOMINATION]:
    """Applies denomination to data frame (i.e. divides by it).

    Args:
        df (pd.DataFrame): Source data frame
        sourceDenomination (DENOMINATION, optional): Current denomination. Defaults to Units.
        targetDenomination (DENOMINATION, optional): Desired denomination. Defaults to None, meaning we will find it.
        maxValue (float, optional): Max value of the data frame. Defaults to None, meaning df.max().max() will be used.

    Returns:
        Tuple[pd.DataFrame, DENOMINATION]: Pair of transformed data frame and applied denomination.
    """
    if targetDenomination is not None:
        return (
            df
            * (
                get_denominations()[targetDenomination]
                / get_denominations()[sourceDenomination]
            ),
            targetDenomination,
        )

    if maxValue is None:
        maxValue = df.max().max()

    foundTargetDenomination = get_denomination(maxValue)

    return (
        df * (foundTargetDenomination[1] / get_denominations()[sourceDenomination]),
        foundTargetDenomination[0],
    )


def get_denominations() -> dict[DENOMINATION, float]:
    """Gets all supported denominations and their lower bound value

    Returns:
        dict[DENOMINATION, int]: All supported denominations and their lower bound value
    """
    return {
        "Trillions": 1_000_000_000_000,
        "Billions": 1_000_000_000,
        "Millions": 1_000_000,
        "Thousands": 1_000,
        "Units": 1,
    }


def get_denomination(value: float) -> Tuple[DENOMINATION, float]:
    """Gets denomination that fits the supplied value.
       If no denomination found, 'Units' is returned.

    Args:
        value (int): Value

    Returns:
        Tuple[DENOMINATION, int]:Denomination that fits the supplied value
    """
    return next((x for x in get_denominations().items() if value > x[1]), ("Units", 1))
