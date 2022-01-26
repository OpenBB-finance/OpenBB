""" Yahoo Finance View """
__docformat__ = "numpy"

import os
from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.stocks.dark_pool_shorts import yahoofinance_model
from gamestonk_terminal.rich_config import console


def display_most_shorted(num_stocks: int, export: str):
    """Display most shorted stocks screener. [Source: Yahoo Finance]

    Parameters
    ----------
    num_stocks: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = yahoofinance_model.get_most_shorted().head(num_stocks)
    df.dropna(how="all", axis=1, inplace=True)
    df = df.replace(float("NaN"), "")

    if df.empty:
        console.print("No data found.")
    else:
        print_rich_table(
            df, headers=list(df.columns), show_index=False, title="Most Shorted Stocks"
        )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "shorted",
        df,
    )
