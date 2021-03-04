import argparse

import pandas_ta as ta
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

from helper_funcs import check_positive

register_matplotlib_converters()

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

    (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
        return

    # Daily
    if s_interval == "1440min":
        df_ta = ta.adx(high=df_stock['2. high'], low=df_stock['3. low'], close=df_stock['5. adjusted close'], length=ns_parser.n_length,
                       scalar=ns_parser.n_scalar, drift=ns_parser.n_drift, offset=ns_parser.n_offset).dropna()

        plt.subplot(211)
        plt.plot(df_stock.index, df_stock['5. adjusted close'].values, 'k', lw=2)
        plt.title(f"Average Directional Movement Index (ADX) on {s_ticker}")
        plt.xlim(df_stock.index[0], df_stock.index[-1])
        plt.ylabel(f'Share Price ($)')
        plt.grid(b=True, which='major', color='#666666', linestyle='-')
        plt.minorticks_on()
        plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
        plt.subplot(212)
        plt.plot(df_ta.index, df_ta.iloc[:,0].values, 'b', lw=2)
        plt.plot(df_ta.index, df_ta.iloc[:,1].values, 'g', lw=1)
        plt.plot(df_ta.index, df_ta.iloc[:,2].values, 'r', lw=1)
        plt.xlim(df_stock.index[0], df_stock.index[-1])
        plt.axhline(25, linewidth=3, color='k', ls='--')
        plt.legend([f'ADX ({df_ta.columns[0]})',
                    f'+DI ({df_ta.columns[1]})',
                    f'- DI ({df_ta.columns[2]})'])
        plt.xlabel('Time')
        plt.grid(b=True, which='major', color='#666666', linestyle='-')
        plt.minorticks_on()
        plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
        plt.ylim([0, 100])
        plt.show()

    # Intraday
    else:
        df_ta = ta.adx(high=df_stock['2. high'], low=df_stock['3. low'], close=df_stock['4. close'], length=ns_parser.n_length,
                       scalar=ns_parser.n_scalar, drift=ns_parser.n_drift, offset=ns_parser.n_offset).dropna()

        plt.subplot(211)
        plt.plot(df_stock.index, df_stock['4. close'].values, 'k', lw=2)
        plt.title(f"Average Directional Movement Index (ADX) on {s_ticker}")
        plt.xlim(df_stock.index[0], df_stock.index[-1])
        plt.ylabel(f'Share Price ($)')
        plt.grid(b=True, which='major', color='#666666', linestyle='-')
        plt.minorticks_on()
        plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
        plt.subplot(212)
        plt.plot(df_ta.index, df_ta.iloc[:,0].values, 'b', lw=2)
        plt.plot(df_ta.index, df_ta.iloc[:,1].values, 'g', lw=1)
        plt.plot(df_ta.index, df_ta.iloc[:,2].values, 'r', lw=1)
        plt.xlim(df_stock.index[0], df_stock.index[-1])
        plt.axhline(25, linewidth=3, color='k', ls='--')
        plt.legend([f'ADX ({df_ta.columns[0]})',
                    f'+DI ({df_ta.columns[1]})',
                    f'- DI ({df_ta.columns[2]})'])
        plt.xlabel('Time')
        plt.grid(b=True, which='major', color='#666666', linestyle='-')
        plt.minorticks_on()
        plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
        plt.ylim([0, 100])
        plt.show()
    print("")

    

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

    parser.add_argument('-l', "--length", action="store", dest="n_length", type=check_positive, default=25, help='length')
    parser.add_argument('-s', "--scalar", action="store", dest="n_scalar", type=check_positive, default=100, help='scalar')
    parser.add_argument('-o', "--offset", action="store", dest="n_offset", type=check_positive, default=0, help='offset')

    (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
        return

    df_ta = ta.aroon(high=df_stock['2. high'], low=df_stock['3. low'], length=ns_parser.n_length,
                     scalar=ns_parser.n_scalar, offset=ns_parser.n_offset).dropna()

    plt.subplot(311)
    # Daily
    if s_interval == "1440min":
        #plot_stock_and_ta(df_stock['5. adjusted close'], s_ticker, df_ta.iloc[:,-1], "AROON")
        plt.plot(df_stock.index, df_stock['5. adjusted close'].values, 'k', lw=2)
    # Intraday
    else:
        #plot_stock_and_ta(df_stock['4. close'], s_ticker, df_ta.iloc[:,-1], "AROON")
        plt.plot(df_stock.index, df_stock['4. close'].values, 'k', lw=2)
    plt.title(f"Aroon on {s_ticker}")
    plt.xlim(df_stock.index[0], df_stock.index[-1])
    plt.ylabel(f'Share Price ($)')
    plt.grid(b=True, which='major', color='#666666', linestyle='-')
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    plt.subplot(312)
    plt.plot(df_ta.index, df_ta.iloc[:,0].values, 'r', lw=2)
    plt.plot(df_ta.index, df_ta.iloc[:,1].values, 'g', lw=2)
    plt.xlim(df_stock.index[0], df_stock.index[-1])
    plt.axhline(50, linewidth=1, color='k', ls='--')
    plt.legend([f'Aroon DOWN ({df_ta.columns[0]})',
                f'Aroon UP ({df_ta.columns[1]})'])
    plt.grid(b=True, which='major', color='#666666', linestyle='-')
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    plt.ylim([0, 100])
    plt.subplot(313)
    plt.plot(df_ta.index, df_ta.iloc[:,2].values, 'b', lw=2)
    plt.xlabel('Time')
    plt.legend([f'Aroon OSC ({df_ta.columns[2]})'])
    plt.grid(b=True, which='major', color='#666666', linestyle='-')
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    plt.ylim([-100, 100])
    plt.show()
    print("")
