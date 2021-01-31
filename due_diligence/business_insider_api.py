from bs4 import BeautifulSoup
from alpha_vantage.timeseries import TimeSeries
from stock_market_helper_funcs import *
import requests
import pandas as pd
import re
import json
import config_bot as cfg
from datetime import datetime
import argparse
from fuzzywuzzy import fuzz
import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


# ------------------------------------------- PRICE_TARGET_FROM_ANALYSTS -------------------------------------------
def price_target_from_analysts(l_args, df_stock, s_ticker, s_start, s_interval):
    parser = argparse.ArgumentParser(prog='price_target_from_analysts', 
                                     description="""Price target from analysts [Source: Business Insider API]""")
        
    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=10, help='Number of latest price targets')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        url_market_business_insider = f"https://markets.businessinsider.com/stocks/{s_ticker.lower()}-stock"
        text_soup_market_business_insider = BeautifulSoup(requests.get(url_market_business_insider).text, "lxml")

        for script in text_soup_market_business_insider.find_all('script'):
            # Get Analyst data
            if 'window.analyseChartConfigs.push' in script.get_text():
                # Extract config data:
                s_analyst_data = script.get_text().split("config: ",1)[1].split(",\r\n",1)[0]
                d_analyst_data = json.loads(s_analyst_data)
                break
                
        #pprint.pprint(d_analyst_data)
        df_analyst_data = pd.DataFrame.from_dict(d_analyst_data['Markers']) 
        df_analyst_data = df_analyst_data[['DateLabel', 'Company', 'InternalRating', 'PriceTarget']]
        df_analyst_data.columns = ['Date', 'Company', 'Rating', 'Price Target']
        df_analyst_data
        df_analyst_data['Rating'].replace({'gut': 'BUY', 
                                           'neutral': 'HOLD', 
                                           'schlecht':'SELL'}, inplace=True)
        df_analyst_data['Date'] = pd.to_datetime(df_analyst_data['Date'])
        df_analyst_data = df_analyst_data.set_index('Date')

        # Slice start of ratings
        if s_start:
            df_analyst_data = df_analyst_data[s_start:]

        if s_interval == "1440min":
            plt.plot(df_stock.index, df_stock['5. adjusted close'].values, lw=3)
        # Intraday 
        else:
            plt.plot(df_stock.index, df_stock['4. close'].values, lw=3)

        if s_start:
            plt.plot(df_analyst_data.groupby(by=['Date']).mean()[s_start:])
        else:
            plt.plot(df_analyst_data.groupby(by=['Date']).mean())

        plt.scatter(df_analyst_data.index, df_analyst_data['Price Target'], c='r', s=40)

        plt.legend(['Closing Price', 'Average Price Target', 'Price Target'])

        plt.title(f"{s_ticker} (Time Series) and Price Target")
        plt.xlim(df_stock.index[0], df_stock.index[-1])
        plt.xlabel('Time')
        plt.ylabel('Share Price ($)')
        plt.grid(b=True, which='major', color='#666666', linestyle='-')
        plt.minorticks_on()
        plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
        plt.show()
        print("")

        pd.set_option('display.max_colwidth', -1)
        print(df_analyst_data.sort_index(ascending=False).head(ns_parser.n_num).to_string())
        print("")
        
    except:
        print("")
        return
