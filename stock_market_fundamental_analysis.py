import FundamentalAnalysis as fa
from alpha_vantage.fundamentaldata import FundamentalData
import config_bot as cfg
import argparse
import datetime
from datetime import datetime
from stock_market_helper_funcs import *
import pandas as pd
import json
import requests
from pandas.io.json import json_normalize


# ---------------------------------------------------- PROFILE ----------------------------------------------------
def profile(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='profile', 
                                     description="""Gives information about, among other things, the industry, sector 
                                     exchange and company description. The following fields are expected: Address, Beta, 
                                     Ceo, Changes, Cik, City, Company name, Country, Currency, Cusip, Dcf, Dcf diff, 
                                     Default image, Description, Exchange, Exchange short name, Full time employees, Image, 
                                     Industry, Ipo date, Isin, Last div, Mkt cap, Phone, Price, Range, Sector, State, Symbol, 
                                     Vol avg, Website, Zip. [Source: Financial Modeling Prep API]""")
        
    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:
        df_fa = fa.profile(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP)
        df_fa.index = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_fa.index.tolist()]
        df_fa.index = [s_val.capitalize() for s_val in df_fa.index]
        print(df_fa.drop(index=['Description', 'Image']).to_string(header=False))
        print(f"\nImage: {df_fa.loc['Image'][0]}")
        print(f"\nDescription: {df_fa.loc['Description'][0]}")
        print("")
    except:
        print("ERROR!\n")


# ---------------------------------------------------- RATING ----------------------------------------------------
def rating(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='rating', 
                                     description="""Based on specific ratios, provides information whether the company 
                                     is a (strong) buy, neutral or a (strong) sell. The following fields are expected:
                                     P/B, ROA, DCF, P/E, ROE, and D/E. [Source: Financial Modeling Prep API]""")
        
    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:
        df_fa = fa.rating(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP)
        print(df_fa)
        print("")
    except:
        print("ERROR!\n")


# ---------------------------------------------------- QUOTE ----------------------------------------------------
def quote(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='quote', 
                                     description="""Provides actual information about the company which is, among 
                                     other things, the day high, market cap, open and close price and price-to-equity 
                                     ratio. The following fields are expected: Avg volume, Change, Changes percentage, 
                                     Day high, Day low, Earnings announcement, Eps, Exchange, Market cap, Name, Open, 
                                     Pe, Previous close, Price, Price avg200, Price avg50, Shares outstanding, Symbol, 
                                     Timestamp, Volume, Year high, and Year low. [Source: Financial Modeling Prep API]""")
        
    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:
        df_fa = fa.quote(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP)
        df_fa.index = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_fa.index.tolist()]
        df_fa.index = [s_val.capitalize() for s_val in df_fa.index]
        df_fa.loc['Market cap'][0] = long_number_format(df_fa.loc['Market cap'][0])
        df_fa.loc['Shares outstanding'][0] = long_number_format(df_fa.loc['Shares outstanding'][0])
        df_fa.loc['Volume'][0] = long_number_format(df_fa.loc['Volume'][0])
        earning_announcment = datetime.strptime(df_fa.loc['Earnings announcement'][0][0:19],"%Y-%m-%dT%H:%M:%S")
        df_fa.loc['Earnings announcement'][0] = f"{earning_announcment.date()} {earning_announcment.time()}"
        print(df_fa.to_string(header=False))
        print("")
    except:
        print("ERROR!\n")


# ---------------------------------------------------- ENTERPRISE ----------------------------------------------------
def enterprise(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='enterprise', 
                                     description="""Displays stock price, number of shares, market capitalization and 
                                     enterprise value over time. The following fields are expected: Add total debt, 
                                     Enterprise value, Market capitalization, Minus cash and cash equivalents, Number 
                                     of shares, Stock price, and Symbol. [Source: Financial Modeling Prep API]""")

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=1, help='Number of latest info')
    parser.add_argument('-q', "--quarter", action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')
        
    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    if ns_parser.n_num == 1:
        pd.set_option('display.max_colwidth', -1)
    else:
        pd.options.display.max_colwidth = 40

    try:
        if ns_parser.b_quarter:
            df_fa = fa.enterprise(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period='quarter')
        else:
            df_fa = fa.enterprise(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP)
        
        df_fa = df_fa.iloc[:, 0:ns_parser.n_num]
        df_fa = df_fa.applymap(lambda x: long_number_format(x))
        df_fa.index = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_fa.index.tolist()]
        df_fa.index = [s_val.capitalize() for s_val in df_fa.index]
        print(df_fa)
        print("")
    except:
        print("ERROR!\n")


