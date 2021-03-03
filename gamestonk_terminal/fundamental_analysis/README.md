# FUNDAMENTAL ANALYSIS

This menu aims to extract all fundamentals of a pre-loaded company, and the usage of the following commands along with an example will be exploited below.

* [screener](#screener)
  * screen info about the company [Finviz]
* [mgmt](#mgmt)
  * management team of the company [Business Insider]

[MARKET WATCH](#MARKET_WATCH)

* [income](#income)
  * income statement of the company
* [assets](#assets)
  * assets of the company
* [liabilities](#liabilities)
  * liabilities and shareholders equity of the company
* [operating](#operating)
  * cash flow operating activities of the company
* [investing](#investing)
  * cash flow investing activities of the company
* [financing](#financing)
  * cash flow financing activities of the company

[YAHOO FINANCE](#YAHOO_FINANCE)

* [info](#info)
  * information scope of the company
* [shrs](#shrs)
  * hareholders of the company
* [sust](#sust)
  * sustainability values of the company
* [cal](#cal)
  * calendar earnings and estimates of the company

[ALPHA VANTAGE](#ALPHA_VANTAGE)

* [overview](#overview)
  * overview of the company
* [incom](#incom)
  * income statements of the company
* [balance](#balance)
  * balance sheet of the company
* [cash](#cash)
  * cash flow of the company
* [earnings](#earnings)
  * earnings dates and reported EPS

[FINANCIAL MODELING PREP](#FINANCIAL_MODELING_PREP)

* [profile](#profile)
  * profile of the company
* [quote](#quote)
  * quote of the company
* [enterprise](#enterprise)
  * enterprise value of the company over time
* [dcf](#dcf)
  * discounted cash flow of the company over time
* [inc](#inc)
  * income statements of the company
* [bal](#bal)
  * balance sheet of the company
* [cashf](#cashf)
  * cash flow of the company
* [metrics](#metrics)
  * key metrics of the company
* [ratios](#ratios)
  * financial ratios of the company
* [growth](#growth)
  * financial statement growth of the company

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

### assets <a name="assets"></a>

```text
usage: assets [-q]
```

Prints either yearly or quarterly assets from balance sheet of the company. The following fields are expected: Cash & Short Term Investments, Cash & Short Term Investments Growth, Cash Only, Short-Term Investments, Cash & ST Investments / Total Assets, Total Accounts Receivable, Total Accounts Receivable Growth, Accounts Receivables, Net, Accounts Receivables, Gross,  Bad Debt/Doubtful Accounts, Other Receivable, Accounts Receivable Turnover, Inventories, Finished Goods, Work in Progress, Raw Materials, Progress Payments & Other, Other Current Assets, Miscellaneous Current Assets, Net Property, Plant & Equipment, Property, Plant & Equipment - Gross, Buildings, Land & Improvements, Computer Software and Equipment, Other Property, Plant & Equipment, Accumulated Depreciation, Total Investments and Advances, Other Long-Term Investments, Long-Term Note Receivables, Intangible Assets, Net Goodwill, Net Other Intangibles, Other Assets. [Source: Market Watch]

* q : Quarter fundamental data flag. Default False.

### liabilities <a name="liabilities"></a>

```text
usage: liabilities [-q]
```

Prints either yearly or quarterly liablities and shareholders' equity from balance sheet of the company. The following fields are expected: ST Debt & Current Portion LT Debt, Short Term Debt, Current Portion of Long Term Debt, Accounts Payable, Accounts Payable Growth, Income Tax Payable, Other Current Liabilities, Dividends Payable, Accrued Payroll, Miscellaneous Current Liabilities, Long-Term Debt, Long-Term Debt excl. Capitalized Leases, Non-Convertible Debt, Convertible Debt, Capitalized Lease Obligations, Provision for Risks & Charges, Deferred Taxes, Deferred Taxes - Credits, Deferred Taxes - Debit, Other Liabilities, Other Liabilities (excl. Deferred Income), Deferred Income, Non-Equity Reserves, Total Liabilities / Total Assets, Preferred Stock (Carrying Value), Redeemable Preferred Stock, Non-Redeemable Preferred Stock, Common Equity (Total), Common Equity/Total Assets, Common Stock Par/Carry Value, Retained Earnings, ESOP Debt Guarantee, Cumulative Translation Adjustment/Unrealized For. Exch. Gain, Unrealized Gain/Loss Marketable Securities, Revaluation Reserves, Treasury Stock, Total Shareholders' Equity, Total Shareholders' Equity / Total Assets, Accumulated Minority Interest, Total Equity, Total Current Assets, Total Assets, Total Current Liabilities, Total Liabilities, and Liabilities & Shareholders' Equity. [Source: Market Watch]

* q : Quarter fundamental data flag. Default False.

### operating <a name="operating"></a>

```text
usage: operating [-q]
```

Prints either yearly or quarterly cash flow operating activities of the company. The following fields are expected: Net Income before Extraordinaries, Net Income Growth, Depreciation, Depletion & Amortization, Depreciation and Depletion, Amortization of Intangible Assets, Deferred Taxes & Investment Tax Credit, Deferred Taxes, Investment Tax Credit, Other Funds, Funds from Operations, Extraordinaries, Changes in Working Capital, Receivables, Accounts Payable, Other Assets/Liabilities, and Net Operating Cash Flow Growth. [Source: Market Watch]

* q : Quarter fundamental data flag. Default False.

### investing <a name="investing"></a>

```text
usage: investing [-q]
```

Prints either yearly or quarterly cash flow investing activities of the company. The following fields are expected: Capital Expenditures, Capital Expenditures Growth, Capital Expenditures/Sales, Capital Expenditures (Fixed Assets), Capital Expenditures (Other Assets), Net Assets from Acquisitions, Sale of Fixed Assets & Businesses, Purchase/Sale of Investments, Purchase of Investments, Sale/Maturity of Investments, Other Uses, Other Sources, Net Investing Cash Flow Growth. [Source: Market Watch]

* q : Quarter fundamental data flag. Default False.

### financing <a name="financing"></a>

```text
usage: financing [-q]
```

Prints either yearly or quarterly cash flow financing activities of the company. The following fields are expected: Cash Dividends Paid - Total, Common Dividends, Preferred Dividends, Change in Capital Stock, Repurchase of Common & Preferred Stk., Sale of Common & Preferred Stock, Proceeds from Stock Options, Other Proceeds from Sale of Stock, Issuance/Reduction of Debt, Net, Change in Current Debt, Change in Long-Term Debt, Issuance of Long-Term Debt, Reduction in Long-Term Debt, Other Funds, Other Uses, Other Sources, Net Financing Cash Flow Growth, Net Financing Cash Flow/Sales, Exchange Rate Effect, Miscellaneous Funds, Net Change in Cash, Free Cash Flow, Free Cash Flow Growth, Free Cash Flow Yield, Net Operating Cash Flow, Net Investing Cash Flow, Net Financing Cash Flow [Source: Market Watch]

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

## ALPHA VANTAGE <a name="ALPHA_VANTAGE"></a>

### overview <a name="overview"></a>

```text
usage: overview
```

Prints an overview about the company. The following fields are expected: Symbol, Asset type, Name, Description, Exchange, Currency, Country, Sector, Industry, Address, Full time employees, Fiscal year end, Latest quarter, Market capitalization, EBITDA, PE ratio, PEG ratio, Book value, Dividend per share, Dividend yield, EPS, Revenue per share TTM, Profit margin, Operating margin TTM, Return on assets TTM, Return on equity TTM, Revenue TTM, Gross profit TTM, Diluted EPS TTM, Quarterly earnings growth YOY, Quarterly revenue growth YOY, Analyst target price, Trailing PE, Forward PE, Price to sales ratio TTM, Price to book ratio, EV to revenue, EV to EBITDA, Beta, 52 week high, 52 week low, 50 day moving average, 200 day moving average, Shares outstanding, Shares float, Shares short, Shares short prior month, Short ratio, Short percent outstanding, Short percent float, Percent insiders, Percent institutions, Forward annual dividend rate, Forward annual dividend yield, Payout ratio, Dividend date, Ex dividend date, Last split factor, and Last split date. [Source: Alpha Vantage]

### incom <a name="incom"></a>

```text
usage: income [-n N_NUM] [-q]
```

Prints a complete income statement over time. This can be either quarterly or annually. The following fields are expected: Accepted date, Cost and expenses, Cost of revenue, Depreciation and amortization, Ebitda, Ebitdaratio, Eps, Epsdiluted, Filling date, Final link, General and administrative expenses, Gross profit, Gross profit ratio, Income before tax, Income before tax ratio, Income tax expense, Interest expense, Link, Net income, Net income ratio, Operating expenses, Operating income, Operating income ratio, Other expenses, Period, Research and development expenses, Revenue, Selling and marketing expenses, Total other income expenses net, Weighted average shs out, Weighted average shs out dil [Source: Alpha Vantage]

* n : Number of latest years/quarters. Default 1.
* q : Quarter fundamental data flag. Default False.

### balance <a name="balance"></a>

```text
usage: balance [-n N_NUM] [-q]
```

Prints a complete balance sheet statement over time. This can be either quarterly or annually. The following fields are expected: Accepted date, Account payables, Accumulated other comprehensive income loss, Cash and cash equivalents, Cash and short term investments, Common stock, Deferred revenue, Deferred revenue non current, Deferred tax liabilities non current, Filling date, Final link, Goodwill, Goodwill and intangible assets, Intangible assets, Inventory, Link, Long term debt, Long term investments, Net debt, Net receivables, Other assets, Other current assets, Other current liabilities, Other liabilities, Other non current assets, Other non current liabilities, Othertotal stockholders equity, Period, Property plant equipment net, Retained earnings, Short term debt, Short term investments, Tax assets, Tax payables, Total assets, Total current assets, Total current liabilities, Total debt, Total investments, Total liabilities, Total liabilities and stockholders equity, Total non current assets, Total non current liabilities, and Total stockholders equity. [Source: Alpha Vantage]

* n : Number of latest years/quarters. Default 1.
* q : Quarter fundamental data flag. Default False.

### cash <a name="cash"></a>

```text
usage: cash [-n N_NUM] [-q]
```

Prints a complete cash flow statement over time. This can be either quarterly or annually. The following fields are expected: Accepted date, Accounts payables, Accounts receivables, Acquisitions net, Capital expenditure, Cash at beginning of period, Cash at end of period, Change in working capital, Common stock issued, Common stock repurchased, Debt repayment, Deferred income tax, Depreciation and amortization, Dividends paid, Effect of forex changes on cash, Filling date, Final link, Free cash flow, Inventory, Investments in property plant and equipment, Link, Net cash provided by operating activities, Net cash used for investing activites, Net cash used provided by financing activities, Net change in cash, Net income, Operating cash flow, Other financing activites, Other investing activites, Other non cash items, Other working capital, Period, Purchases of investments, Sales maturities of investments, Stock based compensation. [Source: Alpha Vantage]

* n : Number of latest years/quarters. Default 1.
* q : Quarter fundamental data flag. Default False.

### earnings <a name="earnings"></a>

```text
usage: earnings [-n N_NUM] [-q]
```

Print earnings dates and reported EPS of the company. The following fields are expected: Fiscal Date Ending and Reported EPS. [Source: Alpha Vantage]

* n : Number of latest years/quarters. Default 1.
* q : Quarter fundamental data flag. Default False.

## FINANCIAL MODELING PREP <a name="FINANCIAL_MODELING_PREP"></a>

### profile <a name="profile"></a>

```text
usage: profile
```

Prints information about, among other things, the industry, sector exchange and company description. The following fields are expected: Address, Beta, Ceo, Changes, Cik, City, Company name, Country, Currency, Cusip, Dcf, Dcf diff, Default image, Description, Exchange, Exchange short name, Full time employees, Image, Industry, Ipo date, Isin, Last div, Mkt cap, Phone, Price, Range, Sector, State, Symbol, Vol avg, Website, Zip. [Source: Financial Modeling Prep]

### quote <a name="quote"></a>

```text
usage: quote
```

Prints actual information about the company which is, among other things, the day high, market cap, open and close price and price-to-equity ratio. The following fields are expected: Avg volume, Change, Changes percentage, Day high, Day low, Earnings announcement, Eps, Exchange, Market cap, Name, Open, Pe, Previous close, Price, Price avg200, Price avg50, Shares outstanding, Symbol, Timestamp, Volume, Year high, and Year low. [Source: Financial Modeling Prep]

### enterprise <a name="enterprise"></a>

```text
usage: enterprise [-n N_NUM] [-q]
```

Prints stock price, number of shares, market capitalization and enterprise value over time. The following fields are expected: Add total debt, Enterprise value, Market capitalization, Minus cash and cash equivalents, Number of shares, Stock price, and Symbol. [Source: Financial Modeling Prep]

* n : Number of latest years/quarters. Default 1.
* q : Quarter fundamental data flag. Default False.

### dcf <a name="dcf"></a>

```text
usage: dcf [-n N_NUM] [-q]
```

Prints the discounted cash flow of a company over time including the DCF of today. The following fields are expected: DCF, Stock price, and Date. [Source: Financial Modeling Prep]

* n : Number of latest years/quarters. Default 1.
* q : Quarter fundamental data flag. Default False.

### inc <a name="inc"></a>

```text
usage: inc [-n N_NUM] [-q]
```

Prints a complete income statement over time. This can be either quarterly or annually. The following fields are expected: Accepted date, Cost and expenses, Cost of revenue, Depreciation and amortization, Ebitda, Ebitdaratio, Eps, Epsdiluted, Filling date, Final link, General and administrative expenses, Gross profit, Gross profit ratio, Income before tax, Income before tax ratio, Income tax expense, Interest expense, Link, Net income, Net income ratio, Operating expenses, Operating income, Operating income ratio, Other expenses, Period, Research and development expenses, Revenue, Selling and marketing expenses, Total other income expenses net, Weighted average shs out, Weighted average shs out dil [Source: Financial Modeling Prep]

* n : Number of latest years/quarters. Default 1.
* q : Quarter fundamental data flag. Default False.

### bal <a name="bal"></a>

```text
usage: bal [-n N_NUM] [-q]
```

Prints a complete balance sheet statement over time. This can be either quarterly or annually. The following fields are expected: Accepted date, Account payables, Accumulated other comprehensive income loss, Cash and cash equivalents, Cash and short term investments, Common stock, Deferred revenue, Deferred revenue non current, Deferred tax liabilities non current, Filling date, Final link, Goodwill, Goodwill and intangible assets, Intangible assets, Inventory, Link, Long term debt, Long term investments, Net debt, Net receivables, Other assets, Other current assets, Other current liabilities, Other liabilities, Other non current assets, Other non current liabilities, Othertotal stockholders equity, Period, Property plant equipment net, Retained earnings, Short term debt, Short term investments, Tax assets, Tax payables, Total assets, Total current assets, Total current liabilities, Total debt, Total investments, Total liabilities, Total liabilities and stockholders equity, Total non current assets, Total non current liabilities, and Total stockholders equity. [Source: Financial Modeling Prep]

* n : Number of latest years/quarters. Default 1.
* q : Quarter fundamental data flag. Default False.

### cashf <a name="cashf"></a>

```text
usage: cashf [-n N_NUM] [-q]
```

Prints a complete cash flow statement over time. This can be either quarterly or annually. The following fields are expected: Accepted date, Accounts payables, Accounts receivables, Acquisitions net, Capital expenditure, Cash at beginning of period, Cash at end of period, Change in working capital, Common stock issued, Common stock repurchased, Debt repayment, Deferred income tax, Depreciation and amortization, Dividends paid, Effect of forex changes on cash, Filling date, Final link, Free cash flow, Inventory, Investments in property plant and equipment, Link, Net cash provided by operating activities, Net cash used for investing activites, Net cash used provided by financing activities, Net change in cash, Net income, Operating cash flow, Other financing activites, Other investing activites, Other non cash items, Other working capital, Period, Purchases of investments, Sales maturities of investments, Stock based compensation. [Source: Financial Modeling Prep]

* n : Number of latest years/quarters. Default 1.
* q : Quarter fundamental data flag. Default False.

### metrics <a name="metrics"></a>

```text
usage: metrics [-n N_NUM] [-q]
```

Prints a list of the key metrics of a company over time. This can be either quarterly or annually. This includes, among other things, Return on Equity (ROE), Working Capital, Current Ratio and Debt to Assets. The following fields are expected: Average inventory, Average payables, Average receivables, Book value per share, Capex per share, Capex to depreciation, Capex to operating cash flow, Capex to revenue, Cash per share, Current ratio, Days of inventory on hand, Days payables outstanding, Days sales outstanding, Debt to assets, Debt to equity, Dividend yield, Earnings yield, Enterprise value, Enterprise value over EBITDA, Ev to free cash flow, Ev to operating cash flow, Ev to sales, Free cash flow per share, Free cash flow yield, Graham net net, Graham number, Income quality, Intangibles to total assets, Interest debt per share, Inventory turnover, Market cap, Net current asset value, Net debt to EBITDA, Net income per share, Operating cash flow per share, Payables turnover, Payout ratio, Pb ratio, Pe ratio, Pfcf ratio, Pocfratio, Price to sales ratio, Ptb ratio, Receivables turnover, Research and ddevelopement to revenue, Return on tangible assets, Revenue per share, Roe, Roic, Sales general and administrative to revenue, Shareholders equity per share, Stock based compensation to revenue, Tangible book value per share, and Working capital. [Source: Financial Modeling Prep]

* n : Number of latest years/quarters. Default 1.
* q : Quarter fundamental data flag. Default False.

### ratios <a name="ratios"></a>

```text
usage: ratios [-n N_NUM] [-q]
```

Prints in-depth ratios of a company over time. This can be either quarterly or annually. This contains, among other things, Price-to-Book Ratio, Payout Ratio and Operating Cycle. The following fields are expected: Asset turnover, Capital expenditure coverage ratio, Cash conversion cycle, Cash flow coverage ratios, Cash flow to debt ratio, Cash per share, Cash ratio, Company equity multiplier, Current ratio, Days of inventory outstanding, Days of payables outstanding, Days of sales outstanding, Debt equity ratio, Debt ratio, Dividend paid and capex coverage ratio, Dividend payout ratio, Dividend yield, Ebit per revenue, Ebt per ebit, Effective tax rate, Enterprise value multiple, Fixed asset turnover, Free cash flow operating cash flow ratio, Free cash flow per share, Gross profit margin, Inventory turnover, Long term debt to capitalization, Net income per EBT, Net profit margin, Operating cash flow per share, Operating cash flow sales ratio, Operating cycle, Operating profit margin, Payables turnover, Payout ratio, Pretax profit margin, Price book value ratio, Price cash flow ratio, Price earnings ratio, Price earnings to growth ratio, Price fair value, Price sales ratio, Price to book ratio, Price to free cash flows ratio, Price to operating cash flows ratio, Price to sales ratio, Quick ratio, Receivables turnover, Return on assets, Return on capital employed, Return on equity, Short term coverage ratios, and Total debt to capitalization. [Source: Financial Modeling Prep]

* n : Number of latest years/quarters. Default 1.
* q : Quarter fundamental data flag. Default False.

### growth <a name="growth"></a>

```text
usage: growth [-n N_NUM] [-q]
```

Prints the growth of several financial statement items and ratios over time. This can be either annually and quarterly. These are, among other things, Revenue Growth (3, 5 and 10 years), inventory growth and operating cash flow growth (3, 5 and 10 years). The following fields are expected: Asset growth, Book valueper share growth, Debt growth, Dividendsper share growth, Ebitgrowth, Epsdiluted growth, Epsgrowth, Five y dividendper share growth per share, Five y net income growth per share, Five y operating c f growth per share, Five y revenue growth per share, Five y shareholders equity growth per share, Free cash flow growth, Gross profit growth, Inventory growth, Net income growth, Operating cash flow growth, Operating income growth, Rdexpense growth, Receivables growth, Revenue growth, Sgaexpenses growth, Ten y dividendper share growth per share, Ten y net income growth per share, Ten y operating c f growth per share, Ten y revenue growth per share, Ten y shareholders equity growth per share, Three y dividendper share growth per share, Three y net income growth per share, Three y operating c f growth per share, Three y revenue growth per share, Three y shareholders equity growth per share, Weighted average shares diluted growth, and Weighted average shares growth [Source: Financial Modeling Prep]

* n : Number of latest years/quarters. Default 1.
* q : Quarter fundamental data flag. Default False.
