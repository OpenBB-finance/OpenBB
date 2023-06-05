"""Tools View"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.cryptocurrency.tools.tools_model import calculate_apy, calculate_il
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_apy(
    apr: float,
    compounding_times: int,
    narrative: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Displays APY value converted from APR

    Parameters
    ----------
    apr: float
        value in percentage
    compounding_times: int
        number of compounded periods in a year
    narrative: str
        display narrative version instead of dataframe
    export : str
        Export dataframe data to csv,json,xlsx file

    Returns
    -------
    """
    df, apy_str = calculate_apy(apr, compounding_times)

    if narrative:
        console.print(apy_str)
    else:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="APR/APY Calculator",
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "aprtoapy",
        apy_str,
        sheet_name,
    )


@log_start_end(log=logger)
def display_il(
    price_changeA: int,
    price_changeB: int,
    proportion: int,
    initial_pool_value: int,
    narrative: bool = False,
    export: str = "",
    sheet_name: Optional[str] = None,
):
    """Displays Impermanent Loss in a custom liquidity pool

    Parameters
    ----------
    price_changeA: float
        price change of crypto A in percentage
    price_changeB: float
        price change of crypto B in percentage
    proportion: float
        percentage of first token in pool
    initial_pool_value: float
        initial value that pool contains
    narrative: str
        display narrative version instead of dataframe
    export : str
        Export dataframe data to csv,json,xlsx file

    Returns
    -------
    """
    df, il_str = calculate_il(
        price_changeA=price_changeA,
        price_changeB=price_changeB,
        proportion=proportion,
        initial_pool_value=initial_pool_value,
    )
    if narrative:
        console.print(il_str)
    else:
        print_rich_table(
            df,
            headers=list(df.columns),
            show_index=False,
            title="Impermanent Loss Calculator",
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "il",
        df,
        sheet_name,
    )
