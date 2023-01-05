---
title: Fundamental Analysis
---

The FA module provides programmatic access to the commands from within the OpenBB Terminal. To get the most out of these functions, we recommend obtaining API keys from:

- AlphaVantage
- EODHD (premium subscribers only)
- Financial Modeling Prep
- Polygon

View [this page](https://docs.openbb.co/terminal/guides/advanced/api-keys) for a list of all API sources used across the platform. 

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

Alteratively the contents of the module can be printed with:

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
