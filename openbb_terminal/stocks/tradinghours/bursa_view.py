"""Stocks Trading Hours View."""
__docformat__ = "numpy"

import logging

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.tradinghours import bursa_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_exchange(symbol: str):
    """Display current exchange trading hours.

    Parameters
    ----------
    symbol : str
        Exchange symbol
    """
    exchange = bursa_model.get_bursa(symbol)

    if len(exchange) == 0 or exchange.empty:
        console.print(
            "[red]"
            + "No exchange data loaded.\n"
            + "Make sure you picked a valid exchange symbol."
            + "[/red]\n"
        )
        return

    exchange_name = exchange.loc["name"]

    print_rich_table(
        exchange,
        show_index=True,
        title=f"[bold]{exchange_name}[/bold]",
    )


@log_start_end(log=logger)
def display_open():
    """Display open exchanges.

    Parameters
    ----------
    """
    exchanges = bursa_model.get_open()

    if exchanges.empty:
        console.print("No exchange open.\n")
        return

    print_rich_table(
        exchanges,
        show_index=True,
        index_name="Symbol",
        title="[bold]Open markets[/bold]",
    )


@log_start_end(log=logger)
def display_closed():
    """Display closed exchanges.

    Parameters
    ----------
    """
    exchanges = bursa_model.get_closed()

    if exchanges.empty:
        console.print("[red]" + "No exchange data loaded.\n" + "[/red]\n")
        return

    print_rich_table(
        exchanges,
        show_index=True,
        index_name="Symbol",
        title="[bold]Closed markets[/bold]",
    )


@log_start_end(log=logger)
def display_all():
    """Display all exchanges.

    Parameters
    ----------
    """
    exchanges = bursa_model.get_all()

    if exchanges.empty:
        console.print("[red]" + "No exchange data loaded.\n" + "[/red]\n")
        return

    print_rich_table(
        exchanges,
        show_index=True,
        index_name="Symbol",
        title="[bold]World markets[/bold]",
    )
