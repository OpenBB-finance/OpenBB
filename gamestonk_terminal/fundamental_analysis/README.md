# FUNDAMENTAL ANALYSIS

This menu aims to extract all fundamentals of a pre-loaded company, and the usage of the following commands along with an example will be exploited below.

* [screener](#screener)
  * screen info about the company [Finviz]
* [mgmt](#mgmt)
  * management team of the company [Business Insider]
* [score](#score)
  * investing score from Warren Buffett, Joseph Piotroski and Benjamin Graham [FMP]
         
[MARKET WATCH](#MARKET_WATCH)

* [income](#income)
  * income statement of the company
* [balance](#balance)
  * balance sheet of the company
* [cash](#cash)
  * cash flow statement of the company

[YAHOO FINANCE](#YAHOO_FINANCE)
  * income statement of the company

* [info](#info)
  * information scope of the company
* [shrs](#shrs)
  * hareholders of the company
* [sust](#sust)
  * sustainability values of the company
* [cal](#cal)
  * calendar earnings and estimates of the company


[ALPHA VANTAGE menu](/gamestonk_terminal/fundamental_analysis/alpha_vantage/)


[FINANCIAL MODELING PREP menu](/gamestonk_terminal/fundamental_analysis/financial_modeling_prep/)


**Note:** _Some of these functionalities are repeated in the sense of the overall information contained within. However, since none of the provided data is paid, there isn't a single all-time up-to-date API source. You get what you pay for. It comes to the user to select the functionalities under the API that they trust the most, or compare their outputs, and then make an informed decision._

## screener <a name="screener"></a>

```text
usage: screener
```

Print several metrics about the company. The following fields are expected: Company, Sector, Industry, Country, Index, P/E, EPS (ttm), Insider Own, Shs Outstand, Perf Week, Market Cap, Forward P/E, EPS next Y, Insider Trans, Shs Float, Perf Month, Income, EPS next Q, Inst Own, Short Float, Perf Quarter, Sales, P/S, EPS this Y, Inst Trans, Short Ratio, Perf Half Y, Book/sh, P/B, ROA, Target Price, Perf Year, Cash/sh, P/C, ROE, 52W Range, Perf YTD, P/FCF, EPS past 5Y, ROI, 52W High, Beta, Quick Ratio, Sales past 5Y, Gross Margin, 52W Low, ATR, Employees, Current Ratio, Sales Q/Q, Oper. Margin, RSI (14), Volatility, Optionable, Debt/Eq, EPS Q/Q, Profit Margin, Rel Volume, Prev Close, Shortable, LT Debt/Eq, Earnings, Payout, Avg Volume, Price, Recom, SMA20, SMA50, SMA200, Volume, Change.  [Source: Finviz]

## mgmt <a name="mgmt"></a>

```text
usage: mgmt
```

Print management team. Namely: Name, Title, Information from google and (potentially) Insider Activity page. [Source: Business Insider]

## MARKET WATCH <a name="MARKET_WATCH"></a>

### income <a name="income"></a>

```text
usage: income [-q]
```

Prints either yearly or quarterly income statement the company. The following fields are expected: Sales Growth, Cost of Goods Sold (COGS) incl. D&A, COGS Growth, COGS excluding D&A, Depreciation & Amortization Expense, Depreciation, Amortization of Intangibles, Gross Income, Gross Income Growth, Gross Profit Margin, SG&A Expense, SGA Growth, Research & Development, Other SG&A, Other Operating Expense, Unusual Expense, EBIT after Unusual Expense, Non Operating Income/Expense, Non-Operating Interest Income, Equity in Affiliates (Pretax), Interest Expense, Interest Expense Growth, Gross Interest Expense, Interest Capitalized, Pretax Income, Pretax Income Growth, Pretax Margin, Income Tax, Income Tax - Current Domestic, Income Tax - Current Foreign, Income Tax - Deferred Domestic, Income Tax - Deferred Foreign, Income Tax Credits, Equity in Affiliates, Other After Tax Income (Expense), Consolidated Net Income, Minority Interest Expense, Net Income Growth, Net Margin Growth, Extraordinaries & Discontinued Operations, Extra Items & Gain/Loss Sale Of Assets, Cumulative Effect - Accounting Chg, Discontinued Operations, Net Income After Extraordinaries, Preferred Dividends, Net Income Available to Common, EPS (Basic), EPS (Basic) Growth, Basic Shares Outstanding, EPS (Diluted), EPS (Diluted) Growth, Diluted Shares Outstanding, EBITDA, EBITDA Growth, EBITDA Margin, Sales/Revenue, and Net Income. [Source: Market Watch]

* q : Quarter fundamental data flag. Default False.

### balance <a name="balance"></a>

```text
usage: assets [-q]
```

Prints either yearly or quarterly assets from balance sheet of the company. The following fields are expected: Cash & Short Term Investments, Cash & Short Term Investments Growth, Cash Only, Short-Term Investments, Cash & ST Investments / Total Assets, Total Accounts Receivable, Total Accounts Receivable Growth, Accounts Receivables, Net, Accounts Receivables, Gross, Bad Debt/Doubtful Accounts, Other Receivable, Accounts Receivable Turnover, Inventories, Finished Goods, Work in Progress, Raw Materials, Progress Payments & Other, Other Current Assets, Miscellaneous Current Assets, Net Property, Plant & Equipment, Property, Plant & Equipment - Gross, Buildings, Land & Improvements, Computer Software and Equipment, Other Property, Plant & Equipment, Accumulated Depreciation, Total Investments and Advances, Other Long-Term Investments, Long-Term Note Receivables, Intangible Assets, Net Goodwill, Net Other Intangibles, Other Assets.

Prints either yearly or quarterly liabilities and shareholders' equity from balance sheet of the company. The following fields are expected: ST Debt & Current Portion LT Debt, Short Term Debt, Current Portion of Long Term Debt, Accounts Payable, Accounts Payable Growth, Income Tax Payable, Other Current Liabilities, Dividends Payable, Accrued Payroll, Miscellaneous Current Liabilities, Long-Term Debt, Long-Term Debt excl. Capitalized Leases, Non-Convertible Debt, Convertible Debt, Capitalized Lease Obligations, Provision for Risks & Charges, Deferred Taxes, Deferred Taxes - Credits, Deferred Taxes - Debit, Other Liabilities, Other Liabilities (excl. Deferred Income), Deferred Income, Non-Equity Reserves, Total Liabilities / Total Assets, Preferred Stock (Carrying Value), Redeemable Preferred Stock, Non-Redeemable Preferred Stock, Common Equity (Total), Common Equity/Total Assets, Common Stock Par/Carry Value, Retained Earnings, ESOP Debt Guarantee, Cumulative Translation Adjustment/Unrealized For. Exch. Gain, Unrealized Gain/Loss Marketable Securities, Revaluation Reserves, Treasury Stock, Total Shareholders' Equity, Total Shareholders' Equity / Total Assets, Accumulated Minority Interest, Total Equity, Total Current Assets, Total Assets, Total Current Liabilities, Total Liabilities, and Liabilities & Shareholders' Equity. [Source: Market Watch]

* q : Quarter fundamental data flag. Default False.

### cash <a name="cash"></a>

```text
usage: cash [-q]
```

Prints either yearly or quarterly cash flow operating activities of the company. The following fields are expected: Net Income before Extraordinaries, Net Income Growth, Depreciation, Depletion & Amortization, Depreciation and Depletion, Amortization of Intangible Assets, Deferred Taxes & Investment Tax Credit, Deferred Taxes, Investment Tax Credit, Other Funds, Funds from Operations, Extraordinaries, Changes in Working Capital, Receivables, Accounts Payable, Other Assets/Liabilities, and Net Operating Cash Flow Growth.
            
Prints either yearly or quarterly cash flow investing activities of the company. The following fields are expected: Capital Expenditures, Capital Expenditures Growth, Capital Expenditures/Sales, Capital Expenditures (Fixed Assets), Capital Expenditures (Other Assets), Net Assets from Acquisitions, Sale of Fixed Assets & Businesses, Purchase/Sale of Investments, Purchase of Investments, Sale/Maturity of Investments, Other Uses, Other Sources, Net Investing Cash Flow Growth.
            
Prints either yearly or quarterly cash flow financing activities of the company. The following fields are expected: Cash Dividends Paid - Total, Common Dividends, Preferred Dividends, Change in Capital Stock, Repurchase of Common & Preferred Stk., Sale of Common & Preferred Stock, Proceeds from Stock Options, Other Proceeds from Sale of Stock, Issuance/Reduction of Debt, Net, Change in Current Debt, Change in Long-Term Debt, Issuance of Long-Term Debt, Reduction in Long-Term Debt, Other Funds, Other Uses, Other Sources, Net Financing Cash Flow Growth, Net Financing Cash Flow/Sales, Exchange Rate Effect, Miscellaneous Funds, Net Change in Cash, Free Cash Flow, Free Cash Flow Growth, Free Cash Flow Yield, Net Operating Cash Flow, Net Investing Cash Flow, Net Financing Cash Flow. [Source: Market Watch]

* q : Quarter fundamental data flag. Default False.


## YAHOO FINANCE <a name="YAHOO_FINANCE"></a>

### info <a name="info"></a>

```text
usage: info
```

Print information about the company. The following fields are expected: Zip, Sector, Full time employees, Long business summary, City, Phone, State, Country,  Website, Max age, Address, Industry, Previous close, Regular market open, Two hundred day average, Payout ratio, Regular market day high, Average daily volume 10 day, Regular market previous close, Fifty day average, Open, Average volume 10 days, Beta, Regular market day low, Price hint, Currency, Trailing PE, Regular market volume, Market cap, Average volume, Price to sales trailing 12 months, Day low, Ask, Ask size, Volume, Fifty two week high, Forward PE, Fifty two week low, Bid, Tradeable, Bid size, Day high, Exchange, Short name, Long name, Exchange timezone name, Exchange timezone short name, Is esg populated, Gmt off set milliseconds, Quote type, Symbol, Message board id, Market, Enterprise to revenue, Profit margins, Enterprise to ebitda, 52 week change, Forward EPS, Shares outstanding, Book value, Shares short, Shares percent shares out, Last fiscal year end, Held percent institutions, Net income to common, Trailing EPS, Sand p52 week change, Price to book, Held percent insiders, Next fiscal year end, Most recent quarter, Short ratio, Shares short previous month date, Float shares,  Enterprise value, Last split date, Last split factor, Earnings quarterly growth, Date short interest, PEG ratio, Short percent of float, Shares short prior month, Regular market price, Logo_url. [Source: Yahoo Finance]

### shrs <a name="shrs"></a>

```text
usage: shrs
```

Print Major, institutional and mutualfunds shareholders. [Source: Yahoo Finance]

### sust <a name="sust"></a>

```text
usage: sust
```

Print sustainability values of the company. The following fields are expected: Palmoil, Controversialweapons, Gambling, Socialscore, Nuclear, Furleather, Alcoholic, Gmo, Catholic, Socialpercentile, Peercount, Governancescore, Environmentpercentile, Animaltesting, Tobacco, Totalesg, Highestcontroversy, Esgperformance, Coal, Pesticides, Adult, Percentile, Peergroup, Smallarms, Environmentscore, Governancepercentile, Militarycontract. [Source: Yahoo Finance]

### cal <a name="cal"></a>

```text
usage: cal
```

Calendar earnings of the company. Including revenue and earnings estimates. [Source: Yahoo Finance]

