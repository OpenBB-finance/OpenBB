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
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


# -----------------------------------------------------------------------------------------------------------------------
def print_help():
    """ Print help
    """
    print("What do you want to do?")
    print("view        view a specific stock tick")
    print("\n--- Screeners:")
    print("gainers     show latest top gainers")
    print("\n--- Technical Analysis:")
    print("sma         simple moving average")
    print("ema         exponential moving average")
    print("\n--- Others:")
    print("help        help to see this menu again")
    print("quit        to abandon the program")


# -----------------------------------------------------------------------------------------------------------------------
def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{value} is an invalid positive int value")
    return ivalue


# -----------------------------------------------------------------------------------------------------------------------
def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError("Not a valid date: {s}")


# -----------------------------------------------------------------------------------------------------------------------
def plot_view_stock(df, symbol):
    pfig, axVolume = plt.subplots()
    plt.bar(df.index, df['5. volume'].values, color='k', alpha=0.8)
    plt.ylabel('Volume')
    axPrice = axVolume.twinx()
    plt.plot(df.index, df.iloc[:, :-1])
    plt.title(symbol + ' (Time Series)')
    plt.xlim(df.index[0], df.index[-1])
    plt.xlabel('Time')
    plt.ylabel('Share Price ($)')
    plt.legend(df.columns)
    plt.grid(b=True, which='major', color='#666666', linestyle='-')
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    plt.show()


# -----------------------------------------------------------------------------------------------------------------------
def plot_stock_ta(df_stock, s_stock, df_ta, s_ta):
    plt.plot(df_stock.index, df_stock['4. close'].values)
    plt.plot(df_ta.index, df_ta.values)
    plt.title(f"{s_ta} on {s_stock}")
    plt.xlim(df_stock.index[0], df_stock.index[-1])
    plt.xlabel('Time')
    plt.ylabel('Share Price ($)')
    plt.legend([s_stock, s_ta])
    plt.grid(b=True, which='major', color='#666666', linestyle='-')
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    plt.show()


