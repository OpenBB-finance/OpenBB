import argparse

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.fred import fred_api


def print_fred():
    """ Print help """

    print("\nFred Economic Data:")  # https://github.com/JerBouma/FundamentalAnalysis
    print("   help          show this menu again")
    print("   q             quit this menu, and shows back to main menu")
    print("   quit          quit to abandon program")
    print(" ")
    print("   GDP           get GDP")
    return

def fred_menu():
    fred_parser = argparse.ArgumentParser(prog="fa", add_help=False)
    choices = [
        "help",
        "q",
        "quit",
        "GDP"]
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
            # Just leave the FA menu
            return False

        elif ns_known_args.cmd == "quit":
            # Abandon the program
            return True

        elif ns_known_args.cmd == "GDP":
            fred_api.get_GDP(l_args)
