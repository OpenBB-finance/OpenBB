import FundamentalAnalysis as fa
from alpha_vantage.fundamentaldata import FundamentalData
import config_bot as cfg
import argparse
import datetime
from datetime import datetime
from stock_market_helper_funcs import *
import pandas as pd
import json
import requests
from pandas.io.json import json_normalize

from fundamental_analysis import alpha_vantage_api as av_api
from fundamental_analysis import financial_modeling_prep_api as fmp_api
from fundamental_analysis import finviz_api as fvz_api
from fundamental_analysis import market_watch_api as mw_api


# -----------------------------------------------------------------------------------------------------------------------
def print_fundamental_analysis(s_ticker, s_start, s_interval):
    """ Print help """

    s_intraday = (f'Intraday {s_interval}', 'Daily')[s_interval == "1440min"]

    if s_start:
        print(f"\n{s_intraday} Stock: {s_ticker} (from {s_start.strftime('%Y-%m-%d')})")
    else:
        print(f"\n{s_intraday} Stock: {s_ticker}")

    print("\nFundamental Analysis:") # https://github.com/JerBouma/FundamentalAnalysis
    print("   info          provides information on main key metrics of company")
    print("   help          show this fundamental analysis menu again")
    print("   q             quit this menu, and shows back to main menu")
    print("   quit          quit to abandon program")
    print("")
    print("   warnings      company warnings according to Sean Seah book [Market Watch]")
    print("\nFinviz API")
    print("   screener      screen info about the company")
    print("   insider       insider trading of the company")
    print("   news          latest news of the company")
    print("   analyst       analyst prices and ratings of the company")
    print("\nMarket Watch BS")
    print("   incom         income statement of the company")
    print("   assets        assets of the company")
    print("   liabilities   liabilities and shareholders equity of the company")
    print("   operating     cash flow operating activities of the company")
    print("   investing     cash flow investing activities of the company")
    print("   financing     cash flow financing activities of the company")
    print("   sec           SEC filings")
    print("")
    print("   more          more finance data from Alpha Vantage and Financial Modeling Prep")
    print("")
    return


# -----------------------------------------------------------------------------------------------------------------------
def print_more_fundamental_analysis():
    """ Print help """

    print("\nMore Fundamental Analysis:") 
    print("   help          show this more fundamental analysis menu again")
    print("   q             quit this menu, and shows back main fundamental analysis menu")
    print("   quit          quit to abandon program")
    print("\nAlpha Vantage API")
    print("   overview      overview of the company")
    print("   income        income statements of the company")
    print("   balance       balance sheet of the company")
    print("   cash          cash flow of the company")
    print("   earnings      earnings dates and reported EPS")
    print("\nFinancial Modeling Prep API")
    print("   profile       profile of the company")
    print("   rating        rating of the company from strong sell to strong buy")
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


# ---------------------------------------------------- INFO ----------------------------------------------------
def info(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='info', 
                                     description="""Provides information about main key metrics. Namely: EBITDA,
                                     EPS, P/E, PEG, FCF, P/B, ROE, DPR, P/S, Dividend Yield Ratio, D/E, and Beta.""")
        
    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}")

        filepath = 'fundamental_analysis/key_metrics_explained.txt'
        with open(filepath) as fp:
            line = fp.readline()
            while line:
                print("{}".format(line.strip()))
                line = fp.readline()
            print("")

    except:
        print("ERROR!\n")
        return
    

