""" FinViz View """
__docformat__ = "numpy"

import logging
import os
from typing import Optional

from openbb_terminal import rich_config
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.fundamental_analysis import finviz_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_screen_data(
    symbol: str, export: str = "", sheet_name: Optional[str] = None
):
    """FinViz ticker screener

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    export : str
        Format to export data
    """
    fund_data = finviz_model.get_data(symbol)

    if fund_data.empty:
        console.print(f"No data found for {symbol}", style="bold red")
        return

    print_rich_table(
        fund_data, title="Ticker Screener", show_index=True, export=bool(export)
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "data",
        fund_data,
        sheet_name,
    )


def lambda_category_color_red_green(val: str) -> str:
    """Add color to analyst rating

    Parameters
    ----------
    val : str
        Analyst rating - Upgrade/Downgrade

    Returns
    -------
    str
        Analyst rating with color
    """

    if val == "Upgrade":
        return f"[green]{val}[/green]"
    if val == "Downgrade":
        return f"[red]{val}[/red]"
    if val == "Reiterated":
        return f"[yellow]{val}[/yellow]"
    return val


@log_start_end(log=logger)
def analyst(symbol: str, export: str = "", sheet_name: Optional[str] = None):
    """Display analyst ratings. [Source: Finviz]

    Parameters
    ----------
    symbol : str
        Stock ticker
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = finviz_model.get_analyst_data(symbol)

    if rich_config.USE_COLOR and not get_current_user().preferences.USE_INTERACTIVE_DF:
        df["category"] = df["category"].apply(lambda_category_color_red_green)

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=True,
        title="Display Analyst Ratings",
        export=bool(export),
    )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "analyst",
        df,
        sheet_name,
    )
