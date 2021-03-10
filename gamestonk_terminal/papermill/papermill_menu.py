import argparse

from gamestonk_terminal.papermill import due_diligence

from gamestonk_terminal.helper_funcs import get_flair


def print_papermill():
    """ Print help """

    print("\nDiscovery Mode:")
    print("   help          show this papermill menu again")
    print("   q             quit this menu, and shows back to main menu")
    print("   quit          quit to abandon program")
    print("")
    print("   dd            run papermill to generate due diligence summary")
    print("")

    return


def papermill_menu():
    papermill_parser = argparse.ArgumentParser(add_help=False, prog="papermill")
    papermill_parser.add_argument(
        "cmd",
        choices=["help", "q", "quit", "dd"],
    )

    print_papermill()

    while True:
        # Get input command from user
        as_input = input(f"{get_flair()} (mill)> ")

        # Parse fundamental analysis command of the list of possible commands
        try:
            (ns_known_args, l_args) = papermill_parser.parse_known_args(
                as_input.split()
            )

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        if ns_known_args.cmd == "help":
            print_papermill()

        elif ns_known_args.cmd == "q":
            # Just leave the MILL menu
            return False

        elif ns_known_args.cmd == "quit":
            # Abandon the program
            return True

        elif ns_known_args.cmd == "dd":
            due_diligence.analysis(l_args)

        else:
            print("Command not recognized!")
