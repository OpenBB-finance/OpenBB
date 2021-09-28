"""Ally View"""
__docformat__ = "numpy"

import os
from tabulate import tabulate
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import export_data
from gamestonk_terminal.portfolio.brokers.ally import ally_model


def display_history(n_to_show: int = 15, export: str = ""):
    history = ally_model.get_history()
    show_history = history[["amount", "date", "symbol", "transactiontype", "quantity"]]
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                show_history.tail(n_to_show),
                headers=show_history.columns,
                tablefmt="fancy_grid",
                floatfmt=".2f",
                showindex=False,
            )
        )
    else:
        print(show_history.tail(n_to_show).to_string())
    print("")
    export_data(
        export, os.path.dirname(os.path.abspath(__file__)), "ally_history", history
    )


def display_holdings(export: str = ""):
    """Display holdings from ally account

    Parameters
    ----------
    export : str, optional
        Format to export data, by default ""
    """
    holdings = ally_model.get_holdings()
    holdings = holdings.set_index("Symbol")
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                holdings,
                headers=holdings.columns,
                tablefmt="fancy_grid",
                floatfmt=".2f",
                showindex=True,
            )
        )
    else:
        print(holdings.to_string())
    print("")
    export_data(
        export,
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "ally_holdings",
        holdings,
    )


def display_balances(export: str = ""):
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
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                balances,
                headers=balances.columns,
                tablefmt="fancy_grid",
                floatfmt=".2f",
                showindex=False,
            )
        )
    else:
        print(balances.to_string())
    print("")


def display_stock_quote(ticker: str):
    """Displays stock quote for ticker/tickers

    Parameters
    ----------
    ticker : str
        Ticker to get.  Can be in form of 'tick1,tick2...'
    """
    quote = ally_model.get_stock_quote(ticker)
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                quote, tablefmt="fancy_grid", headers=quote.columns, showindex=True
            )
        )
    else:
        print(quote.to_string())
    print("")


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
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                movers.head(num_to_show),
                headers=movers.columns,
                tablefmt="fancy_grid",
                floatfmt=".2f",
                showindex=True,
            )
        )
    else:
        print(movers.to_string())
    print("")
    export_data(
        export,
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "ally_movers",
        movers,
    )