# ------------------------------------------ DISCOUNTED CASH FLOW ------------------------------------------------------
def discounted_cash_flow(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='dcf', 
                                     description="""Calculates the discounted cash flow of a company over time including 
                                     the DCF of today. The following fields are expected: DCF, Stock price, and Date. 
                                     [Source: Financial Modeling Prep API]""")
    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=1, help='Number of latest info')
    parser.add_argument('-q', "--quarter", action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')
        
    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    if ns_parser.n_num == 1:
        pd.set_option('display.max_colwidth', -1)
    else:
        pd.options.display.max_colwidth = 40

    try:
        if ns_parser.b_quarter:
            df_fa = fa.discounted_cash_flow(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period='quarter')
        else:
            df_fa = fa.discounted_cash_flow(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP)
        
        df_fa = df_fa.iloc[:, 0:ns_parser.n_num]
        df_fa = df_fa.applymap(lambda x: long_number_format(x))
        df_fa.index = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_fa.index.tolist()]
        df_fa.index = [s_val.capitalize() for s_val in df_fa.index]
        df_fa = df_fa.rename(index={"D c f": "DCF"})
        print(df_fa)
        print("")
    except:
        print("ERROR!\n")


# ---------------------------------------------------- OVERVIEW ----------------------------------------------------
def overview(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='overview', 
                                     description="""Gives an overview about the company. The following fields are expected: 
                                     Symbol, Asset type, Name, Description, Exchange, Currency, Country, Sector, Industry, 
                                     Address, Full time employees, Fiscal year end, Latest quarter, Market capitalization, 
                                     EBITDA, PE ratio, PEG ratio, Book value, Dividend per share, Dividend yield, EPS, 
                                     Revenue per share TTM, Profit margin, Operating margin TTM, Return on assets TTM, 
                                     Return on equity TTM, Revenue TTM, Gross profit TTM, Diluted EPS TTM, Quarterly earnings growth YOY, 
                                     Quarterly revenue growth YOY, Analyst target price, Trailing PE, Forward PE, 
                                     Price to sales ratio TTM, Price to book ratio, EV to revenue, EV to EBITDA, Beta, 52 week high, 
                                     52 week low, 50 day moving average, 200 day moving average, Shares outstanding, Shares float, 
                                     Shares short, Shares short prior month, Short ratio, Short percent outstanding, Short percent float, 
                                     Percent insiders, Percent institutions, Forward annual dividend rate, Forward annual dividend yield, 
                                     Payout ratio, Dividend date, Ex dividend date, Last split factor, and Last split date. 
                                     [Source: Alpha Vantage API]""")
        
    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:
        # Request OVERVIEW data from Alpha Vantage API
        s_req = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={s_ticker}&apikey={cfg.API_KEY_FINANCIALMODELINGPREP}"      
        result = requests.get(s_req, stream=True)
        
        # If the returned data was successful
        if result.status_code == 200:
            # Parse json data to dataframe
            df_fa = json_normalize(result.json())
            # Keep json data sorting in dataframe
            df_fa = df_fa[list(result.json().keys())].T
            df_fa = df_fa.applymap(lambda x: long_number_format(x))
            df_fa.index = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_fa.index.tolist()]
            df_fa.index = [s_val.capitalize() for s_val in df_fa.index]
            df_fa = df_fa.rename(index={"E b i t d a":"EBITDA",
                                        "P e ratio":"PE ratio",
                                        "P e g ratio":"PEG ratio",
                                        "E p s":"EPS",
                                        "Revenue per share t t m":"Revenue per share TTM",
                                        "Operating margin t t m":"Operating margin TTM",
                                        "Return on assets t t m":"Return on assets TTM",
                                        "Return on equity t t m":"Return on equity TTM",
                                        "Revenue t t m":"Revenue TTM",
                                        "Gross profit t t m":"Gross profit TTM",
                                        "Diluted e p s t t m":"Diluted EPS TTM",
                                        "Quarterly earnings growth y o y":"Quarterly earnings growth YOY",
                                        "Quarterly revenue growth y o y":"Quarterly revenue growth YOY",
                                        "Trailing p e":"Trailing PE",
                                        "Forward p e":"Forward PE",
                                        "Price to sales ratio t t m":"Price to sales ratio TTM",
                                        "E v to revenue":"EV to revenue",
                                        "E v to e b i t d a":"EV to EBITDA"})

            pd.set_option('display.max_colwidth', -1)
            
            print(df_fa.drop(index=['Description']).to_string(header=False))
            print(f"Description: {df_fa.loc['Description'][0]}")
            print("")
        else:
            print(f"Error: {result.status_code}")
        
    except:
        print("ERROR!\n")


