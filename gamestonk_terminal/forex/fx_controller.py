import argparse
from typing import List
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.forex import fx_view
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.due_diligence import news_view
from gamestonk_terminal.behavioural_analysis import stocktwits_view
from gamestonk_terminal.exploratory_data_analysis import eda_api
import pandas as pd

account = cfg.OANDA_ACCOUNT

class ForexController:
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
        "order",
        "load",
        "cancel",
        "positions",
        "closetrade",
        "trades",
        "candles",
        "pending",
        "calendar",
        "news",
        "bullbear",
        "messages",
        "edasummary",
    ]

    def __init__(self):
        """Construct Data"""
        self.fx_parser = argparse.ArgumentParser(add_help=False, prog="fx")
        self.fx_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.instrument = None

    @staticmethod
    def print_help():
        """Print help"""

        print("\nForex Mode:")
        print("    help          Show this menu again")
        print("    q             Quit this menu and goes back to main menu")
        print("    quit          Quit to abandon program")
        print("")
        print("    bullbear      Call bullbear from stocktwits")
        print("    cancel        Cancel a pending order by ID -i order ID")
        print("    candles       Show candles")
        print("    calendar      Show calendar")
        print("    closetrade    Close a trade by id")
        print("    list          List order history")
        print("    load          Load an instrument to use")
        print("    messages      Get messages from stocktwits")
        print("    news          Get news")
        print("    order         Place limit order -u # of units -p price")
        print("    orderbook     Print orderbook")
        print("    pending       Get information on pending orders")
        print("    positionbook  Print positionbook")
        print("    positions     Get open positions")
        print("    price         Shows price for selected instrument")
        print("    summary       Shows account summary")
        print("    trades        List open trades")
        print("")

    def switch(self, an_input: str):
        """Process and dispatch input
        Returns
        ______
        True, False, or None
        False - quit the menu
        True - quit the program
        None - continue in the menu
        """
        (known_args, other_args) = self.fx_parser.parse_known_args(an_input.split())

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

    def call_price(self, _):
        """Process Price Command"""
        fx_view.get_fx_price(account, self.instrument)

    def call_load(self, other_args):
        self.instrument = fx_view.load(other_args)

    def call_summary(self, _):
        """Process account summary command"""
        fx_view.get_account_summary(account)

    def call_orderbook(self, _):
        """Process Oanda Order Book"""
        fx_view.get_order_book(self.instrument)

    def call_positionbook(self, _):
        """Process Oanda Position Book"""
        fx_view.get_position_book(self.instrument)

    def call_list(self, other_args: List[str]):
        """Process list orders command"""
        fx_view.list_orders(account, other_args)

    def call_order(self, other_args: List[str]):
        """Place limit order"""
        fx_view.create_order(account, self.instrument, other_args)

    def call_cancel(self, other_args: List[str]):
        """Cancel pending order by ID"""
        fx_view.cancel_pending_order(account, other_args)

    def call_positions(self, _):
        """Get Open Positions"""
        fx_view.get_open_positions(account)

    def call_pending(self, _):
        """See up to 25 pending orders"""
        fx_view.get_pending_orders(account)

    def call_closetrade(self, other_args: List[str]):
        """Close a trade by id"""
        fx_view.close_trade(account, other_args)

    def call_candles(self, other_args: List[str]):
        fx_view.show_candles(account, self.instrument, other_args)

    def call_trades(self, _):
        """List open trades"""
        fx_view.get_open_trades(account)

    def call_calendar(self, other_args: List[str]):
        """Call calendar"""
        fx_view.calendar(self.instrument, other_args)

    def call_news(self, other_args: List[str]):
        news_view.news(other_args, self.instrument)

    def call_bullbear(self, other_args: List[str]):
        instrument = remove_underscore(self.instrument)
        stocktwits_view.bullbear(other_args, instrument)

    def call_messages(self, other_args: List[str]):
        instrument = remove_underscore(self.instrument)
        stocktwits_view.messages(other_args, instrument)

    def call_edasummary(self, other_args: List[str]):
        df = pd.read_csv(".candles.csv")
        eda_api.summary(other_args, df)


def remove_underscore(instrument):
    instrument_list = list(instrument)
    instrument_list.pop(3)
    adjusted_instrument = "".join(map(str, instrument_list))
    return adjusted_instrument


def menu():
    """Oanda Menu"""
    fx_controller = ForexController()
    fx_controller.call_help(None)
    while True:
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in fx_controller.CHOICES}
            )

            an_input = session.prompt(
                f"{get_flair()} (fx)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (fx)> ")

        try:
            process_input = fx_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exit\n")
            continue
