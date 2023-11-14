---
title: Fundamental Analysis
description: Documentation for the FA module in the OpenBB Terminal - providing programmatic
  access to financial analysis commands. Includes a comprehensive list of functionalities,
  such as analysis of SEC disclosure statements, company balance sheet information,
  earnings data, key metrics over time, estimate market cap and more. Detailed information
  for each function and plenty of examples demonstrating their usage.
keywords:
- FA module
- API keys
- AlphaVantage
- EODHD
- Financial Modeling Prep
- Polygon
- SEC disclosure statements
- balance sheet
- earnings data
- company metrics
- market cap
- Jupyter Lab
- VS Code
- financial statement ratios
- EPS estimates
- cash flow
- income statements
- key statistics
- stock suppliers
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Fundamental Analysis - Stocks - Intros - Usage | OpenBB SDK Docs" />


The FA module provides programmatic access to the commands from within the OpenBB Terminal. To get the most out of these functions, we recommend obtaining API keys from:

- AlphaVantage
- EODHD (premium subscribers only)
- Financial Modeling Prep
- Polygon

View [this page](/sdk/usage/api-keys) for a list of all API sources used across the platform.

## The FA Module

A brief description below highlights the properties of the `fa` module.

| Path                          |                                      Description |
| :---------------------------- | -----------------------------------------------: |
| openbb.stocks.fa.analysis     |            Analysis of SEC disclosure statements |
| openbb.stocks.fa.balance      |                            Company balance sheet |
| openbb.stocks.fa.cal          |                  Calendar earnings and estimates |
| openbb.stocks.fa.cash         |                    Company cash flows statements |
| openbb.stocks.fa.customer     |   Lists other public companies who are customers |
| openbb.stocks.fa.dcfc         |               Historical DCF Values for a ticker |
| openbb.stocks.fa.divs         |               Historical Dividends for a company |
| openbb.stocks.fa.divs_chart   |                             A chart for `divs` |
| openbb.stocks.fa.dupont       |                                    DuPont ratios |
| openbb.stocks.fa.earnings     |                            Earnings data and EPS |
| openbb.stocks.fa.enterprise   |                         Company enterprise value |
| openbb.stocks.fa.epsfc        |                            Forward EPS estimates |
| openbb.stocks.fa.fama_coe     |             Fama/French value for cost of equity |
| openbb.stocks.fa.fraud        |                                 Key fraud ratios |
| openbb.stocks.fa.growth       |             Growth of financial statement ratios |
| openbb.stocks.fa.income       |                        Company income statements |
| openbb.stocks.fa.key          |                              Company Key Metrics |
| openbb.stocks.fa.metrics      |                            Key Metrics Over Time |
| openbb.stocks.fa.mgmt         |                          Company Management Team |
| openbb.stocks.fa.mktcap       |                             Estimated Market Cap |
| openbb.stocks.fa.mktcap_chart |                             Chart for `mktcap` |
| openbb.stocks.fa.overview     |                          Overview of the company |
| openbb.stocks.fa.pt           |                            Analyst price targets |
| openbb.stocks.fa.pt_chart     |                                 Chart for `pt` |
| openbb.stocks.fa.rating       | Historical buy/sell/hold ratings based on ratios |
| openbb.stocks.fa.ratios       |           Historical financial statements ratios |
| openbb.stocks.fa.revfc        |                        Forward revenue estimates |
| openbb.stocks.fa.score        |               Investing Score from Warren Buffet |
| openbb.stocks.fa.shrs         |                               Major shareholders |
| openbb.stocks.fa.splits       |        Stock Splits and Reverse Splits Since IPO |
| openbb.stocks.fa.splits_chart |                               Chart for `splits` |
| openbb.stocks.fa.supplier     |   Lists other public companies who are suppliers |

This can be printed to the screen with:

```python
help(openbb.stocks.fa)
```

Parameters for each function are displayed using the same syntax.