# ---------------------------------------------------- EARNINGS ----------------------------------------------------
def earnings(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='earnings', 
                                     description="""Retrieves earnings dates and reported EPS of the company. 
                                     The following fields are expected: Fiscal Date Ending and Reported EPS.
                                     [Source: Alpha Vantage API]""")

    parser.add_argument('-q', "--quarter", action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')
    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=5, help='Number of latest info')
        
    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:
        # Request EARNINGS data from Alpha Vantage API
        s_req = f"https://www.alphavantage.co/query?function=EARNINGS&symbol={s_ticker}&apikey={cfg.API_KEY_FINANCIALMODELINGPREP}"      
        result = requests.get(s_req, stream=True)
        
        # If the returned data was successful
        if result.status_code == 200:
            df_fa = json_normalize(result.json())
            if ns_parser.b_quarter:
                df_fa = pd.DataFrame(df_fa['quarterlyEarnings'][0])
                df_fa = df_fa[["fiscalDateEnding", "reportedDate", "reportedEPS", "estimatedEPS", "surprise", "surprisePercentage"]]
                df_fa = df_fa.rename(columns={"fiscalDateEnding":"Fiscal Date Ending",
                                            "reportedEPS":"Reported EPS",
                                            "estimatedEPS":"Estimated EPS",
                                            "reportedDate":"Reported Date",
                                            "surprise":"Surprise",
                                            "surprisePercentage":"Suprise Percentage"})
            else:
                df_fa = pd.DataFrame(df_fa['annualEarnings'][0])
                df_fa = df_fa.rename(columns={"fiscalDateEnding":"Fiscal Date Ending",
                                            "reportedEPS":"Reported EPS"})

            print(df_fa.head(n=ns_parser.n_num).T.to_string(header=False))
            print("")
        else:
            print(f"Error: {result.status_code}")
        
    except:
        print("ERROR!\n")


# ---------------------------------------------------- INCOME_STATEMENT ----------------------------------------------------
def income_statement(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='income', 
                                     description="""Collects a complete income statement over time. This can be either quarterly 
                                     or annually. The following fields are expected: Accepted date, Cost and expenses, Cost of 
                                     revenue, Depreciation and amortization, Ebitda, Ebitdaratio, Eps, Epsdiluted, Filling date, 
                                     Final link, General and administrative expenses, Gross profit, Gross profit ratio, Income 
                                     before tax, Income before tax ratio, Income tax expense, Interest expense, Link, Net income, 
                                     Net income ratio, Operating expenses, Operating income, Operating income ratio, Other expenses, 
                                     Period, Research and development expenses, Revenue, Selling and marketing expenses, Total other 
                                     income expenses net, Weighted average shs out, Weighted average shs out dil [Default source: 
                                     Alpha Vantage API; Other possible source: Financial Modeling Prep API]""")

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=1, help='Number of latest info')
    parser.add_argument('-q', "--quarter", action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')
    parser.add_argument('--fmp', action="store_true", default=False, dest="b_fmp", help='Use Financial Modeling Prep instead of Alpha Vantage')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:
        if ns_parser.n_num == 1:
            pd.set_option('display.max_colwidth', -1)
        else:
            pd.options.display.max_colwidth = 40

        # Use Financial Modeling Prep API
        if ns_parser.b_fmp:
            if ns_parser.b_quarter:
                df_fa = fa.income_statement(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period='quarter')
            else:
                df_fa = fa.income_statement(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP)

            df_fa = df_fa.iloc[:, 0:ns_parser.n_num]
            df_fa = df_fa.mask(df_fa.astype(object).eq(ns_parser.n_num*['None'])).dropna()
            df_fa = df_fa.mask(df_fa.astype(object).eq(ns_parser.n_num*['0'])).dropna()
            df_fa = df_fa.applymap(lambda x: long_number_format(x))
            df_fa.index = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_fa.index.tolist()]
            df_fa.index = [s_val.capitalize() for s_val in df_fa.index]
            df_fa.columns.name = "Fiscal Date Ending"
            print(df_fa.drop(index=['Final link', 'Link']).to_string())

            pd.set_option('display.max_colwidth', -1)
            print("")
            print(df_fa.loc['Final link'].to_frame().to_string())
            print("")
            print(df_fa.loc['Link'].to_frame().to_string())

        # Use Alpha Vantage API
        else:
            fd = FundamentalData(key=cfg.API_KEY_ALPHAVANTAGE, output_format='pandas')
            if ns_parser.b_quarter:
                df_fa, d_fd_metadata = fd.get_income_statement_quarterly(symbol=s_ticker)
            else:
                df_fa, d_fd_metadata = fd.get_income_statement_annual(symbol=s_ticker)

            df_fa = df_fa.set_index('fiscalDateEnding')
            df_fa = df_fa.head(n=ns_parser.n_num).T
            df_fa = df_fa.mask(df_fa.astype(object).eq(ns_parser.n_num*['None'])).dropna()
            df_fa = df_fa.mask(df_fa.astype(object).eq(ns_parser.n_num*['0'])).dropna()
            df_fa = df_fa.applymap(lambda x: long_number_format(x))
            df_fa.index = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_fa.index.tolist()]
            df_fa.index = [s_val.capitalize() for s_val in df_fa.index]
            df_fa.columns.name = "Fiscal Date Ending"
            print(df_fa)
        print("")
    except:
        print("ERROR!\n")
        return

