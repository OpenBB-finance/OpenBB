""" Market Watch View """
__docformat__ = "numpy"

from tabulate import tabulate
from gamestonk_terminal.stocks.due_diligence import marketwatch_model

# pylint: disable=too-many-branches


def sec_filings(ticker: str, num: int):
    """Display SEC filings for a given stock ticker. [Source: Market Watch]

    Parameters
    ----------
    ticker : str
        Stock ticker
    num : int
        Number of ratings to display
    """
    df_financials = marketwatch_model.get_sec_filings(ticker)
    print(
        tabulate(
            df_financials.head(num),
            headers=df_financials.columns,
            floatfmt=".2f",
            showindex=True,
            tablefmt="fancy_grid",
        )
    )
    print("")
