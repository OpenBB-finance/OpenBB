# FINANCIAL MODELING PREP

This menu aims to provide fundamental analysis of a company based on Financial Modeling Prep data.

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

Prints a complete cash flow statement over time. This can be either quarterly or annually. The following fields are expected: Accepted date, Accounts payables, Accounts receivables, Acquisitions net, Capital expenditure, Cash at beginning of period, Cash at end of period, Change in working capital, Common stock issued, Common stock repurchased, Debt repayment, Deferred income tax, Depreciation and amortization, Dividends paid, Effect of forex changes on cash, Filling date, Final link, Free cash flow, Inventory, Investments in property plant and equipment, Link, Net cash provided by operating activities, Net cash used for investing activities, Net cash used provided by financing activities, Net change in cash, Net income, Operating cash flow, Other financing activities, Other investing activities, Other non cash items, Other working capital, Period, Purchases of investments, Sales maturities of investments, Stock based compensation. [Source: Financial Modeling Prep]

* n : Number of latest years/quarters. Default 1.
* q : Quarter fundamental data flag. Default False.

Prints a complete cash flow statement over time. This can be either quarterly or annually. The following fields are expected: Accepted date, Accounts payables, Accounts receivables, Acquisitions net, Capital expenditure, Cash at beginning of period, Cash at end of period, Change in working capital, Common stock issued, Common stock repurchased, Debt repayment, Deferred income tax, Depreciation and amortization, Dividends paid, Effect of forex changes on cash, Filling date, Final link, Free cash flow, Inventory, Investments in property plant and equipment, Link, Net cash provided by operating activities, Net cash used for investing activities, Net cash used provided by financing activities, Net change in cash, Net income, Operating cash flow, Other financing activities, Other investing activities, Other non cash items, Other working capital, Period, Purchases of investments, Sales maturities of investments, Stock based compensation. [Source: Financial Modeling Prep]

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


### score <a name="score"></a>

```text
usage: score
```

Value investing tool based on Warren Buffett, Joseph Piotroski and Benjamin Graham thoughts [Source: Financial Modeling Prep]
