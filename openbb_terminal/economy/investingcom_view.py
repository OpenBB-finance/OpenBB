""" Investing.com View """
__docformat__ = "numpy"

import logging
import os

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.economy import investingcom_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_yieldcurve(country: str, export: str):
    """Display yield curve. [Source: Investing.com]

    Parameters
    ----------
    country: str
        Country to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    country = country.replace("_", " ")
    df = investingcom_model.get_yieldcurve(country)
    df = df.replace(float("NaN"), "")

    if df.empty:
        console.print("No data found.")
    else:
        print_rich_table(
            df, headers=list(df.columns), show_index=False, title="Country yield curve"
        )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "yieldcurve",
        df,
    )
