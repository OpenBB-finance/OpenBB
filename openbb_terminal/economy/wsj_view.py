"""WSJ view """
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import wsj_model
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_overview(export: str = "", sheet_name: Optional[str] = None):
    """Market overview with daily change. [Source: Wall St. Journal]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_data = wsj_model.market_overview()
    if df_data.empty:
        console.print("No overview data available\n")
        return

    print_rich_table(
        df_data,
        show_index=False,
        headers=list(df_data.columns),
        title="Market Overview",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "overview",
        df_data,
        sheet_name,
    )


@log_start_end(log=logger)
def display_indices(export: str = "", sheet_name: Optional[str] = None):
    """US indices. [Source: Wall St. Journal]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_data = wsj_model.us_indices()
    if df_data.empty:
        console.print("No indices data available\n")
        return

    print_rich_table(
        df_data,
        show_index=False,
        headers=list(df_data.columns),
        title="US Indices",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "indices",
        df_data,
        sheet_name,
    )


@log_start_end(log=logger)
def display_futures(export: str = "", sheet_name: Optional[str] = None):
    """Futures/Commodities. [Source: Wall St. Journal]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_data = wsj_model.top_commodities()
    if df_data.empty:
        console.print("No futures/commodities data available\n")
        return

    print_rich_table(
        df_data,
        show_index=False,
        headers=list(df_data.columns),
        title="Futures/Commodities [Source: Wall St. Journal]",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "futures",
        df_data,
        sheet_name,
    )


@log_start_end(log=logger)
def display_usbonds(export: str = "", sheet_name: Optional[str] = None):
    """US bonds. [Source: Wall St. Journal]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_data = wsj_model.us_bonds()
    if df_data.empty:
        console.print("No US bonds data available\n")
        return

    print_rich_table(
        df_data,
        show_index=False,
        headers=list(df_data.columns),
        title="US Bonds",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "usbonds",
        df_data,
        sheet_name,
    )


@log_start_end(log=logger)
def display_glbonds(export: str = "", sheet_name: Optional[str] = None):
    """Global bonds. [Source: Wall St. Journal]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_data = wsj_model.global_bonds()
    if df_data.empty:
        console.print("No global bonds data available\n")
        return

    print_rich_table(
        df_data,
        show_index=False,
        headers=list(df_data.columns),
        title="Global Bonds",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "glbonds",
        df_data,
        sheet_name,
    )


@log_start_end(log=logger)
def display_currencies(export: str = "", sheet_name: Optional[str] = None):
    """Display currencies. [Source: Wall St. Journal]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_data = wsj_model.global_currencies()
    if df_data.empty:
        console.print("No currencies data available\n")
        return

    print_rich_table(
        df_data,
        show_index=False,
        headers=list(df_data.columns),
        title="Currencies",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "currencies",
        df_data,
        sheet_name,
    )
