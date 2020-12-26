import argparse
from alpha_vantage.timeseries import TimeSeries
import re
import config_bot as cfg
import pandas as pd
from stock_market_helper_funcs import *


# ---------------------------------------------------- GAINERS ----------------------------------------------------
def gainers(l_args):
    parser = argparse.ArgumentParser(prog='gainers', 
                                     description='Show top ticker gainers from Yahoo Finance')
    parser.add_argument('-n', "--num", action="store", dest="n_gainers", type=int, default=5, choices=range(1, 25),
                        help='Number of the top gainers stocks to retrieve (default 5)')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    df_gainers = pd.read_html('https://finance.yahoo.com/screener/predefined/day_gainers')[0]
    print(df_gainers.head(ns_parser.n_gainers).to_string(index=False))
    print("")

# ----------------------------------------------------- LOAD -----------------------------------------------------
def load(l_args, s_ticker, s_start, s_interval, df_stock):
    parser = argparse.ArgumentParser(prog='load', description=""" Load a stock in order to perform analysis""")
    parser.add_argument('-t', "--ticker", action="store", dest="s_ticker", required=True, help="Stock ticker")
    parser.add_argument('-s', "--start", type=valid_date, dest="s_start_date", help="The starting date (format YYYY-MM-DD) of the stock")
    parser.add_argument('-i', "--interval", action="store", dest="n_interval", type=int, default=1440, choices=[1,5,15,30,60], help="Intraday stock minutes")

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return [s_ticker, s_start, s_interval, df_stock]

    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    # Update values:
    s_ticker = ns_parser.s_ticker
    s_start = ns_parser.s_start_date
    s_interval = str(ns_parser.n_interval)+'min'

    try:
        ts = TimeSeries(key=cfg.API_KEY_ALPHAVANTAGE, output_format='pandas')
        # Daily
        if s_interval == "1440min":
            df_stock, d_stock_metadata = ts.get_daily_adjusted(symbol=ns_parser.s_ticker, outputsize='full')     
        # Intraday
        else: 
            df_stock, d_stock_metadata = ts.get_intraday(symbol=ns_parser.s_ticker, outputsize='full', interval=s_interval)  
            
    except:
        print("Either the ticker or the API_KEY are invalids. Try again!")
        return [s_ticker, s_start, s_interval, df_stock]

    s_intraday = (f'Intraday {s_interval}', 'Daily')[s_interval == "1440min"]

    if s_start:
        # Slice dataframe from the starting date YYYY-MM-DD selected
        df_stock = df_stock[ns_parser.s_start_date:]
        print(f"Loading {s_intraday} {s_ticker} stock with starting period {s_start.strftime('%Y-%m-%d')} for analysis.\n")
    else:
        print(f"Loading {s_intraday} {s_ticker} stock for analysis.\n")

    return [s_ticker, s_start, s_interval, df_stock]


# ----------------------------------------------------- VIEW -----------------------------------------------------
def view(l_args, s_ticker, s_start, s_interval, df_stock):
    parser = argparse.ArgumentParser(prog='view', description='Visualise historical data of a stock. An alpha_vantage key is necessary.')
    if s_ticker:
        parser.add_argument('-t', "--ticker", action="store", dest="s_ticker", default=s_ticker, help='Stock ticker')  
    else:
        parser.add_argument('-t', "--ticker", action="store", dest="s_ticker", required=True, help='Stock ticker')
    parser.add_argument('-s', "--start", type=valid_date, dest="s_start_date", help="The starting date (format YYYY-MM-DD) of the stock")
    parser.add_argument('-i', "--interval", action="store", dest="n_interval", type=int, default=0, choices=[1,5,15,30,60], help="Intraday stock minutes")
    parser.add_argument("--type", action="store", dest="n_type", type=check_positive, default=5, # in case it's daily
                        help='1234 corresponds to types: 1. open; 2. high; 3.low; 4. close; while 14 corresponds to types: 1.open; 4. close')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    # Update values:
    s_ticker = ns_parser.s_ticker
    if ns_parser.s_start_date:
        s_start = ns_parser.s_start_date

    # A new interval intraday period was given
    if ns_parser.n_interval != 0:
        s_interval = str(ns_parser.n_interval)+'min'

    try:
        ts = TimeSeries(key=cfg.API_KEY_ALPHAVANTAGE, output_format='pandas')
        # Daily
        if s_interval == "1440min":
            df_stock, d_stock_metadata = ts.get_daily_adjusted(symbol=s_ticker, outputsize='full')
        # Intraday
        else:
            df_stock, d_stock_metadata = ts.get_intraday(symbol=s_ticker, outputsize='full', interval=s_interval)  
              
    except:
        print("Either the ticker or the API_KEY are invalids. Try again!")
        return

    # Slice dataframe from the starting date YYYY-MM-DD selected
    df_stock = df_stock[s_start:]

    # Daily
    if s_interval == "1440min":
         # The default doesn't exist for intradaily data
        ln_col_idx = [int(x)-1 for x in list(str(ns_parser.n_type))]
        if 4 not in ln_col_idx:
            ln_col_idx.append(4)
        # Check that the types given are not bigger than 4, as there are only 5 types (0-4)
        if len([i for i in ln_col_idx if i > 4]) > 0:
            print("An index bigger than 4 was given, which is wrong. Try again")
            return
        # Append last column of df to be filtered which corresponds to: 6. Volume
        ln_col_idx.append(5) 
    # Intraday
    else:
        # The default doesn't exist for intradaily data
        if ns_parser.n_type == 5:
            ln_col_idx = [3]
        else:
            ln_col_idx = [int(x)-1 for x in list(str(ns_parser.n_type))]
        # Check that the types given are not bigger than 3, as there are only 4 types (0-3)
        if len([i for i in ln_col_idx if i > 3]) > 0:
            print("An index bigger than 3 was given, which is wrong. Try again")
            return
        # Append last column of df to be filtered which corresponds to: 5. Volume
        ln_col_idx.append(4) 

    # Plot view of the stock
    plot_view_stock(df_stock.iloc[:, ln_col_idx], ns_parser.s_ticker)
