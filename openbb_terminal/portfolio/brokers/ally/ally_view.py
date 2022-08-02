"""Ally View"""
__docformat__ = "numpy"

import logging
import os

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.portfolio.brokers.ally import ally_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def display_history(n_to_show: int = 15, export: str = "") -> None:
    history = ally_model.get_history()
    show_history = history[["amount", "date", "symbol", "transactiontype", "quantity"]]
    print_rich_table(
        show_history.tail(n_to_show),
        headers=list(show_history.columns),
        show_index=False,
        title="Ally History",
    )

    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "ally_history", history
    )


@log_start_end(log=logger)
def display_holdings(export: str = "") -> None:
    """Display holdings from ally account

    Parameters
    ----------
    export : str, optional
        Format to export data, by default ""
    """
    holdings = ally_model.get_holdings()
    holdings = holdings.set_index("Symbol")
    print_rich_table(
        holdings, headers=list(holdings.columns), show_index=True, title="Ally Holdings"
    )

    export_data(
        export,
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "ally_holdings",
        holdings,
    )


@log_start_end(log=logger)
def display_balances(export: str = "") -> None:
    """Display balances from ally account

    Parameters
    ----------
    export : str, optional
        Format to export data, by default ""
    """
    balances = ally_model.get_balances()
    # Export data here before picking out certain columns
    export_data(
        export,
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "ally_balances",
        balances,
    )
    # Pick which balances to show
    balances = balances[
        [
            "accountvalue",
            "buyingpower.stock",
            "money.cash",
            "securities.stocks",
            "securities.total",
        ]
    ]
    print_rich_table(
        balances,
        headers=list(balances.columns),
        show_index=False,
        title="Ally Balances",
    )


@log_start_end(log=logger)
def display_stock_quote(ticker: str) -> None:
    """Displays stock quote for ticker/tickers

    Parameters
    ----------
    ticker : str
        Ticker to get.  Can be in form of 'tick1,tick2...'
    """
    quote = ally_model.get_stock_quote(ticker)
    print_rich_table(
        quote, headers=list(quote.columns), show_index=True, title="Stock Quote"
    )


@log_start_end(log=logger)
def display_top_lists(
    list_type: str, exchange: str, num_to_show: int = 20, export: str = ""
):
    """
    Display top lists from ally Invest API.  Documentation for parameters below:
    https://www.ally.com/api/invest/documentation/market-toplists-get/

    Parameters
    ----------
    list_type : str
        Which list to get data for
    exchange : str
        Which exchange to look at
    num_to_show : int, optional
        Number of top rows to show, by default 20
    export : str, optional
        Format to export data, by default ""
    """
    movers = ally_model.get_top_movers(list_type, exchange)
    print_rich_table(
        movers.head(num_to_show),
        headers=list(movers.columns),
        show_index=True,
        title="Ally Top Lists",
    )

    export_data(
        export,
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "ally_movers",
        movers,
    )
