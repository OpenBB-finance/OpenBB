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

from due_diligence import finviz_api as fvz_api
from due_diligence import market_watch_api as mw_api
from due_diligence import reddit_api as r_api
from due_diligence import quandl_api as q_api
from due_diligence import financial_modeling_prep_api as fmp_api
from due_diligence import business_insider_api as bi_api


# -----------------------------------------------------------------------------------------------------------------------
def print_due_diligence(s_ticker, s_start, s_interval):
    """ Print help """

    s_intraday = (f'Intraday {s_interval}', 'Daily')[s_interval == "1440min"]

    if s_start:
        print(f"\n{s_intraday} Stock: {s_ticker} (from {s_start.strftime('%Y-%m-%d')})")
    else:
        print(f"\n{s_intraday} Stock: {s_ticker}")

    print("\nDue Diligence:")
    print("   help          show this fundamental analysis menu again")
    print("   q             quit this menu, and shows back to main menu")
    print("   quit          quit to abandon program")
    print("")
    print("   news          latest news of the company [Finviz]")
    print("   red           gets due diligence from another user's post [Reddit]")
    print("   analyst       analyst prices and ratings of the company [Finviz]")
    print("   rating        rating of the company from strong sell to strong buy [FMP]")
    print("   pt            price targets over time [Business Insider]")
    print("   insider       insider trading of the company [Finviz]")
    print("   sec           SEC filings [Market Watch]")
    print("   short         short interest [Quandl]")
    print("   warnings      company warnings according to Sean Seah book [Market Watch]")
    print("")
    return


# ---------------------------------------------------- MENU ----------------------------------------------------
def dd_menu(df_stock, s_ticker, s_start, s_interval):

    # Add list of arguments that the due diligence parser accepts
    dd_parser = argparse.ArgumentParser(prog='due_diligence', add_help=False)
    dd_parser.add_argument('cmd', choices=['info', 'help', 'q', 'quit', 
                                           'red', # Reddit
                                           'short', # Quandl
                                           'rating', # FMP
                                           'pt', # BI
                                           'insider', 'news', 'analyst', # Finviz
                                           'warnings', 'sec']) # MW

    print_due_diligence(s_ticker, s_start, s_interval)

    # Loop forever and ever
    while True:
        # Get input command from user
        as_input = input('> ')
        
        # Parse due diligence command of the list of possible commands
        try:
            (ns_known_args, l_args) = dd_parser.parse_known_args(as_input.split())

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue
            
        if ns_known_args.cmd == 'help':
            print_due_diligence(s_ticker, s_start, s_interval)

        elif ns_known_args.cmd == 'q':
            # Just leave the DD menu
            return False

        elif ns_known_args.cmd == 'quit':
            # Abandon the program
            return True

        # REDDIT API
        elif ns_known_args.cmd == 'red':
            r_api.due_diligence(l_args, s_ticker)
        
        # FINVIZ API
        elif ns_known_args.cmd == 'insider':
            fvz_api.insider(l_args, s_ticker)

        elif ns_known_args.cmd == 'news':
            fvz_api.news(l_args, s_ticker)

        elif ns_known_args.cmd == 'analyst':
            fvz_api.analyst(l_args, s_ticker)

        # BUSINESS INSIDER API
        elif ns_known_args.cmd == 'pt':
            bi_api.price_target_from_analysts(l_args, df_stock, s_ticker, s_start, s_interval)

        # FINANCIAL MODELING PREP API
        elif ns_known_args.cmd == 'rating':
            fmp_api.rating(l_args, s_ticker)

        # MARKET WATCH API
        elif ns_known_args.cmd == 'sec':
            mw_api.sec_fillings(l_args, s_ticker)

        elif ns_known_args.cmd == 'warnings':
            mw_api.sean_seah_warnings(l_args, s_ticker)

        # QUANDL API
        elif ns_known_args.cmd == 'short':
            q_api.short_interest(l_args, s_ticker, s_start)

        else:
            print("Command not recognized!")