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

from technical_analysis import overlap as ta_overlap
from technical_analysis import momentum as ta_momentum
from technical_analysis import trend as ta_trend
from technical_analysis import volatility as ta_volatility
from technical_analysis import volume as ta_volume

# -----------------------------------------------------------------------------------------------------------------------
def print_technical_analysis(s_ticker, s_start, s_interval):
    """ Print help """

    s_intraday = (f'Intraday {s_interval}', 'Daily')[s_interval == "1440min"]

    if s_start:
        print(f"\n{s_intraday} Stock: {s_ticker} (from {s_start.strftime('%Y-%m-%d')})")
    else:
        print(f"\n{s_intraday} Stock: {s_ticker}")

    print("\nTechnical Analysis:") # https://github.com/twopirllc/pandas-ta
    print("   help        show this technical analysis menu again")
    print("   q           quit this menu, and shows back to main menu")
    print("   quit        quit to abandon program")
    print("overlap:")
    print("   ema         exponential moving average")
    print("   sma         simple moving average")
    if s_interval != "1440min":
        print("   vwap        volume weighted average price")
    print("momentum:")
    print("   cci         commodity channel index")
    print("   macd        moving average convergence/divergence")
    print("   rsi         relative strength index")
    print("   stoch       stochastic oscillator")
    print("trend:")
    print("   adx         average directional movement index")
    print("   aroon       aroon indicator")
    print("volatility:")
    print("   bbands      bollinger bands")
    print("volume:")
    print("   ad          chaikin accumulation/distribution line values")
    print("   obv         on balance volume")
    print("")


# ---------------------------------------------------- MENU ----------------------------------------------------
def ta_menu(ta_parser, df_stock, s_ticker, s_start, s_interval):

    print_technical_analysis(s_ticker, s_start, s_interval)

    # Loop forever and ever
    while True:
        # Get input command from user
        as_input = input('> ')
        
        # Parse fundamental analysis command of the list of possible commands
        try:
            (ns_known_args, l_args) = ta_parser.parse_known_args(as_input.split())

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        if ns_known_args.ta == 'help':
            print_technical_analysis(s_ticker, s_start, s_interval)

        elif ns_known_args.ta == 'q':
            # Just leave the FA menu
            return False

        elif ns_known_args.ta == 'quit':
            # Abandon the program
            return True

        # -------------------------------------------------- OVERLAP --------------------------------------------------
        elif ns_known_args.ta == 'ema':
            ta_overlap.ema(l_args, s_ticker, s_interval, df_stock)

        elif ns_known_args.ta == 'sma':
            ta_overlap.sma(l_args, s_ticker, s_interval, df_stock)

        elif ns_known_args.ta == 'vwap':
            ta_overlap.vwap(l_args, s_ticker, s_interval, df_stock)

        # --------------------------------------------------- MOMENTUM ---------------------------------------------------
        elif ns_known_args.ta == 'cci':
            ta_momentum.cci(l_args, s_ticker, s_interval, df_stock)

        elif ns_known_args.ta == 'macd':
            ta_momentum.macd(l_args, s_ticker, s_interval, df_stock)

        elif ns_known_args.ta == 'rsi':
            ta_momentum.rsi(l_args, s_ticker, s_interval, df_stock)

        elif ns_known_args.ta == 'stoch':
            ta_momentum.stoch(l_args, s_ticker, s_interval, df_stock)
            
        # ---------------------------------------------------- TREND ----------------------------------------------------
        elif ns_known_args.ta == 'adx':
            ta_trend.adx(l_args, s_ticker, s_interval, df_stock)

        elif ns_known_args.ta == 'aroon':
            ta_trend.aroon(l_args, s_ticker, s_interval, df_stock)

        # -------------------------------------------------- VOLATILITY --------------------------------------------------
        elif ns_known_args.ta == 'bbands':
            ta_volatility.bbands(l_args, s_ticker, s_interval, df_stock)

        # ---------------------------------------------------- VOLUME ----------------------------------------------------
        elif ns_known_args.ta == 'ad':
            ta_volume.ad(l_args, s_ticker, s_interval, df_stock)

        elif ns_known_args.ta == 'obv':
            ta_volume.obv(l_args, s_ticker, s_interval, df_stock)

        # ------------------------------------------------------------------------------------------------------------
        else:
            print("Command not recognized!")
