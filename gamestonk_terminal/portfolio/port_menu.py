import argparse
from matplotlib import pyplot as plt
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.portfolio import rh_api


def print_port(show_login):
    """ Print help """
    print("\nPortfolio:")
    print("   help          show this menu again")
    print("   q             quit this menu, and shows back to main menu")
    print("   quit          quit to abandon program")
    print(" ")
    print("Robinhood:")
    print("")
    if show_login:
        print("   login         login")
    print("   hold          look at current holdings")
    print("   rhhist        look at historical portfolio")
    print(" ")


def port_menu():
    plt.close("all")
    port_parser = argparse.ArgumentParser(prog="port", add_help=False)
    choices = ["help", "q", "quit", "hold", "rhhist", "login", "logoff"]
    port_parser.add_argument("cmd", choices=choices)
    completer = NestedCompleter.from_nested_dict({c: None for c in choices})
    should_print_help = True
    print_login = True
    while True:
        if should_print_help:
            print_port(print_login)
            should_print_help = False

        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            as_input = session.prompt(
                f"{get_flair()} (port)> ",
                completer=completer,
            )
        else:
            as_input = input(f"{get_flair()} (port)> ")
        try:
            (ns_known_args, l_args) = port_parser.parse_known_args(as_input.split())

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        if ns_known_args.cmd == "help":
            should_print_help = True

        elif ns_known_args.cmd == "q":
            # Leave the port menu + logout of robinhood
            # logoff raises error if not logged in
            try:
                rh_api.logoff()
            except Exception:
                pass
            return False

        elif ns_known_args.cmd == "quit":
            # Will raise exception if not logged in
            try:
                rh_api.logoff()
            except Exception:
                pass
            # Abandon the program
            return True

        elif ns_known_args.cmd == "hold":
            try:
                rh_api.show_holdings()
            except Exception as e:
                print(e)
                print("")

        elif ns_known_args.cmd == "rhhist":
            rh_api.plot_historical(l_args)

        elif ns_known_args.cmd == "login":
            rh_api.login()
            should_print_help = True
            print_login = False

        else:
            print("Command not recognized")
