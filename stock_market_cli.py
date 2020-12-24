""" Example or something

    Is this not informative enough?

    Load a specific stock
    Then apply a specific TA on it

    Do this because AlphaVantage only allows 5 API calls per minutes.
    This way we only need 1 call, and can apply TA to the result without
    using an API request.

    Finviz for data

"""

from alpha_vantage.timeseries import TimeSeries
import argparse
import config_bot as cfg
import pandas as pd
import pandas_ta as ta
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

from stock_market_helper_funcs import *
import stock_market_menu as smm
import stock_market_technical_analysis as smta



# -----------------------------------------------------------------------------------------------------------------------
def print_help(s_ticker, s_start, b_is_market_open):
    """ Print help
    """
    print("What do you want to do?")

    print("\nMenu:")
    print("   gainers     show latest top gainers")
    print("   view        view and load a specific stock ticker for technical analysis")
    print("   clear       clear a specific stock ticker from technical analysis")
    print("   load        load a specific stock ticker for technical analysis")
    print("   help        help to see this menu again")
    print("   quit        to abandon the program")

    if s_ticker and s_start:
        print(f"\n-----> {s_ticker} starting at {s_start.strftime('%Y-%m-%d')} <-----")
    elif s_ticker:
        print(f"\n-----> {s_ticker} <-----")
    else:
        print("\n-----> ? <-----")

    print("\nFundamental Analysis:")
    print("   example         not yet covered")

    print("\nTechnical Analysis:")
    print("   sma         simple moving average")
    print("   ema         exponential moving average")

    print("\nPrediction:")
    print("   ma")
    print("   ema")
    print("   lr")
    print("   knn")
    print("   arima")
    print("   rnn")
    print("   lstm")
    print("   prophet")

    print(f"\nMarket {('Closed', 'Open')[b_is_market_open]}. Play stocks:")
    print("Stock name, and how much money to bet?")


# -----------------------------------------------------------------------------------------------------------------------
def main():
    """ Main function of the program
    """ 

    # temporary
    #parser.add_argument('-a', action="store_true", default=False, help='example of flag')
    #parser.add_argument('-b', action="store", dest="b", help='example of string')
    #parser.add_argument('-c', action="store", dest="c", type=int, help='example of int')

    s_ticker = ""
    s_start = ""
    df_stock = pd.DataFrame()

    main_parser = argparse.ArgumentParser(prog='stock_market_bot', add_help=False)

    # Add list of arguments that the main parser accepts
    main_parser.add_argument('cmd', choices=['quit', 'help', 'gainers' ,'view', 'load', 'clear', 'sma', 'ema'])

    # Print first welcome message and help
    print("\nWelcome to Didier's Stock Market Bot\n")
    print_help(s_ticker, s_start, b_is_stock_market_open())
    print("\n")

    # Loop forever and ever
    while True:
        # Get input command from user
        as_input = input('> ')
        
        # Parse main command of the list of possible commands
        try:
            (ns_known_args, l_args) = main_parser.parse_known_args(as_input.split())
        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------- MENU -----------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        # --------------------------------------------------- GAINERS --------------------------------------------------
        if ns_known_args.cmd == 'gainers':
            smm.gainers(l_args)
            continue

        # --------------------------------------------------- CLEAR ----------------------------------------------------
        elif ns_known_args.cmd == 'clear':
            print("Clearing stock ticker to be used for analysis")
            s_ticker = ""
            s_start = ""

        # ---------------------------------------------------- LOAD ----------------------------------------------------
        elif ns_known_args.cmd == 'load':
            [s_ticker, s_start, df_stock] = smm.load(l_args, s_ticker, s_start, df_stock)
            continue

        # ---------------------------------------------------- VIEW ----------------------------------------------------
        elif ns_known_args.cmd == 'view':
            smm.view(l_args, s_ticker, s_start)
            continue

         # ---------------------------------------------------- HELP ----------------------------------------------------
        elif ns_known_args.cmd == 'help':
            print_help(s_ticker, s_start, b_is_stock_market_open())

        # ----------------------------------------------------- QUIT ----------------------------------------------------
        elif ns_known_args.cmd == 'quit':
            print("Hope you made money today. Good bye my lover, good bye my friend.\n")
            break
        
        # --------------------------------------------------------------------------------------------------------------
        # ------------------------------------------- FUNDAMENTAL ANALYSIS ---------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        # --------------------------------------------------------------------------------------------------------------
        # -------------------------------------------- TECHNICAL ANALYSIS ----------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        # --------------------------------------------------------------------------------------------------------------
        # ------------------------------------------------ PREDICTION --------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        # ---------------------------------------------------- SMA ----------------------------------------------------
        elif ns_known_args.cmd == 'sma':
            [s_ticker, s_start] = smta.sma(l_args, s_ticker, s_start)
            continue

        # ---------------------------------------------------- EMA ----------------------------------------------------
        elif ns_known_args.cmd == 'ema':
            [s_ticker, s_start] = smta.ema(l_args, s_ticker, s_start)
            continue
        
       
            
        else:
            print('Shouldnt see this command!')

        print("\n")

if __name__ == "__main__":
    main()