# ---------------------------------------------------- BALANCE_SHEET ----------------------------------------------------
def balance_sheet(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='balance', 
                                     description="""Collects a complete balance sheet statement over time. This can be 
                                     either quarterly or annually. The following fields are expected: Accepted date, 
                                     Account payables, Accumulated other comprehensive income loss, Cash and cash 
                                     equivalents, Cash and short term investments, Common stock, Deferred revenue, 
                                     Deferred revenue non current, Deferred tax liabilities non current, Filling date, 
                                     Final link, Goodwill, Goodwill and intangible assets, Intangible assets, Inventory, 
                                     Link, Long term debt, Long term investments, Net debt, Net receivables, Other assets, 
                                     Other current assets, Other current liabilities, Other liabilities, Other non current 
                                     assets, Other non current liabilities, Othertotal stockholders equity, Period, Property 
                                     plant equipment net, Retained earnings, Short term debt, Short term investments, Tax assets, 
                                     Tax payables, Total assets, Total current assets, Total current liabilities, Total debt, 
                                     Total investments, Total liabilities, Total liabilities and stockholders equity, Total 
                                     non current assets, Total non current liabilities, and Total stockholders equity. 
                                     [Default source: Alpha Vantage API; Other possible source: Financial Modeling Prep API]""")

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=1, help='Number of informations')
    parser.add_argument('-q', "--quarter", action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')
    parser.add_argument('--fmp', action="store_true", default=False, dest="b_fmp", help='Use Financial Modeling Prep instead of Alpha Vantage')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:
        # Use Financial Modeling Prep API
        if ns_parser.b_fmp:
            if ns_parser.b_quarter:
                df_fa = fa.balance_sheet_statement(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period='quarter')
            else:
                df_fa = fa.balance_sheet_statement(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP)
            
            df_fa = df_fa.iloc[:, 0:ns_parser.n_num]
            df_fa = df_fa.mask(df_fa.astype(object).eq(ns_parser.n_num*['None'])).dropna()
            df_fa = df_fa.mask(df_fa.astype(object).eq(ns_parser.n_num*['0'])).dropna()
            df_fa = df_fa.applymap(lambda x: long_number_format(x))
            df_fa.index = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_fa.index.tolist()]
            df_fa.index = [s_val.capitalize() for s_val in df_fa.index]
            df_fa.columns.name = "Fiscal Date Ending"
            print(df_fa.drop(index=['Final link', 'Link']).to_string())

            pd.set_option('display.max_colwidth', -1)
            print("")
            print(df_fa.loc['Final link'].to_frame().to_string())
            print("")
            print(df_fa.loc['Link'].to_frame().to_string())

        # Use Alpha Vantage API
        else:
            fd = FundamentalData(key=cfg.API_KEY_ALPHAVANTAGE, output_format='pandas')
            if ns_parser.b_quarter:
                df_fa, d_fd_metadata = fd.get_balance_sheet_quarterly(symbol=s_ticker)
            else:
                df_fa, d_fd_metadata = fd.get_balance_sheet_annual(symbol=s_ticker)

            df_fa = df_fa.set_index('fiscalDateEnding')
            df_fa = df_fa.head(n=ns_parser.n_num).T
            df_fa = df_fa.mask(df_fa.astype(object).eq(ns_parser.n_num*['None'])).dropna()
            df_fa = df_fa.mask(df_fa.astype(object).eq(ns_parser.n_num*['0'])).dropna()
            df_fa = df_fa.applymap(lambda x: long_number_format(x))
            df_fa.index = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_fa.index.tolist()]
            df_fa.index = [s_val.capitalize() for s_val in df_fa.index]
            df_fa.columns.name = "Fiscal Date Ending"
            print(df_fa)

        print("")
    except:
        print("ERROR!\n")
        return
    

