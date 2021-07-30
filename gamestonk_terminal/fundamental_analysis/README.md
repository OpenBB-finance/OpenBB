# FUNDAMENTAL ANALYSIS

This menu aims to extract all fundamentals of a pre-loaded company, and the usage of the following commands along with an example will be exploited below.

* [screener](#screener)
  * screen info about the company [Finviz]
* [mgmt](#mgmt)
  * management team of the company [Business Insider]
* [score](#score)
  * investing score from Warren Buffett, Joseph Piotroski and Benjamin Graham [FMP]

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
* [fraud](#fraud)
  * key fraud ratios


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

## ALPHA VANTAGE<a name="ALPHA_VANTAGE"></a>

### overview <a name="overview"></a>

```text
usage: overview
```

Prints an overview about the company. The following fields are expected: Symbol, Asset type, Name, Description, Exchange, Currency, Country, Sector, Industry, Address, Full time employees, Fiscal year end, Latest quarter, Market capitalization, EBITDA, PE ratio, PEG ratio, Book value, Dividend per share, Dividend yield, EPS, Revenue per share TTM, Profit margin, Operating margin TTM, Return on assets TTM, Return on equity TTM, Revenue TTM, Gross profit TTM, Diluted EPS TTM, Quarterly earnings growth YOY, Quarterly revenue growth YOY, Analyst target price, Trailing PE, Forward PE, Price to sales ratio TTM, Price to book ratio, EV to revenue, EV to EBITDA, Beta, 52 week high, 52 week low, 50 day moving average, 200 day moving average, Shares outstanding, Shares float, Shares short, Shares short prior month, Short ratio, Short percent outstanding, Short percent float, Percent insiders, Percent institutions, Forward annual dividend rate, Forward annual dividend yield, Payout ratio, Dividend date, Ex dividend date, Last split factor, and Last split date. Also, the C i k field
corresponds to Central Index Key, which can be used to search a company on
https://www.sec.gov/edgar/searchedgar/cik.htm [Source: Alpha Vantage]

### income <a name="income"></a>

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

Prints a complete cash flow statement over time. This can be either quarterly or annually. The following fields are expected: Accepted date, Accounts payables, Accounts receivables, Acquisitions net, Capital expenditure, Cash at beginning of period, Cash at end of period, Change in working capital, Common stock issued, Common stock repurchased, Debt repayment, Deferred income tax, Depreciation and amortization, Dividends paid, Effect of forex changes on cash, Filling date, Final link, Free cash flow, Inventory, Investments in property plant and equipment, Link, Net cash provided by operating activities, Net cash used for investing activities, Net cash used provided by financing activities, Net change in cash, Net income, Operating cash flow, Other financing activities, Other investing activities, Other non cash items, Other working capital, Period, Purchases of investments, Sales maturities of investments, Stock based compensation. [Source: Alpha Vantage]

* n : Number of latest years/quarters. Default 1.
* q : Quarter fundamental data flag. Default False.

### earnings <a name="earnings"></a>

```text
usage: earnings [-n N_NUM] [-q]
```

Print earnings dates and reported EPS of the company. The following fields are expected: Fiscal Date Ending and Reported EPS. [Source: Alpha Vantage]

* n : Number of latest years/quarters. Default 1.
* q : Quarter fundamental data flag. Default False.

### fraud <a name="fraud"></a>

```text
usage: fraud
```

The Beneish model is a statistical model that uses financial ratios calculated with accounting data of a specific company in order to check if it is likely (high probability) that the reported earnings of the company have been manipulated.[Source: Wikipedia]
