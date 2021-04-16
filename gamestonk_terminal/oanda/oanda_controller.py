import argparse
from typing import List
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
        "price",
        "summary",
        "list",
        "orderbook",
        "positionbook",
        "limitorder",
        "cancel",
        "positions",
        "closetrade",
        "trades",
        "candles",
        "pending",
    ]

    def __init__(
        self,
    ):
        """Construct Data"""
        self.oanda_parser = argparse.ArgumentParser(add_help=False, prog="fx")
        self.oanda_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    @staticmethod
    def print_help():
        """Print help"""

        print("\nForex Mode:")
        print("help \t show this menu again")
        print("q \t quit this menu and goes back to main menu")
        print("quit \t quit to abandon program")
        print("")
        print("price \t shows price for selected instrument")
        print("summary  shows account summary")
        print("list \t list order history")
        print("trades \t list open trades")
        print("orderbook \t print orderbook")
        print("positionbook \t print positionbook")
        print("limitorder \t place limit order -u # of units -p price")
        print("cancel \t cancel a pending order by ID -i order ID")
        print("pending \t get information on pending orders")
        print("positions \t Get open positions")
        print("closetrade \t Close a trade by id")
        print("candles \t show candles")

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

        return getattr(
            self, "call_" + known_args.cmd, lambda: "command not recognized!"
        )(other_args)

    def call_help(self, _):
        """Process Help Command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - exit the program"""
        return True

    def call_price(self, other_args: List[str]):
        """Process Price Command"""
        oanda_functions.get_fx_price(account, other_args)

    def call_summary(self, _):
        """Process account summary command"""
        oanda_functions.get_account_summary(account)

    def call_orderbook(self, other_args: List[str]):
        """Process Oanda Order Book"""
        oanda_functions.get_order_book(other_args)

    def call_positionbook(self, other_args: List[str]):
        """Process Oanda Position Book"""
        oanda_functions.get_position_book(other_args)

    def call_list(self, other_args: List[str]):
        """Process list orders command"""
        oanda_functions.list_orders(account, other_args)

    def call_limitorder(self, other_args: List[str]):
        """Place limit order"""
        oanda_functions.create_limit_order(account, other_args)

    def call_cancel(self, other_args: List[str]):
        """Cancel pending order by ID"""
        oanda_functions.cancel_pending_order(account, other_args)

    def call_positions(self, _):
        """Get Open Positions"""
        oanda_functions.get_open_positions(account)

    def call_pending(self, _):
        """See up to 25 pending orders"""
        oanda_functions.get_pending_orders(account)

    def call_closetrade(self, other_args: List[str]):
        """Close a trade by id"""
        oanda_functions.close_trade(account, other_args)

    def call_candles(self, _):
        oanda_functions.show_candles(account)

    def call_trades(self, _):
        """List open trades"""
        oanda_functions.get_open_trades(account)


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