# ---------------------------------------------------- CASH_FLOW ----------------------------------------------------
def cash_flow(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='cash', 
                                     description="""Collects a complete cash flow statement over time. This can be either 
                                     quarterly or annually. The following fields are expected: Accepted date, Accounts payables, 
                                     Accounts receivables, Acquisitions net, Capital expenditure, Cash at beginning of period, 
                                     Cash at end of period, Change in working capital, Common stock issued, Common stock repurchased, 
                                     Debt repayment, Deferred income tax, Depreciation and amortization, Dividends paid, 
                                     Effect of forex changes on cash, Filling date, Final link, Free cash flow, Inventory, 
                                     Investments in property plant and equipment, Link, Net cash provided by operating activities, 
                                     Net cash used for investing activites, Net cash used provided by financing activities, Net 
                                     change in cash, Net income, Operating cash flow, Other financing activites, Other investing 
                                     activites, Other non cash items, Other working capital, Period, Purchases of investments, 
                                     Sales maturities of investments, Stock based compensation. [Default source: Alpha Vantage API; 
                                     Other possible source: Financial Modeling Prep API]""")

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=1, help='Number of informations')
    parser.add_argument('-q', "--quarter", action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')
    parser.add_argument('--fmp', action="store_true", default=False, dest="b_fmp", help='Use Financial Modeling Prep instead of Alpha Vantage')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:
        if ns_parser.n_num == 1:
            pd.set_option('display.max_colwidth', -1)
        else:
            pd.options.display.max_colwidth = 40

        # Use Financial Modeling Prep API
        if ns_parser.b_fmp:
            if ns_parser.b_quarter:
                df_fa = fa.cash_flow_statement(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period='quarter')
            else:
                df_fa = fa.cash_flow_statement(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP)

            df_fa = df_fa.iloc[:, 0:ns_parser.n_num]
            df_fa = df_fa.mask(df_fa.astype(object).eq(ns_parser.n_num*['None'])).dropna()
            df_fa = df_fa.mask(df_fa.astype(object).eq(ns_parser.n_num*['0'])).dropna()
            df_fa = df_fa.applymap(lambda x: long_number_format(x))
            df_fa.index = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_fa.index.tolist()]
            df_fa.index = [s_val.capitalize() for s_val in df_fa.index]
            df_fa.columns.name = "Fiscal Date Ending"
            print(df_fa.drop(index=['Final link', 'Link']).to_string())

            pd.set_option('display.max_colwidth', -1)
            print("")
            print(df_fa.loc['Final link'].to_frame().to_string())
            print("")
            print(df_fa.loc['Link'].to_frame().to_string())
        # Use Alpha Vantage API
        else:
            fd = FundamentalData(key=cfg.API_KEY_ALPHAVANTAGE, output_format='pandas')
            if ns_parser.b_quarter:
                df_fa, d_fd_metadata = fd.get_cash_flow_quarterly(symbol=s_ticker)
            else:
                df_fa, d_fd_metadata = fd.get_cash_flow_annual(symbol=s_ticker)

            df_fa = df_fa.set_index('fiscalDateEnding')
            df_fa = df_fa.head(n=ns_parser.n_num).T
            df_fa = df_fa.mask(df_fa.astype(object).eq(ns_parser.n_num*['None'])).dropna()
            df_fa = df_fa.mask(df_fa.astype(object).eq(ns_parser.n_num*['0'])).dropna()
            df_fa = df_fa.applymap(lambda x: long_number_format(x))
            df_fa.index = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_fa.index.tolist()]
            df_fa.index = [s_val.capitalize() for s_val in df_fa.index]
            df_fa.columns.name = "Fiscal Date Ending"
            print(df_fa)

        print("")
    except:
        print("ERROR!\n")
        return


