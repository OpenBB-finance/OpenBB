"""Polygon view"""
__docformat__ = "numpy"
import logging
import os

from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import (
    export_data,
    lambda_long_number_format,
    print_rich_table,
)
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.fundamental_analysis import polygon_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_POLYGON_KEY"])
def display_fundamentals(
    ticker: str,
    financial: str,
    limit: int = 10,
    quarterly: bool = False,
    export: str = "",
):
    """Display tickers balance sheet or income statement

    Parameters
    ----------
    ticker: str
        Stock ticker
    financial:str
        Either balance or income
    limit: int
        Number of results to show
    quarterly:bool
        Flag to get quarterly reports
    export: str
        Format to export data
    """
    if financial == "balance":
        fundamentals = polygon_model.get_financials(ticker, financial, quarterly)
        title_str = "Balance Sheet"
    elif financial == "income":
        fundamentals = polygon_model.get_financials(ticker, financial, quarterly)
        title_str = "Income Statement"

    if fundamentals.empty:
        # The empty data frame error handling done in model
        return

    # Snake case to english
    fundamentals.index = fundamentals.index.to_series().apply(
        lambda x: x.replace("_", " ").title()
    )

    # Readable numbers
    fundamentals = fundamentals.applymap(lambda_long_number_format).fillna("-")
    print_rich_table(
        fundamentals.iloc[:, :limit].applymap(lambda x: "-" if x == "nan" else x),
        show_index=True,
        title=f"{ticker} {title_str}",
    )
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), financial, fundamentals
    )
    console.print()
