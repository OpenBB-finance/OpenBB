"""Chartexchange view"""
__docformat__ = "numpy"

import logging
import os

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.options import chartexchange_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_raw(
    ticker: str, date: str, call: bool, price: str, num: int = 20, export: str = ""
) -> None:
    """Return raw stock data[chartexchange]

    Parameters
    ----------
    ticker : str
        Ticker for the given option
    date : str
        Date of expiration for the option
    call : bool
        Whether the underlying asset should be a call or a put
    price : float
        The strike of the expiration
    num : int
        Number of rows to show
    export : str
        Export data as CSV, JSON, XLSX
    """

    df = chartexchange_model.get_option_history(ticker, date, call, price)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "hist",
        df,
    )

    print_rich_table(
        df.head(num),
        headers=list(df.columns),
        show_index=True,
        title=f"{ticker.upper()} raw data",
    )

    console.print()