# ---------------------------------------------------- KEY_METRICS ----------------------------------------------------
def key_metrics(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='metrics', 
                                     description="""Lists the key metrics (in total 57 metrics) of a company over time 
                                     (annual and quarterly). This includes, among other things, Return on Equity (ROE), 
                                     Working Capital, Current Ratio and Debt to Assets. The following fields are expected: 
                                     Average inventory, Average payables, Average receivables, Book value per share, Capex 
                                     per share, Capex to depreciation, Capex to operating cash flow, Capex to revenue, Cash 
                                     per share, Current ratio, Days of inventory on hand, Days payables outstanding, Days sales 
                                     outstanding, Debt to assets, Debt to equity, Dividend yield, Earnings yield, Enterprise value, 
                                     Enterprise value over EBITDA, Ev to free cash flow, Ev to operating cash flow, Ev to sales, 
                                     Free cash flow per share, Free cash flow yield, Graham net net, Graham number, Income quality, 
                                     Intangibles to total assets, Interest debt per share, Inventory turnover, Market cap, Net 
                                     current asset value, Net debt to EBITDA, Net income per share, Operating cash flow per share, 
                                     Payables turnover, Payout ratio, Pb ratio, Pe ratio, Pfcf ratio, Pocfratio, Price to sales ratio, 
                                     Ptb ratio, Receivables turnover, Research and ddevelopement to revenue, Return on tangible assets, 
                                     Revenue per share, Roe, Roic, Sales general and administrative to revenue, Shareholders equity per 
                                     share, Stock based compensation to revenue, Tangible book value per share, and Working capital.
                                     [Source: Financial Modeling Prep API]""")

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=1, help='Number of informations')
    parser.add_argument('-q', "--quarter", action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:
        if ns_parser.n_num == 1:
            pd.set_option('display.max_colwidth', -1)
        else:
            pd.options.display.max_colwidth = 50

        if ns_parser.b_quarter:
            df_fa = fa.key_metrics(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period='quarter')
        else:
            df_fa = fa.key_metrics(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP)

        df_fa = df_fa.iloc[:, 0:ns_parser.n_num]
        df_fa = df_fa.mask(df_fa.astype(object).eq(ns_parser.n_num*['None'])).dropna()
        df_fa = df_fa.mask(df_fa.astype(object).eq(ns_parser.n_num*['0'])).dropna()
        df_fa = df_fa.applymap(lambda x: long_number_format(x))
        df_fa.index = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_fa.index.tolist()]
        df_fa.index = [s_val.capitalize() for s_val in df_fa.index]
        df_fa.columns.name = "Fiscal Date Ending"
        df_fa = df_fa.rename(index={"Enterprise value over e b i t d a": "Enterprise value over EBITDA"})
        df_fa = df_fa.rename(index={"Net debt to e b i t d a": "Net debt to EBITDA"})
        print(df_fa)
        print("")
    except:
        print("ERROR!\n")
        return


