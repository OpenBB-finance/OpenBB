""" Example or something

    Is this not informative enough?

    Load a specific stock
    Then apply a specific TA on it

    Do this because AlphaVantage only allows 5 API calls per minutes.
    This way we only need 1 call, and can apply TA to the result without
    using an API request.

    Finviz for data
    Multiple TA with kind stock

    Do my own personal Fundamental Analysis Dataframe
    Do option to explain important key metrics

    Do own personal Technical Analysis with multiple indicators perhaps?

    Split Menu into fa, ta and pred. Fundamental Analysis, Technical Analysis and Prediction, respectively.

"""

import argparse
import pandas as pd
from stock_market_helper_funcs import *
import command as cmd
from fundamental_analysis import menu as fam
from technical_analysis import menu as tam

# delete this important when automatic loading tesla
#i.e. when program is done
import config_bot as cfg
from alpha_vantage.timeseries import TimeSeries


# -----------------------------------------------------------------------------------------------------------------------
def main():
    """ Main function of the program
    """ 

    s_ticker = ""
    s_start = ""
    df_stock = pd.DataFrame()
    b_intraday = False
    s_interval = "1440min"

    # Set stock by default to speed up testing
    s_ticker = "NIO"
    s_start = datetime.strptime("2020-06-04", "%Y-%m-%d")
    ts = TimeSeries(key=cfg.API_KEY_ALPHAVANTAGE, output_format='pandas')
    df_stock, d_stock_metadata = ts.get_daily_adjusted(symbol=s_ticker, outputsize='full')  
    df_stock = df_stock[s_start:] 
    # Delete above in the future

    
    # Add list of arguments that the main parser accepts
    menu_parser = argparse.ArgumentParser(prog='stock_market_bot', add_help=False)
    menu_parser.add_argument('opt', choices=['gainers', 'sectors', 'view', 'clear', 'load', 
                                             'fa', 'ta', 'help', 'quit'])

    # Add list of arguments that the fundamental analysis parser accepts
    fa_parser = argparse.ArgumentParser(prog='fundamental_analysis', add_help=False)
    fa_parser.add_argument('fa', choices=['info', 'help', 'q', 'quit',
                                          'overview', 'key', 'income', 'balance', 'cash', 'earnings', # AV
                                          'profile', 'rating', 'quote', 'enterprise', 'dcf', # FMP
                                          'inc', 'bal', 'cashf', 'metrics', 'ratios', 'growth', # FMP
                                          'screener', 'insider', 'news', 'analyst', # Finviz
                                          'incom', 'assets']) # MW
                                             
    # Add list of arguments that the technical analysis parser accepts
    ta_parser = argparse.ArgumentParser(prog='technical_analysis', add_help=False)
    ta_parser.add_argument('ta', choices=['help', 'q', 'quit',
                                          'ema', 'sma', 'vwap', # overlap
                                          'cci', 'macd', 'rsi', 'stoch', # momentum
                                          'adx', 'aroon', # trend
                                          'bbands', # volatility
                                          'ad', 'obv']) # volume


    # Print first welcome message and help
    print("\nWelcome to Didier's Stock Market Bot\n")
    cmd.print_help(s_ticker, s_start, s_interval, b_is_stock_market_open())
    print("\n")

    # Loop forever and ever
    while True:
        # Get input command from user
        as_input = input('> ')
        
        # Parse main command of the list of possible commands
        try:
            (ns_known_args, l_args) = menu_parser.parse_known_args(as_input.split())

        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        # --------------------------------------------------- GAINERS --------------------------------------------------
        if ns_known_args.opt == 'gainers':
            cmd.gainers(l_args)

        # --------------------------------------------------- SECTORS --------------------------------------------------
        if ns_known_args.opt == 'sectors':
            cmd.sectors(l_args)

        # --------------------------------------------------- CLEAR ----------------------------------------------------
        elif ns_known_args.opt == 'clear':
            print("Clearing stock ticker to be used for analysis")
            s_ticker = ""
            s_start = ""

        # ---------------------------------------------------- LOAD ----------------------------------------------------
        elif ns_known_args.opt == 'load':
            [s_ticker, s_start, s_interval, df_stock] = cmd.load(l_args, s_ticker, s_start, s_interval, df_stock)

        # ---------------------------------------------------- VIEW ----------------------------------------------------
        elif ns_known_args.opt == 'view':
            cmd.view(l_args, s_ticker, s_start, s_interval, df_stock)

        # ---------------------------------------------------- HELP ----------------------------------------------------
        elif ns_known_args.opt == 'help':
            cmd.print_help(s_ticker, s_start, s_interval, b_is_stock_market_open())

        # ----------------------------------------------------- QUIT ----------------------------------------------------
        elif ns_known_args.opt == 'quit':
            print("Hope you made money today. Good bye my lover, good bye my friend.\n")
            return
        
        # ------------------------------------------- FUNDAMENTAL ANALYSIS ---------------------------------------------
        elif ns_known_args.opt == 'fa':
            b_quit = fam.fa_menu(fa_parser, s_ticker, s_start, s_interval)

            if b_quit:
                print("Hope you made money today. Good bye my lover, good bye my friend.\n")
                return
            else:
                cmd.print_help(s_ticker, s_start, s_interval, b_is_stock_market_open())

        # -------------------------------------------- TECHNICAL ANALYSIS ----------------------------------------------
        elif ns_known_args.opt == 'ta':
            b_quit = tam.ta_menu(ta_parser, df_stock, s_ticker, s_start, s_interval)

            if b_quit:
                print("Hope you made money today. Good bye my lover, good bye my friend.\n")
                return
            else:
                cmd.print_help(s_ticker, s_start, s_interval, b_is_stock_market_open())

        # ------------------------------------------------ PREDICTION --------------------------------------------------


        # --------------------------------------------------------------------------------------------------------------
        else:
            print('Shouldnt see this command!')

        print("")

if __name__ == "__main__":
    main()