# -----------------------------------------------------------------------------------------------------------------------
def main():
    """ Main function of the program
    """ 

    # temporary
    #parser.add_argument('-a', action="store_true", default=False, help='example of flag')
    #parser.add_argument('-b', action="store", dest="b", help='example of string')
    #parser.add_argument('-c', action="store", dest="c", type=int, help='example of int')

    main_parser = argparse.ArgumentParser(prog='stock_market_bot', add_help=False)

    # Add list of arguments that the main parser accepts
    main_parser.add_argument('cmd', choices=['quit', 'help', 'gainers' ,'view', 'sma', 'ema'])

    # Print first welcome message and help
    print("\nWelcome to Didier's Stock Market Bot\n")
    print_help()
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

        # ---------------------------------------------------- GAINERS ----------------------------------------------------
        if ns_known_args.cmd == 'gainers':
            parser = argparse.ArgumentParser(prog='gainers', 
                                             description='Show top ticker gainers from Yahoo Finance')
            parser.add_argument('-n', action="store", dest="n_gainers", type=int, default=5, choices=range(1, 25),
                                help='Number of the top gainers stocks to retrieve (default 5)')

            try:
                (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
            except SystemExit:
                print("")
                continue
            
            if l_unknown_args:
                print(f"The following args couldn't be interpreted: {l_unknown_args}")

            df_gainers = pd.read_html('https://finance.yahoo.com/screener/predefined/day_gainers')[0]
            print(df_gainers.head(ns_parser.n_gainers).to_string(index=False))


        # ---------------------------------------------------- VIEW ----------------------------------------------------
        elif ns_known_args.cmd == 'view':
            parser = argparse.ArgumentParser(prog='view', 
                                             description='Given a stock market ticker, allows to see historical data of \
                                                the corresponding stock. Note that the alpha_vantage key is necessary \
                                                for this to work!')
            parser.add_argument('-t', action="store", dest="s_ticker", required=True, help='Stock ticker')
            parser.add_argument('--type', action="store", dest="n_type", type=check_positive, default=4,
                                help='1234 corresponds to types: 1. open; 2. high; 3.low; 4. close \
                                    while 14 corresponds to types: 1.open; 4. close')
            parser.add_argument("-s", "--start", type=valid_date, dest="s_start_date",
                                help="The starting date (format YYYY-MM-DD) of the stock")

            try:
                (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
            except SystemExit:
                print("")
                continue
            
            if l_unknown_args:
                print(f"The following args couldn't be interpreted: {l_unknown_args}")

            # Currently only supports daily stocks
            # TODO: Intra-daily perhaps
            ts = TimeSeries(key=cfg.API_KEY, output_format='pandas')
            try:
                df_stock, d_stock_metadata = ts.get_daily(symbol=ns_parser.s_ticker, outputsize='full')     
            except:
                print("Either the ticker or the API_KEY are invalids. Try again!")
                continue   

            # Add function to plot data
            ln_col_idx = [int(x)-1 for x in list(str(ns_parser.n_type))]
            # Check that the types given are not bigger than 3, as there are only 4 types (0-3)
            if len([i for i in ln_col_idx if i > 3]) > 0:
                print("An index bigger than 3 was given, which is wrong. Try again")
                continue

            # Slice dataframe from the starting date YYYY-MM-DD selected
            if ns_parser.s_start_date:
                df_stock = df_stock[ns_parser.s_start_date:]

            ln_col_idx.append(4) # Append last column of df to be filtered which corresponds to: 5. Volume

            plot_view_stock(df_stock.iloc[:, ln_col_idx], ns_parser.s_ticker)
        
        # --------------------------------------------------------------------------------------------------------------
        # -------------------------------------------- TECHNICAL ANALYSIS ----------------------------------------------
        # --------------------------------------------------------------------------------------------------------------

        # ---------------------------------------------------- SMA ----------------------------------------------------
        elif ns_known_args.cmd == 'sma':
            parser = argparse.ArgumentParser(prog='sma',
                                             description=""" Moving Averages are used to smooth the data in an array to 
                                             help eliminate noise and identify trends. The Simple Moving Average is literally 
                                             the simplest form of a moving average. Each output value is the average of the 
                                             previous n values. In a Simple Moving Average, each value in the time period carries 
                                             equal weight, and values outside of the time period are not included in the average. 
                                             This makes it less responsive to recent changes in the data, which can be useful for 
                                             filtering out those changes. """)
            parser.add_argument('-t', action="store", dest="s_ticker", required=True, help='Stock ticker')
            parser.add_argument('--period', action="store", dest="n_time_period", type=check_positive, default=20,
                                help='Number of data points used to calculate each moving average value.')
            parser.add_argument("-s", "--start", type=valid_date, dest="s_start_date",
                                help="The starting date (format YYYY-MM-DD) of the stock")
            try:
                (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
            except SystemExit:
                print("")
                continue
            
            if l_unknown_args:
                print(f"The following args couldn't be interpreted: {l_unknown_args}")

            try: # Get stock data
                ts = TimeSeries(key=cfg.API_KEY, output_format='pandas')
                df_stock, d_stock_metadata = ts.get_daily(symbol=ns_parser.s_ticker, outputsize='full')    
            except:
                print("ERROR! Try again!")
                print("Check that: 1. The ticker symbol exists and is valid")
                print("            2. Less than 5 AlphaVantage requests have been made in 1 minute")
                print("            3. The API_KEY is (still) valid")
                continue

            # Slice dataframe from the starting date YYYY-MM-DD selected
            if ns_parser.s_start_date:
                df_stock = df_stock[ns_parser.s_start_date:]

            df_ta = ta.sma(df_stock['4. close'], timeperiod=ns_parser.n_time_period).dropna()

            plot_stock_ta(df_stock, d_stock_metadata['2. Symbol'], df_ta, f"{ns_parser.n_time_period} SMA")

            continue


        # ---------------------------------------------------- EMA ----------------------------------------------------
        elif ns_known_args.cmd == 'ema':
            parser = argparse.ArgumentParser(prog='ema', 
                                             description=""" The Exponential Moving Average is a staple of technical 
                                             analysis and is used in countless technical indicators. In a Simple Moving 
                                             Average, each value in the time period carries equal weight, and values outside 
                                             of the time period are not included in the average. However, the Exponential 
                                             Moving Average is a cumulative calculation, including all data. Past values have 
                                             a diminishing contribution to the average, while more recent values have a greater 
                                             contribution. This method allows the moving average to be more responsive to changes 
                                             in the data. """)
            parser.add_argument('-t', action="store", dest="s_ticker", required=True, help='Stock ticker')
            parser.add_argument('--period', action="store", dest="n_time_period", type=check_positive, default=20,
                                help='Number of data points used to calculate each moving average value.')
            parser.add_argument("-s", "--start", type=valid_date, dest="s_start_date",
                                help="The starting date (format YYYY-MM-DD) of the stock")
            try:
                (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
            except SystemExit:
                print("")
                continue
            
            if l_unknown_args:
                print(f"The following args couldn't be interpreted: {l_unknown_args}")

            try: # Get stock data
                ts = TimeSeries(key=cfg.API_KEY, output_format='pandas')
                df_stock, d_stock_metadata = ts.get_daily(symbol=ns_parser.s_ticker, outputsize='full')    
            except:
                print("ERROR! Try again!")
                print("Check that: 1. The ticker symbol exists and is valid")
                print("            2. Less than 5 AlphaVantage requests have been made in 1 minute")
                print("            3. The API_KEY is (still) valid")
                continue   

            # Slice dataframe from the starting date YYYY-MM-DD selected
            if ns_parser.s_start_date:
                df_stock = df_stock[ns_parser.s_start_date:]

            df_ta = ta.ema(df_stock['4. close'], timeperiod=ns_parser.n_time_period).dropna()

            plot_stock_ta(df_stock, d_stock_metadata['2. Symbol'], df_ta, f"{ns_parser.n_time_period} EMA")

            continue
        

        # ---------------------------------------------------- HELP ----------------------------------------------------
        elif ns_known_args.cmd == 'help':
            print_help()

        # ---------------------------------------------------- QUIT ----------------------------------------------------
        elif ns_known_args.cmd == 'quit':
            print("Hope you made money today. Good bye my lover, good bye my friend.\n")
            break
            
        else:
            print('Shouldnt see this command!')

        print("\n")

if __name__ == "__main__":
    main()
