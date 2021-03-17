import argparse
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.fred import fred_api


def print_fred():
    """ Print help """

    print("\nFred Economic Data:")
    print("   help          show this menu again")
    print("   q             quit this menu, and shows back to main menu")
    print("   quit          quit to abandon program")
    print(" ")
    print("   gdp           GDP")
    print("   unemp         Unemployment Rate")
    print("   t01           1-Year Treasury Constant Maturity Rate")
    print("   t05           5-Year Treasury Constant Maturity Rate")
    print("   t10           10-Year Treasury Constant Maturity Rate")
    print("   t30           30-Year Treasury Constant Maturity Rate")
    print("   mort30        30-Year Fixed Rate Mortgage Average")
    print("   libor3m       3-Month LIBOR, based on U.S. Dollar")
    print("   moodAAA       Moody's Seasoned AAA Corporate Bond Yield")
    print("")
    print("   cust          User Specified FRED Data - Please Specify --id")
    print("")
    return


def fred_menu():
    fred_parser = argparse.ArgumentParser(prog="fred", add_help=False)
    defined_choices = [
        "gdp",
        "unemp",
        "t01",
        "t05",
        "t10",
        "t30",
        "mort30",
        "libor3m",
        "moodAAA",
    ]
    choices = ["help", "q", "quit", "cust"] + defined_choices

    fred_parser.add_argument("cmd", choices=choices)
    completer = NestedCompleter.from_nested_dict({c: None for c in choices})

    should_print_help = True
    while True:
        if should_print_help:
            print_fred()
            should_print_help = False

        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            as_input = session.prompt(
                f"{get_flair()} (fred)> ",
                completer=completer,
            )
        else:
            as_input = input(f"{get_flair()} (fred)> ")
        try:
            (ns_known_args, l_args) = fred_parser.parse_known_args(as_input.split())

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        if ns_known_args.cmd == "help":
            should_print_help = True

        elif ns_known_args.cmd == "q":
            # Leave the fred menu
            return False

        elif ns_known_args.cmd == "quit":
            # Abandon the program
            return True

        elif ns_known_args.cmd in defined_choices:
            fred_api.get_fred_data(l_args, ns_known_args.cmd)

        elif ns_known_args.cmd == "cust":
            fred_api.custom_data(l_args)
