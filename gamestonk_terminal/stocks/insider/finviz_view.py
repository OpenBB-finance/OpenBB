""" Finviz View """
__docformat__ = "numpy"

import logging
import os

import pandas as pd

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.insider import finviz_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def last_insider_activity(ticker: str, num: int, export: str):
    """Display insider activity for a given stock ticker. [Source: Finviz]

    Parameters
    ----------
    ticker : str
        Stock ticker
    num : int
        Number of latest insider activity to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    d_finviz_insider = finviz_model.get_last_insider_activity(ticker)
    df = pd.DataFrame.from_dict(d_finviz_insider)
    if df.empty:
        console.print(f"[red]No insider information found for {ticker}.\n[/red]")
        return
    df.set_index("Date", inplace=True)
    df = df[
        [
            "Relationship",
            "Transaction",
            "#Shares",
            "Cost",
            "Value ($)",
            "#Shares Total",
            "Insider Trading",
            "SEC Form 4",
        ]
    ]

    print_rich_table(
        df.head(num),
        headers=list(df.columns),
        show_index=True,
        title="Insider Activity",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "lins",
        df,
    )
