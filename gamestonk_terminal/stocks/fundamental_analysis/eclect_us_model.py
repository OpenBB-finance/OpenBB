"""Eclect.us model"""
__docformat__ = "numpy"

import requests

# pylint: disable=R1718


def get_filings_analysis(ticker: str) -> str:
    """Save time reading SEC filings with the help of machine learning. [Source: https://eclect.us]

    Parameters
    ----------
    ticker: str
        Ticker to see analysis of filings

    Returns
    -------
    str
        Analysis of filings text
    """
    result = requests.get(f"https://api.eclect.us/symbol/{ticker.lower()}?page=1")

    if result.status_code == 200:
        if result.json():
            return "\n\n".join(
                {
                    sentence["sentence"]
                    for sentence in result.json()[0]["daa_highlights"]
                }
            )

    return ""
