import argparse
from datetime import timedelta, datetime
from typing import List

import pandas as pd
from prompt_toolkit.completion import NestedCompleter
from colorama import Style
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.forex.oanda import oanda_controller
from gamestonk_terminal.forex import av_view, av_model


# from gamestonk_terminal.forex.exploratory_data_analysis import eda_controller
from gamestonk_terminal.helper_funcs import (
    get_flair,
    system_clear,
    MENU_GO_BACK,
    MENU_QUIT,
    MENU_RESET,
    parse_known_args_and_warn,
    try_except,
    valid_date,
)
from gamestonk_terminal.menu import session


class ForexController:
    """Forex Controller class"""

    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
        "reset",
    ]

    CHOICES_COMMANDS = ["select", "load", "quote", "candle"]
    CHOICES_MENUS = ["oanda"]

    CHOICES += CHOICES_COMMANDS
    CHOICES += CHOICES_MENUS

    def __init__(self):
        """Construct Data"""
        self.fx_parser = argparse.ArgumentParser(add_help=False, prog="forex")
        self.fx_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.from_symbol = "USD"
        self.to_symbol = ""
        self.data = pd.DataFrame()

    def print_help(self):
        """Print help"""
        dim_bool = self.from_symbol and self.to_symbol
        help_str = f"""
What would you like to do?
    cls           clear screen
    ?/help        show this menu again
    q             quit this menu and goes back to main menu
    quit          quit to abandon program
    reset         reset terminal and reload configs

    select        select fx pair

From: {None or self.from_symbol}
To:   {None or self.to_symbol}
{Style.DIM if not dim_bool else ""}
AlphaVantage:
    quote         get last quote
    load          get historical data
    candle        show candle plot for loaded data
{Style.RESET_ALL}
Brokerages:
>   oanda         access oanda menu
 """
        print(help_str)

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
            system_clear()
            return None

        return getattr(
            self, "call_" + known_args.cmd, lambda: "command not recognized!"
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

    @try_except
    def call_select(self, other_args: List[str]):
        """Process select command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="select",
            description="Select Forex pair in the form of TO -f FROM",
        )
        parser.add_argument(
            "-t",
            "--to",
            help="To currency",
            type=av_model.check_valid_forex_currency,
            dest="to_symbol",
        )
        parser.add_argument(
            "-f",
            "--from",
            help="From currency",
            type=av_model.check_valid_forex_currency,
            dest="from_symbol",
            default=None,
        )

        if (
            other_args
            and "-f" not in other_args[0]
            and "--from" not in other_args[0]
            and "-t" not in other_args
            and "-h" not in other_args
        ):
            other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        self.to_symbol = ns_parser.to_symbol
        if ns_parser.from_symbol:
            self.from_symbol = ns_parser.from_symbol
        print("")

    @try_except
    def call_load(self, other_args: List[str]):
        """Process select command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load historical exchange rate data.",
        )
        parser.add_argument(
            "-r",
            "--resolution",
            choices=["i", "d", "w", "m"],
            default="d",
            help="Resolution of data.  Can be intraday, daily, weekly or monthly",
            dest="resolution",
        )
        parser.add_argument(
            "-i",
            "--interval",
            choices=[1, 5, 15, 30, 60],
            default="5",
            help="Interval of intraday data.  Can be 1, 5, 15, 30 or 60.",
            dest="interval",
        )
        parser.add_argument(
            "-s",
            "--start_date",
            default=(datetime.now() - timedelta(days=366)),
            type=valid_date,
            help="Start date of data.",
            dest="start_date",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if not self.to_symbol or not self.from_symbol:
            print(
                "Make sure both a to symbol and a from symbol are supplied using <select> \n"
            )
            return

        self.data = av_model.get_historical(
            to_symbol=self.to_symbol,
            from_symbol=self.from_symbol,
            resolution=ns_parser.resolution,
            interval=ns_parser.interval,
            start_date=ns_parser.start_date.strftime("%Y-%m-%d"),
        )
        print("")

    @try_except
    def call_candle(self, other_args: List[str]):
        """Process quote command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="candle",
            description="Show candle for loaded fx data",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if self.data.empty:
            print("No forex historical data loaded.  Load first using <load>.")
            return

        av_view.display_candle(self.data, self.to_symbol, self.from_symbol)

    @try_except
    def call_quote(self, other_args: List[str]):
        """Process quote command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="quote",
            description="Get current exchange rate quote",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if not self.to_symbol or not self.from_symbol:
            print(
                "Make sure both a to symbol and a from symbol are supplied using <select> \n"
            )
            return

        av_view.display_quote(self.to_symbol, self.from_symbol)

    # pylint: disable=inconsistent-return-statements
    def call_oanda(self, _):
        ret = oanda_controller.menu()
        if ret:
            return True
        self.print_help()

    # TODO: Add news and reddit commands back

    # def call_eda(self, _):
    #    try:
    #        df = fx_view.get_candles_dataframe(account, self.instrument, None)
    #        df = df.rename(columns={"Close": "Adj Close"})
    #        instrument = self.instrument
    #        s_start = pd.to_datetime(df.index.values[0])
    #        s_interval = "1440min"
    #        eda_controller.menu(df, instrument, s_start, s_interval)
    #    except AttributeError:
    #        print("No data found, do you have your oanda API keys set?")

    # def call_ba(self, _):
    #    instrument = fx_view.format_instrument(self.instrument, " ")
    #    try:
    #        df = fx_view.get_candles_dataframe(account, self.instrument, None)
    #        s_start = pd.to_datetime(df.index.values[0])
    #        ba_controller.menu(instrument, s_start)
    #    except AttributeError:
    #        print("No data found, do you have your oanda API keys set?")


def menu():
    """Forex Menu"""
    fx_controller = ForexController()
    fx_controller.call_help(None)
    while True:
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in fx_controller.CHOICES}
            )

            an_input = session.prompt(
                f"{get_flair()} (forex)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (forex)> ")

        try:
            process_input = fx_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exit\n")
            continue
