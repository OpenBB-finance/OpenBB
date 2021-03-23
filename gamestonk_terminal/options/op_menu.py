"""Control options main menu."""
import argparse


from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.options import volume as vol
from gamestonk_terminal.menu import session


def opt_menu(s_ticker):
    """Control options main menu."""
    # Add list of arguments that the options parser accepts
    opt_parser = argparse.ArgumentParser(prog="op", add_help=False)
    choices = ["help", "q", "quit", "volume", "oi"]
    opt_parser.add_argument("cmd", choices=choices)
    completer = NestedCompleter.from_nested_dict({c: None for c in choices})

    # print_options(s_ticker)
    should_print_help = True
    options_data_loaded = False
    exp_date_chosen = False
    # Loop forever and ever

    # print expiry dates 1 time

    while True:
        if not options_data_loaded:
            # raw_options_data = options_helper.load_op_data(s_ticker)
            # options_data_loaded = True
            pass
        if not exp_date_chosen:
            # exp_date = options_helper.choose_exp_date(raw_options_data)
            # exp_date_chosen = True
            pass

        if should_print_help:
            print_options(s_ticker)
            should_print_help = False
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            as_input = session.prompt(
                f"{get_flair()} (op)> ",
                completer=completer,
            )
        else:
            as_input = input(f"{get_flair()} (op)> ")

        # Parse fundamental analysis command of the list of possible commands
        try:
            (ns_known_args, l_args) = opt_parser.parse_known_args(as_input.split())

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        if ns_known_args.cmd == "help":
            should_print_help = True

        elif ns_known_args.cmd == "q":
            # Just leave the options menu
            return False

        elif ns_known_args.cmd == "quit":
            # Abandon the program
            return True

        elif ns_known_args.cmd == "volume":
            # call the volume graph
            # vol.volume_graph(l_args, s_ticker)
            vol.volume_graph(s_ticker, l_args)

        else:
            print("Command not recognized!")


def print_options(s_ticker):
    """Print help."""
    print(f"\nOptions analytics for {s_ticker}:")
    print("   help          show this options menu again")
    print("   q             quit this menu, and shows back to main menu")
    print("   quit          quit to abandon program")
    print("")
    # print(
    #    "   volume -e     show traded volume for expiry date. Usage : volume -e yyyy-mm-dd [Yahoo finance]"
    # )

    print("")
    return
