""" Yahoo Finance View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.stocks.discovery import yahoofinance_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_gainers(
    limit: int = 5, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Display gainers. [Source: Yahoo Finance]

    Parameters
    ----------
    limit: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df_gainers = yahoofinance_model.get_gainers()

    if not df_gainers.empty:
        print_rich_table(
            df_gainers,
            headers=list(df_gainers.columns),
            show_index=False,
            title="Gainers",
            export=bool(export),
            limit=limit,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "gainers",
        df_gainers,
        sheet_name,
    )


@log_start_end(log=logger)
def display_losers(
    limit: int = 5, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Display losers. [Source: Yahoo Finance]

    Parameters
    ----------
    limit: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df_losers = yahoofinance_model.get_losers()

    if not df_losers.empty:
        print_rich_table(
            df_losers,
            headers=list(df_losers.columns),
            show_index=False,
            title="Display Losers",
            export=bool(export),
            limit=limit,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "losers",
        df_losers,
        sheet_name,
    )


@log_start_end(log=logger)
def display_ugs(
    limit: int = 5, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Display most undervalued growth stock. [Source: Yahoo Finance]

    Parameters
    ----------
    limit: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = yahoofinance_model.get_ugs()
    if not df.empty:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Undervalued Growth Stocks",
            export=bool(export),
            limit=limit,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ugs",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_gtech(
    limit: int = 5, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Display growth technology stocks. [Source: Yahoo Finance]

    Parameters
    ----------
    limit: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = yahoofinance_model.get_gtech()

    if not df.empty:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Growth Tech Stocks",
            export=bool(export),
            limit=limit,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "gtech",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_active(
    limit: int = 5, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Display most active stocks. [Source: Yahoo Finance]

    Parameters
    ----------
    limit: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = yahoofinance_model.get_active()

    if not df.empty:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Most Active Stocks",
            export=bool(export),
            limit=limit,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "active",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_ulc(
    limit: int = 5, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Display potentially undervalued large cap stocks. [Source: Yahoo Finance]

    Parameters
    ----------
    limit: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = yahoofinance_model.get_ulc()

    if not df.empty:
        print_rich_table(
            df.dropna(),
            headers=list(df.columns),
            show_index=False,
            title="Undervalued Large Cap Stocks",
            export=bool(export),
            limit=limit,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ulc",
        df,
        sheet_name,
    )


@log_start_end(log=logger)
def display_asc(
    limit: int = 5, export: str = "", sheet_name: Optional[str] = None
) -> None:
    """Display small cap stocks with earnings growth rates better than 25%. [Source: Yahoo Finance]

    Parameters
    ----------
    limit: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = yahoofinance_model.get_asc()

    if not df.empty:
        print_rich_table(
            df.dropna(),
            headers=list(df.columns),
            show_index=False,
            title="High Growth Small Caps",
            export=bool(export),
            limit=limit,
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "asc",
        df,
        sheet_name,
    )
