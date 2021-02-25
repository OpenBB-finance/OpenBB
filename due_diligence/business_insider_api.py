import argparse
import json
import re

import matplotlib.pyplot as plt
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pandas.plotting import register_matplotlib_converters

from helper_funcs import check_positive, get_next_stock_market_days

register_matplotlib_converters()


# ------------------------------------------- PRICE_TARGET_FROM_ANALYSTS -------------------------------------------
def price_target_from_analysts(l_args, df_stock, s_ticker, s_start, s_interval):
    parser = argparse.ArgumentParser(prog='pt',
                                     description="""Prints price target from analysts. [Source: Business Insider]""")

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=10,
                        help='number of latest price targets from analysts to print.')

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


# ----------------------------------------------- ESTIMATES -----------------------------------------------
def estimates(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='est',
                                     description="""Yearly estimates and quarter earnings/revenues [Source: Business Insider]""")

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        url_market_business_insider = f"https://markets.businessinsider.com/stocks/{s_ticker.lower()}-stock"
        text_soup_market_business_insider = BeautifulSoup(requests.get(url_market_business_insider).text, "lxml")

        l_estimates_year_header = list()
        l_estimates_quarter_header = list()
        for estimates_header in text_soup_market_business_insider.findAll('th', {'class': 'table__th text-right'}):
            s_estimates_header = estimates_header.text.strip()
            if s_estimates_header.isdigit():
                l_estimates_year_header.append(s_estimates_header)
            elif ('in %' not in s_estimates_header) and ('Job' not in s_estimates_header):
                l_estimates_quarter_header.append(s_estimates_header)

        l_estimates_year_metric = list()
        for estimates_year_metric in text_soup_market_business_insider.findAll('td', {'class': 'table__td black'}):
            l_estimates_year_metric.append(estimates_year_metric.text)

        l_estimates_quarter_metric = list()
        for estimates_quarter_metric in text_soup_market_business_insider.findAll('td', {'class': 'table__td font-color-dim-gray'}):
            l_estimates_quarter_metric.append(estimates_quarter_metric.text)

        d_metric_year = dict()
        d_metric_quarter_earnings = dict()
        d_metric_quarter_revenues = dict()
        l_metrics = list()
        n_metrics = 0
        b_year = True
        for idx, metric_value in enumerate(text_soup_market_business_insider.findAll('td', {'class': 'table__td text-right'})):

            if b_year:
                # YEAR metrics
                l_metrics.append(metric_value.text.strip())

                # Check if we have processed all year metrics
                if n_metrics > len(l_estimates_year_metric)-1:
                    b_year = False
                    n_metrics = 0
                    l_metrics = list()
                    idx_y = idx

                # Add value to dictionary
                if (idx+1)%len(l_estimates_year_header) == 0:
                    d_metric_year[l_estimates_year_metric[n_metrics]] = l_metrics
                    l_metrics = list()
                    n_metrics += 1

            if not b_year:
                # QUARTER metrics
                l_metrics.append(metric_value.text.strip())

                # Check if we have processed all quarter metrics
                if n_metrics > len(l_estimates_quarter_metric)-1:
                    break

                # Add value to dictionary
                if (idx-idx_y+1)%len(l_estimates_quarter_header) == 0:
                    if n_metrics < 4:
                        d_metric_quarter_earnings[l_estimates_quarter_metric[n_metrics]] = l_metrics
                    else:
                        d_metric_quarter_revenues[l_estimates_quarter_metric[n_metrics-4]] = l_metrics
                    l_metrics = list()
                    n_metrics += 1

        df_year_estimates = pd.DataFrame.from_dict(d_metric_year, orient='index', columns=l_estimates_year_header)
        df_year_estimates.index.name = 'YEARLY ESTIMATES'
        df_quarter_earnings = pd.DataFrame.from_dict(d_metric_quarter_earnings, orient='index', columns=l_estimates_quarter_header)
        #df_quarter_earnings.index.name = 'Earnings'
        df_quarter_revenues = pd.DataFrame.from_dict(d_metric_quarter_revenues, orient='index', columns=l_estimates_quarter_header)
        #df_quarter_revenues.index.name = 'Revenues'

        l_quarter = list()
        l_date = list()
        for quarter_title in df_quarter_earnings.columns:
            l_quarter.append(re.split('  ending',quarter_title)[0])
            if len(re.split('  ending',quarter_title)) == 2:
                l_date.append('ending ' + re.split('  ending',quarter_title)[1].strip())
            else:
                l_date.append('-')

        df_quarter_earnings.columns = l_quarter
        df_quarter_earnings.loc["Date"] = l_date
        df_quarter_earnings = df_quarter_earnings.reindex(["Date", "No. of Analysts", "Average Estimate", "Year Ago", "Publish Date"])

        df_quarter_revenues.columns = l_quarter
        df_quarter_revenues.loc["Date"] = l_date
        df_quarter_revenues = df_quarter_revenues.reindex(["Date", "No. of Analysts", "Average Estimate", "Year Ago", "Publish Date"])

        print(df_year_estimates.to_string())
        print("")
        print("QUARTER ESTIMATES EARNINGS")
        print(df_quarter_earnings.to_string())
        print("")
        print("QUARTER ESTIMATES REVENUES")
        print(df_quarter_revenues.to_string())
        print("")

        print(text_soup_market_business_insider.find('div', {'class': "text_right instrument-description"}).text.strip())
        print("")

    except:
        print("")
        return