```python
help(openbb.stocks.fa.balance)

Signature:
openbb.stocks.fa.balance(
    symbol: str,
    quarterly: bool = False,
    ratios: bool = False,
    source: str = 'YahooFinance',
    limit: int = 10,
) -> pandas.core.frame.DataFrame
Call signature: openbb.stocks.fa.balance(*args: Any, **kwargs: Any) -> Any
Type:           get_balance_sheet
String form:    <openbb_terminal.stocks.fundamental_analysis.sdk_helpers.Operation object at 0x1684e8f70>
File:           ~/GitHub/OpenBBTerminal/openbb_terminal/stocks/fundamental_analysis/sdk_helpers.py
Docstring:
Get balance sheet.

Parameters
----------
symbol : str
    Symbol to get balance sheet for
source : str, optional
    Data source for balance sheet, by default "YahooFinance"
    Sources: YahooFinance, AlphaVantage, FinancialModelingPrep, Polygon, EODHD
quarterly : bool, optional
    Flag to get quarterly data
ratios : bool, optional
   Flag to return data as a percent change.
limit : int
    Number of statements to return (free tiers may be limited to 5 years)

Returns
-------
pd.DataFrame
    Dataframe of balance sheet

Examples
--------
>>> from openbb_terminal.sdk import openbb
>>> balance_sheet = openbb.stocks.fa.balance("AAPL", source="YahooFinance")

If you have a premium AlphaVantage key, you can use the quarterly flag to get quarterly statements
>>> quarterly_income_statement = openbb.stocks.fa.balance("AAPL", source="AlphaVantage", quarterly=True)
```

This information is also displayed in the contextual help window, when using Jupyter Lab or VS Code.

## Examples

The examples provided below will assume that the following import block is included at the beginning of the Python script or Notebook file:

```python
import pandas as pd
from openbb_terminal.sdk import openbb
```

### Earnings

The `openbb.stocks.fa.earnings` function returns upcoming earnings dates and estimates for EPS. There are two data sources available - YahooFinance or AlphaVantage, both of which provide historical context.

```python
openbb.stocks.fa.earnings('COST', quarterly = True)
```

| Earnings Date | EPS Estimate | Reported EPS | Surprise(%) |
| :------------ | :----------- | :----------- | :---------- |
| 2024-02-29    | -            | -            | -           |
| 2023-12-06    | -            | -            | -           |
| 2023-09-20    | -            | -            | -           |
| 2023-05-25    | 3.21         | -            | -           |
| 2023-05-25    | -            | -            | -           |
| 2023-03-02    | 3.21         | 3.3          | 0.0288      |
| 2022-12-08    | 3.11         | 3.1          | -0.00451    |
| 2022-09-22    | 4.17         | 4.2          | 0.0084      |
| 2022-05-26    | 3.03         | 3.17         | 0.0449      |
| 2022-03-03    | 2.74         | 2.92         | 0.0647      |
| 2021-12-09    | 2.64         | 2.98         | 0.12890     |

### Growth

`openbb.stocks.fa.growth` provides annualized financial ratios as growth metrics.

```python
openbb.stocks.fa.growth('COST')
```

**Note**: This returns thirty-five ratios, the table below is truncated for illustrative purposes.

|                         | 2018  | 2019   | 2020  | 2021  | 2022  |
| :---------------------- | :---- | :----- | :---- | :---- | :---- |
| Period                  | FY    | FY     | FY    | FY    | FY    |
| Revenue growth          | 0.097 | 0.079  | 0.092 | 0.175 | 0.158 |
| Gross profit growth     | 0.075 | 0.076  | 0.101 | 0.157 | 0.092 |
| Ebitgrowth              | 0.090 | -0.236 | 0.134 | 0.306 | 0.203 |
| Operating income growth | 0.090 | -0.236 | 0.134 | 0.306 | 0.203 |

### Analysis

