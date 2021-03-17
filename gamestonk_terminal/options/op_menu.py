import argparse

from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.options import volume as vol
from gamestonk_terminal.menu import session


def opt_menu(df_stock, s_ticker, s_start, s_interval):

    # Add list of arguments that the options parser accepts
    opt_parser = argparse.ArgumentParser(prog="opt", add_help=False)
    choices = ["help", "q", "quit", "volume", "oi"]
    opt_parser.add_argument("cmd", choices=choices)
    completer = NestedCompleter.from_nested_dict({c: None for c in choices})

    # print_options(s_ticker, s_start, s_interval)

    # Loop forever and ever
    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            as_input = session.prompt(
                f"{get_flair()} (opt)> ",
                completer=completer,
            )
        else:
            as_input = input(f"{get_flair()} (opt)> ")

        # Parse fundamental analysis command of the list of possible commands
        try:
            (ns_known_args, l_args) = opt_parser.parse_known_args(as_input.split())

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        if ns_known_args.cmd == "help":
            pass
            # print_options(s_ticker)

        elif ns_known_args.cmd == "q":
            # Just leave the options menu
            return False

        elif ns_known_args.cmd == "quit":
            # Abandon the program
            return True

        elif ns_known_args.cmd == "volume":
            # call the volume graph
            vol.volume_graph(l_args, s_ticker)

        elif ns_known_args.cmd == "oi":
            # call the volume graph
            vol.open_interest_graph(l_args, s_ticker)
        else:
            print("Command not recognized!")
