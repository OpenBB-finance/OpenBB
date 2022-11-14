"""Yahoo Finance model"""
__docformat__ = "numpy"

import logging
from typing import Dict

import yfinance as yf

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_etf_sector_weightings(name: str) -> Dict:
    """Return sector weightings allocation of ETF. [Source: Yahoo Finance]

    Parameters
    ----------
    name: str
        ETF name

    Returns
    -------
    Dict[str, Any]
        Dictionary with sector weightings allocation
    """
    weights = yf.Ticker(name).info
    if "sectorWeightings" in weights:
        sectors = {}
        for item in weights["sectorWeightings"]:
            k = list(item.keys())[0].replace("_", " ").title()
            k = "Real Estate" if k == "Realestate" else k
            v = round(100 * list(item.values())[0], 2)
            sectors[k] = v

        sectors = dict(sorted(sectors.items(), key=lambda x: x[1], reverse=True))
        return sectors

    return dict()


@log_start_end(log=logger)
def get_etf_summary_description(name: str) -> str:
    """Return summary description of ETF. [Source: Yahoo Finance]

    Parameters
    ----------
    name: str
        ETF name

    Returns
    -------
    str
        Summary description of the ETF
    """
    data = yf.Ticker(name).info

    if "longBusinessSummary" in data:
        return data["longBusinessSummary"]

    return ""
