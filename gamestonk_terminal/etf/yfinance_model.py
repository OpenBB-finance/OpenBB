"""Yahoo Finance model"""
__docformat__ = "numpy"

from typing import Dict
import yfinance as yf


def get_etf_sector_weightings(name: str) -> Dict:
    """Return sector weightings allocation of ETF. [Source: Yahoo Finance]

    Parameters
    ----------
    name: str
        ETF name

    Returns
    ----------
    Dict
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


def get_etf_summary_description(name: str) -> str:
    """Return summary description of ETF. [Source: Yahoo Finance]

    Parameters
    ----------
    name: str
        ETF name

    Returns
    ----------
    str
        Summary description of the ETF
    """
    data = yf.Ticker(name).info

    if "longBusinessSummary" in data:
        return data["longBusinessSummary"]

    return ""
