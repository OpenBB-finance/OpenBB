"""Eclect.us model"""
__docformat__ = "numpy"

import logging

import requests
import pandas as pd

from openbb_terminal.decorators import log_start_end

# pylint: disable=R1718


logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_filings_analysis(symbol: str) -> pd.DataFrame:
    """Save time reading SEC filings with the help of machine learning. [Source: https://eclect.us]

    Parameters
    ----------
    symbol: str
        Ticker symbol to see analysis of filings

    Returns
    -------
    str
        Analysis of filings text
    """

    response = requests.get(f"https://api.eclect.us/symbol/{symbol.lower()}?page=1")

    if response.status_code != 200:
        return pd.DataFrame()

    response_dict = response.json()

    def resultGroupMapper(g):
        def resultMapper(a):
            return {
                "Good": a["good_or_bad"] == "good",
                "Sentence": a["sentence"],
                "Group": g,
            }

        return resultMapper

    if len(response_dict) == 0:
        return pd.DataFrame()

    risk = pd.DataFrame(
        map(resultGroupMapper("Risk factors"), response_dict[0]["rf_highlights"]),
        columns=["Group", "Good", "Sentence"],
    )
    analysis = pd.DataFrame(
        map(
            resultGroupMapper("Discussion and Analysis"),
            response_dict[0]["daa_highlights"],
        ),
        columns=["Group", "Good", "Sentence"],
    )

    return pd.concat([risk, analysis], ignore_index=True)
