import argparse
from typing import List
import requests
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
)


def get_technical_summary_report(ticker: str) -> str:
    """Get technical summary report provided by FinBrain's API

    Parameters
    ----------
    ticker : str
        Ticker to get the technical summary

    Returns
    -------
    str
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


def technical_summary_report(other_args: List[str], ticker: str):
    """Print technical summary report provided by FinBrain's API

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker : str
        Ticker to get the technical summary
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="summary",
        description="""
            Technical summary report provided by FinBrain's API.
            FinBrain Technologies develops deep learning algorithms for financial analysis
            and prediction, which currently serves traders from more than 150 countries
            all around the world. [Source:  https://finbrain.tech]
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        report = get_technical_summary_report(ticker)
        if report:
            print(report.replace(". ", ".\n"))
        print("")

    except Exception as e:
        print(e)
        print("")
