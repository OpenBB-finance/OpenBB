"""Eclect.us model"""
__docformat__ = "numpy"

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
    result = requests.get(f"https://api.eclect.us/symbol/{ticker.lower()}?page=1")

    if result.status_code == 200:
        if result.json():
            rf_highlights = f"{Style.BRIGHT}\n\tRISK FACTORS:{Style.RESET_ALL}\n"
            rf_highlights_txt = "\n\n".join(
                {sentence["sentence"] for sentence in result.json()[0]["rf_highlights"]}
            )

            daa_highlights = (
                f"{Style.BRIGHT}\n\tDISCUSSION AND ANALYSIS:{Style.RESET_ALL}\n"
            )
            daa_highlights += "\n\n".join(
                {
                    sentence["sentence"]
                    for sentence in result.json()[0]["daa_highlights"]
                }
            )

            return (
                rf_highlights + rf_highlights_txt + "\n" + daa_highlights
                if rf_highlights_txt
                else daa_highlights
            )

    return ""
