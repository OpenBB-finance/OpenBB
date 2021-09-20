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
