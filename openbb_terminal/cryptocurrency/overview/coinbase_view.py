"""Coinbase view"""
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal.cryptocurrency.overview import coinbase_model
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
@check_api_key(["API_COINBASE_KEY", "API_COINBASE_SECRET", "API_COINBASE_PASS_PHRASE"])
def display_trading_pairs(
    limit: int = 20,
    sortby: str = "quote_increment",
    ascend: bool = True,
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Displays a list of available currency pairs for trading. [Source: Coinbase]

    Parameters
    ----------
    limit: int
        Top n of pairs
    sortby: str
        Key to sortby data
    ascend: bool
        Sort ascending flag
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df = coinbase_model.get_trading_pairs(limit, sortby, ascend)

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title="Available Pairs for Trading",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "cbpairs",
        df,
        sheet_name,
    )
