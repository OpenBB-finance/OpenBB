""" Fidelity View """
__docformat__ = "numpy"

import logging
import os
import re
from typing import Optional

from openbb_terminal import rich_config
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.stocks.discovery import fidelity_model

logger = logging.getLogger(__name__)


def lambda_buy_sell_ratio_color_red_green(val: str) -> str:
    """Add color tags to the Buys/Sells ratio cell

    Parameters
    ----------
    val : str
        Buys/Sells ratio cell

    Returns
    -------
    str
        Buys/Sells ratio cell with color tags
    """

    buy_sell_match = re.match(r"(\d+)% Buys, (\d+)% Sells", val, re.M | re.I)

    if not buy_sell_match:
        return val

    buys = int(buy_sell_match.group(1))
    sells = int(buy_sell_match.group(2))

    if buys >= sells:
        return f"[green]{buys}%[/green] Buys, {sells}% Sells"

    return f"{buys}% Buys, [red]{sells}%[/red] Sells"


def lambda_price_change_color_red_green(val: str) -> str:
    """Add color tags to the price change cell

    Parameters
    ----------
    val : str
        Price change cell

    Returns
    -------
    str
        Price change cell with color tags
    """

    val_float = float(val.split(" ")[0])
    if val_float > 0:
        return f"[green]{val}[/green]"
    return f"[red]{val}[/red]"


@log_start_end(log=logger)
def orders_view(limit: int = 5, export: str = "", sheet_name: Optional[str] = None):
    """Prints last N orders by Fidelity customers. [Source: Fidelity]

    Parameters
    ----------
    limit: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    order_header, df_orders = fidelity_model.get_orders()

    if rich_config.USE_COLOR and not get_current_user().preferences.USE_INTERACTIVE_DF:
        df_orders["Buy / Sell Ratio"] = df_orders["Buy / Sell Ratio"].apply(
            lambda_buy_sell_ratio_color_red_green
        )
        df_orders["Price Change"] = df_orders["Price Change"].apply(
            lambda_price_change_color_red_green
        )

    df_orders = df_orders.head(n=limit).iloc[:, :-1]

    print_rich_table(
        df_orders,
        headers=[x.title() for x in df_orders.columns],
        show_index=False,
        title=f"{order_header}:",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "ford",
        df_orders,
        sheet_name,
    )
