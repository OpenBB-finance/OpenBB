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
        df_ta = ta.sma(df_stock['4. close'], timeperiod=ns_parser.n_time_period).dropna()
        plot_stock_ta(df_stock['4. close'], s_ticker, df_ta, f"{ns_parser.n_time_period} SMA")
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
        df_ta = ta.ema(df_stock['4. close'], timeperiod=ns_parser.n_time_period).dropna()
        plot_stock_ta(df_stock['4. close'], s_ticker, df_ta, f"{ns_parser.n_time_period} EMA")
    except:
        print("")
        return


# ----------------------------------------------------- MACD -----------------------------------------------------
def macd(l_args, s_ticker, df_stock):
    parser = argparse.ArgumentParser(prog='macd', 
                                     description=""" The Moving Average Convergence Divergence (MACD) is the difference 
                                     between two Exponential Moving Averages. The Signal line is an Exponential Moving 
                                     Average of the MACD. \n \n The MACD signals trend changes and indicates the start 
                                     of new trend direction. High values indicate overbought conditions, low values 
                                     indicate oversold conditions. Divergence with the price indicates an end to the 
                                     current trend, especially if the MACD is at extreme high or low values. When the MACD 
                                     line crosses above the signal line a buy signal is generated. When the MACD crosses 
                                     below the signal line a sell signal is generated. To confirm the signal, the MACD 
                                     should be above zero for a buy, and below zero for a sell. """)

    parser.add_argument('-f', "--fast", action="store", dest="n_fast", type=check_positive, default=12,
                        help='The short period.')
    parser.add_argument('-s', "--slow", action="store", dest="n_slow", type=check_positive, default=26,
                        help='The long period.')
    parser.add_argument("--signal", action="store", dest="n_signal", type=check_positive, default=9,
                        help='The signal period.')
    parser.add_argument('-o', "--offset", action="store", dest="n_offset", type=check_positive, default=9,
                        help='How many periods to offset the result.')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:
        df_ta = ta.macd(df_stock['4. close'],
                        fast=ns_parser.n_fast,
                        slow=ns_parser.n_slow,
                        signal=ns_parser.n_signal,
                        offset=ns_parser.n_offset).dropna()

        plot_ta(s_ticker, df_ta, f"{ns_parser.n_fast}-{ns_parser.n_slow}-{ns_parser.n_signal}-{ns_parser.n_offset} MACD")
    except:
        print("")
        return
