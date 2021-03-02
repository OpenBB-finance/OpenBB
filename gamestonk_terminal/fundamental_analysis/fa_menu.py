import argparse

from gamestonk_terminal.fundamental_analysis import alpha_vantage_api as av_api
from gamestonk_terminal.fundamental_analysis import (
    financial_modeling_prep_api as fmp_api,
)
from gamestonk_terminal.fundamental_analysis import finviz_api as fvz_api
from gamestonk_terminal.fundamental_analysis import market_watch_api as mw_api
from gamestonk_terminal.fundamental_analysis import business_insider_api as bi_api
from gamestonk_terminal.fundamental_analysis import yahoo_finance_api as yf_api


# -----------------------------------------------------------------------------------------------------------------------
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
    print("   assets        assets of the company")
    print("   liabilities   liabilities and shareholders equity of the company")
    print("   operating     cash flow operating activities of the company")
    print("   investing     cash flow investing activities of the company")
    print("   financing     cash flow financing activities of the company")
    print("")
    print("Yahoo Finance API")
    print("   info          information scope of the company")
    print("   shrs          hareholders of the company")
    print("   sust          sustainability values of the company")
    print("   cal           calendar earnings and estimates of the company")
    print("")
    print("Alpha Vantage API")
    print("   overview      overview of the company")
    print("   incom         income statements of the company")
    print("   balance       balance sheet of the company")
    print("   cash          cash flow of the company")
    print("   earnings      earnings dates and reported EPS")
    print("")
    print("Financial Modeling Prep API")
    print("   profile       profile of the company")
    print("   quote         quote of the company")
    print("   enterprise    enterprise value of the company over time")
    print("   dcf           discounted cash flow of the company over time")
    print("   inc           income statements of the company")
    print("   bal           balance sheet of the company")
    print("   cashf         cash flow of the company")
    print("   metrics       key metrics of the company")
    print("   ratios        financial ratios of the company")
    print("   growth        financial statement growth of the company")
    print("")
    return


# ---------------------------------------------------- INFO ----------------------------------------------------
# pylint: disable=unused-argument
def info(l_args, s_ticker):
    parser = argparse.ArgumentParser(
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
                print("{}".format(line.strip()))
                line = fp.readline()
            print("")

    except Exception as e:
        print(e)
        print("ERROR!\n")
        return


# ---------------------------------------------------- MENU ----------------------------------------------------
# pylint: disable=too-many-branches
def fa_menu(s_ticker, s_start, s_interval):

    # Add list of arguments that the fundamental analysis parser accepts
    fa_parser = argparse.ArgumentParser(prog="fa", add_help=False)
    fa_parser.add_argument(
        "cmd",
        choices=[
            "help",
            "q",
            "quit",  #
            "screener",  # Finviz
            "mgmt",  # Business Insider
            "info",
            "shrs",
            "sust",
            "cal",  # Yahoo Finance
            "income",
            "assets",
            "liabilities",
            "operating",
            "investing",
            "financing",  # MW
            "overview",
            "key",
            "incom",
            "balance",
            "cash",
            "earnings",  # AV
            "profile",
            "quote",
            "enterprise",
            "dcf",  # FMP
            "inc",
            "bal",
            "cashf",
            "metrics",
            "ratios",
            "growth",
        ],
    )  # FMP

    print_fundamental_analysis(s_ticker, s_start, s_interval)

    # Loop forever and ever
    while True:
        # Get input command from user
        as_input = input("> ")

        # Parse fundamental analysis command of the list of possible commands
        try:
            (ns_known_args, l_args) = fa_parser.parse_known_args(as_input.split())

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        # if ns_known_args.cmd == 'info':
        #    info(l_args, s_ticker)

        if ns_known_args.cmd == "help":
            print_fundamental_analysis(s_ticker, s_start, s_interval)

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

        elif ns_known_args.cmd == "assets":
            mw_api.assets(l_args, s_ticker)

        elif ns_known_args.cmd == "liabilities":
            mw_api.liabilities(l_args, s_ticker)

        elif ns_known_args.cmd == "operating":
            mw_api.operating(l_args, s_ticker)

        elif ns_known_args.cmd == "investing":
            mw_api.investing(l_args, s_ticker)

        elif ns_known_args.cmd == "financing":
            mw_api.financing(l_args, s_ticker)

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
        elif ns_known_args.cmd == "overview":
            av_api.overview(l_args, s_ticker)

        elif ns_known_args.cmd == "incom":
            av_api.income_statement(l_args, s_ticker)

        elif ns_known_args.cmd == "balance":
            av_api.balance_sheet(l_args, s_ticker)

        elif ns_known_args.cmd == "cash":
            av_api.cash_flow(l_args, s_ticker)

        elif ns_known_args.cmd == "earnings":
            av_api.earnings(l_args, s_ticker)

        # FINANCIAL MODELING PREP API
        # Details:
        elif ns_known_args.cmd == "profile":
            fmp_api.profile(l_args, s_ticker)

        elif ns_known_args.cmd == "quote":
            fmp_api.quote(l_args, s_ticker)

        elif ns_known_args.cmd == "enterprise":
            fmp_api.enterprise(l_args, s_ticker)

        elif ns_known_args.cmd == "dcf":
            fmp_api.discounted_cash_flow(l_args, s_ticker)

        # Financial statement:
        elif ns_known_args.cmd == "inc":
            fmp_api.income_statement(l_args, s_ticker)

        elif ns_known_args.cmd == "bal":
            fmp_api.balance_sheet(l_args, s_ticker)

        elif ns_known_args.cmd == "cashf":
            fmp_api.cash_flow(l_args, s_ticker)

        # Ratios:
        elif ns_known_args.cmd == "metrics":
            fmp_api.key_metrics(l_args, s_ticker)

        elif ns_known_args.cmd == "ratios":
            fmp_api.financial_ratios(l_args, s_ticker)

        elif ns_known_args.cmd == "growth":
            fmp_api.financial_statement_growth(l_args, s_ticker)

        else:
            print("Command not recognized!")
