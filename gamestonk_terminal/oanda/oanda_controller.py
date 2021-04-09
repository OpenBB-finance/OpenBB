import argparse
# import matplotlib.pyplot as plt
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.helper_funcs import get_flair, parse_known_args_and_warn
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.oanda import oanda_functions
from gamestonk_terminal import config_terminal as cfg

account = cfg.OANDA_ACCOUNT


class OandaController:
    """Oanda Controller class"""

    CHOICES = [
        "help",
        "q",
        "quit",
        "hist",
        "price",
        "summary",
        "list"]

    def __init__(
        self,
#         instrument:str,
        ):
        """Construct Data"""
#         self.instrument = instrument
        self.oanda_parser = argparse.ArgumentParser(add_help=False, prog="fx")
        self.oanda_parser.add_argument(
        "cmd",
        choices=self.CHOICES,
        )

    @staticmethod
    def print_help():
        """Print help"""

        print("\nForex Mode:")
        print("\t help \t show this menu again")
        print("\t q \t quit this menu and goes back to main menu")
        print("\t quit \t quit to abandon program")
        print("")
        print("\t price \t shows price for selected instrument")
        print("\t summary  shows account summary")
        print("\t list \t list orders")

    def switch(self, an_input: str):
        """Process and dispatch input
        Returns
        ______
        True, False, or None
        False - quit the menu
        True - quit the program
        None - contiue in the menu
        """
        (known_args, other_args) = self.oanda_parser.parse_known_args(an_input.split())

        return getattr(self, "call_" + known_args.cmd, lambda: "command not recognized!")(other_args)

    def call_help(self, _):
        """Process Help Command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - exit the program"""
        return True

    def call_price(self, _):
        """Process Price Command"""
        try:
            oanda_functions.get_fx_price(account, instrument)
        except NameError as e:
            print(e)

    def call_summary(self, _):
        """Process account summary command"""
        oanda_functions.get_account_summary(account)

    def call_list(self, _):
        """Process list orders command"""
        oanda_functions.list_orders(account)


def menu():
        """Oanda Menu"""
        oanda_controller = OandaController()
        oanda_controller.call_help(None)
        while True:
            if session and gtff.USE_PROMPT_TOOLKIT:
                completer = NestedCompleter.from_nested_dict(
                    {c: None for c in oanda_controller.CHOICES}
                )

                an_input = session.prompt(
                f"{get_flair()} (fx)> ",
                completer=completer,
                )
            else:
                an_input = input(f"{get_flair()} (fx)> ")

            try:
                process_input = oanda_controller.switch(an_input)

                if process_input is not None:
                    return process_input

            except SystemExit:
                print("The command selected doesn't exit\n")
                continue

