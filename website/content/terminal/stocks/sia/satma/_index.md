```text
usage: satma [-s {BS,bs,IS,is,CF,cf,}] [-h]
```
See all balance sheet, income and cash flow statement metrics available [source: StockAnalysis]

```
optional arguments:
  -s {BS,bs,IS,is,CF,cf,}, --statement {BS,bs,IS,is,CF,cf,}
                        See all metrics available for the given choice (default: None)
  -h, --help            show this help message (default: False)
```
The current list of available options is:

````
Balance Sheet Statement
  ce          Cash & Equivalents
  sti         Short-Term Investments
  cce         Cash & Cash Equivalents
  rec         Receivables
  inv         Inventory
  oca         Other Current Assets
  tca         Total Current Assets
  ppe         Property, Plant & Equipment
  lti         Long-Term Investments
  gai         Goodwill and Intangibles
  olta        Other Long-Term Assets
  tlta        Total Long-Term Assets
  ta          Total Assets
  ap          Accounts Payable
  dr          Deferred Revenue
  cd          Current Debt
  ocl         Other Current Liabilities
  tcl         Total Current Liabilities
  ltd         Long-Term Debt
  oltl        Other Long-Term Liabilities
  tltl        Total Long-Term Liabilities
  tl          Total Liabilities
  ret         Retained Earnings
  ci          Comprehensive Income
  se          Shareholders' Equity
  tle         Total Liabilities and Equity

Income Statement
  re          Revenue
  cr          Cost of Revenue
  gp          Gross Profit
  sga         Selling, Genera & Admin
  rd          Research & Development
  ooe         Other Operating Expenses
  oi          Operating Income
  ie          Interest Expense / Income
  oe          Other Expense / Income
  it          Income Tax
  ni          Net Income
  pd          Preferred Dividends

Cash Flow Statement
  ninc        Net Income
  da          Depreciation & Amortization
  sbc         Share-Based Compensation
  ooa         Other Operating Activities
  ocf         Operating Cash Flow
  cex         Capital Expenditures
  acq         Acquisitions
  cii         Change in Investments
  oia         Other Investing Activities
  icf         Investing Cash Flow
  dp          Dividends Paid
  si          Share Insurance / Repurchase
  di          Debt Issued / Paid
  ofa         Other Financing Activities
  fcf         Financing Cash Flow
  ncf         Net Cash Flow
````