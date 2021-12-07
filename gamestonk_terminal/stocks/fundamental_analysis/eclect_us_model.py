"""Eclect.us model"""
__docformat__ = "numpy"

from collections import OrderedDict
import requests
from colorama import Style

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

    response = requests.get(f"https://api.eclect.us/symbol/{ticker.lower()}?page=1")

    if response.status_code != 200:
        filings_analysis = ""
    else:
        response_dict = response.json()

        rf_highlights = f"{Style.BRIGHT}\n\tRISK FACTORS:{Style.RESET_ALL}\n"
        rf_highlights_list = [
            sentence["sentence"] for sentence in response_dict[0]["rf_highlights"]
        ]
        rf_highlights_list = list(OrderedDict.fromkeys(rf_highlights_list))
        rf_highlights_txt = "\n\n".join(rf_highlights_list)

        daa_highlights = (
            f"{Style.BRIGHT}\n\tDISCUSSION AND ANALYSIS:{Style.RESET_ALL}\n"
        )
        daa_highlights_list = [
            sentence["sentence"] for sentence in response_dict[0]["daa_highlights"]
        ]
        daa_highlights_list = list(OrderedDict.fromkeys(daa_highlights_list))
        daa_highlights += "\n\n".join(daa_highlights_list)

        if rf_highlights_txt:
            filings_analysis = rf_highlights + rf_highlights_txt + "\n" + daa_highlights
        else:
            filings_analysis = daa_highlights

    return filings_analysis
