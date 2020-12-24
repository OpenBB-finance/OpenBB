import argparse
from alpha_vantage.timeseries import TimeSeries
import pandas_ta as ta
import config_bot as cfg
from stock_market_helper_funcs import *

# ----------------------------------------------------- SMA -----------------------------------------------------
def sma(l_args, s_ticker, s_start):
    parser = argparse.ArgumentParser(prog='sma',
                                     description=""" Moving Averages are used to smooth the data in an array to 
                                     help eliminate noise and identify trends. The Simple Moving Average is literally 
                                     the simplest form of a moving average. Each output value is the average of the 
                                     previous n values. In a Simple Moving Average, each value in the time period carries 
                                     equal weight, and values outside of the time period are not included in the average. 
                                     This makes it less responsive to recent changes in the data, which can be useful for 
                                     filtering out those changes. """)
    parser.add_argument('-p', "--period", action="store", dest="n_time_period", type=check_positive, default=20,
                        help='Number of data points used to calculate each moving average value.')
    parser.add_argument("-s", "--start", type=valid_date, dest="s_start_date",
                        help="The starting date (format YYYY-MM-DD) of the stock")
    if s_ticker:
        parser.add_argument('-t', "--ticker", action="store", dest="s_ticker", default=s_ticker, help='Stock ticker')
    else:
        parser.add_argument('-t', "--ticker", action="store", dest="s_ticker", required=True, help='Stock ticker')
    
    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return [s_ticker, s_start]
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try: # Get stock data
        ts = TimeSeries(key=cfg.API_KEY_ALPHAVANTAGE, output_format='pandas')
        df_stock, d_stock_metadata = ts.get_daily(symbol=ns_parser.s_ticker, outputsize='full')    
    except:
        print("ERROR! Try again!")
        print("Check that: 1. The ticker symbol exists and is valid")
        print("            2. Less than 5 AlphaVantage requests have been made in 1 minute")
        print("            3. The API_KEY is (still) valid")
        return [s_ticker, s_start]

    # Update TA ticker
    s_ticker = ns_parser.s_ticker

    # Update TA starting point if needed
    if ns_parser.s_start_date:
        s_start = ns_parser.s_start_date

    # Slice dataframe from the starting date YYYY-MM-DD selected
    if s_start:
        df_stock = df_stock[ns_parser.s_start_date:]

    df_ta = ta.sma(df_stock['4. close'], timeperiod=ns_parser.n_time_period).dropna()

    plot_stock_ta(df_stock, d_stock_metadata['2. Symbol'], df_ta, f"{ns_parser.n_time_period} SMA")

    return [s_ticker, s_start]


# ----------------------------------------------------- EMA -----------------------------------------------------
def ema(l_args, s_ticker, s_start):
    parser = argparse.ArgumentParser(prog='ema', 
                                     description=""" The Exponential Moving Average is a staple of technical 
                                     analysis and is used in countless technical indicators. In a Simple Moving 
                                     Average, each value in the time period carries equal weight, and values outside 
                                     of the time period are not included in the average. However, the Exponential 
                                     Moving Average is a cumulative calculation, including all data. Past values have 
                                     a diminishing contribution to the average, while more recent values have a greater 
                                     contribution. This method allows the moving average to be more responsive to changes 
                                     in the data. """)
    parser.add_argument('-p', "--period", action="store", dest="n_time_period", type=check_positive, default=20,
                        help='Number of data points used to calculate each moving average value.')
    parser.add_argument("-s", "--start", type=valid_date, dest="s_start_date",
                        help="The starting date (format YYYY-MM-DD) of the stock")
    if s_ticker:
        parser.add_argument('-t', "--ticker", action="store", dest="s_ticker", default=s_ticker, help='Stock ticker')
    else:
        parser.add_argument('-t', "--ticker", action="store", dest="s_ticker", required=True, help='Stock ticker')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return [s_ticker, s_start]
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try: # Get stock data
        ts = TimeSeries(key=cfg.API_KEY_ALPHAVANTAGE, output_format='pandas')
        df_stock, d_stock_metadata = ts.get_daily(symbol=ns_parser.s_ticker, outputsize='full')    
    except:
        print("ERROR! Try again!")
        print("Check that: 1. The ticker symbol exists and is valid")
        print("            2. Less than 5 AlphaVantage requests have been made in 1 minute")
        print("            3. The API_KEY is (still) valid")
        return [s_ticker, s_start]

    # Update TA ticker
    s_ticker = ns_parser.s_ticker

    # Update TA starting point if needed
    if ns_parser.s_start_date:
        s_start = ns_parser.s_start_date

    # Slice dataframe from the starting date YYYY-MM-DD selected
    if s_start:
        df_stock = df_stock[ns_parser.s_start_date:]

    df_ta = ta.ema(df_stock['4. close'], timeperiod=ns_parser.n_time_period).dropna()

    plot_stock_ta(df_stock, d_stock_metadata['2. Symbol'], df_ta, f"{ns_parser.n_time_period} EMA")

    return [s_ticker, s_start]