import argparse
from alpha_vantage.timeseries import TimeSeries
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
def load(l_args, s_ticker, s_start, df_stock):
    parser = argparse.ArgumentParser(prog='load', 
                                     description=""" Given a stock market ticker, and an optional starting time,
                                     load a stock in order to perform analysis""")
    parser.add_argument('-t', "--ticker", action="store", dest="s_ticker", required=True, help='Stock ticker')
    parser.add_argument('-s', "--start", type=valid_date, dest="s_start_date",
                        help="The starting date (format YYYY-MM-DD) of the stock")

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return [s_ticker, s_start, df_stock]

    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    # Currently only supports daily stocks
    ts = TimeSeries(key=cfg.API_KEY_ALPHAVANTAGE, output_format='pandas')
    try:
        df_stock, d_stock_metadata = ts.get_daily(symbol=ns_parser.s_ticker, outputsize='full')     
    except:
        print("Either the ticker or the API_KEY are invalids. Try again!")
        return [s_ticker, s_start, df_stock]

    s_ticker = ns_parser.s_ticker

    if ns_parser.s_start_date:
        s_start = ns_parser.s_start_date

    # Slice dataframe from the starting date YYYY-MM-DD selected
    if ns_parser.s_start_date:
        df_stock = df_stock[ns_parser.s_start_date:]

    # Get stock close price
    df_stock = df_stock.iloc[:, 3]

    if s_start:
        print(f"Loading {s_ticker} stock with starting period {s_start.strftime('%Y-%m-%d')} for analysis.\n")
    else:
        print(f"Loading {s_ticker} stock for analysis.\n")

    return [s_ticker, s_start, df_stock]


# ----------------------------------------------------- VIEW -----------------------------------------------------
def view(l_args, s_ticker, s_start):
    parser = argparse.ArgumentParser(prog='view', 
                                     description='Given a stock market ticker, allows to see historical data of \
                                     the corresponding stock. Note that the alpha_vantage key is necessary \
                                     for this to work!')
    if s_ticker:
        parser.add_argument('-t', "--ticker" ,action="store", dest="s_ticker", default=s_ticker, help='Stock ticker')  
    else:
        parser.add_argument('-t', "--ticker" ,action="store", dest="s_ticker", required=True, help='Stock ticker')
        
    parser.add_argument('-s', "--start", type=valid_date, dest="s_start_date",
                        help="The starting date (format YYYY-MM-DD) of the stock")
    parser.add_argument("--type", action="store", dest="n_type", type=check_positive, default=4,
                        help='1234 corresponds to types: 1. open; 2. high; 3.low; 4. close \
                            while 14 corresponds to types: 1.open; 4. close')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    # Currently only supports daily stocks
    ts = TimeSeries(key=cfg.API_KEY_ALPHAVANTAGE, output_format='pandas')
    try:
        df_stock, d_stock_metadata = ts.get_daily(symbol=ns_parser.s_ticker, outputsize='full')     
    except:
        print("Either the ticker or the API_KEY are invalids. Try again!")
        return

    # Slice dataframe from the starting date YYYY-MM-DD selected
    if ns_parser.s_start_date:
        df_stock = df_stock[ns_parser.s_start_date:]

    # Add function to plot data
    ln_col_idx = [int(x)-1 for x in list(str(ns_parser.n_type))]
    # Check that the types given are not bigger than 3, as there are only 4 types (0-3)
    if len([i for i in ln_col_idx if i > 3]) > 0:
        print("An index bigger than 3 was given, which is wrong. Try again")
        return

    ln_col_idx.append(4) # Append last column of df to be filtered which corresponds to: 5. Volume

    plot_view_stock(df_stock.iloc[:, ln_col_idx], ns_parser.s_ticker)

