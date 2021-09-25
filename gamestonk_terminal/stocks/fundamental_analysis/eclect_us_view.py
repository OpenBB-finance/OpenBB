"""Eclect.us view"""
__docformat__ = "numpy"

from gamestonk_terminal.stocks.fundamental_analysis import eclect_us_model


def display_analysis(
    ticker: str,
) -> None:
    """Display analysis of SEC filings based on NLP model. [Source: https://eclect.us]

    Parameters
    ----------
    ticker: str
        Ticker to do SEC filings analysis from
    """

    analysis = eclect_us_model.get_filings_analysis(ticker)

    if analysis:
        print(analysis)
    else:
        print("No SEC filings analysis found for this ticker")
    print("")
