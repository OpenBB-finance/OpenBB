"""Finbrain model"""
__docformat__ = "numpy"

import requests


def get_technical_summary_report(ticker: str) -> str:
    """Get technical summary report provided by FinBrain's API

    Parameters
    ----------
    ticker : str
        Ticker to get the technical summary

    Returns
    -------
    report:str
        technical summary report
    """
    result = requests.get(f"https://api.finbrain.tech/v0/technicalSummary/{ticker}")
    report = ""
    if result.status_code == 200:
        if "technicalSummary" in result.json():
            report = result.json()["technicalSummary"]
        else:
            print("Unexpected data format from FinBrain API")
    else:
        print("Request error in retrieving sentiment from FinBrain API")

    return report
