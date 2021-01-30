import argparse
import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np
from stock_market_helper_funcs import *

# ---------------------------------------------------- INCOME ----------------------------------------------------
def income(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='incom', 
                                     description="""Gives income statement the company. The following fields are expected: 
                                     Sales Growth, Cost of Goods Sold (COGS) incl. D&A, COGS Growth, COGS excluding D&A, 
                                     Depreciation & Amortization Expense, Depreciation, Amortization of Intangibles, Gross Income, 
                                     Gross Income Growth, Gross Profit Margin, SG&A Expense, SGA Growth, Research & Development, 
                                     Other SG&A, Other Operating Expense, Unusual Expense, EBIT after Unusual Expense, 
                                     Non Operating Income/Expense, Non-Operating Interest Income, Equity in Affiliates (Pretax), 
                                     Interest Expense, Interest Expense Growth, Gross Interest Expense, Interest Capitalized, 
                                     Pretax Income, Pretax Income Growth, Pretax Margin, Income Tax, Income Tax - Current Domestic, 
                                     Income Tax - Current Foreign, Income Tax - Deferred Domestic, Income Tax - Deferred Foreign, 
                                     Income Tax Credits, Equity in Affiliates, Other After Tax Income (Expense), Consolidated Net Income, 
                                     Minority Interest Expense, Net Income Growth, Net Margin Growth, Extraordinaries & Discontinued Operations, 
                                     Extra Items & Gain/Loss Sale Of Assets, Cumulative Effect - Accounting Chg, Discontinued Operations, 
                                     Net Income After Extraordinaries, Preferred Dividends, Net Income Available to Common, EPS (Basic), 
                                     EPS (Basic) Growth, Basic Shares Outstanding, EPS (Diluted), EPS (Diluted) Growth, Diluted Shares Outstanding, 
                                     EBITDA, EBITDA Growth, EBITDA Margin, Sales/Revenue, and Net Income. [Source: Market Watch BS]""")
    
    parser.add_argument('-q', "--quarter", action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        if ns_parser.b_quarter:
            url_financials = f"https://www.marketwatch.com/investing/stock/{s_ticker}/financials/income/quarter"
        else:
            url_financials = f"https://www.marketwatch.com/investing/stock/{s_ticker}/financials/income"
            
        text_soup_financials = BeautifulSoup(requests.get(url_financials).text, "lxml")

        # Define financials columns
        a_financials_header = list()
        for financials_header in text_soup_financials.findAll('th',  {'class': 'overflow__heading'}):
            a_financials_header.append(financials_header.text.strip('\n').split('\n')[0])
        df_financials = pd.DataFrame(columns=a_financials_header[0:-1])

        # Add financials values
        soup_financials = text_soup_financials.findAll('tr', {'class': 'table__row '})
        soup_financials += text_soup_financials.findAll('tr', {'class': 'table__row is-highlighted'})
        for financials_info in soup_financials:
            a_financials_info = financials_info.text.split('\n')
            l_financials = [a_financials_info[2]] 
            l_financials.extend(a_financials_info[5:-2])
            # Append data values to financials
            df_financials.loc[len(df_financials.index)] = l_financials

        print(df_financials.to_string(index=False))
        print("")

    except:
        print("")
        return


# ---------------------------------------------------- ASSETS ----------------------------------------------------
def assets(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='assets', 
                                     description="""Gives assets from balance sheet of the company. The following fields are expected: 
                                     Cash & Short Term Investments, Cash & Short Term Investments Growth, Cash Only, 
                                     Short-Term Investments, Cash & ST Investments / Total Assets, Total Accounts Receivable, 
                                     Total Accounts Receivable Growth, Accounts Receivables, Net, Accounts Receivables, Gross, 
                                     Bad Debt/Doubtful Accounts, Other Receivable, Accounts Receivable Turnover, Inventories, 
                                     Finished Goods, Work in Progress, Raw Materials, Progress Payments & Other, Other Current Assets, 
                                     Miscellaneous Current Assets, Net Property, Plant & Equipment, Property, Plant & Equipment - Gross, 
                                     Buildings, Land & Improvements, Computer Software and Equipment, Other Property, Plant & Equipment, 
                                     Accumulated Depreciation, Total Investments and Advances, Other Long-Term Investments, 
                                     Long-Term Note Receivables, Intangible Assets, Net Goodwill, Net Other Intangibles, Other Assets
                                     [Source: Market Watch BS]""")
    
    parser.add_argument('-q', "--quarter", action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}")

        if ns_parser.b_quarter:
            url_financials = f"https://www.marketwatch.com/investing/stock/{s_ticker}/financials/balance-sheet/quarter"
        else:
            url_financials = f"https://www.marketwatch.com/investing/stock/{s_ticker}/financials/balance-sheet"
            
        text_soup_financials = BeautifulSoup(requests.get(url_financials).text, "lxml")

        # Define financials columns
        a_financials_header = list()
        for financials_header in text_soup_financials.findAll('th',  {'class': 'overflow__heading'}):
            a_financials_header.append(financials_header.text.strip('\n').split('\n')[0])
        s_header_end_trend = ("5-year trend", "5- qtr trend")[ns_parser.b_quarter]
        df_financials = pd.DataFrame(columns=a_financials_header[0:a_financials_header.index(s_header_end_trend)])

        # Add financials values
        soup_financials = text_soup_financials.findAll('tr', {'class': 'table__row '})
        soup_financials += text_soup_financials.findAll('tr', {'class': 'table__row is-highlighted'})
        for financials_info in soup_financials:
            a_financials_info = financials_info.text.split('\n')
            l_financials = [a_financials_info[2]] 
            l_financials.extend(a_financials_info[5:-2])
            # Append data values to financials
            df_financials.loc[len(df_financials.index)] = l_financials

        # Set item name as index
        df_financials = df_financials.set_index('Item')

        print(df_financials.iloc[:33].to_string())
        print("")

    except:
        print("ERROR!\n")
        return


# ---------------------------------------------------- LIABILITIES ----------------------------------------------------
def liabilities(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='liabilities', 
                                     description="""Gives liablities and shareholders' equity from balance sheet of the company. 
                                     The following fields are expected: ST Debt & Current Portion LT Debt, Short Term Debt, 
                                     Current Portion of Long Term Debt, Accounts Payable, Accounts Payable Growth, Income Tax Payable, 
                                     Other Current Liabilities, Dividends Payable, Accrued Payroll, Miscellaneous Current Liabilities, 
                                     Long-Term Debt, Long-Term Debt excl. Capitalized Leases, Non-Convertible Debt, Convertible Debt, 
                                     Capitalized Lease Obligations, Provision for Risks & Charges, Deferred Taxes, Deferred Taxes - Credits, 
                                     Deferred Taxes - Debit, Other Liabilities, Other Liabilities (excl. Deferred Income), Deferred Income, 
                                     Non-Equity Reserves, Total Liabilities / Total Assets, Preferred Stock (Carrying Value), 
                                     Redeemable Preferred Stock, Non-Redeemable Preferred Stock, Common Equity (Total), Common Equity/Total Assets, 
                                     Common Stock Par/Carry Value, Retained Earnings, ESOP Debt Guarantee, Cumulative Translation 
                                     Adjustment/Unrealized For. Exch. Gain, Unrealized Gain/Loss Marketable Securities, Revaluation Reserves, 
                                     Treasury Stock, Total Shareholders' Equity, Total Shareholders' Equity / Total Assets, 
                                     Accumulated Minority Interest, Total Equity, Total Current Assets, Total Assets, Total Current Liabilities, 
                                     Total Liabilities, and Liabilities & Shareholders' Equity. [Source: Market Watch BS]""")
    
    parser.add_argument('-q', "--quarter", action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        if ns_parser.b_quarter:
            url_financials = f"https://www.marketwatch.com/investing/stock/{s_ticker}/financials/balance-sheet/quarter"
        else:
            url_financials = f"https://www.marketwatch.com/investing/stock/{s_ticker}/financials/balance-sheet"
            
        text_soup_financials = BeautifulSoup(requests.get(url_financials).text, "lxml")

        # Define financials columns
        a_financials_header = list()
        for financials_header in text_soup_financials.findAll('th',  {'class': 'overflow__heading'}):
            a_financials_header.append(financials_header.text.strip('\n').split('\n')[0])
        s_header_end_trend = ("5-year trend", "5- qtr trend")[ns_parser.b_quarter]
        df_financials = pd.DataFrame(columns=a_financials_header[0:a_financials_header.index(s_header_end_trend)])

        # Add financials values
        soup_financials = text_soup_financials.findAll('tr', {'class': 'table__row '})
        soup_financials += text_soup_financials.findAll('tr', {'class': 'table__row is-highlighted'})
        for financials_info in soup_financials:
            a_financials_info = financials_info.text.split('\n')
            l_financials = [a_financials_info[2]] 
            l_financials.extend(a_financials_info[5:-2])
            # Append data values to financials
            df_financials.loc[len(df_financials.index)] = l_financials

        # Set item name as index
        df_financials = df_financials.set_index('Item')

        print(df_financials.iloc[34:].to_string())
        print("")

    except:
        print("")
        return


# ---------------------------------------------------- OPERATING ----------------------------------------------------
def operating(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='operating', 
                                     description="""Gives cash flow operating activities of the company. The following fields 
                                     are expected: Net Income before Extraordinaries, Net Income Growth, Depreciation, 
                                     Depletion & Amortization, Depreciation and Depletion, Amortization of Intangible Assets, 
                                     Deferred Taxes & Investment Tax Credit, Deferred Taxes, Investment Tax Credit, Other Funds, 
                                     Funds from Operations, Extraordinaries, Changes in Working Capital, Receivables, Accounts Payable, 
                                     Other Assets/Liabilities, and Net Operating Cash Flow Growth. [Source: Market Watch BS]""")
    
    parser.add_argument('-q', "--quarter", action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return
            

        if ns_parser.b_quarter:
            url_financials = f"https://www.marketwatch.com/investing/stock/{s_ticker}/financials/cash-flow/quarter"
        else:
            url_financials = f"https://www.marketwatch.com/investing/stock/{s_ticker}/financials/cash-flow"
            
        text_soup_financials = BeautifulSoup(requests.get(url_financials).text,"lxml")

        # Define financials columns
        a_financials_header = list()
        for financials_header in text_soup_financials.findAll('th',  {'class': 'overflow__heading'}):
            a_financials_header.append(financials_header.text.strip('\n').split('\n')[0])

        s_header_end_trend = ("5-year trend", "5- qtr trend")[ns_parser.b_quarter]
        df_financials = pd.DataFrame(columns=a_financials_header[0:a_financials_header.index(s_header_end_trend)])

        # Add financials values
        soup_financials = text_soup_financials.findAll('tr', {'class': 'table__row '})
        soup_financials += text_soup_financials.findAll('tr', {'class': 'table__row is-highlighted'})
        for financials_info in soup_financials:
            a_financials_info = financials_info.text.split('\n')
            l_financials = [a_financials_info[2]] 
            l_financials.extend(a_financials_info[5:-2])
            n_vals_to_add = len(df_financials.columns)-len(l_financials)
            if n_vals_to_add > 0:
                l_financials.append(n_vals_to_add * ' ')
            # Append data values to financials
            df_financials.loc[len(df_financials.index)] = l_financials

        # Set item name as index
        df_financials = df_financials.set_index('Item')

        print(df_financials.iloc[:16].to_string())
        print("")

    except:
        print("")
        return


# ---------------------------------------------------- INVESTING ----------------------------------------------------
def investing(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='investing', 
                                     description="""Gives cash flow investing activities of the company. The following fields 
                                     are expected: Capital Expenditures, Capital Expenditures Growth, Capital Expenditures/Sales, 
                                     Capital Expenditures (Fixed Assets), Capital Expenditures (Other Assets), Net Assets from Acquisitions, 
                                     Sale of Fixed Assets & Businesses, Purchase/Sale of Investments, Purchase of Investments, 
                                     Sale/Maturity of Investments, Other Uses, Other Sources, Net Investing Cash Flow Growth. 
                                     [Source: Market Watch BS]""")
    
    parser.add_argument('-q', "--quarter", action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        if ns_parser.b_quarter:
            url_financials = f"https://www.marketwatch.com/investing/stock/{s_ticker}/financials/cash-flow/quarter"
        else:
            url_financials = f"https://www.marketwatch.com/investing/stock/{s_ticker}/financials/cash-flow"
            
        text_soup_financials = BeautifulSoup(requests.get(url_financials).text,"lxml")

        # Define financials columns
        a_financials_header = list()
        for financials_header in text_soup_financials.findAll('th',  {'class': 'overflow__heading'}):
            a_financials_header.append(financials_header.text.strip('\n').split('\n')[0])

        s_header_end_trend = ("5-year trend", "5- qtr trend")[ns_parser.b_quarter]
        df_financials = pd.DataFrame(columns=a_financials_header[0:a_financials_header.index(s_header_end_trend)])

        # Add financials values
        soup_financials = text_soup_financials.findAll('tr', {'class': 'table__row '})
        soup_financials += text_soup_financials.findAll('tr', {'class': 'table__row is-highlighted'})
        for financials_info in soup_financials:
            a_financials_info = financials_info.text.split('\n')
            l_financials = [a_financials_info[2]] 
            l_financials.extend(a_financials_info[5:-2])
            n_vals_to_add = len(df_financials.columns)-len(l_financials)
            if n_vals_to_add > 0:
                l_financials.append(n_vals_to_add * ' ')
            # Append data values to financials
            df_financials.loc[len(df_financials.index)] = l_financials

        # Set item name as index
        df_financials = df_financials.set_index('Item')

        print(df_financials.iloc[17:30].to_string())
        print("")

    except:
        print("")
        return


# ---------------------------------------------------- FINANCING ----------------------------------------------------
def financing(l_args, s_ticker):
    parser = argparse.ArgumentParser(prog='financing', 
                                     description="""Gives cash flow financing activities of the company. The following fields 
                                     are expected: Cash Dividends Paid - Total, Common Dividends, Preferred Dividends, 
                                     Change in Capital Stock, Repurchase of Common & Preferred Stk., Sale of Common & Preferred Stock, 
                                     Proceeds from Stock Options, Other Proceeds from Sale of Stock, Issuance/Reduction of Debt, Net, 
                                     Change in Current Debt, Change in Long-Term Debt, Issuance of Long-Term Debt, Reduction in Long-Term Debt, 
                                     Other Funds, Other Uses, Other Sources, Net Financing Cash Flow Growth, Net Financing Cash Flow/Sales, 
                                     Exchange Rate Effect, Miscellaneous Funds, Net Change in Cash, Free Cash Flow, Free Cash Flow Growth, 
                                     Free Cash Flow Yield, Net Operating Cash Flow, Net Investing Cash Flow, Net Financing Cash Flow 
                                     [Source: Market Watch BS]""")
    
    parser.add_argument('-q', "--quarter", action="store_true", default=False, dest="b_quarter", help='Quarter fundamental data')

    try:
        (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)

        if l_unknown_args:
            print(f"The following args couldn't be interpreted: {l_unknown_args}\n")
            return

        if ns_parser.b_quarter:
            url_financials = f"https://www.marketwatch.com/investing/stock/{s_ticker}/financials/cash-flow/quarter"
        else:
            url_financials = f"https://www.marketwatch.com/investing/stock/{s_ticker}/financials/cash-flow"
            
        text_soup_financials = BeautifulSoup(requests.get(url_financials).text,"lxml")

        # Define financials columns
        a_financials_header = list()
        for financials_header in text_soup_financials.findAll('th',  {'class': 'overflow__heading'}):
            a_financials_header.append(financials_header.text.strip('\n').split('\n')[0])

        s_header_end_trend = ("5-year trend", "5- qtr trend")[ns_parser.b_quarter]
        df_financials = pd.DataFrame(columns=a_financials_header[0:a_financials_header.index(s_header_end_trend)])

        # Add financials values
        soup_financials = text_soup_financials.findAll('tr', {'class': 'table__row '})
        soup_financials += text_soup_financials.findAll('tr', {'class': 'table__row is-highlighted'})
        for financials_info in soup_financials:
            a_financials_info = financials_info.text.split('\n')
            l_financials = [a_financials_info[2]] 
            l_financials.extend(a_financials_info[5:-2])
            n_vals_to_add = len(df_financials.columns)-len(l_financials)
            if n_vals_to_add > 0:
                l_financials.append(n_vals_to_add * ' ')
            # Append data values to financials
            df_financials.loc[len(df_financials.index)] = l_financials

        # Set item name as index
        df_financials = df_financials.set_index('Item')

        print(df_financials.iloc[31:].to_string())
        print("")
        
    except:
        print("")
        return
