"""Dune view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional, Union

from openbb_terminal import OpenBBFigure
from openbb_terminal.cryptocurrency.onchain.dune_model import get_query
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_DUNE_KEY"])
def display_query(
    id: str,
    limit: int = 500,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> Union[OpenBBFigure, None]:
    """
    Display Dune query [Source: https://dune.com/]

    Parameters
    ----------
    id : str
        Query id (e.g., 2412896)
    raw : bool
        Show raw data
    limit : int
        Limit of rows
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = get_query(id)
    if df.empty:
        return console.print("[red]No data found.[/red]")

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=True,
        export=bool(export),
        limit=limit,
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "dquery",
        df,
        sheet_name,
    )
