"""Finance Database model"""
__docformat__ = "numpy"

import logging
from typing import Dict, List

import financedatabase as fd

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
    data = fd.select_etfs()
    data = fd.search_products(data, query=name, search="long_name")

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
    data = fd.select_etfs()
    data = fd.search_products(data, query=description, search="summary")

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
    data = fd.select_etfs(category=category)

    return data


@log_start_end(log=logger)
def get_etfs_categories() -> List[str]:
    """Return a selection of ETF categories. [Source: Finance Database]

    Returns
    -------
    List[str]
        ETF categories
    """

    return fd.show_options("etfs")
