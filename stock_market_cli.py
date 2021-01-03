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
    print("   gainers     show latest top gainers")
    print("   sectors     show sectors performance")
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
    print(f"Market {('CLOSED', 'OPEN')[b_is_market_open]}.")

    if s_ticker:
        print("\nMenus:")
        print("   fa          fundamental analysis")
        print("   ta          technical analysis")
        print("   pred        prediction techniques")

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


# -----------------------------------------------------------------------------------------------------------------------
def print_fundamental_analysis(s_ticker, s_start, s_interval):
    """ Print help """

    s_intraday = (f'Intraday {s_interval}', 'Daily')[s_interval == "1440min"]

    if s_start:
        print(f"\n{s_intraday} Stock: {s_ticker} (from {s_start.strftime('%Y-%m-%d')})")
    else:
        print(f"\n{s_intraday} Stock: {s_ticker}")

    print("\nFundamental Analysis:") # https://github.com/JerBouma/FundamentalAnalysis
    print("   info        provides information on main key metrics of company")
    print("   help        show this fundamental analysis menu again")
    print("   q           quit this menu, and shows back to main menu")
    print("   quit        quit to abandon program")
    print("details:")
    print("   overview    overview of the company [AV]")
    print("   key         main key metrics of the company [AV]")
    print("   profile     profile of the company [FMP]")
    print("   rating      rating of the company from strong sell to strong buy [FMP]")
    print("   quote       quote of the company [FMP]")
    print("   enterprise  enterprise value of the company over time [FMP]")
    print("   dcf         discounted cash flow of the company over time [FMP]")
    print("financial statement:")
    print("   income      income statements of the company [default: AV, FMP]")
    print("   balance     balance sheet of the company [default: AV, FMP]")
    print("   cash        cash flow of the company [default: AV, FMP]")
    print("   earnings    earnings dates and reported EPS [AV]")
    print("ratios:")
    print("   metrics     key metrics of the company [FMP]")
    print("   ratios      financial ratios of the company [FMP]")
    print("   growth      financial statement growth of the company [FMP]")
    print("")
    

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
    menu_parser.add_argument('cmd', choices=['gainers', 'sectors', 'view', 'clear', 'load', 
                                             'fa', 'ta', 'help', 'quit'])

    # Add list of arguments that the fundamental analysis parser accepts
    fa_parser = argparse.ArgumentParser(prog='fundamental_analysis', add_help=False)
    fa_parser.add_argument('fa', choices=['info', 'help', 'q', 'quit',
                                          'overview', 'key', 'profile', 'rating', 'quote', 'enterprise', 'dcf', # details
                                          'income', 'balance', 'cash', 'earnings', # financial statement
                                          'metrics', 'ratios', 'growth']) # ratios
                                             
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
    print_help(s_ticker, s_start, s_interval, b_is_stock_market_open())
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

        # --------------------------------------------------------------------------------------------------------------
        # --------------------------------------------------- MENU -----------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        # --------------------------------------------------- GAINERS --------------------------------------------------
        if ns_known_args.cmd == 'gainers':
            smm.gainers(l_args)

        # --------------------------------------------------- SECTORS --------------------------------------------------
        if ns_known_args.cmd == 'sectors':
            smm.sectors(l_args)

        # --------------------------------------------------- CLEAR ----------------------------------------------------
        elif ns_known_args.cmd == 'clear':
            print("Clearing stock ticker to be used for analysis")
            s_ticker = ""
            s_start = ""

        # ---------------------------------------------------- LOAD ----------------------------------------------------
        elif ns_known_args.cmd == 'load':
            [s_ticker, s_start, s_interval, df_stock] = smm.load(l_args, s_ticker, s_start, s_interval, df_stock)

        # ---------------------------------------------------- VIEW ----------------------------------------------------
        elif ns_known_args.cmd == 'view':
            smm.view(l_args, s_ticker, s_start, s_interval, df_stock)

        # ---------------------------------------------------- HELP ----------------------------------------------------
        elif ns_known_args.cmd == 'help':
            print_help(s_ticker, s_start, s_interval, b_is_stock_market_open())

        # ----------------------------------------------------- QUIT ----------------------------------------------------
        elif ns_known_args.cmd == 'quit':
            print("Hope you made money today. Good bye my lover, good bye my friend.\n")
            return
        
        # --------------------------------------------------------------------------------------------------------------
        # ------------------------------------------- FUNDAMENTAL ANALYSIS ---------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        elif ns_known_args.cmd == 'fa':
            # Print fundamental analysis menun
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
                    smfa.info(l_args, s_ticker)

                elif ns_known_args.fa == 'help':
                    print_fundamental_analysis(s_ticker, s_start, s_interval)

                elif ns_known_args.fa == 'q':
                    print_help(s_ticker, s_start, s_interval, b_is_stock_market_open())
                    break

                elif ns_known_args.fa == 'quit':
                    print("Hope you made money today. Good bye my lover, good bye my friend.\n")
                    return
                
                # -------------------------------------------------- DETAILS --------------------------------------------------
                elif ns_known_args.fa == 'profile':
                    smfa.profile(l_args, s_ticker)

                elif ns_known_args.fa == 'rating':
                    smfa.rating(l_args, s_ticker)

                elif ns_known_args.fa == 'quote':
                    smfa.quote(l_args, s_ticker)
                
                elif ns_known_args.fa == 'enterprise':
                    smfa.enterprise(l_args, s_ticker)

                elif ns_known_args.fa == 'dcf':
                    smfa.discounted_cash_flow(l_args, s_ticker)

                elif ns_known_args.fa == 'overview':
                    smfa.overview(l_args, s_ticker)

                elif ns_known_args.fa == 'key':
                    smfa.key(l_args, s_ticker)

                # --------------------------------------------- FINANCIAL STATEMENT --------------------------------------------
                elif ns_known_args.fa == 'income':
                    smfa.income_statement(l_args, s_ticker)

                elif ns_known_args.fa == 'balance':
                    smfa.balance_sheet(l_args, s_ticker)

                elif ns_known_args.fa == 'cash':
                    smfa.cash_flow(l_args, s_ticker)

                elif ns_known_args.fa == 'earnings':
                    smfa.earnings(l_args, s_ticker)

                # --------------------------------------------------- RATIOS -----------------------------------------------------
                elif ns_known_args.fa == 'metrics':
                    smfa.key_metrics(l_args, s_ticker)

                elif ns_known_args.fa == 'ratios':
                    smfa.financial_ratios(l_args, s_ticker)

                elif ns_known_args.fa == 'growth':
                    smfa.financial_statement_growth(l_args, s_ticker)

                # ------------------------------------------------------------------------------------------------------------
                else:
                    print("Command not recognized!")
                
            print("")

        # --------------------------------------------------------------------------------------------------------------
        # -------------------------------------------- TECHNICAL ANALYSIS ----------------------------------------------
        # --------------------------------------------------------------------------------------------------------------
        elif ns_known_args.cmd == 'ta':
            # Print technical analysis menun
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
                    print_help(s_ticker, s_start, s_interval, b_is_stock_market_open())
                    break

                elif ns_known_args.ta == 'quit':
                    print("Hope you made money today. Good bye my lover, good bye my friend.\n")
                    return

                # -------------------------------------------------- OVERLAP --------------------------------------------------
                elif ns_known_args.ta == 'ema':
                    smta.ema(l_args, s_ticker, s_interval, df_stock)

                elif ns_known_args.ta == 'sma':
                    smta.sma(l_args, s_ticker, s_interval, df_stock)

                elif ns_known_args.ta == 'vwap':
                    smta.vwap(l_args, s_ticker, s_interval, df_stock)

                # --------------------------------------------------- MOMENTUM ---------------------------------------------------
                elif ns_known_args.ta == 'cci':
                    smta.cci(l_args, s_ticker, s_interval, df_stock)

                elif ns_known_args.ta == 'macd':
                    smta.macd(l_args, s_ticker, s_interval, df_stock)

                elif ns_known_args.ta == 'rsi':
                    smta.rsi(l_args, s_ticker, s_interval, df_stock)

                elif ns_known_args.ta == 'stoch':
                    smta.stoch(l_args, s_ticker, s_interval, df_stock)
                    
                # ---------------------------------------------------- TREND ----------------------------------------------------
                elif ns_known_args.ta == 'adx':
                    smta.adx(l_args, s_ticker, s_interval, df_stock)

                elif ns_known_args.ta == 'aroon':
                    smta.aroon(l_args, s_ticker, s_interval, df_stock)

                # -------------------------------------------------- VOLATILITY --------------------------------------------------
                elif ns_known_args.ta == 'bbands':
                    smta.bbands(l_args, s_ticker, s_interval, df_stock)

                # ---------------------------------------------------- VOLUME ----------------------------------------------------
                elif ns_known_args.ta == 'ad':
                    smta.ad(l_args, s_ticker, s_interval, df_stock)

                elif ns_known_args.ta == 'obv':
                    smta.obv(l_args, s_ticker, s_interval, df_stock)

                # ------------------------------------------------------------------------------------------------------------
                else:
                    print("Command not recognized!")

        # --------------------------------------------------------------------------------------------------------------
        # ------------------------------------------------ PREDICTION --------------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        else:
            print('Shouldnt see this command!')

        print("")

if __name__ == "__main__":
    main()