# ----------------------------------------------- INSIDER_ACTIVITY -----------------------------------------------
def insider_activity(l_args, df_stock, s_ticker, s_start, s_interval):
    parser = argparse.ArgumentParser(prog='ins',
                                     description="""Prints insider activity over time [Source: Business Insider]""")
    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=10,
                        help='number of latest insider activity.')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        url_market_business_insider = f"https://markets.businessinsider.com/stocks/{s_ticker.lower()}-stock"
        text_soup_market_business_insider = BeautifulSoup(requests.get(url_market_business_insider).text, "lxml")

        d_insider = dict()
        l_insider_vals = list()
        for idx, insider_val in enumerate(text_soup_market_business_insider.findAll('td', {'class':"table__td text-center"})):
            #print(insider_val.text.strip())

            l_insider_vals.append(insider_val.text.strip())

            # Add value to dictionary
            if (idx+1)%6 == 0:
                # Check if we are still parsing insider trading activity
                if '/' not in l_insider_vals[0]:
                    break
                d_insider[(idx+1)//6] = l_insider_vals
                l_insider_vals = list()

        df_insider = pd.DataFrame.from_dict(d_insider, orient='index',
                                            columns = ['Date', 'Shares Traded', 'Shares Held', 'Price', 'Type', 'Option'])

        df_insider['Date'] = pd.to_datetime(df_insider['Date'])
        df_insider = df_insider.set_index('Date')
        df_insider = df_insider.sort_index(ascending=True)

        if s_start:
            df_insider = df_insider[s_start:]

        pfig, ax = plt.subplots()

        if s_interval == "1440min":
            plt.plot(df_stock.index, df_stock['5. adjusted close'].values, lw=3)
        else: # Intraday
            plt.plot(df_stock.index, df_stock['4. close'].values, lw=3)

        plt.title(f"{s_ticker.upper()} (Time Series) and Price Target")

        plt.xlabel('Time')
        plt.ylabel('Share Price ($)')

        df_insider['Trade'] = df_insider.apply(lambda row: (1, -1)[row.Type == 'Sell'] * float(row['Shares Traded'].replace(',','')), axis=1)
        plt.xlim(df_insider.index[0], df_stock.index[-1])
        min_price, max_price = ax.get_ylim()

        price_range = max_price - min_price
        shares_range = df_insider[df_insider['Type'] == 'Buy'].groupby(by=['Date']).sum()['Trade'].max() - df_insider[df_insider['Type'] == 'Sell'].groupby(by=['Date']).sum()['Trade'].min()
        n_proportion = price_range / shares_range

        for ind in df_insider[df_insider['Type'] == 'Sell'].groupby(by=['Date']).sum().index:
            if ind in df_stock.index:
                ind_dt = ind
            else:
                ind_dt = get_next_stock_market_days(ind, 1)[0]

            n_stock_price = 0
            if s_interval == "1440min":
                n_stock_price = df_stock['5. adjusted close'][ind_dt]
            else:
                n_stock_price = df_stock['4. close'][ind_dt]

            plt.vlines(x=ind_dt,
                       ymin= n_stock_price + n_proportion * float(df_insider[df_insider['Type'] == 'Sell'].groupby(by=['Date']).sum()['Trade'][ind]),
                       ymax= n_stock_price,
                       colors='red', ls='-', lw=5)

        for ind in df_insider[df_insider['Type'] == 'Buy'].groupby(by=['Date']).sum().index:
            if ind in df_stock.index:
                ind_dt = ind
            else:
                ind_dt = get_next_stock_market_days(ind, 1)[0]

            n_stock_price = 0
            if s_interval == "1440min":
                n_stock_price = df_stock['5. adjusted close'][ind_dt]
            else:
                n_stock_price = df_stock['4. close'][ind_dt]

            plt.vlines(x=ind_dt,
                       ymin=n_stock_price,
                       ymax=n_stock_price + n_proportion * float(df_insider[df_insider['Type'] == 'Buy'].groupby(by=['Date']).sum()['Trade'][ind]),
                       colors='green', ls='-', lw=5)

        plt.grid(b=True, which='major', color='#666666', linestyle='-')
        plt.minorticks_on()
        plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
        plt.show()

        l_names = list()
        for s_name in text_soup_market_business_insider.findAll('a', {'onclick':"silentTrackPI()"}):
            l_names.append(s_name.text.strip())
        df_insider['Insider'] = l_names

        print(df_insider.sort_index(ascending=False).head(n=ns_parser.n_num).to_string())
        print("")

    except:
        print("")
        return
