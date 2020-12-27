""" Example or something

    Is this not informative enough?

    Load a specific stock
    Then apply a specific TA on it

    Do this because AlphaVantage only allows 5 API calls per minutes.
    This way we only need 1 call, and can apply TA to the result without
    using an API request.

    Finviz for data

    Check AlphaVantage for TA as well.
    Add s_ylabel and s_legend to plot_ta or plot_stock_ta

     Daily Stock vs Intraday 5min Stock
     Only show menu that allow daily TA or intraday TA,
    i.e. if daily Stock don't show VWAP bc doesn't make sense!
     Fix the 'help' params

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
import stock_market_fundamental_analysis as smfa

# -----------------------------------------------------------------------------------------------------------------------
def print_help(s_ticker, s_start, s_interval, b_is_market_open):
    """ Print help
    """
    print("What do you want to do?")

    print("\nMenu:")
    print("   gainers     show latest top gainers")
    print("   view        view and load a specific stock ticker for technical analysis")
    print("   clear       clear a specific stock ticker from analysis")
    print("   load        load a specific stock ticker for analysis")
    print("   help        help to see this menu again")
    print("   quit        to abandon the program")

    s_intraday = (f'Intraday {s_interval}', 'Daily')[s_interval == "1440min"]

    if s_ticker and s_start:
        print(f"\n{s_intraday} Stock: {s_ticker} (from {s_start.strftime('%Y-%m-%d')})")
    elif s_ticker:
        print(f"\n{s_intraday} Stock: {s_ticker}")
    else:
        print("\nStock: ?")

    if s_ticker:
        print("\nFundamental Analysis:")
        #print("- details - ")
        print("   ratings     company ratings from strong sell to strong buy")
        # print("- financial statement -")
        print("   income      income statements of the company (default: AV)")
        print("   balance     balance sheet of the company (default: AV)")
        print("   cash        cash flow of the company (default: AV)")
        #print("- ratios -")
        print("   metrics     key metrics of the company")

        print("\nTechnical Analysis:")
        print("   sma         simple moving average")
        print("   ema         exponential moving average")
        print("   macd        moving average convergence/divergence")
        print("   stoch       stochastic oscillator")
        print("   rsi         relative strength index")
        print("   adx         average directional movement index")
        print("   cci         commodity channel index")
        print("   aroon       aroon indicator")
        print("   bbands      bollinger bands")
        print("   ad          chaikin accumulation/distribution line values")
        print("   obv         on balance volume")
        if s_interval != "1440min":
            print("   vwap        volume weighted average price")

        '''
        print("\nPrediction:")
        print("   ma")
        print("   ema")
        print("   lr")
        print("   knn")
        print("   arima")
        print("   rnn")
        print("   lstm")
        print("   prophet")
        '''
    print(f"\nMarket {('CLOSED', 'OPEN')[b_is_market_open]}.")
    print("Stonks and things")


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
    s_ticker = "TSLA"
    s_start = datetime.strptime("2020-06-04", "%Y-%m-%d")
    ts = TimeSeries(key=cfg.API_KEY_ALPHAVANTAGE, output_format='pandas')
    df_stock, d_stock_metadata = ts.get_daily_adjusted(symbol=s_ticker, outputsize='full')  
    df_stock = df_stock[s_start:] 
    # Delete above in the future

    main_parser = argparse.ArgumentParser(prog='stock_market_bot', add_help=False)

    # Add list of arguments that the main parser accepts
    main_parser.add_argument('cmd', choices=['quit', 'help', 'gainers', 'sectors', 'view', 'load', 'clear', 
                                             'sma', 'ema', 'macd', 'vwap', 'stoch', 'rsi', 'adx',
                                             'cci', 'aroon', 'bbands', 'ad', 'obv', 'ratings',
                                             'income', 'balance', 'cash', 'metrics'])

    # Print first welcome message and help
    print("\nWelcome to Didier's Stock Market Bot\n")
    print_help(s_ticker, s_start, s_interval, b_is_stock_market_open())
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

        # --------------------------------------------------- GAINERS --------------------------------------------------
        if ns_known_args.cmd == 'sectors':
            smm.sectors(l_args)
            continue

        # --------------------------------------------------- CLEAR ----------------------------------------------------
        elif ns_known_args.cmd == 'clear':
            print("Clearing stock ticker to be used for analysis")
            s_ticker = ""
            s_start = ""

        # ---------------------------------------------------- LOAD ----------------------------------------------------
        elif ns_known_args.cmd == 'load':
            [s_ticker, s_start, s_interval, df_stock] = smm.load(l_args, s_ticker, s_start, s_interval, df_stock)
            continue

        # ---------------------------------------------------- VIEW ----------------------------------------------------
        elif ns_known_args.cmd == 'view':
            smm.view(l_args, s_ticker, s_start, s_interval, df_stock)
            continue

         # ---------------------------------------------------- HELP ----------------------------------------------------
        elif ns_known_args.cmd == 'help':
            print_help(s_ticker, s_start, s_interval, b_is_stock_market_open())

        # ----------------------------------------------------- QUIT ----------------------------------------------------
        elif ns_known_args.cmd == 'quit':
            print("Hope you made money today. Good bye my lover, good bye my friend.\n")
            break
        
        # --------------------------------------------------------------------------------------------------------------
        # ------------------------------------------- FUNDAMENTAL ANALYSIS ---------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        # --------------------------------------------------- RATINGS --------------------------------------------------
        elif ns_known_args.cmd == 'ratings':
            smfa.ratings(l_args, s_ticker)
            continue

        # ----------------------------------------------- INCOME_STATEMENT -----------------------------------------------
        elif ns_known_args.cmd == 'income':
            smfa.income_statement(l_args, s_ticker)
            continue

        # ------------------------------------------------- BALANCE_SHEET -----------------------------------------------
        elif ns_known_args.cmd == 'balance':
            smfa.balance_sheet(l_args, s_ticker)
            continue

        # -------------------------------------------------- CASH_FLOW --------------------------------------------------
        elif ns_known_args.cmd == 'cash':
            smfa.cash_flow(l_args, s_ticker)
            continue

        # ------------------------------------------------- KEY_METRICS --------------------------------------------------
        elif ns_known_args.cmd == 'metrics':
            smfa.key_metrics(l_args, s_ticker)
            continue

        # --------------------------------------------------------------------------------------------------------------
        # -------------------------------------------- TECHNICAL ANALYSIS ----------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        # ---------------------------------------------------- SMA ----------------------------------------------------
        elif ns_known_args.cmd == 'sma':
            smta.sma(l_args, s_ticker, s_interval, df_stock)
            continue

        # ---------------------------------------------------- EMA ----------------------------------------------------
        elif ns_known_args.cmd == 'ema':
            smta.ema(l_args, s_ticker, s_interval, df_stock)
            continue

        # ---------------------------------------------------- MACD ----------------------------------------------------
        elif ns_known_args.cmd == 'macd':
            smta.macd(l_args, s_ticker, s_interval, df_stock)
            continue

        # ---------------------------------------------------- VWAP ----------------------------------------------------
        elif ns_known_args.cmd == 'vwap':
            smta.vwap(l_args, s_ticker, s_interval, df_stock)
            continue

        # ---------------------------------------------------- STOCH ----------------------------------------------------
        elif ns_known_args.cmd == 'stoch':
            smta.stoch(l_args, s_ticker, s_interval, df_stock)
            continue
            
        # ---------------------------------------------------- RSI ----------------------------------------------------
        elif ns_known_args.cmd == 'rsi':
            smta.rsi(l_args, s_ticker, s_interval, df_stock)
            continue

        # ---------------------------------------------------- ADX ----------------------------------------------------
        elif ns_known_args.cmd == 'adx':
            smta.adx(l_args, s_ticker, s_interval, df_stock)
            continue

        # ---------------------------------------------------- CCI ----------------------------------------------------
        elif ns_known_args.cmd == 'cci':
            smta.cci(l_args, s_ticker, s_interval, df_stock)
            continue

        # --------------------------------------------------- AROON ---------------------------------------------------
        elif ns_known_args.cmd == 'aroon':
            smta.aroon(l_args, s_ticker, s_interval, df_stock)
            continue

        # --------------------------------------------------- BBANDS ---------------------------------------------------
        elif ns_known_args.cmd == 'bbands':
            smta.bbands(l_args, s_ticker, s_interval, df_stock)
            continue

        # ----------------------------------------------------- AD -----------------------------------------------------
        elif ns_known_args.cmd == 'ad':
            smta.ad(l_args, s_ticker, s_interval, df_stock)
            continue

        # ---------------------------------------------------- OBV -----------------------------------------------------
        elif ns_known_args.cmd == 'obv':
            smta.obv(l_args, s_ticker, s_interval, df_stock)
            continue

        # --------------------------------------------------------------------------------------------------------------
        # ------------------------------------------------ PREDICTION --------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        else:
            print('Shouldnt see this command!')

        print("\n")

if __name__ == "__main__":
    main()
