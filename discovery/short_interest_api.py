import argparse
import webbrowser
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from stock_market_helper_funcs import *


# ------------------------------------------------ HIGH_SHORT_INTEREST -------------------------------------------------
def high_short_interest(l_args):
    parser = argparse.ArgumentParser(prog='high_short', 
                                    description='''HighShortInterest.com provides a convenient sorted database of stocks 
                                    which have a short interest of over 20 percent. Additional key data such as the float, 
                                    number of outstanding shares, and company industry is displayed. Data is presented for 
                                    the Nasdaq Stock Market, the New York Stock Exchange, and the American Stock Exchange. 
                                    Stocks with high short interest are often very volatile and are well known for making 
                                    explosive upside moves (known as a short squeeze). Stock traders will often flock to 
                                    such stocks for no reason other than the fact that they have a high short interest and 
                                    the price can potentially move up very quickly as traders with open short positions move 
                                    to cover.''')
    
    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=10, help='Number of top stocks')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    url_high_short_interested_stocks = f"https://www.highshortinterest.com"
    text_soup_high_short_interested_stocks = BeautifulSoup(requests.get(url_high_short_interested_stocks).text, "lxml")

    a_high_short_interest_header = list()
    for high_short_interest_header in text_soup_high_short_interested_stocks.findAll('td',  {'class': 'tblhdr'}):
        a_high_short_interest_header.append(high_short_interest_header.text.strip('\n').split('\n')[0])
    df_high_short_interest = pd.DataFrame(columns=a_high_short_interest_header)
    df_high_short_interest.loc[0] = ['', '', '', '', '', '', '']

    a_high_short_interested_stocks = re.sub('<!--.*?//-->','', text_soup_high_short_interested_stocks.find_all('td')[3].text, flags=re.DOTALL).split('\n')[2:]
    a_high_short_interested_stocks[0] = a_high_short_interested_stocks[0].replace('TickerCompanyExchangeShortIntFloatOutstdIndustry','')

    l_stock_info = list()
    for elem in a_high_short_interested_stocks:
        if elem is '':
            continue
            
        l_stock_info.append(elem)
            
        if len(l_stock_info) == 7:
            df_high_short_interest.loc[len(df_high_short_interest.index)] = l_stock_info
            l_stock_info = list()
        
    pd.set_option('display.max_colwidth', -1)
    print(df_high_short_interest.head(n=ns_parser.n_num).to_string(index=False))
    print("")


# ---------------------------------------------------- LOW_FLOAT -----------------------------------------------------
def low_float(l_args):
    parser = argparse.ArgumentParser(prog='low_float', 
                                    description='''LowFloat.com provides a convenient sorted database of stocks which 
                                    have a float of under 10 million shares. Additional key data such as the number of 
                                    outstanding shares, short interest, and company industry is displayed. Data is 
                                    presented for the Nasdaq Stock Market, the New York Stock Exchange, the American 
                                    Stock Exchange, and the Over the Counter Bulletin Board. You can view the data for 
                                    all exchanges together or only view exchanges of interest by clicking on the appropriate tab.
                                    Low float stocks are often very volatile and are well known for making explosive upside moves. 
                                    Stock traders will often flock to such stocks for no reason other than the fact that they 
                                    have a low float and the price can potentially move up very quickly.''')
    
    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=10, help='Number of top stocks')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    url_high_short_interested_stocks = f"https://www.lowfloat.com"
    text_soup_low_float_stocks = BeautifulSoup(requests.get(url_high_short_interested_stocks).text, "lxml")

    a_low_float_header = list()
    for low_float_header in text_soup_low_float_stocks.findAll('td',  {'class': 'tblhdr'}):
        a_low_float_header.append(low_float_header.text.strip('\n').split('\n')[0])
    df_low_float = pd.DataFrame(columns=a_low_float_header)
    df_low_float.loc[0] = ['', '', '', '', '', '', '']

    a_low_float_stocks = re.sub('<!--.*?//-->','', text_soup_low_float_stocks.find_all('td')[3].text, flags=re.DOTALL).split('\n')[2:]
    a_low_float_stocks[0] = a_low_float_stocks[0].replace('TickerCompanyExchangeFloatOutstdShortIntIndustry','')

    l_stock_info = list()
    for elem in a_low_float_stocks:
        if elem is '':
            continue
            
        l_stock_info.append(elem)
            
        if len(l_stock_info) == 7:
            df_low_float.loc[len(df_low_float.index)] = l_stock_info
            l_stock_info = list()
        
    pd.set_option('display.max_colwidth', -1)
    print(df_low_float.head(n=ns_parser.n_num).to_string(index=False))
    print("")