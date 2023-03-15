---
title: Fundamental Analysis
keywords: [fundamentals, fundamental, fa, ratios, earnings, balance, income, cash, statement, statements, sec, multiples, price, ebitda, ebitdam, revenue, quarter, annual, change, company, performance, filing, filings, 10K, 8K, audit, audited, due diligence, research, company, ticker, analyst, rating, rot, pt, est, sec, supplier, customer, arktrades, ratings, analysts, filings, form, forms, customers, suppliers]
description: This guide introduces the Fundamental Analysis menu within the Stocks menu, briefly explains the features, and provides examples in context.
---

The FA module provides programmatic access to the commands from within the OpenBB Terminal. To get the most out of these functions, we recommend obtaining API keys from:

- AlphaVantage
- EODHD (premium subscribers only)
- Financial Modeling Prep
- Polygon

View [this page](https://docs.openbb.co/terminal/quickstart/api-keys) for a list of all API sources used across the platform.

## How to Use

The contextual help will be activated upon entering ., after, openbb.stocks.fa. A brief description below highlights the functions within the `fa` module.

| Path                              |                                    Description |
| :---------------------------------|----------------------------------------------: |
| openbb.stocks.fa.analysis         |    Analysis SEC Fillings with Machine Learning |
| openbb.stocks.fa.balance          |                          Company Balance Sheet |
| openbb.stocks.fa.cal              |                Calendar Earnings and Estimates |
| openbb.stocks.fa.cash             |                             Company Cash Flows |
| openbb.stocks.fa.data             |                 Fundamental and Technical Data |
| openbb.stocks.fa.dcfc             |                  Shows DCF Values for a Ticker |
| openbb.stocks.fa.divs             |             Historical Dividends for a Company |
| openbb.stocks.fa.dupont           |                         Detailed ROE Breakdown |
| openbb.stocks.fa.earnings         |                          Earnings Data and EPS |
| openbb.stocks.fa.enterprise       |                       Company Enterprise Value |
| openbb.stocks.fa.fama_coe         |           Fama/French value for Cost of Equity |
| openbb.stocks.fa.fraud            |                               Key Fraud Ratios |
| openbb.stocks.fa.growth           |            Growth of Financial Statement Items |
| openbb.stocks.fa.hq               |                        HQ Location for Company |
| openbb.stocks.fa.income           |                       Company Income Statement |
| openbb.stocks.fa.info             |                    Information About a Company |
| openbb.stocks.fa.key              |                            Company Key Metrics |
| openbb.stocks.fa.metrics          |                          Key Metrics Over Time |
| openbb.stocks.fa.mgmt             |                        Company Management Team |
| openbb.stocks.fa.mktcap           |                           Estimated Market Cap |
| openbb.stocks.fa.overview         |                        Overview of the Company |
| openbb.stocks.fa.profile          |                                Company Profile |
| openbb.stocks.fa.ratios           |                      In-Depth Ratios over Time |
| openbb.stocks.fa.score            |             Investing Score from Warren Buffet |
| openbb.stocks.fa.shrs             |   Shareholders (Insiders, Institutions, Funds) |
| openbb.stocks.fa.splits           |      Stock Splits and Reverse Splits Since IPO |
| openbb.stocks.fa.sust             |                          Sustainability Values |
|openbb.stocks.fa.analyst |Analyst Prices and Ratings |
|openbb.stocks.fa.arktrades |Ark Trades for the Ticker |
|openbb.stocks.fa.customer |List of Customers |
|openbb.stocks.fa.est |Earnings Estimates |
|openbb.stocks.fa.pt |Historical Price Targets |
|openbb.stocks.fa.rating |Daily Ratings |
|openbb.stocks.fa.rot |Historical Number of Analysts and Ratings |
|openbb.stocks.fa.sec |List of SEC Filings |
|openbb.stocks.fa.supplier |List of Suppliers |

Alternatively the contents of the module can be printed with:

```python
help(openbb.stocks.fa)
```

## Examples

The examples provided below will assume that the following import block is included at the beginning of the Python script or Notebook file:

```python
from openbb_terminal.sdk import openbb
```

### Earnings

The `openbb.stocks.fa.earnings` function returns upcoming earnings dates and estimates for EPS. There are two data sources available - YahooFinance or AlphaVantage, both of which provide historical context.

```python
openbb.stocks.fa.earnings('COST', quarterly = True)
```

|    | Symbol   | Company                      | Earnings Date          |   EPS Estimate |   Reported EPS |   Surprise(%) |
|---:|:---------|:-----------------------------|:-----------------------|---------------:|---------------:|--------------:|
|  0 | COST     | Costco Wholesale Corp        | Sep 20, 2023, 4 PMEDT  |         nan    |          nan   |        nan    |
|  1 | COST     | Costco Wholesale Corp        | May 24, 2023, 4 PMEDT  |         nan    |          nan   |        nan    |
|  2 | COST     | Costco Wholesale Corp        | Dec 08, 2022, 5 PMEST  |           3.11 |          nan   |        nan    |
|  3 | COST     | Costco Wholesale Corp        | Dec 07, 2022, 4 PMEST  |           3.11 |          nan   |        nan    |
|  4 | COST     | Costco Wholesale Corporation | Sep 22, 2022, 12 PMEDT |           4.17 |            4.2 |          0.84 |
| 95 | COST     | Costco Wholesale Corporation | Oct 06, 1999, 12 AMEDT |           0.38 |           0.4  |          3.64 |
| 96 | COST     | Costco Wholesale Corporation | May 26, 1999, 12 AMEDT |           0.22 |           0.23 |          4.41 |
| 97 | COST     | Costco Wholesale Corporation | Mar 04, 1999, 12 AMEST |           0.32 |           0.35 |          8.57 |
| 98 | COST     | Costco Wholesale Corporation | Dec 17, 1998, 12 AMEST |           0.23 |           0.23 |          0.9  |
| 99 | COST     | Costco Wholesale Corporation | Oct 08, 1998, 12 AMEDT |           0.32 |           0.33 |          1.87 |

### Growth

`openbb.stocks.fa.growth` provides annualized financial ratios as growth metrics.

```python
openbb.stocks.fa.growth('COST', limit = 20)
```

|                     | 2022   | 2021   | 2020   | 2019   | 2018   | 2017   | 2016   | 2015   | 2014   | 2013   | 2012   | 2011   | 2010   | 2009   | 2008   | 2007   | 2006   | 2005   | 2004   | 2003   |
|:--------------------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|:-------|
| Period              | FY     | FY     | FY     | FY     | FY     | FY     | FY     | FY     | FY     | FY     | FY     | FY     | FY     | FY     | FY     | FY     | FY     | FY     | FY     | FY     |
| Revenue growth      | 0.158  | 0.175  | 0.092  | 0.079  | 0.097  | 0.087  | 0.022  | 0.032  | 0.071  | 0.061  | 0.115  | 0.141  | 0.091  | -0.015 | 0.126  | 0.071  | 0.136  | 0.100  | 0.131  | 0.098  |
| Gross profit growth | 0.092  | 0.157  | 0.101  | 0.076  | 0.075  | 0.084  | 0.045  | 0.067  | 0.074  | 0.073  | 0.102  | 0.123  | 0.095  | 0.012  | 0.130  | 0.074  | 0.124  | 0.095  | 0.133  | 0.111  |
| Debt growth        | -0.108 | -0.003 |   0.49 |  0.052 | -0.026 |   0.29 |  -0.16 |  0.207 |  0.019 |  2.616 | -0.358 | -0.006 | -0.059 | -0.018 |  0.056 |   2.93 | -0.264 | -0.418 | -0.012 |  0.023 |

### Analysis

The `openbb.stocks.fa.analysis` function scans 10K SEC filings with NLP to highlight risk factors and notable statements provided by the company.

```python
openbb.stocks.fa.analysis('COST')
```

|    | Group                   | Good   | Sentence |
|---:|:------------------------|:-------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|  0 | Risk factors            | False  | During 2022, our international operations, including Canada, generated 27% and 32% of our net sales and operating income, respectively.     |
|  1 | Risk factors            | False  | Changes in tax rates, new U. S. or foreign tax legislation, and exposure to additional tax liabilities could adversely affect our financial condition and results of operations. |
|  8 | Risk factors            | True   | Declines in financial performance of our U. S. operations, particularly in California, and our Canadian operations could arise from, among other things: slow growth or declines in comparable warehouse sales (comparable sales); negative trends in operating expenses, including increased labor, healthcare and energy costs; failing to meet targets for warehouse openings; cannibalizing existing locations with new warehouses; shifts in sales mix toward lower gross margin products; changes or uncertainties in economic conditions in our markets, including higher levels of unemployment and depressed home values; and failing to consistently provide high quality and innovative new products. |
| 26 | Discussion and Analysis | True   | Stock Repurchase ProgramsDuring 2022 and 2021, we repurchased 863,000 and 1,358, 000 shares of common stock, at average prices of $511.46 and $364.39, respectively, totaling approximately $442 and $495, respectively. |

### Sust

A company's ESG scores are fetched with:

```python
openbb.stocks.fa.sust('COST')
```

|                        | Value          |
|:-----------------------|:---------------|
| Palm oil               | False          |
| Controversial weapons  | False          |
| Gambling               | False          |
| Social score           | 11.21          |
| Nuclear                | False          |
| Fur leather            | False          |
| Alcoholic              | False          |
| Gmo                    | False          |
| Catholic               | False          |
| Social percentile      |                |
| Peer count             | 33             |
| Governance score       | 5.72           |
| Environment percentile |                |
| Animal testing         | False          |
| Tobacco                | False          |
| Total esg              | 24.19          |
| Highest controversy    | 3              |
| Esg performance        | AVG_PERF       |
| Coal                   | False          |
| Pesticides             | False          |
| Adult                  | False          |
| Percentile             | 40.87          |
| Peer group             | Food Retailers |
| Small arms             | False          |
| Environment score      | 7.26           |
| Governance percentile  |                |
| Military contract      | False          |

### Key

Use `openbb.stocks.fa.key` for a small table of key statistics.

```python
openbb.stocks.fa.key('COST')
```

|                          |           |
|:-------------------------|:----------|
| Market capitalization    | 238.674 B |
| EBITDA                   | 9.693 B   |
| EPS                      | 13.14     |
| PE ratio                 | 41.04     |
| PEG ratio                | 3.759     |
| Price to book ratio      | 11.34     |
| Return on equity TTM     | 0.305     |
| Price to sales ratio TTM | 1.052     |
| Dividend yield           | 0.0068    |
| 50 day moving average    | 493.34    |
| Analyst target price     | 562.93    |
| Beta                     | 0.717     |

### SHRS

Ownership metrics for a company are listed with:

```python
openbb.stocks.fa.shrs(symbol = 'COST', holder = 'major')
```

|    |        |                                           |
|---:|:-------|:------------------------------------------|
|  0 | 0.22%  | Percentage of Shares Held by All Insider  |
|  1 | 69.05% | Percentage of Shares Held by Institutions |
|  2 | 69.21% | Percentage of Float Held by Institutions  |
|  3 | 3444   | Number of Institutions Holding Shares     |

Accepted arguments for `holder` are `major`, `mutualfund`, and `institutional`.

```python
openbb.stocks.fa.shrs(symbol = 'COST', holder = 'mutualfund')
```

|    | Holder                                                     | Shares   | Date Reported       | Stake   | Value   |
|---:|:-----------------------------------------------------------|:---------|:--------------------|:--------|:--------|
|  0 | Vanguard Total Stock Market Index Fund                     | 13.051 M | 2022-06-29 00:00:00 | 2.95 %  | 6.576 B |
|  1 | Vanguard 500 Index Fund                                    | 10.041 M | 2022-09-29 00:00:00 | 2.27 %  | 5.059 B |
|  2 | Invesco ETF Tr-Invesco QQQ Tr, Series 1 ETF                | 6.504 M  | 2022-09-29 00:00:00 | 1.47 %  | 3.277 B |
|  3 | SPDR S&P 500 ETF Trust                                     | 5.062 M  | 2022-10-30 00:00:00 | 1.14 %  | 2.551 B |
|  4 | Fidelity 500 Index Fund                                    | 4.785 M  | 2022-09-29 00:00:00 | 1.08 %  | 2.411 B |
|  5 | iShares Core S&P 500 ETF                                   | 3.938 M  | 2022-09-29 00:00:00 | 0.89 %  | 1.984 B |
|  6 | Vanguard Growth Index Fund                                 | 3.648 M  | 2022-09-29 00:00:00 | 0.82 %  | 1.838 B |
|  7 | Vanguard Institutional Index Fund-Institutional Index Fund | 3.216 M  | 2022-09-29 00:00:00 | 0.73 %  | 1.621 B |
|  8 | Select Sector SPDR Fund-Consumer Staples                   | 3.131 M  | 2022-10-30 00:00:00 | 0.71 %  | 1.577 B |
|  9 | Vanguard Specialized-Dividend Appreciation Index Fund      | 2.740 M  | 2022-07-30 00:00:00 | 0.62 %  | 1.380 B |

```python
openbb.stocks.fa.shrs(symbol = 'COST', holder = 'institutional')
```

|    | Holder                              | Shares   | Date Reported       | Stake   | Value    |
|---:|:------------------------------------|:---------|:--------------------|:--------|:---------|
|  0 | Vanguard Group, Inc. (The)          | 39.030 M | 2022-09-29 00:00:00 | 8.82 %  | 19.666 B |
|  1 | Blackrock Inc.                      | 30.060 M | 2022-09-29 00:00:00 | 6.79 %  | 15.146 B |
|  2 | State Street Corporation            | 18.802 M | 2022-09-29 00:00:00 | 4.25 %  | 9.473 B  |
|  3 | FMR, LLC                            | 10.346 M | 2022-09-29 00:00:00 | 2.34 %  | 5.213 B  |
|  4 | Geode Capital Management, LLC       | 8.044 M  | 2022-09-29 00:00:00 | 1.82 %  | 4.053 B  |
|  5 | Bank of America Corporation         | 7.875 M  | 2022-09-29 00:00:00 | 1.78 %  | 3.968 B  |
|  6 | Morgan Stanley                      | 7.319 M  | 2022-09-29 00:00:00 | 1.65 %  | 3.688 B  |
|  7 | Northern Trust Corporation          | 4.976 M  | 2022-09-29 00:00:00 | 1.12 %  | 2.507 B  |
|  8 | AllianceBernstein, L.P.             | 4.680 M  | 2022-09-29 00:00:00 | 1.06 %  | 2.358 B  |
|  9 | Bank Of New York Mellon Corporation | 4.481 M  | 2022-09-29 00:00:00 | 1.01 %  | 2.258 B  |

### Balance

Financial statement items can be displayed as their reported value or as a percent change.

```python
openbb.stocks.fa.balance(symbol = 'COST', ratios=True)
```

| Breakdown                                  |   2022-08-31 |   2021-08-31 |   2020-08-31 |
|:-------------------------------------------|-------------:|-------------:|-------------:|
| Cash and cash equivalents                  |   -0.0937111 |   -0.0830007 |   0.464337   |
| Other short-term investments               |   -0.0774264 |   -0.107977  |  -0.0301887  |
| Total cash                                 |   -0.0924846 |   -0.0849305 |   0.408831   |
| Net receivables                            |    0.242928  |    0.163226  |   0.00977199 |
| Inventory                                  |    0.259726  |    0.161166  |   0.0743308  |
| Other current assets                       |    0.14253   |    0.282502  |  -0.0792079  |
| Total current assets                       |    0.108151  |    0.0492532 |   0.19736    |
| Gross property, plant and equipment        |    0.0532209 |    0.0815396 |   0.149114   |
| Accumulated depreciation                   |    0.0790625 |    0.0984801 |   0.0988412  |
| Net property, plant and equipment          |    0.039345  |    0.072657  |   0.177358   |
| Other long-term assets                     |    0.19787   |    0.190074  |   1.77171    |
| Total non-current assets                   |    0.0573531 |    0.0848156 |   0.251928   |
| Total assets                               |    0.0826416 |    0.0668155 |   0.2237     |
| Current debt                               |   -0.908636  |    7.41053   |  -0.944085   |
| Accounts payable                           |    0.0964492 |    0.148603  |   0.21346    |
| Accrued liabilities                        |    0.0921715 |    0.152661  |   0.147383   |
| Other current liabilities                  |    0.230213  |    0.223444  |  -0.0168776  |
| Total current liabilities                  |    0.0868517 |    0.185035  |   0.0691569  |
| Long-term debt                             |   -0.0310819 |   -0.109396  |   0.466432   |
| Other long-term liabilities                |    0.057971  |    0.248062  |   0.329897   |
| Total non-current liabilities              |   -0.0194059 |   -0.0214875 |   0.825049   |
| Total liabilities                          |    0.0565429 |    0.117744  |   0.235947   |
| Common stock                               |   -0.5       |    0         |   0          |
| Retained earnings                          |    0.335933  |   -0.0941843 |   0.255508   |
| Accumulated other comprehensive income     |    0.608619  |   -0.123362  |  -0.0967967  |
| Total stockholders' equity                 |    0.175245  |   -0.0393787 |   0.199501   |
| Total liabilities and stockholders' equity |    0.0826416 |    0.0668155 |   0.2237     |


Cashflow and Income statements function in the same way as `balance` does.

### Cash

Get the company's cash statements.

```python
openbb.stocks.fa.cash(symbol = 'COST')
```

| Breakdown                                                 |         ttm |   2022-08-31 |   2021-08-31 |   2020-08-31 | 2019-08-31   |
|:----------------------------------------------------------|------------:|-------------:|-------------:|-------------:|:-------------|
| Net income                                                |  5844000000 |   5844000000 |   5007000000 |   4002000000 | 3659000000   |
| Depreciation & amortisation                               |  1900000000 |   1900000000 |   1781000000 |   1645000000 | 1492000000   |
| Deferred income taxes                                     |   -37000000 |    -37000000 |     59000000 |    104000000 | 147000000    |
| Stock-based compensation                                  |   724000000 |    724000000 |    665000000 |    619000000 | 595000000    |
| Change in working capital                                 | -1563000000 |  -1563000000 |   1003000000 |   2198000000 | 409000000    |
| Inventory                                                 | -4003000000 |  -4003000000 |  -1892000000 |   -791000000 | -536000000   |
| Accounts payable                                          |  1891000000 |   1891000000 |   1838000000 |   2261000000 | 322000000    |
| Other working capital                                     |  3501000000 |   3501000000 |   5370000000 |   6051000000 | 3358000000   |
| Other non-cash items                                      |   453000000 |    453000000 |    371000000 |    236000000 | 9000000      |
| Net cash provided by operating activities                 |  7392000000 |   7392000000 |   8958000000 |   8861000000 | 6356000000   |
| Investments in property, plant and equipment              | -3891000000 |  -3891000000 |  -3588000000 |  -2810000000 | -2998000000  |
| Acquisitions, net                                         |           0 |            0 |            0 |  -1163000000 | `<NA>`         |
| Purchases of investments                                  | -1121000000 |  -1121000000 |  -1331000000 |  -1626000000 | -1094000000  |
| Sales/maturities of investments                           |  1145000000 |   1145000000 |   1446000000 |   1678000000 | 1231000000   |
| Other investing activities                                |   -48000000 |    -48000000 |    -62000000 |     30000000 | -4000000     |
| Net cash used for investing activities                    | -3915000000 |  -3915000000 |  -3535000000 |  -3891000000 | -2865000000  |
| Debt repayment                                            |  -800000000 |   -800000000 |    -94000000 |  -3200000000 | -89000000    |
| Common stock repurchased                                  |  -439000000 |   -439000000 |   -496000000 |   -196000000 | -247000000   |
| Dividends paid                                            | -1498000000 |  -1498000000 |  -5748000000 |  -1479000000 | -1038000000  |
| Other financing activities                                | -1546000000 |  -1546000000 |   -379000000 |   -401000000 | -281000000   |
| Net cash used provided by (used for) financing activities | -4283000000 |  -4283000000 |  -6488000000 |  -1147000000 | -1147000000  |
| Net change in cash                                        | -1055000000 |  -1055000000 |  -1019000000 |   3893000000 | 2329000000   |
| Cash at beginning of period                               | 11258000000 |  11258000000 |  12277000000 |   8384000000 | 6055000000   |
| Cash at end of period                                     | 10203000000 |  10203000000 |  11258000000 |  12277000000 | 8384000000   |
| Operating cash flow                                       |  7392000000 |   7392000000 |   8958000000 |   8861000000 | 6356000000   |
| Capital expenditure                                       | -3891000000 |  -3891000000 |  -3588000000 |  -2810000000 | -2998000000  |
| Free cash flow                                            |  3501000000 |   3501000000 |   5370000000 |   6051000000 | 3358000000   |

### Income

Get the company's income statements.

```python
openbb.stocks.fa.income('COST')
```

| Breakdown                                                 |         ttm |   2022-08-31 |   2021-08-31 |   2020-08-31 | 2019-08-31   |
|:----------------------------------------------------------|------------:|-------------:|-------------:|-------------:|:-------------|
| Net income                                                |  5844000000 |   5844000000 |   5007000000 |   4002000000 | 3659000000   |
| Depreciation & amortisation                               |  1900000000 |   1900000000 |   1781000000 |   1645000000 | 1492000000   |
| Deferred income taxes                                     |   -37000000 |    -37000000 |     59000000 |    104000000 | 147000000    |
| Stock-based compensation                                  |   724000000 |    724000000 |    665000000 |    619000000 | 595000000    |
| Change in working capital                                 | -1563000000 |  -1563000000 |   1003000000 |   2198000000 | 409000000    |
| Inventory                                                 | -4003000000 |  -4003000000 |  -1892000000 |   -791000000 | -536000000   |
| Accounts payable                                          |  1891000000 |   1891000000 |   1838000000 |   2261000000 | 322000000    |
| Other working capital                                     |  3501000000 |   3501000000 |   5370000000 |   6051000000 | 3358000000   |
| Other non-cash items                                      |   453000000 |    453000000 |    371000000 |    236000000 | 9000000      |
| Net cash provided by operating activities                 |  7392000000 |   7392000000 |   8958000000 |   8861000000 | 6356000000   |
| Investments in property, plant and equipment              | -3891000000 |  -3891000000 |  -3588000000 |  -2810000000 | -2998000000  |
| Acquisitions, net                                         |           0 |            0 |            0 |  -1163000000 | `<NA>`         |
| Purchases of investments                                  | -1121000000 |  -1121000000 |  -1331000000 |  -1626000000 | -1094000000  |
| Sales/maturities of investments                           |  1145000000 |   1145000000 |   1446000000 |   1678000000 | 1231000000   |
| Other investing activities                                |   -48000000 |    -48000000 |    -62000000 |     30000000 | -4000000     |
| Net cash used for investing activities                    | -3915000000 |  -3915000000 |  -3535000000 |  -3891000000 | -2865000000  |
| Debt repayment                                            |  -800000000 |   -800000000 |    -94000000 |  -3200000000 | -89000000    |
| Common stock repurchased                                  |  -439000000 |   -439000000 |   -496000000 |   -196000000 | -247000000   |
| Dividends paid                                            | -1498000000 |  -1498000000 |  -5748000000 |  -1479000000 | -1038000000  |
| Other financing activities                                | -1546000000 |  -1546000000 |   -379000000 |   -401000000 | -281000000   |
| Net cash used provided by (used for) financing activities | -4283000000 |  -4283000000 |  -6488000000 |  -1147000000 | -1147000000  |
| Net change in cash                                        | -1055000000 |  -1055000000 |  -1019000000 |   3893000000 | 2329000000   |
| Cash at beginning of period                               | 11258000000 |  11258000000 |  12277000000 |   8384000000 | 6055000000   |
| Cash at end of period                                     | 10203000000 |  10203000000 |  11258000000 |  12277000000 | 8384000000   |
| Operating cash flow                                       |  7392000000 |   7392000000 |   8958000000 |   8861000000 | 6356000000   |
| Capital expenditure                                       | -3891000000 |  -3891000000 |  -3588000000 |  -2810000000 | -2998000000  |
| Free cash flow                                            |  3501000000 |   3501000000 |   5370000000 |   6051000000 | 3358000000   |

### Customer

`openbb.stocks.fa.customer` returns a table of a company's publicly-listed customers and their changes in revenue and income.

```python
gtlb_customers = openbb.stocks.fa.customer('GTLB')

gtlb_customers
```

| TICKER   | Company Name                 | Rev. Y/Y     | Rev. Seq.    | Inc. Y/Y   | Inc. Seq.   |
|:---------|:-----------------------------|:-------------|:-------------|:-----------|:------------|
| GTLB     | Gitlab Inc.                  | -            | 15.6 %       | -          | -           |
| TICKER   | CUSTOMER NAME                | COST OF REV. | COST OF REV. | SG&A       | SG&A        |
| ALRM     | Alarm com Holdings Inc       | 6.47 %       | -2 %         | -44.1 %    | -55.87 %    |
| YOU      | Clear Secure Inc             | -            | -            | -          | -82.32 %    |
| EFX      | Equifax Inc                  | 10.94 %      | 0.07 %       | -7.61 %    | -3.69 %     |
| EVBG     | Everbridge Inc               | 16.95 %      | 6.64 %       | -25.27 %   | -35.71 %    |
| EVCM     | Evercommerce Inc             | 34.21 %      | 4.63 %       | -42.2 %    | -53.49 %    |
| RSKIA    | George Risk Industries Inc.  | 14.62 %      | -5.51 %      | -2.11 %    | -3.44 %     |
| INFY     | Infosys Limited              | 24.56 %      | -            | -          | -           |
| XM       | Qualtrics International Inc  | 67.05 %      | 6.91 %       | -43.49 %   | -44.79 %    |
| SEM      | Select Medical Holdings Corp | 7.41 %       | 0.23 %       | 4.24 %     | 5.96 %      |
| CXM      | Sprinklr Inc.                | 12.91 %      | 1.05 %       | 15.26 %    | 1.01 %      |
| SPT      | Sprout Social Inc            | 24.02 %      | 1.14 %       | -1.88 %    | -28.69 %    |
| TRU      | Transunion                   | -            | -            | 34.9 %     | 1.99 %      |

### Supplier

`openbb.stocks.fa.supplier` is the supply side to the `customer` function. It returns revenue, net income, net margin, and cash flow, for the companies feeding the ticker's supply chain.

```python
gtlb_suppliers = openbb.stocks.fa.supplier('GTLB')

gtlb_suppliers
```

| TICKER   | Company Name                                |   Revenue |   Net Income | Net Margin   |   Cash Flow |
|:---------|:--------------------------------------------|----------:|-------------:|:-------------|------------:|
| MSFT     | Microsoft Corporation                       |  50122    |     17556    | 35.03 %      |     8953    |
| DELL     | Dell Technologies Inc.                      |  26425    |       506    | 1.91 %       |    -1183    |
| ORCL     | Oracle Corporation                          |  21529    |      1548    | 7.19 %       |   -10935    |
| HPQ      | Hp Inc.                                     |  14664    |      1119    | 7.63 %       |      909    |
| IBM      | International Business Machines Corporation |  14107    |     -3196    | -            |      721    |
| CSCO     | Cisco Systems Inc                           |  13632    |      2670    | 19.59 %      |      213    |
| NCR      | Ncr Corp                                    |   1972    |        69    | 3.5 %        |       81    |
| FFIV     | F5 Inc                                      |    700.03 |        89.35 | 12.76 %      |      218.82 |
| PTC      | Ptc Inc                                     |    507.93 |       106.84 | 21.03 %      |      -50.16 |
| CGNT     | Cognyte Software Ltd                        |    474.04 |       -10.26 | -            |       43.56 |
| UIS      | Unisys Corp                                 |    461.2  |       -39.9  | -            |      -24.3  |
| NTNX     | Nutanix Inc.                                |    385.54 |      -150.99 | -            |       16.08 |
| ZS       | Zscaler Inc.                                |    372.17 |      -129.99 | -            |      418.32 |
| PAYC     | Paycom Software Inc                         |    334.17 |        52.15 | 15.61 %      |    -1618.67 |
| CDAY     | Ceridian Hcm Holding Inc                    |    315.6  |       -21    | -            |     -959.6  |
| TUYA     | Tuya Inc                                    |    302.08 |      -175.42 | -            |      805.62 |
| NET      | Cloudflare Inc                              |    253.86 |       -42.55 | -            |       -4.76 |
| PCTY     | Paylocity Holding Corporation               |    253.28 |        30.35 | 11.98 %      |    -1836.35 |
| ZI       | Zoominfo Technologies Inc                   |    251.7  |        17.9  | 7.11 %       |       53.9  |
| PATH     | Uipath Inc.                                 |    242.22 |      -120.38 | -            |      -71.86 |
| BL       | Blackline Inc                               |    134.27 |       -18.99 | -            |      -17.95 |
| WK       | Workiva Inc                                 |    132.85 |       -29.69 | -            |       80.07 |
| PYCR     | Paycor Hcm Inc                              |    118.3  |       -29.05 | -            |     -915.72 |
| APPN     | Appian Corporation                          |    117.88 |       -44    | -            |      -25.24 |
| AVID     | Avid Technology Inc                         |    102.99 |        12.02 | 11.67 %      |      -13.12 |
| GTLB     | Gitlab Inc.                                 |    101.04 |       -61.5  | -            |     -476.73 |
| ATTU     | Attunity Ltd                                |     86.25 |         5.96 | 6.91 %       |      -17.32 |
| ESMT     | Engagesmart Inc                             |     78.8  |         6.77 | 8.59 %       |       19.25 |
| FROG     | Jfrog Ltd                                   |     71.99 |       -23.55 | -            |       -1.24 |
| DWCH     | Datawatch Corp                              |     11.59 |        -2.27 | -            |        0.15 |
| GSB      | Globalscape Inc                             |     10.03 |         3.5  | 34.9 %       |        3.17 |
| STVVY    | China Digital Tv Holding Co., Ltd.          |      6.2  |        -4.1  | -            |      -92.87 |
| FALC     | Falconstor Software Inc                     |      3.06 |         0.6  | 19.64 %      |       -0.14 |
| ZRFY     | Zerify Inc                                  |      0.02 |        -1.25 | -            |       -0.32 |

### ROT

`openbb.stocks.fa.rot` returns a table with the number of analyst recommendations for each score, updated monthly.

```python
gtlb_rot = openbb.stocks.fa.rot('GTLB')

gtlb_rot
```

|    |   buy |   hold | period     |   sell |   strongBuy |   strongSell | symbol   |
|---:|------:|-------:|:-----------|-------:|------------:|-------------:|:---------|
|  0 |    14 |      2 | 2022-11-01 |      0 |           4 |            0 | GTLB     |
|  1 |    14 |      2 | 2022-10-01 |      0 |           4 |            0 | GTLB     |
|  2 |    13 |      1 | 2022-09-01 |      0 |           4 |            0 | GTLB     |
|  3 |    13 |      1 | 2022-08-01 |      0 |           4 |            0 | GTLB     |

### Analyst

Returns a DataFrame of analyst price targets, and their coverage history.

```python
gtlb_pt = openbb.stocks.fa.analyst('GTLB')

gtlb_pt
```

| date       | category   | analyst          | rating                |   target |   target_from |   target_to |
|:-----------|:-----------|:-----------------|:----------------------|---------:|--------------:|------------:|
| 2022-09-22 | Initiated  | MoffettNathanson | Buy                   |      104 |           nan |         nan |
| 2022-09-01 | Downgrade  | JP Morgan        | Overweight -> Neutral |       63 |           nan |         nan |
| 2022-07-07 | Initiated  | Needham          | Buy                   |       70 |           nan |         nan |
| 2022-06-27 | Upgrade    | Goldman          | Neutral -> Buy        |      nan |            69 |          80 |
| 2022-06-09 | Initiated  | Scotiabank       | Sector Outperform     |       62 |           nan |         nan |

### SEC

`openbb.stocks.fa.sec` gets a DataFrame of the recent SEC filings submitted by the company and a link to view each one.

```python
gtlb_sec = openbb.stocks.fa.sec('GTLB')

gtlb_sec
```

| Filing Date   | Document Date   | Type     | Category                | Amended   | Link                                                                                  |
|:--------------|:----------------|:---------|:------------------------|:----------|:--------------------------------------------------------------------------------------|
| 09/07/2022    | 07/31/2022      | 10-Q     | Quarterly Reports       |           | https://www.marketwatch.com/investing/stock/gtlb/financials/secfilings?docid=16067993 |
| 09/06/2022    | 09/06/2022      | 8-K      | Special Events          |           | https://www.marketwatch.com/investing/stock/gtlb/financials/secfilings?docid=16066715 |
| 07/08/2022    | N/A             | SC 13G/A | Institutional Ownership | *         | https://www.marketwatch.com/investing/stock/gtlb/financials/secfilings?docid=15940277 |
| 06/23/2022    | 06/17/2022      | 8-K      | Special Events          |           | https://www.marketwatch.com/investing/stock/gtlb/financials/secfilings?docid=15906497 |
| 06/07/2022    | 04/30/2022      | 10-Q     | Quarterly Reports       |           | https://www.marketwatch.com/investing/stock/gtlb/financials/secfilings?docid=15877097 |
| 06/06/2022    | 06/06/2022      | 8-K      | Special Events          |           | https://www.marketwatch.com/investing/stock/gtlb/financials/secfilings?docid=15875737 |
| 05/13/2022    | N/A             | SC 13G   | Institutional Ownership |           | https://www.marketwatch.com/investing/stock/gtlb/financials/secfilings?docid=15814288 |
| 05/05/2022    | 01/31/2022      | DEF 14A  | Proxy Statement         |           | https://www.marketwatch.com/investing/stock/gtlb/financials/secfilings?docid=15792144 |
| 04/11/2022    | N/A             | SC 13G/A | Institutional Ownership | *         | https://www.marketwatch.com/investing/stock/gtlb/financials/secfilings?docid=15724191 |
| 04/11/2022    | N/A             | S-8      | Registration Statement  |           | https://www.marketwatch.com/investing/stock/gtlb/financials/secfilings?docid=15723998 |
| 04/08/2022    | 01/31/2022      | 10-K     | Annual Reports          |           | https://www.marketwatch.com/investing/stock/gtlb/financials/secfilings?docid=15723401 |
continued...

### EST

`openbb.stocks.fa.est` returns a Tuple with forward earnings and revenue estimates.

```python
year_estimates_df,qtr_earnings_df,qtr_revenue_df = openbb.stocks.fa.est('GTLB')

year_estimates_df
```

| YEARLY ESTIMATES               | 2022   | 2023   | 2024   | 2025    | 2026      | 2027   |
|:-------------------------------|:-------|:-------|:-------|:--------|:----------|:-------|
| Revenue                        | 245    | 414    | 586    | 814     | 1,044     | 1,305  |
| Dividend                       | 0.00   | -      | 0.00   | 0.00    | -         | -      |
| Dividend Yield (in %)          | -      | -      | -      | -       | -         | -      |
| EPS                            | -1.40  | -0.65  | -0.65  | -0.35   | -0.02     | 0.27   |
| P/E Ratio                      | -28.07 | -60.24 | -60.97 | -113.57 | -1,970.00 | 145.93 |
| EBIT                           | -103   | -109   | -101   | -62     | -17       | 30     |
| EBITDA                         | -99    | -123   | -124   | -51     | -10       | 40     |
| Net Profit                     | -152   | -151   | -177   | -100    | -4        | 50     |
| Net Profit Adjusted            | -114   | -98    | -99    | -55     | -4        | 51     |
| Pre-Tax Profit                 | -121   | -100   | -96    | -53     | -4        | 48     |
| Net Profit (Adjusted)          | -134   | -198   | -218   | -70     | -         | -      |
| EPS (Non-GAAP) ex. SOE         | -1.55  | -0.65  | -0.63  | -0.48   | -         | -      |
| EPS (GAAP)                     | -1.90  | -1.34  | -1.56  | -1.20   | -         | -      |
| Gross Income                   | 217    | 368    | 509    | 692     | 911       | 1,134  |
| Cash Flow from Investing       | -100   | -486   | -9     | -12     | -14       | -17    |
| Cash Flow from Operations      | -75    | -67    | -31    | 28      | 120       | 251    |
| Cash Flow from Financing       | 561    | 80     | 8      | 0       | -         | -      |
| Cash Flow per Share            | -1.06  | -0.52  | -0.23  | -0.08   | -         | -      |
| Free Cash Flow                 | -73    | -77    | -39    | 37      | 106       | 234    |
| Free Cash Flow per Share       | -0.96  | -0.56  | -0.22  | -       | -         | -      |
| Book Value per Share           | 7.16   | 5.11   | 4.52   | 4.10    | -         | -      |
| Net Debt                       | -798   | -403   | -372   | -460    | -         | -      |
| Research & Development Exp.    | 90     | 120    | 158    | 208     | 244       | 292    |
| Capital Expenditure            | 0      | 6      | 8      | 13      | -         | -      |
| Selling, General & Admin. Exp. | 230    | 361    | 473    | 509     | -         | -      |
| Shareholder’s Equity           | 831    | 729    | 649    | 611     | 589       | 639    |
| Total Assets                   | 1,093  | 1,105  | 1,159  | 1,397   | 1,658     | 2,027  |
