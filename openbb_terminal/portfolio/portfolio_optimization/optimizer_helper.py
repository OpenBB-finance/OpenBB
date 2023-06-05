"""Optimization helpers"""
__docformat__ = "numpy"

from typing import Any, Optional

import pandas as pd

from openbb_terminal.portfolio.portfolio_optimization.statics import (
    OPTIMIZATION_PARAMETERS,
    RISK_CHOICES,
    TERMINAL_TEMPLATE_MAP,
)
from openbb_terminal.rich_config import console


def dict_to_df(d: dict) -> pd.DataFrame:
    """Convert a dictionary to a DataFrame

    Parameters
    ----------
    d : dict
        Dictionary to convert

    Returns
    -------
    pd.DataFrame
        DataFrame with dictionary
    """

    if not d:
        return pd.DataFrame()

    df = pd.DataFrame.from_dict(data=d, orient="index", columns=["value"])

    return df


def validate_risk_measure(risk_measure: str, warning: bool = True) -> str:
    """Check that the risk measure selected is valid

    Parameters
    ----------
    risk_measure : str
        Risk measure to check

    Returns
    -------
    str
        Validated risk measure
    """
    if risk_measure.lower() in RISK_CHOICES:
        return RISK_CHOICES[risk_measure.lower()]
    if warning:
        console.print("[yellow]Risk measure not found. Using 'MV'.[/yellow]")
    return "MV"


def get_kwarg(key: str, kwargs: dict, default: Optional[Any] = None) -> Any:
    """Get a key from kwargs

    If key is in kwargs, returns it.
    Otherwise, if default provided, returns it.
    Otherwise, if key is in OPTIMIZATION_PARAMETERS, returns it.

    Parameters
    ----------
    key : str
        The key to be searched
    kwargs : dict
        The kwargs to be searched
    default : Any
        The default value to be returned if the key is not found

    Returns
    -------
    Any
        The value of the key if it exists, else None
    """

    if key in kwargs:
        return kwargs[key]

    if default:
        return default

    # TODO: Remove this line when mapping between template and terminal is not needed
    template_key = TERMINAL_TEMPLATE_MAP.get(key, key)

    PARAMETER = OPTIMIZATION_PARAMETERS.get(template_key)
    if PARAMETER is None:
        return default
    return PARAMETER.default
