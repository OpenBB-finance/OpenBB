import argparse
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import pandas_ta as ta
import config_bot as cfg
from stock_market_helper_funcs import *

# ----------------------------------------------------- SMA -----------------------------------------------------
def sma(l_args, s_ticker, s_interval, df_stock):
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
        # Daily
        if s_interval == "1440min":
            df_ta = ta.sma(df_stock['5. adjusted close'], timeperiod=ns_parser.n_time_period).dropna()
            plot_stock_ta(df_stock['5. adjusted close'], s_ticker, df_ta, f"{ns_parser.n_time_period} SMA")
        # Intraday 
        else:
            df_ta = ta.sma(df_stock['4. close'], timeperiod=ns_parser.n_time_period).dropna()
            plot_stock_ta(df_stock['4. close'], s_ticker, df_ta, f"{ns_parser.n_time_period} SMA")          
    except:
        print("")
        return


# ----------------------------------------------------- EMA -----------------------------------------------------
def ema(l_args, s_ticker, s_interval, df_stock):
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
        # Daily
        if s_interval == "1440min":
            df_ta = ta.ema(df_stock['5. adjusted close'], timeperiod=ns_parser.n_time_period).dropna()
            plot_stock_ta(df_stock['5. adjusted close'], s_ticker, df_ta, f"{ns_parser.n_time_period} EMA")
        # Intraday 
        else:
            df_ta = ta.ema(df_stock['4. close'], timeperiod=ns_parser.n_time_period).dropna()
            plot_stock_ta(df_stock['4. close'], s_ticker, df_ta, f"{ns_parser.n_time_period} EMA")   
    except:
        print("")
        return


# ----------------------------------------------------- MACD -----------------------------------------------------
def macd(l_args, s_ticker, s_interval, df_stock):
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
        # Daily
        if s_interval == "1440min":
            df_ta = ta.macd(df_stock['5. adjusted close'],
                        fast=ns_parser.n_fast, slow=ns_parser.n_slow,
                        signal=ns_parser.n_signal, offset=ns_parser.n_offset).dropna()
        # Intraday 
        else:
            df_ta = ta.macd(df_stock['4. close'],
                        fast=ns_parser.n_fast, slow=ns_parser.n_slow,
                        signal=ns_parser.n_signal, offset=ns_parser.n_offset).dropna()
        
        plot_ta(s_ticker, df_ta, f"{ns_parser.n_fast}-{ns_parser.n_slow}-{ns_parser.n_signal}-{ns_parser.n_offset} MACD")
    except:
        print("")
        return


# ----------------------------------------------------- VWAP -----------------------------------------------------
def vwap(l_args, s_ticker, s_interval, df_stock):
    parser = argparse.ArgumentParser(prog='vwap', 
                                     description=""" The Volume Weighted Average Price that measures the average typical price
                                     by volume.  It is typically used with intraday charts to identify general direction. """)

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:
        df_ta = ta.vwap(high=df_stock['2. high'], low=df_stock['3. low'], close=df_stock['4. close'], volume=df_stock['5. volume'], interval=s_interval)
        plot_stock_ta(df_stock['4. close'], s_ticker, df_ta, f"{s_interval} VWAP")
    except:
        print("")
        return


# ----------------------------------------------------- STOCH -----------------------------------------------------
def stoch(l_args, s_ticker, s_interval, df_stock):
    parser = argparse.ArgumentParser(prog='stoch', 
                                     description=""" The Stochastic Oscillator measures where the close is in relation 
                                     to the recent trading range. The values range from zero to 100. %D values over 75 
                                     indicate an overbought condition; values under 25 indicate an oversold condition. 
                                     When the Fast %D crosses above the Slow %D, it is a buy signal; when it crosses 
                                     below, it is a sell signal. The Raw %K is generally considered too erratic to use 
                                     for crossover signals. """)

    parser.add_argument('-k', "--fastkperiod", action="store", dest="n_fastkperiod", type=check_positive, default=5, 
                        help='The time period of the fastk moving average')
    parser.add_argument('-d', "--slowdperiod", action="store", dest="n_slowdperiod", type=check_positive, default=3,
                        help='TThe time period of the slowd moving average')
    parser.add_argument("--slowkperiod", action="store", dest="n_slowkperiod", type=check_positive, default=3,
                        help='The time period of the slowk moving average')
    parser.add_argument("--slowkmatype", action="store", dest="n_slowkmatype", type=check_positive, default=0,
                        help='Moving average type for the slowk moving average')
    parser.add_argument("--slowdmatype", action="store", dest="n_slowdmatype", type=check_positive, default=0,
                        help='Moving average type for the slowd moving average')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:
        df_ta = ta.stoch(high=df_stock['2. high'], 
                         low=df_stock['3. low'], 
                         close=df_stock['4. close'], 
                         k=ns_parser.n_fastkperiod, 
                         d=ns_parser.n_slowdperiod, 
                         smooth_k=ns_parser.n_slowkperiod).dropna()

        plot_ta(s_ticker, df_ta, f"SlowK{ns_parser.n_slowkperiod}-SlowD{ns_parser.n_slowdperiod} STOCH")
    except:
        print("")
        return


