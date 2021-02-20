# FUNDAMENTAL ANALYSIS

This menu aims to extract all fundamentals of a pre-loaded company, and the usage of the following commands along with an example will be exploited below.

  * [screener](#screener)    
    - screen info about the company [Finviz]
  * [mgmt](#mgmt)
    - management team of the company [Business Insider]

Market Watch API
  * [income](#income)
    - income statement of the company
  * [assets](#assets)
    - assets of the company
  * [liabilities](#liabilities)   
    - liabilities and shareholders equity of the company
  * [operating](#operating)
    - cash flow operating activities of the company
  * [investing](#investing)
    - cash flow investing activities of the company
  * [financing](#financing)
    - cash flow financing activities of the company

Yahoo Finance API
  * [info](#info)
    - information scope of the company
  * [shrs](#shrs)
    - hareholders of the company
  * [sust](#sust)
    - sustainability values of the company
  * [cal](#cal)
    - calendar earnings and estimates of the company

Alpha Vantage API
  * [overview](#overview)
    - overview of the company
  * [incom](#incom)
    - income statements of the company
  * [balance](#balance)
    - balance sheet of the company
  * [cash](#cash)
    - cash flow of the company
  * [earnings](#earnings)
    - earnings dates and reported EPS

Financial Modeling Prep API
  * [profile](#profile)       
    - profile of the company
  * [quote](#quote)
    - quote of the company
  * [enterprise](#enterprise)
    - enterprise value of the company over time
  * [dcf](#dcf)
    - discounted cash flow of the company over time
  * [inc](#inc)
    - income statements of the company
  * [bal](#bal)
    - balance sheet of the company
  * [cashf](#cashf)
    - cash flow of the company
  * [metrics](#metrics)
    - key metrics of the company
  * [ratios](#ratios)
    - financial ratios of the company
  * [growth](#growth)
    - financial statement growth of the company
    
    
## screener <a name="screener"></a>
```
usage: screener
```
Print several metrics about the company. The following fields are expected: Company, Sector, Industry, Country, Index, P/E, EPS (ttm), Insider Own, Shs Outstand, Perf Week, Market Cap, Forward P/E, EPS next Y, Insider Trans, Shs Float, Perf Month, Income, EPS next Q, Inst Own, Short Float, Perf Quarter, Sales, P/S, EPS this Y, Inst Trans, Short Ratio, Perf Half Y, Book/sh, P/B, ROA, Target Price, Perf Year, Cash/sh, P/C, ROE, 52W Range, Perf YTD, P/FCF, EPS past 5Y, ROI, 52W High, Beta, Quick Ratio, Sales past 5Y, Gross Margin, 52W Low, ATR, Employees, Current Ratio, Sales Q/Q, Oper. Margin, RSI (14), Volatility, Optionable, Debt/Eq, EPS Q/Q, Profit Margin, Rel Volume, Prev Close, Shortable, LT Debt/Eq, Earnings, Payout, Avg Volume, Price, Recom, SMA20, SMA50, SMA200, Volume, Change.  [Source: Finviz API]

## mgmt <a name="mgmt"></a>
```
usage: mgmt
```
Print management team. Namely: Name, Title, Information from google and (potentially) Insider Activity page. [Source: Business Insider API]


# Market Watch

## income <a name="income"></a>
```
usage: income [-q]
```
Prints either yearly or quarterly income statement the company. The following fields are expected: Sales Growth, Cost of Goods Sold (COGS) incl. D&A, COGS Growth, COGS excluding D&A, Depreciation & Amortization Expense, Depreciation, Amortization of Intangibles, Gross Income, Gross Income Growth, Gross Profit Margin, SG&A Expense, SGA Growth, Research & Development, Other SG&A, Other Operating Expense, Unusual Expense, EBIT after Unusual Expense, Non Operating Income/Expense, Non-Operating Interest Income, Equity in Affiliates (Pretax), Interest Expense, Interest Expense Growth, Gross Interest Expense, Interest Capitalized, Pretax Income, Pretax Income Growth, Pretax Margin, Income Tax, Income Tax - Current Domestic, Income Tax - Current Foreign, Income Tax - Deferred Domestic, Income Tax - Deferred Foreign, Income Tax Credits, Equity in Affiliates, Other After Tax Income (Expense), Consolidated Net Income, Minority Interest Expense, Net Income Growth, Net Margin Growth, Extraordinaries & Discontinued Operations, Extra Items & Gain/Loss Sale Of Assets, Cumulative Effect - Accounting Chg, Discontinued Operations, Net Income After Extraordinaries, Preferred Dividends, Net Income Available to Common, EPS (Basic), EPS (Basic) Growth, Basic Shares Outstanding, EPS (Diluted), EPS (Diluted) Growth, Diluted Shares Outstanding, EBITDA, EBITDA Growth, EBITDA Margin, Sales/Revenue, and Net Income. [Source: Market Watch]
  * - q : Quarter fundamental data flag. Default False.

## assets <a name="assets"></a>
```
usage: assets [-q]
```
Prints either yearly or quarterly assets from balance sheet of the company. The following fields are expected: Cash & Short Term Investments, Cash & Short Term Investments Growth, Cash Only, Short-Term Investments, Cash & ST Investments / Total Assets, Total Accounts Receivable, Total Accounts Receivable Growth, Accounts Receivables, Net, Accounts Receivables, Gross,  Bad Debt/Doubtful Accounts, Other Receivable, Accounts Receivable Turnover, Inventories, Finished Goods, Work in Progress, Raw Materials, Progress Payments & Other, Other Current Assets, Miscellaneous Current Assets, Net Property, Plant & Equipment, Property, Plant & Equipment - Gross, Buildings, Land & Improvements, Computer Software and Equipment, Other Property, Plant & Equipment, Accumulated Depreciation, Total Investments and Advances, Other Long-Term Investments, Long-Term Note Receivables, Intangible Assets, Net Goodwill, Net Other Intangibles, Other Assets. [Source: Market Watch]
  * - q : Quarter fundamental data flag. Default False.


## liabilities <a name="liabilities"></a>
```
usage: liabilities [-q]
```
Prints either yearly or quarterly liablities and shareholders' equity from balance sheet of the company. The following fields are expected: ST Debt & Current Portion LT Debt, Short Term Debt, Current Portion of Long Term Debt, Accounts Payable, Accounts Payable Growth, Income Tax Payable, Other Current Liabilities, Dividends Payable, Accrued Payroll, Miscellaneous Current Liabilities, Long-Term Debt, Long-Term Debt excl. Capitalized Leases, Non-Convertible Debt, Convertible Debt, Capitalized Lease Obligations, Provision for Risks & Charges, Deferred Taxes, Deferred Taxes - Credits, Deferred Taxes - Debit, Other Liabilities, Other Liabilities (excl. Deferred Income), Deferred Income, Non-Equity Reserves, Total Liabilities / Total Assets, Preferred Stock (Carrying Value), Redeemable Preferred Stock, Non-Redeemable Preferred Stock, Common Equity (Total), Common Equity/Total Assets, Common Stock Par/Carry Value, Retained Earnings, ESOP Debt Guarantee, Cumulative Translation Adjustment/Unrealized For. Exch. Gain, Unrealized Gain/Loss Marketable Securities, Revaluation Reserves, Treasury Stock, Total Shareholders' Equity, Total Shareholders' Equity / Total Assets, Accumulated Minority Interest, Total Equity, Total Current Assets, Total Assets, Total Current Liabilities, Total Liabilities, and Liabilities & Shareholders' Equity. [Source: Market Watch]
  * - q : Quarter fundamental data flag. Default False.

## operating <a name="operating"></a>
```
usage: operating [-q]
```
Prints either yearly or quarterly cash flow operating activities of the company. The following fields are expected: Net Income before Extraordinaries, Net Income Growth, Depreciation, Depletion & Amortization, Depreciation and Depletion, Amortization of Intangible Assets, Deferred Taxes & Investment Tax Credit, Deferred Taxes, Investment Tax Credit, Other Funds, Funds from Operations, Extraordinaries, Changes in Working Capital, Receivables, Accounts Payable, Other Assets/Liabilities, and Net Operating Cash Flow Growth. [Source: Market Watch]
  * - q : Quarter fundamental data flag. Default False.

## investing <a name="investing"></a>

Prints either yearly or quarterly cash flow investing activities of the company. The following fields are expected: Capital Expenditures, Capital Expenditures Growth, Capital Expenditures/Sales, Capital Expenditures (Fixed Assets), Capital Expenditures (Other Assets), Net Assets from Acquisitions, Sale of Fixed Assets & Businesses, Purchase/Sale of Investments, Purchase of Investments, Sale/Maturity of Investments, Other Uses, Other Sources, Net Investing Cash Flow Growth. [Source: Market Watch]
  * - q : Quarter fundamental data flag. Default False.

## financing <a name="financing"></a>

Prints either yearly or quarterly cash flow financing activities of the company. The following fields are expected: Cash Dividends Paid - Total, Common Dividends, Preferred Dividends, Change in Capital Stock, Repurchase of Common & Preferred Stk., Sale of Common & Preferred Stock, Proceeds from Stock Options, Other Proceeds from Sale of Stock, Issuance/Reduction of Debt, Net, Change in Current Debt, Change in Long-Term Debt, Issuance of Long-Term Debt, Reduction in Long-Term Debt, Other Funds, Other Uses, Other Sources, Net Financing Cash Flow Growth, Net Financing Cash Flow/Sales, Exchange Rate Effect, Miscellaneous Funds, Net Change in Cash, Free Cash Flow, Free Cash Flow Growth, Free Cash Flow Yield, Net Operating Cash Flow, Net Investing Cash Flow, Net Financing Cash Flow [Source: Market Watch]
  * - q : Quarter fundamental data flag. Default False.


# Yahoo Finance

## info <a name="info"></a>

## shrs <a name="shrs"></a>

## sust <a name="sust"></a>

## cal <a name="cal"></a>

# Alpha Vantage

## overview <a name="overview"></a>

## incom <a name="incom"></a>

## balance <a name="balance"></a>

## cash <a name="cash"></a>

## earnings <a name="earnings"></a>

# Financial Modeling Prep

## profile <a name="profile"></a>

## quote <a name="quote"></a>

## enterprise <a name="enterprise"></a>

## dcf <a name="dcf"></a>

## inc <a name="inc"></a>

## bal <a name="bal"></a>

## cashf <a name="cashf"></a>

## metrics <a name="metrics"></a>

## ratios <a name="ratios"></a>

## growth <a name="growth"></a>


