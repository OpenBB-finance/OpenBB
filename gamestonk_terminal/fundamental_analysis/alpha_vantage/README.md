# ALPHA VANTAGE

This menu aims to provide fundamental analysis of a company based on Alpha Vantage data.

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


### overview <a name="overview"></a>

```text
usage: overview
```

Prints an overview about the company. The following fields are expected: Symbol, Asset type, Name, Description, Exchange, Currency, Country, Sector, Industry, Address, Full time employees, Fiscal year end, Latest quarter, Market capitalization, EBITDA, PE ratio, PEG ratio, Book value, Dividend per share, Dividend yield, EPS, Revenue per share TTM, Profit margin, Operating margin TTM, Return on assets TTM, Return on equity TTM, Revenue TTM, Gross profit TTM, Diluted EPS TTM, Quarterly earnings growth YOY, Quarterly revenue growth YOY, Analyst target price, Trailing PE, Forward PE, Price to sales ratio TTM, Price to book ratio, EV to revenue, EV to EBITDA, Beta, 52 week high, 52 week low, 50 day moving average, 200 day moving average, Shares outstanding, Shares float, Shares short, Shares short prior month, Short ratio, Short percent outstanding, Short percent float, Percent insiders, Percent institutions, Forward annual dividend rate, Forward annual dividend yield, Payout ratio, Dividend date, Ex dividend date, Last split factor, and Last split date. Also, the C i k field
corresponds to Central Index Key, which can be used to search a company on
https://www.sec.gov/edgar/searchedgar/cik.htm [Source: Alpha Vantage]

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