# ----------------------------------------------------- RSI -----------------------------------------------------
def rsi(l_args, s_ticker, s_interval, df_stock):
    parser = argparse.ArgumentParser(prog='rsi', 
                                     description=""" The Relative Strength Index (RSI) calculates a ratio of the 
                                     recent upward price movements to the absolute price movement. The RSI ranges 
                                     from 0 to 100. The RSI is interpreted as an overbought/oversold indicator when 
                                     the value is over 70/below 30. You can also look for divergence with price. If 
                                     the price is making new highs/lows, and the RSI is not, it indicates a reversal. """)

    parser.add_argument('-p', "--timeperiod", action="store", dest="n_timeperiod", type=check_positive, default=60,
                        help='Number of data points used to calculate each RSI value')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:
        # Daily
        if s_interval == "1440min":
            df_ta = ta.rsi(df_stock['5. adjusted close'], time_period=ns_parser.n_timeperiod).dropna()
        # Intraday 
        else:
            df_ta = ta.rsi(df_stock['4. close'], time_period=ns_parser.n_timeperiod).dropna()

        plot_ta(s_ticker, df_ta, f"{ns_parser.n_timeperiod} RSI")
    except:
        print("")
        return


# ----------------------------------------------------- ADX -----------------------------------------------------
def adx(l_args, s_ticker, s_interval, df_stock):
    parser = argparse.ArgumentParser(prog='adx', 
                                     description=""" The ADX is a Welles Wilder style moving average of the Directional 
                                     Movement Index (DX). The values range from 0 to 100, but rarely get above 60. 
                                     To interpret the ADX, consider a high number to be a strong trend, and a low number, 
                                     a weak trend. """)

    parser.add_argument('-p', "--timeperiod", action="store", dest="n_timeperiod", type=check_positive, default=60,
                        help='Number of data points used to calculate each ADX value')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:
        # Daily
        if s_interval == "1440min":
            df_ta = ta.adx(high=df_stock['2. high'], low=df_stock['3. low'],
                           close=df_stock['5. adjusted close'], time_period=ns_parser.n_timeperiod).dropna()
        # Intraday 
        else:
            df_ta = ta.adx(high=df_stock['2. high'], low=df_stock['3. low'],
                           close=df_stock['4. close'], time_period=ns_parser.n_timeperiod).dropna()

        plot_ta(s_ticker, df_ta, f"{ns_parser.n_timeperiod} ADX")
    except:
        print("")
        return


# ----------------------------------------------------- CCI -----------------------------------------------------
def cci(l_args, s_ticker, s_interval, df_stock):
    parser = argparse.ArgumentParser(prog='cci', 
                                     description=""" The CCI is designed to detect beginning and ending market trends. 
                                     The range of 100 to -100 is the normal trading range. CCI values outside of this 
                                     range indicate overbought or oversold conditions. You can also look for price 
                                     divergence in the CCI. If the price is making new highs, and the CCI is not, 
                                     then a price correction is likely. """)

    parser.add_argument('-p', "--timeperiod", action="store", dest="n_timeperiod", type=check_positive, default=60,
                        help='Number of data points used to calculate each ADX value')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:
        # Daily
        if s_interval == "1440min":
            df_ta = ta.cci(high=df_stock['2. high'], low=df_stock['3. low'],
                           close=df_stock['5. adjusted close'], time_period=ns_parser.n_timeperiod).dropna()
        # Intraday 
        else:
            df_ta = ta.cci(high=df_stock['2. high'], low=df_stock['3. low'],
                           close=df_stock['4. close'], time_period=ns_parser.n_timeperiod).dropna()

        plot_ta(s_ticker, df_ta, f"{ns_parser.n_timeperiod} CCI")
    except:
        print("")
        return