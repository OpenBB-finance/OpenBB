""" ARK View """
__docformat__ = "numpy"

import logging
import os

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import export_data, print_rich_table
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.stocks.discovery import ark_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def direction_color_red_green(val: str) -> str:
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
    num: int,
    sort_col: str = "",
    ascending: bool = False,
    buys_only: bool = False,
    sells_only: bool = False,
    fund: str = "",
    export: str = "",
) -> None:
    """Prints a table of the last N ARK Orders

    Parameters
    ----------
    num: int
        Number of stocks to display
    sort_col : str
        Column to sort on
    ascending : bool
        Flag to sort in ascending order
    buys_only : bool
        Flag to filter on buys only
    sells_only : bool
        Flag to sort on sells only
    fund : str
        Optional filter by fund
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df_orders = ark_model.get_ark_orders()

    if df_orders.empty:
        console.print("The ARK orders aren't available at the moment.\n")
        return
    if fund:
        df_orders = df_orders[df_orders.fund == fund]
    if buys_only:
        df_orders = df_orders[df_orders.direction == "Buy"]
    if sells_only:
        df_orders = df_orders[df_orders.direction == "Sell"]
    df_orders = ark_model.add_order_total(df_orders.head(num))

    if sort_col:
        df_orders = df_orders.sort_values(by=sort_col, ascending=ascending)
    if gtff.USE_COLOR:
        df_orders["direction"] = df_orders["direction"].apply(direction_color_red_green)

    print_rich_table(
        df_orders,
        headers=[x.title() for x in df_orders.columns],
        show_index=False,
        title="Orders by ARK Investment Management LLC",
    )
    console.print("")

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "arkord",
        df_orders,
    )
