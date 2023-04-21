""" ARK View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal import rich_config
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.stocks.discovery import ark_model

logger = logging.getLogger(__name__)


def lambda_direction_color_red_green(val: str) -> str:
    """Adds color tags to the Direction information: Buy -> Green, Sell -> Red

    Parameters
    ----------
    val : str
        Direction string - either Buy or Sell

    Returns
    -------
    str
        Direction string with color tags added
    """
    color = "green" if val == "Buy" else "red" if val == "Sell" else ""
    return f"[{color}]{val}[/{color}]"


@log_start_end(log=logger)
def ark_orders_view(
    limit: int = 10,
    sortby: str = "",
    ascend: bool = False,
    buys_only: bool = False,
    sells_only: bool = False,
    fund: str = "",
    export: str = "",
    sheet_name: Optional[str] = None,
) -> None:
    """Prints a table of the last N ARK Orders

    Parameters
    ----------
    limit: int
        Number of stocks to display
    sortby: str
        Column to sort on
    ascend: bool
        Flag to sort in ascending order
    buys_only: bool
        Flag to filter on buys only
    sells_only: bool
        Flag to sort on sells only
    fund: str
        Optional filter by fund
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    export: str
        Export dataframe data to csv,json,xlsx file
    """
    df_orders = ark_model.get_ark_orders(buys_only, sells_only, fund)
    if not df_orders.empty:
        df_orders = ark_model.add_order_total(df_orders.head(limit))

        if (
            rich_config.USE_COLOR
            and not get_current_user().preferences.USE_INTERACTIVE_DF
        ):
            df_orders["direction"] = df_orders["direction"].apply(
                lambda_direction_color_red_green
            )

        if sortby:
            df_orders = df_orders.sort_values(by=sortby, ascending=ascend)

        print_rich_table(
            df_orders,
            headers=[x.title() for x in df_orders.columns],
            show_index=False,
            title="Orders by ARK Investment Management LLC",
            export=bool(export),
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "arkord",
        df_orders,
        sheet_name,
    )
