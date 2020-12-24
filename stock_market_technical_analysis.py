import argparse
from alpha_vantage.timeseries import TimeSeries
import pandas_ta as ta
import config_bot as cfg
from stock_market_helper_funcs import *

# ----------------------------------------------------- SMA -----------------------------------------------------
def sma(l_args, s_ticker, df_stock):
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

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:
        df_ta = ta.sma(df_stock, timeperiod=ns_parser.n_time_period).dropna()
        plot_stock_ta(df_stock, s_ticker, df_ta, f"{ns_parser.n_time_period} SMA")
    except:
        print("")
        return


# ----------------------------------------------------- EMA -----------------------------------------------------
def ema(l_args, s_ticker, df_stock):
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

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:
        df_ta = ta.ema(df_stock, timeperiod=ns_parser.n_time_period).dropna()
        plot_stock_ta(df_stock, s_ticker, df_ta, f"{ns_parser.n_time_period} EMA")
    except:
        print("")
        return