# ---------------------------------------------------- FINANCIAL_RATIOS ----------------------------------------------------
def financial_ratios(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='ratios', 
                                     description="""Includes in-depth ratios (in total 57 ratios) of a company over time 
                                     (annual and quarterly). This contains, among other things, Price-to-Book Ratio, Payout 
                                     Ratio and Operating Cycle. The following fields are expected: Asset turnover, Capital 
                                     expenditure coverage ratio, Cash conversion cycle, Cash flow coverage ratios, Cash flow 
                                     to debt ratio, Cash per share, Cash ratio, Company equity multiplier, Current ratio, 
                                     Days of inventory outstanding, Days of payables outstanding, Days of sales outstanding, 
                                     Debt equity ratio, Debt ratio, Dividend paid and capex coverage ratio, Dividend payout ratio, 
                                     Dividend yield, Ebit per revenue, Ebt per ebit, Effective tax rate, Enterprise value multiple, 
                                     Fixed asset turnover, Free cash flow operating cash flow ratio, Free cash flow per share, Gross 
                                     profit margin, Inventory turnover, Long term debt to capitalization, Net income per EBT, Net 
                                     profit margin, Operating cash flow per share, Operating cash flow sales ratio, Operating cycle, 
                                     Operating profit margin, Payables turnover, Payout ratio, Pretax profit margin, Price book value 
                                     ratio, Price cash flow ratio, Price earnings ratio, Price earnings to growth ratio, Price fair value, 
                                     Price sales ratio, Price to book ratio, Price to free cash flows ratio, Price to operating cash flows 
                                     ratio, Price to sales ratio, Quick ratio, Receivables turnover, Return on assets, Return on capital 
                                     employed, Return on equity, Short term coverage ratios, and Total debt to capitalization. 
                                     [Source: Financial Modeling Prep API]""")

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=1, help='Number of informations')
    parser.add_argument('-q', "--quarter", action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:        
        if ns_parser.n_num == 1:
            pd.set_option('display.max_colwidth', -1)
        else:
            pd.options.display.max_colwidth = 40
        
        if ns_parser.b_quarter:
            df_fa = fa.financial_ratios(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period='quarter')
        else:
            df_fa = fa.financial_ratios(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP)

        df_fa = df_fa.iloc[:, 0:ns_parser.n_num]
        df_fa = df_fa.mask(df_fa.astype(object).eq(ns_parser.n_num*['None'])).dropna()
        df_fa = df_fa.mask(df_fa.astype(object).eq(ns_parser.n_num*['0'])).dropna()
        df_fa = df_fa.applymap(lambda x: long_number_format(x))
        df_fa.index = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_fa.index.tolist()]
        df_fa.index = [s_val.capitalize() for s_val in df_fa.index]
        df_fa.columns.name = "Fiscal Date Ending"
        df_fa = df_fa.rename(index={"Net income per e b t": "Net income per EBT"})

        print(df_fa)
        print("")
    except:
        print("ERROR!\n")
        return


# ---------------------------------------------------- FINANCIAL_STATEMENT_GROWTH ----------------------------------------------------
def financial_statement_growth(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='growth', 
                                     description="""Measures the growth of several financial statement items and ratios over time 
                                     (annual and quarterly). These are, among other things, Revenue Growth (3, 5 and 10 years), 
                                     inventory growth and operating cash flow growth (3, 5 and 10 years). The following fields 
                                     are expected: Asset growth, Book valueper share growth, Debt growth, Dividendsper share growth, 
                                     Ebitgrowth, Epsdiluted growth, Epsgrowth, Five y dividendper share growth per share, Five y net 
                                     income growth per share, Five y operating c f growth per share, Five y revenue growth per share, 
                                     Five y shareholders equity growth per share, Free cash flow growth, Gross profit growth, Inventory 
                                     growth, Net income growth, Operating cash flow growth, Operating income growth, Rdexpense growth, 
                                     Receivables growth, Revenue growth, Sgaexpenses growth, Ten y dividendper share growth per share, 
                                     Ten y net income growth per share, Ten y operating c f growth per share, Ten y revenue growth per 
                                     share, Ten y shareholders equity growth per share, Three y dividendper share growth per share, 
                                     Three y net income growth per share, Three y operating c f growth per share, Three y revenue growth 
                                     per share, Three y shareholders equity growth per share, Weighted average shares diluted growth, 
                                     and Weighted average shares growth [Source: Financial Modeling Prep API]""")

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=1, help='Number of informations')
    parser.add_argument('-q', "--quarter", action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
    except SystemExit:
        print("")
        return
    
    if l_unknown_args:
        print(f"The following args couldn't be interpreted: {l_unknown_args}")

    try:        
        if ns_parser.n_num == 1:
            pd.set_option('display.max_colwidth', -1)
        else:
            pd.options.display.max_colwidth = 50
        
        if ns_parser.b_quarter:
            df_fa = fa.financial_statement_growth(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP, period='quarter')
        else:
            df_fa = fa.financial_statement_growth(s_ticker, cfg.API_KEY_FINANCIALMODELINGPREP)

        df_fa = df_fa.iloc[:, 0:ns_parser.n_num]
        df_fa = df_fa.mask(df_fa.astype(object).eq(ns_parser.n_num*['None'])).dropna()
        df_fa = df_fa.mask(df_fa.astype(object).eq(ns_parser.n_num*['0'])).dropna()
        df_fa = df_fa.applymap(lambda x: long_number_format(x))
        df_fa.index = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_fa.index.tolist()]
        df_fa.index = [s_val.capitalize() for s_val in df_fa.index]
        df_fa.columns.name = "Fiscal Date Ending"

        print(df_fa)
        print("")
    except:
        print("ERROR!\n")
        return
