import FundamentalAnalysis as fa
from alpha_vantage.fundamentaldata import FundamentalData
import config_bot as cfg
import argparse
import datetime
from stock_market_helper_funcs import *
import pandas as pd


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
        df_fa = fa.quote(s_ticker, API_KEY_FINANCIALMODELINGPREP)
        df_fa.index = [''.join(' ' + char if char.isupper() else char.strip() for char in idx).strip() for idx in df_fa.index.tolist()]
        df_fa.index = [s_val.capitalize() for s_val in df_fa.index]
        df_fa.loc['Market cap'][0] = long_number_format(df_fa.loc['Market cap'][0])
        df_fa.loc['Shares outstanding'][0] = long_number_format(df_fa.loc['Shares outstanding'][0])
        df_fa.loc['Volume'][0] = long_number_format(df_fa.loc['Volume'][0])
        earning_announcment = datetime.datetime.strptime(df_fa.loc['Earnings announcement'][0][0:19],"%Y-%m-%dT%H:%M:%S")
        df_fa.loc['Earnings announcement'][0] = f"{earning_announcment.date()} {earning_announcment.time()}"
        print(df_fa.to_string(header=False))
        print("")
    except:
        print("ERROR!\n")


# ---------------------------------------------------- ENTERPRISE ----------------------------------------------------
def enterprise(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='enterprise', 
                                     description=""" """)

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=1, help='Number of latest info')
    parser.add_argument('-q', action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')
        
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
        print("")


# ---------------------------------------------------- RATING ----------------------------------------------------
def rating(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='rating', 
                                     description=""" Gives information about the rating of a company which includes 
                                                 i.a. the company rating and recommendation as well as ratings based 
                                                 on a variety of ratios.""")
        
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
        print("")


# ------------------------------------------ DISCOUNTED CASH FLOW ------------------------------------------------------
def discounted_cash_flow(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='dcf', 
                                     description=""" """)
    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=1, help='Number of latest info')
    parser.add_argument('-q', action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')
        
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
        print(df_fa)
        print("")
    except:
        print("")


# ---------------------------------------------------- INCOME_STATEMENT ----------------------------------------------------
def income_statement(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='income', 
                                     description=""" """)

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=1, help='Number of latest info')
    parser.add_argument('-q', action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')
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
        print("")
        return

# ---------------------------------------------------- BALANCE_SHEET ----------------------------------------------------
def balance_sheet(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='balance', 
                                     description=""" """)

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=1, help='Number of informations')
    parser.add_argument('-q', action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')
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
        print("")
        return
    

# ---------------------------------------------------- CASH_FLOW ----------------------------------------------------
def cash_flow(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='cash', 
                                     description=""" """)

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=1, help='Number of informations')
    parser.add_argument('-q', action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')
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
        print("")
        return


# ---------------------------------------------------- KEY_METRICS ----------------------------------------------------
def key_metrics(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='metrics', 
                                     description=""" """)

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=1, help='Number of informations')
    parser.add_argument('-q', action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')

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

        print(df_fa)
        print("")
    except:
        print("")
        return


# ---------------------------------------------------- FINANCIAL_RATIOS ----------------------------------------------------
def financial_ratios(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='ratios', 
                                     description=""" """)

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=1, help='Number of informations')
    parser.add_argument('-q', action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')

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

        print(df_fa)
        print("")
    except:
        print("")
        return


# ---------------------------------------------------- FINANCIAL_STATEMENT_GROWTH ----------------------------------------------------
def financial_statement_growth(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='growth', 
                                     description=""" """)

    parser.add_argument('-n', "--num", action="store", dest="n_num", type=check_positive, default=1, help='Number of informations')
    parser.add_argument('-q', action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')

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
        print("")
        return

