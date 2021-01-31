import yfinance as yf
import pandas as pd
import config_bot as cfg
import argparse
from stock_market_helper_funcs import *


# ---------------------------------------------------- INFO ----------------------------------------------------
def info(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='info', 
                                     description="""Information about the company. The following fields are expected: 
                                     Zip, Sector, Full time employees, Long business summary, City, Phone, State, Country, 
                                     Website, Max age, Address, Industry, Previous close, Regular market open, Two hundred 
                                     day average, Payout ratio, Regular market day high, Average daily volume 10 day, 
                                     Regular market previous close, Fifty day average, Open, Average volume 10 days, Beta, 
                                     Regular market day low, Price hint, Currency, Trailing PE, Regular market volume, 
                                     Market cap, Average volume, Price to sales trailing 12 months, Day low, Ask, Ask size, 
                                     Volume, Fifty two week high, Forward PE, Fifty two week low, Bid, Tradeable, Bid size, 
                                     Day high, Exchange, Short name, Long name, Exchange timezone name, Exchange timezone 
                                     short name, Is esg populated, Gmt off set milliseconds, Quote type, Symbol, Message board id, 
                                     Market, Enterprise to revenue, Profit margins, Enterprise to ebitda, 52 week change, 
                                     Forward EPS, Shares outstanding, Book value, Shares short, Shares percent shares out, 
                                     Last fiscal year end, Held percent institutions, Net income to common, Trailing EPS, 
                                     Sand p52 week change, Price to book, Held percent insiders, Next fiscal year end, 
                                     Most recent quarter, Short ratio, Shares short previous month date, Float shares, 
                                     Enterprise value, Last split date, Last split factor, Earnings quarterly growth, 
                                     Date short interest, PEG ratio, Short percent of float, Shares short prior month, 
                                     Regular market price, Logo_url. [Source: Yahoo Finance API]""")

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        stock = yf.Ticker(s_ticker)
        df_info = pd.DataFrame(stock.info.items(), columns=['Metric', 'Value'])
        df_info = df_info.set_index('Metric')

        df_info.index = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_info.index.tolist()]
        df_info.index = [s_val.capitalize() for s_val in df_info.index]

        df_info.loc['Last split date'].values[0] = datetime.fromtimestamp(df_info.loc['Last split date'].values[0]).strftime('%d/%m/%Y')

        df_info = df_info.mask(df_info['Value'].astype(str).eq('[]')).dropna()
        df_info = df_info.applymap(lambda x: long_number_format(x))

        df_info = df_info.rename(index={"Address1": "Address",
                                        "Average daily volume10 day": "Average daily volume 10 day",
                                        "Average volume10days": "Average volume 10 days",
                                        "Price to sales trailing12 months": "Price to sales trailing 12 months"})
        df_info.index = df_info.index.str.replace('eps','EPS')
        df_info.index = df_info.index.str.replace('p e','PE')
        df_info.index = df_info.index.str.replace('Peg','PEG')

        pd.set_option('display.max_colwidth', -1)
        print(df_info.drop(index=['Long business summary']).to_string(header=False))
        print("")
        print(df_info.loc['Long business summary'].values[0])
        print("")

    except:
        print("")
        return



# ---------------------------------------------------- SHAREHOLDERS ----------------------------------------------------
def shareholders(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='shareholders', 
                                     description="""Major, institutional and mutualfunds shareholders [Source: Yahoo Finance API]""")

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        stock = yf.Ticker(s_ticker)
        pd.set_option('display.max_colwidth', -1)
        
        # Major holders
        print("Major holders")
        df_major_holders = stock.major_holders
        df_major_holders[1] = df_major_holders[1].apply(lambda x: x.replace('%', 'Percentage'))
        print(df_major_holders.to_string(index=False, header=False))
        print("")

        # Institutional holders
        print("Institutional holders")
        df_institutional_shareholders = stock.institutional_holders
        df_institutional_shareholders.columns = df_institutional_shareholders.columns.str.replace('% Out','Stake')
        df_institutional_shareholders['Shares'] = df_institutional_shareholders['Shares'].apply(lambda x: long_number_format(x))
        df_institutional_shareholders['Value'] = df_institutional_shareholders['Value'].apply(lambda x: long_number_format(x))
        df_institutional_shareholders['Stake'] = df_institutional_shareholders['Stake'].apply(lambda x: str("{:.2f}".format(100*x))+' %')
        print(df_institutional_shareholders.to_string(index=False))
        print("")

        # Mutualfunds holders
        print("Mutualfunds holders")
        df_mutualfund_shareholders = stock.mutualfund_holders
        df_mutualfund_shareholders.columns = df_mutualfund_shareholders.columns.str.replace('% Out','Stake')
        df_mutualfund_shareholders['Shares'] = df_mutualfund_shareholders['Shares'].apply(lambda x: long_number_format(x))
        df_mutualfund_shareholders['Value'] = df_mutualfund_shareholders['Value'].apply(lambda x: long_number_format(x))
        df_mutualfund_shareholders['Stake'] = df_mutualfund_shareholders['Stake'].apply(lambda x: str("{:.2f}".format(100*x))+' %')
        print(df_mutualfund_shareholders.to_string(index=False))

        print("")

    except:
        print("")
        return