# ---------------------------------------------------- MENU ----------------------------------------------------
def fa_menu(s_ticker, s_start, s_interval):

    # Add list of arguments that the fundamental analysis parser accepts
    fa_parser = argparse.ArgumentParser(prog='fundamental_analysis', add_help=False)
    fa_parser.add_argument('fa', choices=['info', 'warnings', 'help', 'q', 'quit', 'more',
                                          'screener', 'insider', 'news', 'analyst', # Finviz
                                          'income', 'assets', 'liabilities', 'operating', 'investing', 'financing', 'sec']) # MW

    print_fundamental_analysis(s_ticker, s_start, s_interval)

    # Loop forever and ever
    while True:
        # Get input command from user
        as_input = input('> ')
        
        # Parse fundamental analysis command of the list of possible commands
        try:
            (ns_known_args, l_args) = fa_parser.parse_known_args(as_input.split())

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        if ns_known_args.fa == 'info':
            info(l_args, s_ticker)
            
        elif ns_known_args.fa == 'help':
            print_fundamental_analysis(s_ticker, s_start, s_interval)

        elif ns_known_args.fa == 'q':
            # Just leave the FA menu
            return False

        elif ns_known_args.fa == 'quit':
            # Abandon the program
            return True

        elif ns_known_args.fa == 'warnings':
            mw_api.sean_seah_warnings(l_args, s_ticker)
        
        # -------------------------------------------------- FINVIZ -----------------------------------------------
        elif ns_known_args.fa == 'screener':
            fvz_api.screener(l_args, s_ticker)

        elif ns_known_args.fa == 'insider':
            fvz_api.insider(l_args, s_ticker)

        elif ns_known_args.fa == 'news':
            fvz_api.news(l_args, s_ticker)

        elif ns_known_args.fa == 'analyst':
            fvz_api.analyst(l_args, s_ticker)

        # ------------------------------------------------ MARKET WATCH ---------------------------------------------
        elif ns_known_args.fa == 'income':
            mw_api.income(l_args, s_ticker)

        elif ns_known_args.fa == 'assets':
            mw_api.assets(l_args, s_ticker)

        elif ns_known_args.fa == 'liabilities':
            mw_api.liabilities(l_args, s_ticker)

        elif ns_known_args.fa == 'operating':
            mw_api.operating(l_args, s_ticker)

        elif ns_known_args.fa == 'investing':
            mw_api.investing(l_args, s_ticker)

        elif ns_known_args.fa == 'financing':
            mw_api.financing(l_args, s_ticker)

        elif ns_known_args.fa == 'sec':
            mw_api.sec_fillings(l_args, s_ticker)

        # --------------------------------------------- MORE FUNDAMENTAL ANALYSIS ---------------------------------------------
        elif ns_known_args.fa == 'more':

            # Add list of arguments that the more fundamental analysis parser accepts
            mfa_parser = argparse.ArgumentParser(prog='more_fundamental_analysis', add_help=False)
            mfa_parser.add_argument('mfa', choices=['help', 'q', 'quit',
                                                    'overview', 'key', 'income', 'balance', 'cash', 'earnings', # AV
                                                    'profile', 'rating', 'quote', 'enterprise', 'dcf', # FMP
                                                    'inc', 'bal', 'cashf', 'metrics', 'ratios', 'growth']) # FMP

            print_more_fundamental_analysis()

            # Loop forever and ever
            while True:
                # Get input command from user
                as_input = input('> ')
                
                # Parse fundamental analysis command of the list of possible commands
                try:
                    (ns_known_args, l_args) = mfa_parser.parse_known_args(as_input.split())

                except SystemExit:
                    print("The command selected doesn't exist\n")
                    continue

                if ns_known_args.mfa == 'help':
                    print_more_fundamental_analysis()

                elif ns_known_args.mfa == 'q':
                    # Just leave the more FA menu
                    print_fundamental_analysis(s_ticker, s_start, s_interval)
                    break

                elif ns_known_args.mfa == 'quit':
                    # Abandon the program
                    return True

                # ----------------------------------------------- ALPHA VANTAGE ----------------------------------------------
                elif ns_known_args.mfa == 'overview':
                    av_api.overview(l_args, s_ticker)

                elif ns_known_args.mfa == 'income':
                    av_api.income_statement(l_args, s_ticker)

                elif ns_known_args.mfa == 'balance':
                    av_api.balance_sheet(l_args, s_ticker)

                elif ns_known_args.mfa == 'cash':
                    av_api.cash_flow(l_args, s_ticker)

                elif ns_known_args.mfa == 'earnings':
                    av_api.earnings(l_args, s_ticker)

                # -------------------------------------------- FINANCIAL MODELING PREP -----------------------------------------
                # Details:
                elif ns_known_args.mfa == 'profile':
                    fmp_api.profile(l_args, s_ticker)

                elif ns_known_args.mfa == 'rating':
                    fmp_api.rating(l_args, s_ticker)

                elif ns_known_args.mfa == 'quote':
                    fmp_api.quote(l_args, s_ticker)
                
                elif ns_known_args.mfa == 'enterprise':
                    fmp_api.enterprise(l_args, s_ticker)

                elif ns_known_args.mfa == 'dcf':
                    fmp_api.discounted_cash_flow(l_args, s_ticker)

                # Financial statement:
                elif ns_known_args.mfa == 'inc':
                    fmp_api.income_statement(l_args, s_ticker)

                elif ns_known_args.mfa == 'bal':
                    fmp_api.balance_sheet(l_args, s_ticker)

                elif ns_known_args.mfa == 'cashf':
                    fmp_api.cash_flow(l_args, s_ticker)

                # Ratios:
                elif ns_known_args.mfa == 'metrics':
                    fmp_api.key_metrics(l_args, s_ticker)

                elif ns_known_args.mfa == 'ratios':
                    fmp_api.financial_ratios(l_args, s_ticker)

                elif ns_known_args.mfa == 'growth':
                    fmp_api.financial_statement_growth(l_args, s_ticker)

                # ------------------------------------------------------------------------------------------------------------
                else:
                    print("Command not recognized!")

        # ------------------------------------------------------------------------------------------------------------
        else:
            print("Command not recognized!")