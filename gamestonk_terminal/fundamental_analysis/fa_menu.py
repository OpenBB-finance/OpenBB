import argparse

from gamestonk_terminal.fundamental_analysis import alpha_vantage_api as av_api
from gamestonk_terminal.fundamental_analysis import business_insider_api as bi_api
from gamestonk_terminal.fundamental_analysis import (
    financial_modeling_prep_api as fmp_api,
)
from gamestonk_terminal.fundamental_analysis import finviz_api as fvz_api
from gamestonk_terminal.fundamental_analysis import market_watch_api as mw_api
from gamestonk_terminal.fundamental_analysis import yahoo_finance_api as yf_api
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from prompt_toolkit.completion import NestedCompleter


def print_fundamental_analysis(s_ticker, s_start, s_interval):
    """ Print help """

    s_intraday = (f"Intraday {s_interval}", "Daily")[s_interval == "1440min"]

    if s_start:
        print(f"\n{s_intraday} Stock: {s_ticker} (from {s_start.strftime('%Y-%m-%d')})")
    else:
        print(f"\n{s_intraday} Stock: {s_ticker}")

    print("\nFundamental Analysis:")  # https://github.com/JerBouma/FundamentalAnalysis
    print("   help          show this fundamental analysis menu again")
    print("   q             quit this menu, and shows back to main menu")
    print("   quit          quit to abandon program")
    print("")
    print("   screener      screen info about the company [Finviz]")
    print("   mgmt          management team of the company [Business Insider]")
    print("")
    print("Market Watch API")
    print("   income        income statement of the company")
    print("   balance       balance sheet of the company")
    print("   cash          cash flow statement of the company")
    print("")
    print("Yahoo Finance API")
    print("   info          information scope of the company")
    print("   shrs          shareholders of the company")
    print("   sust          sustainability values of the company")
    print("   cal           calendar earnings and estimates of the company")
    print("")
    print("Other Sources:")
    print(">  av            Alpha Vantage MENU")
    print(">  fmp           Financial Modeling Prep MENU")
    print("")
    return


def key_metrics_explained(l_args):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="info",
        description="""
            Provides information about main key metrics. Namely: EBITDA,
            EPS, P/E, PEG, FCF, P/B, ROE, DPR, P/S, Dividend Yield Ratio, D/E, and Beta.
        """,
    )

    try:
        (_, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}")

        filepath = "fundamental_analysis/key_metrics_explained.txt"
        with open(filepath) as fp:
            line = fp.readline()
            while line:
                print(f"{line.strip()}")
                line = fp.readline()
            print("")

    except Exception as e:
        print(e)
        print("ERROR!\n")
        return


# pylint: disable=too-many-branches
def fa_menu(s_ticker, s_start, s_interval):

    # Add list of arguments that the fundamental analysis parser accepts
    fa_parser = argparse.ArgumentParser(prog="fa", add_help=False)
    choices = [
        "help",
        "q",
        "quit",
        "screener",
        "income",
        "balance",
        "cash",
        "mgmt",
        "info",
        "shrs",
        "sust",
        "cal",
        "av",
        "fmp",
    ]
    fa_parser.add_argument("cmd", choices=choices)
    completer = NestedCompleter.from_nested_dict({c: None for c in choices})

    should_print_help = True

    # Loop forever and ever
    while True:
        if should_print_help:
            print_fundamental_analysis(s_ticker, s_start, s_interval)
            should_print_help = False

        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            as_input = session.prompt(
                f"{get_flair()} (fa)> ",
                completer=completer,
            )
        else:
            as_input = input(f"{get_flair()} (fa)> ")

        # Parse fundamental analysis command of the list of possible commands
        try:
            (ns_known_args, l_args) = fa_parser.parse_known_args(as_input.split())

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        if ns_known_args.cmd == "help":
            should_print_help = True

        elif ns_known_args.cmd == "q":
            # Just leave the FA menu
            return False

        elif ns_known_args.cmd == "quit":
            # Abandon the program
            return True

        # BUSINESS INSIDER API
        elif ns_known_args.cmd == "mgmt":
            bi_api.management(l_args, s_ticker)

        # FINVIZ API
        elif ns_known_args.cmd == "screener":
            fvz_api.screener(l_args, s_ticker)

        # MARKET WATCH API
        elif ns_known_args.cmd == "income":
            mw_api.income(l_args, s_ticker)

        elif ns_known_args.cmd == "balance":
            mw_api.balance(l_args, s_ticker)

        elif ns_known_args.cmd == "cash":
            mw_api.cash(l_args, s_ticker)

        # YAHOO FINANCE API
        elif ns_known_args.cmd == "info":
            yf_api.info(l_args, s_ticker)

        elif ns_known_args.cmd == "shrs":
            yf_api.shareholders(l_args, s_ticker)

        elif ns_known_args.cmd == "sust":
            yf_api.sustainability(l_args, s_ticker)

        elif ns_known_args.cmd == "cal":
            yf_api.calendar_earnings(l_args, s_ticker)

        # ALPHA VANTAGE API
        elif ns_known_args.cmd == "av":
            b_quit = av_api.menu(s_ticker, s_start, s_interval)

            if b_quit:
                return True
            else:
                should_print_help = True

        # FINANCIAL MODELING PREP API
        elif ns_known_args.cmd == "fmp":
            b_quit = fmp_api.menu(s_ticker, s_start, s_interval)

            if b_quit:
                return True
            else:
                should_print_help = True

        else:
            print("Command not recognized!")
