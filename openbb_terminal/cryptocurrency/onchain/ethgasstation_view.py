"""ETH Gas Station view"""
import logging
import os
from typing import Optional

from openbb_terminal.cryptocurrency.onchain.ethgasstation_model import get_gwei_fees
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_gwei_fees(
    export: str = "", sheet_name: Optional[str] = None, limit: int = 10
) -> None:
    """Current gwei fees
    [Source: https://ethgasstation.info]

    Parameters
    ----------
    export : str
        Export dataframe data to csv,json,xlsx file
    """

    df_fees = get_gwei_fees()

    if df_fees.empty:
        console.print("\nError in ethgasstation request\n")
    else:
        console.print("\nCurrent ETH gas fees (gwei):")

        print_rich_table(
            df_fees,
            headers=list(df_fees.columns),
            show_index=False,
            title="Current GWEI Fees",
            export=bool(export),
            limit=limit,
        )

        export_data(
            export,
            os.path.dirname(os.path.abspath(__file__)),
            "gwei",
            df_fees,
            sheet_name,
        )
