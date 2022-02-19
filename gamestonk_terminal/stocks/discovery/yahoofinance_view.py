""" Yahoo Finance View """
__docformat__ = "numpy"

import logging
import os

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.discovery import yahoofinance_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_gainers(num_stocks: int, export: str) -> None:
    """Display gainers. [Source: Yahoo Finance]

    Parameters
    ----------
    num_stocks: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df_gainers = yahoofinance_model.get_gainers()
    df_gainers.dropna(how="all", axis=1, inplace=True)
    df_gainers = df_gainers.replace(float("NaN"), "")

    if df_gainers.empty:
        console.print("No gainers found.")
    else:
        print_rich_table(
            df_gainers.head(num_stocks),
            headers=list(df_gainers.columns),
            show_index=False,
            title="Gainers",
        )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "gainers",
        df_gainers,
    )


@log_start_end(log=logger)
def display_losers(num_stocks: int, export: str) -> None:
    """Display losers. [Source: Yahoo Finance]

    Parameters
    ----------
    num_stocks: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df_losers = yahoofinance_model.get_losers()
    df_losers.dropna(how="all", axis=1, inplace=True)
    df_losers = df_losers.replace(float("NaN"), "")

    if df_losers.empty:
        console.print("No losers found.")
    else:
        print_rich_table(
            df_losers.head(num_stocks),
            headers=list(df_losers.columns),
            show_index=False,
            title="Display Losers",
        )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "losers",
        df_losers,
    )


@log_start_end(log=logger)
def display_ugs(num_stocks: int, export: str) -> None:
    """Display most undervalued growth stock. [Source: Yahoo Finance]

    Parameters
    ----------
    num_stocks: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = yahoofinance_model.get_ugs()
    df.dropna(how="all", axis=1, inplace=True)
    df = df.replace(float("NaN"), "")

    if df.empty:
        console.print("No data found.")
    else:
        print_rich_table(
            df.head(num_stocks),
            headers=list(df.columns),
            show_index=False,
            title="Undervalued Growth Stocks",
        )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ugs",
        df,
    )


@log_start_end(log=logger)
def display_gtech(num_stocks: int, export: str) -> None:
    """Display growth technology stocks. [Source: Yahoo Finance]

    Parameters
    ----------
    num_stocks: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = yahoofinance_model.get_gtech()
    df.dropna(how="all", axis=1, inplace=True)
    df = df.replace(float("NaN"), "")

    if df.empty:
        console.print("No data found.")
    else:
        print_rich_table(
            df.head(num_stocks),
            headers=list(df.columns),
            show_index=False,
            title="Growth Tech Stocks",
        )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "gtech",
        df,
    )


@log_start_end(log=logger)
def display_active(num_stocks: int, export: str) -> None:
    """Display most active stocks. [Source: Yahoo Finance]

    Parameters
    ----------
    num_stocks: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = yahoofinance_model.get_active()
    df.dropna(how="all", axis=1, inplace=True)
    df = df.replace(float("NaN"), "")

    if df.empty:
        console.print("No data found.")
    else:
        print_rich_table(
            df.head(num_stocks),
            headers=list(df.columns),
            show_index=False,
            title="Most Active Stocks",
        )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "active",
        df,
    )


@log_start_end(log=logger)
def display_ulc(num_stocks: int, export: str) -> None:
    """Display potentially undervalued large cap stocks. [Source: Yahoo Finance]

    Parameters
    ----------
    num_stocks: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = yahoofinance_model.get_ulc()
    df.dropna(how="all", axis=1, inplace=True)
    df = df.replace(float("NaN"), "")

    if df.empty:
        console.print("No data found.")
    else:
        print_rich_table(
            df.head(num_stocks).dropna(),
            headers=list(df.columns),
            show_index=False,
            title="Undervalued Large Cap Stocks",
        )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ulc",
        df,
    )


@log_start_end(log=logger)
def display_asc(num_stocks: int, export: str) -> None:
    """Display small cap stocks with earnings growth rates better than 25%. [Source: Yahoo Finance]

    Parameters
    ----------
    num_stocks: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = yahoofinance_model.get_asc()
    df.dropna(how="all", axis=1, inplace=True)
    df = df.replace(float("NaN"), "")

    if df.empty:
        console.print("No data found.")
    else:
        print_rich_table(
            df.head(num_stocks).dropna(),
            headers=list(df.columns),
            show_index=False,
            title="High Growth Small Caps",
        )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "asc",
        df,
    )
