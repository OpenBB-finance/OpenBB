""" Short Interest View """
__docformat__ = "numpy"

import logging
import os

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.stocks.discovery import shortinterest_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def low_float(limit: int = 5, export: str = ""):
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
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "lowfloat",
        df_low_float,
    )


@log_start_end(log=logger)
def hot_penny_stocks(limit: int = 5, export: str = ""):
    """Prints top N hot penny stocks from https://www.pennystockflow.com

    Parameters
    ----------
    limit: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_penny_stocks = shortinterest_model.get_today_hot_penny_stocks()

    print_rich_table(
        df_penny_stocks.head(limit),
        headers=list(df_penny_stocks.columns),
        show_index=True,
        title="Top Penny Stocks",
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "hotpenny",
        df_penny_stocks,
    )
