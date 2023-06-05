"""Finance Database model"""
__docformat__ = "numpy"

import logging
from typing import Dict, List

import financedatabase as fd
import numpy as np
import pandas as pd

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_etfs_by_name(name: str) -> Dict:
    """Return a selection of ETFs based on name filtered by total assets. [Source: Finance Database]

    Parameters
    ----------
    name: str
        Search by name to find ETFs matching the criteria.

    Returns
    -------
    data : Dict[str, Any]
        Dictionary with ETFs that match a certain name
    """
    etfs = fd.ETFs()

    data = etfs.search(name=name, exclude_exchanges=True)
    data = pd.concat([data, etfs.search(index=name, exclude_exchanges=True)])

    # Ensures that data that's missing values is at the bottom of the DataFrame
    data = data.iloc[np.argsort(-data.isnull().mul(-1).sum(axis=1))]

    return data


@log_start_end(log=logger)
def get_etfs_by_description(description: str) -> Dict:
    """Return a selection of ETFs based on description filtered by total assets.
    [Source: Finance Database]

    Parameters
    ----------
    description: str
        Search by description to find ETFs matching the criteria.

    Returns
    -------
    data: Dict[str, Any]
        Dictionary with ETFs that match a certain description
    """
    etfs = fd.ETFs()

    data = etfs.search(summary=description, exclude_exchanges=True)

    # Ensures that data that's missing values is at the bottom of the DataFrame
    data = data.iloc[np.argsort(-data.isnull().mul(-1).sum(axis=1))]

    return data


@log_start_end(log=logger)
def get_etfs_by_category(category: str) -> Dict:
    """Return a selection of ETFs based on category filtered by total assets.
    [Source: Finance Database]

    Parameters
    ----------
    category: str
        Search by category to find ETFs matching the criteria.

    Returns
    -------
    data: Dict[str, Any]
        Dictionary with ETFs that match a certain description
    """
    etfs = fd.ETFs()

    data = etfs.select(category=category, exclude_exchanges=True)

    # Ensures that data that's missing values is at the bottom of the DataFrame
    data = data.iloc[np.argsort(-data.isnull().mul(-1).sum(axis=1))]

    return data


@log_start_end(log=logger)
def get_etfs_categories() -> List[str]:
    """Return a selection of ETF categories. [Source: Finance Database]

    Returns
    -------
    List[str]
        ETF categories
    """
    etfs = fd.ETFs()

    return etfs.options("category")
