import argparse

from gamestonk_terminal.discovery import (
    alpha_vantage_api,
    ark_api,
    fidelity_api,
    finviz_api,
    seeking_alpha_api,
    short_interest_api,
    simply_wallst_api,
    spachero_api,
    unusual_whales_api,
    yahoo_finance_api,
)
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from prompt_toolkit.completion import NestedCompleter


def print_discovery():
    """ Print help """

    print("\nDiscovery Mode:")
    print("   help          show this discovery menu again")
    print("   q             quit this menu, and shows back to main menu")
    print("   quit          quit to abandon program")
    print("")
    print("   map           S&P500 index stocks map [Finviz]")
    print("   sectors       show sectors performance [Alpha Vantage]")
    print("   gainers       show latest top gainers [Yahoo Finance]")
    print("   orders        orders by Fidelity Customers [Fidelity]")
    print("   ark_orders    orders by ARK Investment Management LLC")
    print("   up_earnings   upcoming earnings release dates [Seeking Alpha]")
    print(
        "   high_short    show top high short interest stocks of over 20% ratio [www.highshortinterest.com]"
    )
    print(
        "   low_float     show low float stocks under 10M shares float [www.lowfloat.com]"
    )
    print("   simply_wallst Simply Wall St. research data [Simply Wall St.]")
    print("   spachero      great website for SPACs research [SpacHero]")
    print("   uwhales       good website for SPACs research [UnusualWhales]")
    print("")
    return


def disc_menu():

    # Add list of arguments that the discovery parser accepts
    disc_parser = argparse.ArgumentParser(add_help=False, prog="discovery")
    choices = [
        "help",
        "q",
        "quit",
        "map",
        "sectors",
        "gainers",
        "spacs",
        "orders",
        "ark_orders",
        "spachero",
        "high_short",
        "low_float",
        "up_earnings",
        "simply_wallst",
        "uwhales",
        "mill",
    ]
    disc_parser.add_argument("cmd", choices=choices)
    completer = NestedCompleter.from_nested_dict({c: None for c in choices})

    print_discovery()

    # Loop forever and ever
    while True:
        # Get input command from user
        if session:
            as_input = session.prompt(
                f"{get_flair()} (disc)> ",
                completer=completer,
            )
        else:
            as_input = input(f"{get_flair()} (disc)> ")

        # Parse fundamental analysis command of the list of possible commands
        try:
            (ns_known_args, l_args) = disc_parser.parse_known_args(as_input.split())

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        if ns_known_args.cmd == "help":
            print_discovery()

        elif ns_known_args.cmd == "q":
            # Just leave the DISC menu
            return False

        elif ns_known_args.cmd == "quit":
            # Abandon the program
            return True

        elif ns_known_args.cmd == "map":
            finviz_api.map_sp500(l_args)

        elif ns_known_args.cmd == "sectors":
            alpha_vantage_api.sectors(l_args)

        elif ns_known_args.cmd == "gainers":
            yahoo_finance_api.gainers(l_args)

        elif ns_known_args.cmd == "spachero":
            spachero_api.spachero(l_args)

        elif ns_known_args.cmd == "uwhales":
            unusual_whales_api.unusual_whales(l_args)

        elif ns_known_args.cmd == "orders":
            fidelity_api.orders(l_args)

        elif ns_known_args.cmd == "ark_orders":
            ark_api.ark_orders(l_args)

        elif ns_known_args.cmd == "simply_wallst":
            simply_wallst_api.simply_wallst(l_args)

        elif ns_known_args.cmd == "up_earnings":
            seeking_alpha_api.earnings_release_dates(l_args)

        elif ns_known_args.cmd == "high_short":
            short_interest_api.high_short_interest(l_args)

        elif ns_known_args.cmd == "low_float":
            short_interest_api.low_float(l_args)

        else:
            print("Command not recognized!")
