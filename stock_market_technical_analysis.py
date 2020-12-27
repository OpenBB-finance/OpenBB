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

    parser.add_argument('-l', "--length", action="store", dest="n_length", type=check_positive, default=10, help='length')
    parser.add_argument('-o', "--offset", action="store", dest="n_offset", type=check_positive, default=0, help='offset')

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
            df_ta = ta.sma(df_stock['5. adjusted close'], length=ns_parser.n_length, offset=ns_parser.n_offset).dropna()
            plot_stock_ta(df_stock['5. adjusted close'], s_ticker, df_ta, "SMA")
        # Intraday 
        else:
            df_ta = ta.sma(df_stock['4. close'], length=ns_parser.n_length, offset=ns_parser.n_offset).dropna()
            plot_stock_ta(df_stock['4. close'], s_ticker, df_ta, "SMA")     
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

    parser.add_argument('-l', "--length", action="store", dest="n_length", type=check_positive, default=10, help='length')
    parser.add_argument('-o', "--offset", action="store", dest="n_offset", type=check_positive, default=0, help='offset')

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
            df_ta = ta.ema(df_stock['5. adjusted close'], length=ns_parser.n_length, offset=ns_parser.n_offset).dropna()
            plot_stock_ta(df_stock['5. adjusted close'], s_ticker, df_ta, "EMA")
        # Intraday 
        else:
            df_ta = ta.ema(df_stock['4. close'], length=ns_parser.n_length, offset=ns_parser.n_offset).dropna()
            plot_stock_ta(df_stock['4. close'], s_ticker, df_ta, "EMA")   
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
    parser.add_argument('-o', "--offset", action="store", dest="n_offset", type=check_positive, default=0,
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
            df_ta = ta.macd(df_stock['5. adjusted close'], fast=ns_parser.n_fast, slow=ns_parser.n_slow,
                            signal=ns_parser.n_signal, offset=ns_parser.n_offset).dropna()
            plot_stock_and_ta(df_stock['5. adjusted close'], s_ticker, df_ta, "MACD")
        # Intraday 
        else:
            df_ta = ta.macd(df_stock['4. close'], fast=ns_parser.n_fast, slow=ns_parser.n_slow,
                            signal=ns_parser.n_signal, offset=ns_parser.n_offset).dropna()
            plot_stock_and_ta(df_stock['4. close'], s_ticker, df_ta, "MACD")
    except:
        print("")
        return


# ----------------------------------------------------- VWAP -----------------------------------------------------
def vwap(l_args, s_ticker, s_interval, df_stock):
    parser = argparse.ArgumentParser(prog='vwap', 
                                     description=""" The Volume Weighted Average Price that measures the average typical price
                                     by volume.  It is typically used with intraday charts to identify general direction. """)

    parser.add_argument('-o', "--offset", action="store", dest="n_offset", type=check_positive, default=0, help='offset')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:
        df_ta = ta.vwap(high=df_stock['2. high'], low=df_stock['3. low'],  close=df_stock['4. close'], 
                        volume=df_stock['5. volume'], offset=ns_parser.n_offset)

        plot_stock_ta(df_stock['4. close'], s_ticker, df_ta, "VWAP")
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

    parser.add_argument('-k', "--fastkperiod", action="store", dest="n_fastkperiod", type=check_positive, default=14, 
                        help='The time period of the fastk moving average')
    parser.add_argument('-d', "--slowdperiod", action="store", dest="n_slowdperiod", type=check_positive, default=3,
                        help='TThe time period of the slowd moving average')
    parser.add_argument("--slowkperiod", action="store", dest="n_slowkperiod", type=check_positive, default=3,
                        help='The time period of the slowk moving average')
    parser.add_argument('-o', "--offset", action="store", dest="n_offset", type=check_positive, default=0, help='offset')

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
            df_ta = ta.stoch(high=df_stock['2. high'], low=df_stock['3. low'], close=df_stock['5. adjusted close'], k=ns_parser.n_fastkperiod, 
                         d=ns_parser.n_slowdperiod, smooth_k=ns_parser.n_slowkperiod, offset=ns_parser.n_offset).dropna()
            plot_stock_and_ta(df_stock['5. adjusted close'], s_ticker, df_ta, "STOCH")
        # Intraday 
        else:
            df_ta = ta.stoch(high=df_stock['2. high'], low=df_stock['3. low'], close=df_stock['4. close'], k=ns_parser.n_fastkperiod, 
                         d=ns_parser.n_slowdperiod, smooth_k=ns_parser.n_slowkperiod, offset=ns_parser.n_offset).dropna()
            plot_stock_and_ta(df_stock['4. close'], s_ticker, df_ta, "STOCH")
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

    parser.add_argument('-l', "--length", action="store", dest="n_length", type=check_positive, default=14, help='length')
    parser.add_argument('-s', "--scalar", action="store", dest="n_scalar", type=check_positive, default=100, help='scalar')
    parser.add_argument('-d', "--drift", action="store", dest="n_drift", type=check_positive, default=1, help='drift')
    parser.add_argument('-o', "--offset", action="store", dest="n_offset", type=check_positive, default=0, help='offset')

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
            df_ta = ta.rsi(df_stock['5. adjusted close'], length=ns_parser.n_length, scalar=ns_parser.n_scalar, 
                           drift=ns_parser.n_drift, offset=ns_parser.n_offset).dropna()
            plot_stock_and_ta(df_stock['5. adjusted close'], s_ticker, df_ta, "RSI")
        # Intraday 
        else:
            df_ta = ta.rsi(df_stock['4. close'], length=ns_parser.n_length, scalar=ns_parser.n_scalar, 
                           drift=ns_parser.n_drift, offset=ns_parser.n_offset).dropna()
            plot_stock_and_ta(df_stock['4. close'], s_ticker, df_ta, "RSI")
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

    parser.add_argument('-l', "--length", action="store", dest="n_length", type=check_positive, default=14, help='length')
    parser.add_argument('-s', "--scalar", action="store", dest="n_scalar", type=check_positive, default=100, help='scalar')
    parser.add_argument('-d', "--drift", action="store", dest="n_drift", type=check_positive, default=1, help='drift')
    parser.add_argument('-o', "--offset", action="store", dest="n_offset", type=check_positive, default=0, help='offset')

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
            df_ta = ta.adx(high=df_stock['2. high'], low=df_stock['3. low'], close=df_stock['5. adjusted close'], length=ns_parser.n_length, 
                           scalar=ns_parser.n_scalar, drift=ns_parser.n_drift, offset=ns_parser.n_offset).dropna()
            plot_stock_and_ta(df_stock['5. adjusted close'], s_ticker, df_ta, "ADX")
        # Intraday 
        else:
            df_ta = ta.adx(high=df_stock['2. high'], low=df_stock['3. low'], close=df_stock['4. close'], length=ns_parser.n_length, 
                           scalar=ns_parser.n_scalar, drift=ns_parser.n_drift, offset=ns_parser.n_offset).dropna()
            plot_stock_and_ta(df_stock['4. close'], s_ticker, df_ta, "ADX")
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

    parser.add_argument('-l', "--length", action="store", dest="n_length", type=check_positive, default=14, help='length')
    parser.add_argument('-s', "--scalar", action="store", dest="n_scalar", type=check_positive, default=0.015, help='scalar')
    parser.add_argument('-o', "--offset", action="store", dest="n_offset", type=check_positive, default=0, help='offset')

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
            df_ta = ta.cci(high=df_stock['2. high'], low=df_stock['3. low'], close=df_stock['5. adjusted close'], 
                           length=ns_parser.n_length, scalar=ns_parser.n_scalar, offset=ns_parser.n_offset).dropna()
            plot_stock_and_ta(df_stock['5. adjusted close'], s_ticker, df_ta, "CCI")
        # Intraday 
        else:
            df_ta = ta.cci(high=df_stock['2. high'], low=df_stock['3. low'], close=df_stock['4. close'], 
                           length=ns_parser.n_length, scalar=ns_parser.n_scalar, offset=ns_parser.n_offset).dropna()
            plot_stock_and_ta(df_stock['4. close'], s_ticker, df_ta, "CCI")
    except:
        print("")
        return


# ----------------------------------------------------- AROON -----------------------------------------------------
def aroon(l_args, s_ticker, s_interval, df_stock):
    parser = argparse.ArgumentParser(prog='aroon', 
                                     description=""" The word aroon is Sanskrit for "dawn's early light." The Aroon 
                                     indicator attempts to show when a new trend is dawning. The indicator consists 
                                     of two lines (Up and Down) that measure how long it has been since the highest 
                                     high/lowest low has occurred within an n period range. \n \n When the Aroon Up is 
                                     staying between 70 and 100 then it indicates an upward trend. When the Aroon Down 
                                     is staying between 70 and 100 then it indicates an downward trend. A strong upward 
                                     trend is indicated when the Aroon Up is above 70 while the Aroon Down is below 30. 
                                     Likewise, a strong downward trend is indicated when the Aroon Down is above 70 while 
                                     the Aroon Up is below 30. Also look for crossovers. When the Aroon Down crosses above 
                                     the Aroon Up, it indicates a weakening of the upward trend (and vice versa). """)

    parser.add_argument('-l', "--length", action="store", dest="n_length", type=check_positive, default=14, help='length')
    parser.add_argument('-s', "--scalar", action="store", dest="n_scalar", type=check_positive, default=100, help='scalar')
    parser.add_argument('-o', "--offset", action="store", dest="n_offset", type=check_positive, default=0, help='offset')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try: 
        df_ta = ta.aroon(high=df_stock['2. high'], low=df_stock['3. low'], length=ns_parser.n_length,
                         scalar=ns_parser.n_scalar, offset=ns_parser.n_offset).dropna()
        # Daily
        if s_interval == "1440min":
            plot_stock_and_ta(df_stock['5. adjusted close'], s_ticker, df_ta.iloc[:,-1], "AROON")
        # Intraday
        else:
            plot_stock_and_ta(df_stock['4. close'], s_ticker, df_ta.iloc[:,-1], "AROON")
    except:
        print("")
        return


# ----------------------------------------------------- BBANDS -----------------------------------------------------
def bbands(l_args, s_ticker, s_interval, df_stock):
    parser = argparse.ArgumentParser(prog='bbands', 
                                     description=""" Bollinger Bands consist of three lines. The middle band is a simple 
                                     moving average (generally 20 periods) of the typical price (TP). The upper and lower 
                                     bands are F standard deviations (generally 2) above and below the middle band. 
                                     The bands widen and narrow when the volatility of the price is higher or lower, respectively.
                                     \n \nBollinger Bands do not, in themselves, generate buy or sell signals; they are an 
                                     indicator of overbought or oversold conditions. When the price is near the upper or lower 
                                     band it indicates that a reversal may be imminent. The middle band becomes a support or 
                                     resistance level. The upper and lower bands can also be interpreted as price targets. 
                                     When the price bounces off of the lower band and crosses the middle band, then the 
                                     upper band becomes the price target. """)

    parser.add_argument('-l', "--length", action="store", dest="n_length", type=check_positive, default=5, help='length')
    parser.add_argument('-s', "--std", action="store", dest="n_std", type=check_positive, default=2, help='std')
    parser.add_argument('-m', "--mamode", action="store", dest="s_mamode", default="sma", help='mamode')
    parser.add_argument('-o', "--offset", action="store", dest="n_offset", type=check_positive, default=0, help='offset')

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
            df_ta = ta.bbands(close=df_stock['5. adjusted close'], length=ns_parser.n_length, std=ns_parser.n_std, 
                              mamode=ns_parser.s_mamode, offset=ns_parser.n_offset).dropna()
            plot_stock_ta(df_stock['5. adjusted close'], s_ticker, df_ta, "BBANDS")
        # Intraday 
        else:
            df_ta = ta.bbands(close=df_stock['4. close'], length=ns_parser.n_length, std=ns_parser.n_std, 
                              mamode=ns_parser.s_mamode, offset=ns_parser.n_offset).dropna()
            plot_stock_ta(df_stock['4. close'], s_ticker, df_ta, "BBANDS")
        
    except:
        print("")
        return


# ------------------------------------------------------- AD -------------------------------------------------------
def ad(l_args, s_ticker, s_interval, df_stock):
    parser = argparse.ArgumentParser(prog='ad', 
                                     description=""" The Accumulation/Distribution Line is similar to the On Balance 
                                     Volume (OBV), which sums the volume times +1/-1 based on whether the close is 
                                     higher than the previous close. The Accumulation/Distribution indicator, however 
                                     multiplies the volume by the close location value (CLV). The CLV is based on the 
                                     movement of the issue within a single bar and can be +1, -1 or zero. \n \n 
                                     The Accumulation/Distribution Line is interpreted by looking for a divergence in 
                                     the direction of the indicator relative to price. If the Accumulation/Distribution 
                                     Line is trending upward it indicates that the price may follow. Also, if the 
                                     Accumulation/Distribution Line becomes flat while the price is still rising (or falling) 
                                     then it signals an impending flattening of the price.""")

    parser.add_argument('-o', "--offset", action="store", dest="n_offset", type=check_positive, default=0, help='offset')
    parser.add_argument('--open', action="store_true", default=False, dest="b_use_open", help='uses open value of stock')

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
            # Use open stock values
            if ns_parser.b_use_open:
                df_ta = ta.ad(high=df_stock['2. high'], low=df_stock['3. low'], close=df_stock['5. adjusted close'], 
                              volume=df_stock['6. volume'], offset=ns_parser.n_offset, open_=df_stock['1. open']).dropna()
            # Do not use open stock values
            else:
                df_ta = ta.ad(high=df_stock['2. high'], low=df_stock['3. low'], close=df_stock['5. adjusted close'], 
                              volume=df_stock['6. volume'], offset=ns_parser.n_offset).dropna()

            plot_stock_and_ta(df_stock['5. adjusted close'], s_ticker, df_ta, "AD")
        # Intraday 
        else:
            # Use open stock values
            if ns_parser.b_use_open:
                df_ta = ta.ad(high=df_stock['2. high'], low=df_stock['3. low'], close=df_stock['4. close'], 
                              volume=df_stock['5. volume'], offset=ns_parser.n_offset, open_=df_stock['1. open']).dropna()
            # Do not use open stock values
            else:
                df_ta = ta.ad(high=df_stock['2. high'], low=df_stock['3. low'], close=df_stock['4. close'], 
                              volume=df_stock['5. volume'], offset=ns_parser.n_offset).dropna()
        
            plot_stock_and_ta(df_stock['4. close'], s_ticker, df_ta, "AD")
        
    except:
        print("")
        return


# ------------------------------------------------------- OBV -------------------------------------------------------
def obv(l_args, s_ticker, s_interval, df_stock):
    parser = argparse.ArgumentParser(prog='obv', 
                                     description=""" The On Balance Volume (OBV) is a cumulative total of the up and 
                                     down volume. When the close is higher than the previous close, the volume is added 
                                     to the running total, and when the close is lower than the previous close, the volume 
                                     is subtracted from the running total. \n \n To interpret the OBV, look for the OBV 
                                     to move with the price or precede price moves. If the price moves before the OBV, 
                                     then it is a non-confirmed move. A series of rising peaks, or falling troughs, in the 
                                     OBV indicates a strong trend. If the OBV is flat, then the market is not trending. """)

    parser.add_argument('-o', "--offset", action="store", dest="n_offset", type=check_positive, default=0, help='offset')

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
            df_ta = ta.obv(close=df_stock['5. adjusted close'], volume=df_stock['6. volume'], offset=ns_parser.n_offset).dropna()
            plot_stock_and_ta(df_stock['5. adjusted close'], s_ticker, df_ta, "OBV")
        # Intraday 
        else:
            df_ta = ta.ad(close=df_stock['4. close'], volume=df_stock['5. volume'], offset=ns_parser.n_offset).dropna()
            plot_stock_and_ta(df_stock['4. close'], s_ticker, df_ta, "OBV")
    except:
        print("")
        return