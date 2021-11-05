__docformat__ = "numpy"

# pylint: disable=R1710

import argparse
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair, system_clear
from gamestonk_terminal.menu import session

from gamestonk_terminal.portfolio.brokers.ally import ally_controller
from gamestonk_terminal.portfolio.brokers.degiro import degiro_controller
from gamestonk_terminal.portfolio.brokers.robinhood import robinhood_controller
from gamestonk_terminal.portfolio.brokers.coinbase import coinbase_controller


class BrokersController:
    """Brokers Controller"""

    CHOICES = ["?", "cls", "help", "q", "quit"]

    BROKERS = ["cb", "ally", "rh", "degiro"]

    CHOICES += BROKERS

    def __init__(self):
        self.bro_parser = argparse.ArgumentParser(add_help=False, prog="bro")
        self.bro_parser.add_argument("cmd", choices=self.CHOICES)
        self.broker_list = set()
        self.merged_holdings = None

    def print_help(self):
        """Print help"""
        help_string = """
What would you like to do?
    cls           clear screen
    ?/help        show this menu again
    q             quit this menu, and shows back to  >Portfolio, logs out of brokers
    quit          quit to abandon program, logs out of brokers

Brokers:
>   ally         Ally Invest Menu
>   degiro       Degiro Menu
>   rh           Robinhood Menu

Crypto Brokers:
>   cb           Coinbase Pro Menu
    """
        print(help_string)

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        True, False or None
            False - quit the menu
            True - quit the program
            None - continue in the menu
        """

        # Empty command
        if not an_input:
            print("")
            return None

        (known_args, other_args) = self.bro_parser.parse_known_args(an_input.split())

        # Help menu again
        if known_args.cmd == "?":
            self.print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            system_clear()
            return None

        return getattr(
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
        )(other_args)

    def call_help(self, _):
        """Process help command"""
        self.print_help()

    def call_q(self, _):
        """Process q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process quit command - quit the program"""
        return True

    def call_degiro(self, _):
        """Process degiro command."""
        if degiro_controller.menu():
            return True
        print("")

    def call_ally(self, _):
        """Process degiro command."""
        if ally_controller.menu():
            return True
        print("")

    def call_rh(self, _):
        """Process degiro command."""
        if robinhood_controller.menu():
            return True
        print("")

    def call_cb(self, _):
        """Process degiro command."""
        if coinbase_controller.menu():
            return True
        print("")

    # TODO: Consistent way of merging across brokers including crypto
    # def call_login(self, other_args):
    #    """Process login command"""
    #    logged_in = False
    #    if not other_args:
    #        print("Please enter brokers you wish to login to")
    #        print("")
    #        return
    #    for broker in other_args:
    #        if broker in self.BROKERS:
    #            api = broker + "_api"
    #            try:
    #                # pylint: disable=eval-used
    #                eval(api + ".login()")
    #                self.broker_list.add(broker)
    #                logged_in = True
    #            except Exception as e:
    #                print("")
    #                print(f"Error at broker : {broker}")
    #                print(e)
    #                print("Make sure credentials are defined in config_terminal.py ")
    #                print("")
    #        else:
    #            print(f"{broker} not supported")


def menu():
    """Brokers Menu"""
    bro_controller = BrokersController()
    print(
        "\nUSE THIS MENU AT YOUR OWN DISCRETION\n"
        "   - This menu is the only one in the entire repository that has access to your broker accounts. "
        "If you have provided your login details on the config_terminal.py file"
        "   - We review the code thoroughly from each contributor, hence, we can ensure that our codebase "
        "does not take advantage of your data.\n"
        "   - HOWEVER, our project imports almost 200 different open source python modules. Therefore, it "
        "is impossible for us to check the coding standards and security of each of these modules. "
        "Hence why adding this disclaimer here."
    )
    bro_controller.print_help()

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in bro_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (portfolio)>(bro)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (portfolio)>(bro)> ")

        try:
            process_input = bro_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
