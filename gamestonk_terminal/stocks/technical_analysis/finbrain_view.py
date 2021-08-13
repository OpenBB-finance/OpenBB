"""Finbrain view"""
__docformat__ = "numpy"

from gamestonk_terminal.stocks.technical_analysis import finbrain_model


def technical_summary_report(ticker: str):
    """Print technical summary report provided by FinBrain's API

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker : str
        Ticker to get the technical summary
    """

    report = finbrain_model.get_technical_summary_report(ticker)
    if report:
        print(report.replace(". ", ".\n"))
    print("")
