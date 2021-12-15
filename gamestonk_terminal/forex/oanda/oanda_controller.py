"""Oanda Controller"""
__docformat__ = "numpy"

import argparse
import difflib
from typing import List, Union

from colorama import Style
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.forex.oanda import oanda_view

# from gamestonk_terminal.forex.exploratory_data_analysis import eda_controller
from gamestonk_terminal.helper_funcs import (
    get_flair,
    try_except,
    system_clear,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.paths import cd_CHOICES


account = cfg.OANDA_ACCOUNT


class OandaController:

    CHOICES = [
        "cls",
        "cd",
        "h",
        "help",
        "?",
        "q",
        "quit",
        "..",
        "exit",
        "r",
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

    def __init__(self, queue: List[str] = None):
        """Construct Data"""
        self.fx_parser = argparse.ArgumentParser(add_help=False, prog="oanda")
        self.fx_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            choices["cd"] = {c: None for c in cd_CHOICES}

            self.completer = NestedCompleter.from_nested_dict(choices)

        self.instrument = None

        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def print_help(self):
        """Print help"""
        dim_if_no_ticker = Style.DIM if not self.instrument else ""
        reset_style_if_no_ticker = Style.RESET_ALL if not self.instrument else ""

        help_text = f"""
    ?/help        show this menu again
    q             quit this menu and goes back to main menu
    quit          quit to abandon program
    reset         reset terminal and reload configs

    summary       shows account summary
    calendar      show calendar
    list          list order history
    pending       get information on pending orders
    cancel        cancel a pending order by ID -i order ID
    positions     get open positions
    trades        list open trades
    closetrade    close a trade by id

    Loaded instrument: {self.instrument if self.instrument else ""}

    load          load an instrument to use
    {dim_if_no_ticker}
    candles       show candles
    price         shows price for selected instrument
    order         place limit order -u # of units -p price
    orderbook     print orderbook
    positionbook  print positionbook
    {reset_style_if_no_ticker}

    """
        print(help_text)

    def switch(self, an_input: str):
        """Process and dispatch input

        Returns
        -------
        List[str]
            List of commands in the queue to execute
        """

        # Empty command
        if not an_input:
            print("")
            return self.queue if len(self.queue) > 0 else []

        if "/" in an_input:
            actions = an_input.split("/")
            an_input = actions[0]
            for cmd in actions[1:][::-1]:
                self.queue.insert(0, cmd)

        (known_args, other_args) = self.fx_parser.parse_known_args(an_input.split())

        if known_args.cmd:
            if known_args.cmd in ("..", "q"):
                known_args.cmd = "quit"
            elif known_args.cmd in ("?", "h"):
                known_args.cmd = "help"
            elif known_args.cmd == "r":
                known_args.cmd = "reset"

        return getattr(
            self, "call_" + known_args.cmd, lambda: "command not recognized!"
        )(other_args)

    def call_cls(self, _):
        """Process cls command"""
        system_clear()
        return self.queue if len(self.queue) > 0 else []

    def call_cd(self, other_args):
        """Process cd command"""
        if other_args:
            args = other_args[0].split("/")
            if len(args) > 0:
                for m in args[::-1]:
                    if m:
                        self.queue.insert(0, m)
            else:
                self.queue.insert(0, args[0])

        self.queue.insert(0, "q")

        return self.queue if len(self.queue) > 0 else []

    def call_help(self, _):
        """Process Help Command"""
        self.print_help()
        return self.queue if len(self.queue) > 0 else []

    def call_quit(self, _):
        """Process quit menu command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "q")
            return self.queue
        return ["q"]

    def call_exit(self, _):
        """Process exit terminal command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "q")
            self.queue.insert(0, "q")
            return self.queue
        return ["q", "q", "q"]

    def call_reset(self, _):
        """Process reset command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "forex")
            self.queue.insert(0, "r")
            self.queue.insert(0, "q")
            self.queue.insert(0, "q")
            return self.queue
        return ["q", "q", "r", "forex"]

    @try_except
    def call_price(self, other_args):
        """Process Price Command"""
        oanda_view.get_fx_price(account, self.instrument, other_args)
        return self.queue if len(self.queue) > 0 else []

    @try_except
    def call_load(self, other_args):
        """Load a currency from Oanda"""
        self.instrument = oanda_view.load(other_args)
        return self.queue if len(self.queue) > 0 else []

    @try_except
    def call_summary(self, other_args):
        """Process account summary command"""
        oanda_view.get_account_summary(account, other_args)
        return self.queue if len(self.queue) > 0 else []

    @try_except
    def call_orderbook(self, other_args):
        """Process Oanda Order Book"""
        oanda_view.get_order_book(self.instrument, other_args)
        return self.queue if len(self.queue) > 0 else []

    @try_except
    def call_positionbook(self, other_args):
        """Process Oanda Position Book"""
        oanda_view.get_position_book(self.instrument, other_args)
        return self.queue if len(self.queue) > 0 else []

    @try_except
    def call_list(self, other_args: List[str]):
        """Process list orders command"""
        oanda_view.list_orders(account, other_args)
        return self.queue if len(self.queue) > 0 else []

    @try_except
    def call_order(self, other_args: List[str]):
        """Place limit order"""
        oanda_view.create_order(account, self.instrument, other_args)
        return self.queue if len(self.queue) > 0 else []

    @try_except
    def call_cancel(self, other_args: List[str]):
        """Cancel pending order by ID"""
        oanda_view.cancel_pending_order(account, other_args)
        return self.queue if len(self.queue) > 0 else []

    @try_except
    def call_positions(self, other_args):
        """Get Open Positions"""
        oanda_view.get_open_positions(account, other_args)
        return self.queue if len(self.queue) > 0 else []

    @try_except
    def call_pending(self, other_args):
        """See up to 25 pending orders"""
        oanda_view.get_pending_orders(account, other_args)
        return self.queue if len(self.queue) > 0 else []

    @try_except
    def call_closetrade(self, other_args: List[str]):
        """Close a trade by id"""
        oanda_view.close_trade(account, other_args)
        return self.queue if len(self.queue) > 0 else []

    @try_except
    def call_candles(self, other_args: List[str]):
        oanda_view.show_candles(account, self.instrument, other_args)
        return self.queue if len(self.queue) > 0 else []

    @try_except
    def call_trades(self, other_args):
        """List open trades"""
        oanda_view.get_open_trades(account, other_args)
        return self.queue if len(self.queue) > 0 else []

    @try_except
    def call_calendar(self, other_args: List[str]):
        """Call calendar"""
        oanda_view.calendar(self.instrument, other_args)
        return self.queue if len(self.queue) > 0 else []


def menu(queue: List[str] = None):
    """Oanda Forex Menu"""
    oanda_controller = OandaController(queue)
    HELP_ME = True

    while True:
        # There is a command in the queue
        if oanda_controller.queue and len(oanda_controller.queue) > 0:
            if oanda_controller.queue[0] in ("q", ".."):
                if len(oanda_controller.queue) > 1:
                    return oanda_controller.queue[1:]
                return []

            an_input = oanda_controller.queue[0]
            oanda_controller.queue = oanda_controller.queue[1:]
            if an_input and an_input in oanda_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /forex/oanda/ $ {an_input}")

        else:
            if HELP_ME:
                oanda_controller.print_help()
                HELP_ME = False

            if session and gtff.USE_PROMPT_TOOLKIT and oanda_controller.completer:
                an_input = session.prompt(
                    f"{get_flair()} /forex/oanda/ $ ",
                    completer=oanda_controller.completer,
                    search_ignore_case=True,
                )

            else:
                an_input = input(f"{get_flair()} /forex/oanda/ $ ")

        try:
            oanda_controller.queue = oanda_controller.switch(an_input)

        except SystemExit:
            print(f"\nThe command '{an_input}' doesn't exist.", end="")
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                oanda_controller.CHOICES,
                n=1,
                cutoff=0.7,
            )

            if similar_cmd:
                if " " in an_input:
                    an_input = f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                else:
                    an_input = similar_cmd[0]
                print(f" Replacing by '{an_input}'.")
                oanda_controller.queue.insert(0, an_input)
            print("\n")
