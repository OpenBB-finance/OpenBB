""" Short Interest View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.discovery import shortinterest_model, yahoofinance_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def low_float(limit: int = 5, export: str = "", sheet_name: Optional[str] = None):
    """Prints top N low float stocks from https://www.lowfloat.com

    Parameters
    ----------
    limit: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_low_float = shortinterest_model.get_low_float()
    df_low_float = df_low_float.iloc[1:].head(n=limit)

    print_rich_table(
        df_low_float,
        headers=list(df_low_float.columns),
        show_index=False,
        title="Top Float Stocks",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "lowfloat",
        df_low_float,
        sheet_name,
    )


@log_start_end(log=logger)
def hot_penny_stocks(
    limit: int = 10,
    export: str = "",
    sheet_name: Optional[str] = None,
    source: str = "YahooFinance",
):
    """Prints top N hot penny stocks from https://www.pennystockflow.com
    Parameters
    ----------
    limit: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    source : str
        Where to get the data from. Choose from - YahooFinance or Shortinterest
    """
    if source == "YahooFinance":
        df_penny_stocks = yahoofinance_model.get_hotpenny()
    elif source == "Shortinterest":
        console.print("[red]Data from this source is often not penny stocks[/red]\n")
        df_penny_stocks = shortinterest_model.get_today_hot_penny_stocks()
    else:
        console.print("[red]Invalid source provided[/red]\n")
        return

    if df_penny_stocks.empty:
        console.print("[red]No data found.[/red]")
        return

    print_rich_table(
        df_penny_stocks,
        headers=list(df_penny_stocks.columns) if source != "Shortinterest" else None,
        show_index=False,
        title="Top Penny Stocks",
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "hotpenny",
        df_penny_stocks,
        sheet_name,
    )
