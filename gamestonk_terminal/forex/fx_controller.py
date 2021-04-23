import argparse
from typing import List
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.forex import fx_view
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.due_diligence import news_view, reddit_view
from gamestonk_terminal.behavioural_analysis import stocktwits_view
from gamestonk_terminal.exploratory_data_analysis import eda_api

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
        "edarolling",
        "edadecompose",
        "edacusum",
        "edahist",
        "reddit",
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
    def print_help(self):
        """Print help"""

        print("\nForex Mode:")
        print("    help          show this menu again")
        print("    q             quit this menu and goes back to main menu")
        print("    quit          quit to abandon program")
        print("")
        print("    summary       shows account summary")
        print("    calendar      show calendar")
        print("    list          list order history")
        print("    pending       get information on pending orders")
        print("    cancel        cancel a pending order by ID -i order ID")
        print("    positions     get open positions")
        print("    trades        list open trades")
        print("    closetrade    close a trade by id")
        print("")
        print(f"Loaded instrument: {self.instrument if self.instrument else ''}")
        print("")
        print("    load          load an instrument to use")
        if self.instrument:
            print("    candles       show candles")
            print("    price         shows price for selected instrument")
            print("    order         place limit order -u # of units -p price")
            print("    orderbook     print orderbook")
            print("    positionbook  print positionbook")
            print("    news          print news [News API]")
            print(
                "    bullbear      estimate quick sentiment from last 30 messages on stocktwits"
            )
            print(
                "    messages      output up to the 30 last messages on the stocktwits board"
            )
            print(
                "    reddit        search reddit for posts about the loaded instrument"
            )
            print(
                "    edasummary    brief summary statistics using exploratory data analysis"
            )
            print("    edarolling    rolling mean and std deviation")
            print(
                "    edadecompose  decomposition in cyclic-trend, season, and residuals"
            )
            print(
                "    edacusum      detects abrupt changes using cumulative sum algorithm"
            )
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
        self.print_help(self)

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - exit the program"""
        return True

    def call_price(self, other_args):
        """Process Price Command"""
        fx_view.get_fx_price(account, self.instrument, other_args)

    def call_load(self, other_args):
        self.instrument = fx_view.load(other_args)

    def call_summary(self, other_args):
        """Process account summary command"""
        fx_view.get_account_summary(account, other_args)

    def call_orderbook(self, other_args):
        """Process Oanda Order Book"""
        fx_view.get_order_book(self.instrument, other_args)

    def call_positionbook(self, other_args):
        """Process Oanda Position Book"""
        fx_view.get_position_book(self.instrument, other_args)

    def call_list(self, other_args: List[str]):
        """Process list orders command"""
        fx_view.list_orders(account, other_args)

    def call_order(self, other_args: List[str]):
        """Place limit order"""
        fx_view.create_order(account, self.instrument, other_args)

    def call_cancel(self, other_args: List[str]):
        """Cancel pending order by ID"""
        fx_view.cancel_pending_order(account, other_args)

    def call_positions(self, other_args):
        """Get Open Positions"""
        fx_view.get_open_positions(account, other_args)

    def call_pending(self, other_args):
        """See up to 25 pending orders"""
        fx_view.get_pending_orders(account, other_args)

    def call_closetrade(self, other_args: List[str]):
        """Close a trade by id"""
        fx_view.close_trade(account, other_args)

    def call_candles(self, other_args: List[str]):
        fx_view.show_candles(account, self.instrument, other_args)

    def call_trades(self, other_args):
        """List open trades"""
        fx_view.get_open_trades(account, other_args)

    def call_calendar(self, other_args: List[str]):
        """Call calendar"""
        fx_view.calendar(self.instrument, other_args)

    def call_news(self, other_args: List[str]):
        """Call news [News API]"""
        news_view.news(other_args, self.instrument)

    def call_bullbear(self, other_args):
        """Call bullbear fom stocktwits"""
        instrument = fx_view.format_instrument(self.instrument, " ")
        stocktwits_view.bullbear(other_args, instrument)

    def call_messages(self, other_args):
        """Call messages from stocktwits"""
        instrument = fx_view.format_instrument(self.instrument, " ")
        stocktwits_view.messages(other_args, instrument)

    def call_edasummary(self, other_args: List[str]):
        df = fx_view.get_candles_dataframe(account, self.instrument, None)
        eda_api.summary(other_args, df)

    def call_edarolling(self, other_args: List[str]):
        df = fx_view.get_candles_dataframe(account, self.instrument, None)
        df.columns = ["Open", "Low", "High", "5. adjusted close", "Volume"]
        eda_api.rolling(other_args, self.instrument, df)

    def call_edadecompose(self, other_args: List[str]):
        df = fx_view.get_candles_dataframe(account, self.instrument, None)
        df.columns = ["Open", "Low", "High", "5. adjusted close", "Volume"]
        eda_api.decompose(other_args, self.instrument, df)

    def call_edacusum(self, other_args: List[str]):
        df = fx_view.get_candles_dataframe(account, self.instrument, None)
        df.columns = ["Open", "Low", "High", "5. adjusted close", "Volume"]
        eda_api.cusum(other_args, self.instrument, df)

    def call_reddit(self, other_args: List[str]):
        instrument = fx_view.format_instrument(self.instrument, " ")
        reddit_view.due_diligence(other_args, instrument)


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
