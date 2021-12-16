"""Oanda Controller"""
__docformat__ = "numpy"
import argparse
import os
from typing import List

from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.forex.oanda import oanda_view

# from gamestonk_terminal.forex.exploratory_data_analysis import eda_controller
from gamestonk_terminal.helper_funcs import (
    get_flair,
    MENU_GO_BACK,
    MENU_QUIT,
    MENU_RESET,
)
from gamestonk_terminal.menu import session


account = cfg.OANDA_ACCOUNT


class OandaController:

    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
        "reset",
    ]

    CHOICES_COMMANDS = [
        "price",
        "summary",
        "list",
        "orderbook",
        "positionbook",
        "order",
        "load",
        "cancel",
        "positions",
        "closetrade",
        "trades",
        "candles",
        "pending",
        "calendar",
        # "news",
        # "reddit",
    ]
    CHOICES += CHOICES_COMMANDS

    def __init__(self):
        """Construct Data"""
        self.fx_parser = argparse.ArgumentParser(add_help=False, prog="oanda")
        self.fx_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.instrument = None

    def print_help(self):
        """Print help"""
        print("   ?/help        show this menu again")
        print("   q             quit this menu and goes back to main menu")
        print("   quit          quit to abandon program")
        print("   reset         reset terminal and reload configs")
        print("")
        print("   summary       shows account summary")
        print("   calendar      show calendar")
        print("   list          list order history")
        print("   pending       get information on pending orders")
        print("   cancel        cancel a pending order by ID -i order ID")
        print("   positions     get open positions")
        print("   trades        list open trades")
        print("   closetrade    close a trade by id")
        print("")
        print(f"Loaded instrument: {self.instrument if self.instrument else ''}")
        print("")
        print("   load          load an instrument to use")
        if self.instrument:
            print("   candles       show candles")
            print("   price         shows price for selected instrument")
            print("   order         place limit order -u # of units -p price")
            print("   orderbook     print orderbook")
            print("   positionbook  print positionbook")
        print("")

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        MENU_GO_BACK, MENU_QUIT, MENU_RESET
            MENU_GO_BACK - Show main context menu again
            MENU_QUIT - Quit terminal
            MENU_RESET - Reset terminal and go back to same previous menu
        """

        # Empty command
        if not an_input:
            print("")
            return None

        (known_args, other_args) = self.fx_parser.parse_known_args(an_input.split())

        # Help menu again
        if known_args.cmd == "?":
            self.print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            os.system("cls||clear")
            return None

        return getattr(
            self,
            "call_" + known_args.cmd,
            lambda _: "Command not recognized!",
        )(other_args)

    def call_help(self, _):
        """Process Help Command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return MENU_GO_BACK

    def call_quit(self, _):
        """Process Quit command - exit the program"""
        return MENU_QUIT

    def call_reset(self, _):
        """Process Reset command - reset the program"""
        return MENU_RESET

    def call_price(self, other_args):
        """Process Price Command"""
        oanda_view.get_fx_price(account, self.instrument, other_args)

    def call_load(self, other_args):
        self.instrument = oanda_view.load(other_args)

    def call_summary(self, other_args):
        """Process account summary command"""
        oanda_view.get_account_summary(account, other_args)

    def call_orderbook(self, other_args):
        """Process Oanda Order Book"""
        oanda_view.get_order_book(self.instrument, other_args)

    def call_positionbook(self, other_args):
        """Process Oanda Position Book"""
        oanda_view.get_position_book(self.instrument, other_args)

    def call_list(self, other_args: List[str]):
        """Process list orders command"""
        oanda_view.list_orders(account, other_args)

    def call_order(self, other_args: List[str]):
        """Place limit order"""
        oanda_view.create_order(account, self.instrument, other_args)

    def call_cancel(self, other_args: List[str]):
        """Cancel pending order by ID"""
        oanda_view.cancel_pending_order(account, other_args)

    def call_positions(self, other_args):
        """Get Open Positions"""
        oanda_view.get_open_positions(account, other_args)

    def call_pending(self, other_args):
        """See up to 25 pending orders"""
        oanda_view.get_pending_orders(account, other_args)

    def call_closetrade(self, other_args: List[str]):
        """Close a trade by id"""
        oanda_view.close_trade(account, other_args)

    def call_candles(self, other_args: List[str]):
        oanda_view.show_candles(account, self.instrument, other_args)

    def call_trades(self, other_args):
        """List open trades"""
        oanda_view.get_open_trades(account, other_args)

    def call_calendar(self, other_args: List[str]):
        """Call calendar"""
        oanda_view.calendar(self.instrument, other_args)


def menu():
    """Forex Menu"""
    oanda_controller = OandaController()
    oanda_controller.call_help(None)
    while True:
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in oanda_controller.CHOICES}
            )

            an_input = session.prompt(
                f"{get_flair()} (forex)(oanda)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (forex)(oanda)> ")

        try:
            process_input = oanda_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exit\n")
            continue