The `openbb.stocks.fa.analysis` function scans 10K SEC filings with NLP to highlight risk factors and statements provided in the Discussion and Analysis sections.  Summarizations by, [elclect.us](https://eclect.us/)

```python
openbb.stocks.fa.analysis('COST').head(1)
```

| Group        | Good  | Sentence                                                                                                                                |
| :----------- | :---- | :-------------------------------------------------------------------------------------------------------------------------------------- |
| Risk factors | False | During 2022, our international operations, including Canada, generated 27% and 32% of our net sales and operating income, respectively. |

```python
df = openbb.stocks.fa.analysis('COST')
hp = df["Group"].str.contains('Discussion')
df[hp].head(1)
```

| Group                   | Good | Sentence                                                                                                                                                              |
| :---------------------- | :--- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Discussion and Analysis | True | Cash Flows from Operating ActivitiesNet cash provided by operating activities totaled $5,802 in the first half of 2023, compared to $3,659 in the first half of 2022. |

### Key

Use `openbb.stocks.fa.key` for a small table of key statistics.

```python
openbb.stocks.fa.key('COST')
```

|                          |           |
| :----------------------- | :-------- |
| Market capitalization    | 219.440 B |
| EBITDA                   | 9.891 B   |
| EPS                      | 13.62     |
| PE ratio                 | 36.33     |
| PEG ratio                | 3.433     |
| Price to book ratio      | 10.39     |
| Return on equity TTM     | 0.284     |
| Price to sales ratio TTM | 0.891     |
| Dividend yield           | 0.0083    |
| 50 day moving average    | 491.41    |
| Analyst target price     | 547.64    |
| Beta                     | 0.787     |

### SHRS

The top 10 mutual funds holding the stock are retrieved with:

```python
openbb.stocks.fa.shrs(symbol = 'COST', holder = 'mutualfund')
```

| Holder                                                     | Shares   | Date Reported       | Stake  | Value   |
| :--------------------------------------------------------- | :------- | :------------------ | :----- | :------ |
| Vanguard Total Stock Market Index Fund                     | 13.453 M | 2022-12-30 00:00:00 | 3.03 % | 6.591 B |
| Vanguard 500 Index Fund                                    | 10.232 M | 2022-12-30 00:00:00 | 2.31 % | 5.012 B |
| Invesco ETF Tr-Invesco QQQ Tr, Series 1 ETF                | 5.834 M  | 2023-03-30 00:00:00 | 1.32 % | 2.858 B |
| Fidelity 500 Index Fund                                    | 4.852 M  | 2023-02-27 00:00:00 | 1.09 % | 2.377 B |
| SPDR S&P 500 ETF Trust                                     | 4.804 M  | 2023-03-30 00:00:00 | 1.08 % | 2.353 B |
| iShares Core S&P 500 ETF                                   | 3.950 M  | 2023-02-27 00:00:00 | 0.89 % | 1.935 B |
| Vanguard Growth Index Fund                                 | 3.736 M  | 2022-12-30 00:00:00 | 0.84 % | 1.830 B |
| Select Sector SPDR Fund-Consumer Staples                   | 3.241 M  | 2023-02-27 00:00:00 | 0.73 % | 1.588 B |
| Vanguard Institutional Index Fund-Institutional Index Fund | 3.102 M  | 2022-12-30 00:00:00 | 0.70 % | 1.519 B |
| Vanguard Specialized-Dividend Appreciation Index Fund      | 2.804 M  | 2023-01-30 00:00:00 | 0.63 % | 1.374 B |

### Balance

Financial statement items can be displayed as their reported value or as a percent change.

```python
openbb.stocks.fa.balance(symbol = 'COST', ratios=True)
```

| Breakdown                                  | 2022-08-31 | 2021-08-31 | 2020-08-31 |
| :----------------------------------------- | ---------: | ---------: | ---------: |
| Cash and cash equivalents                  | -0.0937111 | -0.0830007 |   0.464337 |
| Other short-term investments               | -0.0774264 |  -0.107977 | -0.0301887 |
| Total cash                                 | -0.0924846 | -0.0849305 |   0.408831 |
| Net receivables                            |   0.242928 |   0.163226 | 0.00977199 |
| Inventory                                  |   0.259726 |   0.161166 |  0.0743308 |
| Other current assets                       |    0.14253 |   0.282502 | -0.0792079 |
| Total current assets                       |   0.108151 |  0.0492532 |    0.19736 |
| Gross property, plant and equipment        |  0.0532209 |  0.0815396 |   0.149114 |
| Accumulated depreciation                   |  0.0790625 |  0.0984801 |  0.0988412 |
| Net property, plant and equipment          |   0.039345 |   0.072657 |   0.177358 |
| Other long-term assets                     |    0.19787 |   0.190074 |    1.77171 |
| Total non-current assets                   |  0.0573531 |  0.0848156 |   0.251928 |
| Total assets                               |  0.0826416 |  0.0668155 |     0.2237 |
| Current debt                               |  -0.908636 |    7.41053 |  -0.944085 |
| Accounts payable                           |  0.0964492 |   0.148603 |    0.21346 |
| Accrued liabilities                        |  0.0921715 |   0.152661 |   0.147383 |
| Other current liabilities                  |   0.230213 |   0.223444 | -0.0168776 |
| Total current liabilities                  |  0.0868517 |   0.185035 |  0.0691569 |
| Long-term debt                             | -0.0310819 |  -0.109396 |   0.466432 |
| Other long-term liabilities                |   0.057971 |   0.248062 |   0.329897 |
| Total non-current liabilities              | -0.0194059 | -0.0214875 |   0.825049 |
| Total liabilities                          |  0.0565429 |   0.117744 |   0.235947 |
| Common stock                               |       -0.5 |          0 |          0 |
| Retained earnings                          |   0.335933 | -0.0941843 |   0.255508 |
| Accumulated other comprehensive income     |   0.608619 |  -0.123362 | -0.0967967 |
| Total stockholders' equity                 |   0.175245 | -0.0393787 |   0.199501 |
| Total liabilities and stockholders' equity |  0.0826416 |  0.0668155 |     0.2237 |

Cashflow and Income statements are requested in the same way.

### Cash

Get the company's cash statements.

```python
openbb.stocks.fa.cash(symbol = 'COST').tail(4)
```

| Breakdown             |        ttm | 2022-08-31 | 2021-08-31 | 2020-08-31 | 2019-08-31 |
| :-------------------- | ---------: | ---------: | ---------: | ---------: | ---------: |
| Cash at end of period | 13136000.0 | 10203000.0 | 11258000.0 | 12277000.0 |  8384000.0 |
| Operating cash flow   |  9535000.0 |  7392000.0 |  8958000.0 |  8861000.0 |  6356000.0 |
| Capital expenditure   | -4060000.0 | -3891000.0 | -3588000.0 | -2810000.0 | -2998000.0 |
| Free cash flow        |  5475000.0 |  3501000.0 |  5370000.0 |  6051000.0 |  3358000.0 |

### Income

Get the company's income statements.

```python
openbb.stocks.fa.income('COST').tail(4)
```

| Breakdown              | 2022-08-31 | 2021-08-31 | 2020-08-31 | 2019-08-31 |
| :--------------------- | :--------: | :--------: | :--------: | ---------: |
| Diluted EPS            |   13.14   |   11.27   |    9.02    |       8.26 |
| Basic average shares   | 443651.00 | 443089.00 | 442297.00 |  439755.00 |
| Diluted average shares | 444757.00 | 444346.00 | 443901.00 |  442923.00 |
| EBITDA                 | 7998000.00 | 6851000.00 | 5527000.00 | 4915000.00 |

### Supplier

`openbb.stocks.fa.supplier` will return a list of suppliers for the compnay, that are also listed US stocks.

```python
openbb.stocks.fa.supplier('COST').head(5)
```

| TICKER | Company Name            | Revenue | Net Income | Net Margin | Cash Flow |
| :----- | :---------------------- | ------: | ---------: | :--------- | --------: |
| BRKA   | Berkshire Hathaway Inc  |   78165 |      18321 | 23.44 %    |    -52307 |
| ULVR   | Unilever Plc            | 58737.3 |    7415.52 | 12.62 %    |         0 |
| COST   | Costco Wholesale Corp   |   54437 |       1364 | 2.51 %     |       653 |
| BUD    | Anheuser busch Inbev Sa |   54304 |       6114 | 11.26 %    |         0 |
| DEO    | Diageo Plc              |   22448 |       3338 | 14.87 %    |      2749 |

### EPSFC

Returns a DataFrame of forward EPS estimates consensus.

```python
openbb.stocks.fa.epsfc('COST')
```

|   fiscalyear |   consensus_mean |   change % |   analysts |   actual |   consensus_low |   consensus_high |
|-------------:|-----------------:|-----------:|-----------:|---------:|----------------:|-----------------:|
|         2022 |           13.151 |   18.6918  |         20 |    13.27 |           12.43 |            13.43 |
|         2023 |           14.5   |    9.2679  |         13 |     0    |           14.22 |            15.18 |
|         2024 |           15.801 |    8.97478 |         20 |     0    |           14.75 |            17.09 |
|         2025 |           17.337 |    9.71807 |         10 |     0    |           16.47 |            18.92 |
|         2026 |           19.332 |   11.5088  |          5 |     0    |           17.55 |            21.84 |
|         2027 |           21.408 |   10.7387  |          5 |     0    |           18.6  |            25.72 |
|         2028 |           23.625 |   10.3559  |          2 |     0    |           22.19 |            25.06 |
|         2029 |           27.2   |   15.1323  |          1 |     0    |           27.2  |            27.2  |
|         2030 |           29.6   |    8.82353 |          1 |     0    |           29.6  |            29.6  |
|         2031 |           32.05  |    8.27703 |          1 |     0    |           32.05 |            32.05 |
|         2032 |           34.87  |    8.79875 |          1 |     0    |           34.87 |            34.87 |

### SEC

`openbb.stocks.fa.sec` SEC forms filed by year and type.

```python
openbb.stocks.fa.sec('COST').head(4)
```

|Filed |Company Name |Reporting Owner |Form Type |Period |View |
|:-----------|:--------------------------|:------------|:------------|:-----------|:-----------|
|04/19/2023  |Costco Wholesale Corporation | |8-K  |04/19/2023  |https://app.quotemedia.com/data/downloadFiling...|
|04/13/2023  |Costco Wholesale Corporation | |4  |04/11/2023  |https://app.quotemedia.com/data/downloadFiling...|
|03/15/2023  |Costco Wholesale Corporation    |JELINEK W CRAIG         |4  |03/13/2022  |https://app.quotemedia.com/data/downloadFiling...|
|03/15/2023  |Costco Wholesale Corporation  |GALANTI RICHARD A         |4  |03/14/2023  |https://app.quotemedia.com/data/downloadFiling...|

### PT

`openbb.stocks.fa.pt` returns historical ratings and price targets, by firm.

```python
openbb.stocks.fa.pt('COST').tail(10)
```

| Date        | Company                | Rating   |   Price Target |
|:------------|:-----------------------|:---------|---------------:|
| 2023-02-08  | Barclays Capital       | HOLD     |            510 |
| 2023-02-27  | Telsey Advisory Group  | BUY      |            580 |
| 2023-03-03  | Baird Patrick & Co     | BUY      |            535 |
| 2023-03-03  | Telsey Advisory Group  | BUY      |            540 |
| 2023-03-03  | Morgan Stanley         | BUY      |            520 |
| 2023-03-07  | Northcoast             | BUY      |            560 |
| 2023-03-28  | Telsey Advisory Group  | BUY      |            540 |
| 2023-04-06  | Telsey Advisory Group  | BUY      |            540 |
| 2023-04-06  | Oppenheimer & Co. Inc. | BUY      |            550 |
| 2023-05-01  | Telsey Advisory Group  | BUY      |            540 |
