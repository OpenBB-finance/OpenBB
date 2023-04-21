---
title: Fixed Income
keywords: [fixed income, government bonds, bonds, corporate bonds, fixed, income, interest, rates, inflation, central bank, reference, rates, sofr, sonia, ester, estr]
description: The Fixed Income menu is the high-level menu for the Fixed Income asset class. It contains reference rates, central bank rates, government bonds, yield curves, corporate bond benchmarks and more.
---

The Fixed Income module is the high-level menu for the Fixed Income asset class. It contains reference rates (ESTER, SOFR, SONIA and Ameribor), central bank rates (FRED, FOMC projections and ECB key interest rates), government bonds (treasury rates for any country, us-specific rates, yield curves), corporate bonds (ICE BofA Corporate Indices, Moody's AAA and BAA Corporate Indices, Commercial Paper, Spot Rates and HQM Corporate Yield Curve) and spread (ICE BofA spreads, constant maturity spreads, and federal funds rate)

## How to Use

​The examples provided below will assume that the following import block is included at the beginning of the Python script or Notebook file:
​

```python
from openbb_terminal.sdk import openbb
import pandas as pd
```

​Below is a brief description of each function within the Fixed Income module:

|Path |Type |Description |
|:---------|:---------:|------------------------------:|
|openbb.fixedincome.ameribor |Function | Obtain data for American Interbank Offered Rate (AMERIBOR) |
|openbb.fixedincome.cp | Function | Obtain Commercial Paper data |
|openbb.fixedincome.dwpcr |Function | Obtain data for the Discount Window Primary Credit Rate |
|openbb.fixedincome.ecb |Function | Obtain data for ECB interest rates |
|openbb.fixedincome.ecbycrv |Function | Gets euro area yield curve data from ECB |
|openbb.fixedincome.estr |Function | Obtain data for Euro Short-Term Rate (ESTR) |
|openbb.fixedincome.fed |Function | Obtain data for Effective Federal Funds Rate |
|openbb.fixedincome.ffrmc |Function | Get data for Selected Treasury Constant Maturity Minus Federal Funds Rate |
|openbb.fixedincome.hqm |Function | Obtain the HQM yield curve |
|openbb.fixedincome.icebofa |Function | Get data for ICE BofA US Corporate Bond Indices |
|openbb.fixedincome.icespread |Function | Get data for ICE BofA US Corporate Bond Spreads |
|openbb.fixedincome.iorb |Function | Obtain data for Interest Rate on Reserve Balances. |
|openbb.fixedincome.moody |Function | Get data for Moody Corporate Bond Index |
|openbb.fixedincome.projection |Function | Obtain data for the Federal Reserve's projection of the federal funds rate |
|openbb.fixedincome.sofr |Function | Obtain data for Secured Overnight Financing Rate (SOFR)|
|openbb.fixedincome.sonia |Function | Obtain data for Sterling Overnight Index Average (SONIA) |
|openbb.fixedincome.spot |Function | Obtain HQM spot rate data |
|openbb.fixedincome.tbffr |Function | Get data for Selected Treasury Bill Minus Federal Funds Rate |
|openbb.fixedincome.tmc |Function | Get data for 10-Year Treasury Constant Maturity Minus Selected Treasury Constant Maturity |
|openbb.fixedincome.treasury |Function | Obtain 3-month or 10-year treasury rates for any country |
|openbb.fixedincome.usrates |Function | Plot various treasury rates from the United States |
|openbb.fixedincome.ycrv |Function | Gets yield curve data from FRED |

Alternatively you can print the contents of the Fixed Income SDK with:
​
```python
help(openbb.fixedincome)
```

## Examples
Starting off by calling some reference rates, these can be either `estr`, `sofr`, `sonia` or `ameribor`. For example the 1 year term structure of Ameribor is plotted with `openbb.fixedincome.ameribor('1_year_term_structure')` as shown below, showing only the last 10 periods in this example:


|                     |       AMERIBOR|
|:--------------------|--------:|
| 2023-02-12 00:00:00 | 5.13275 |
| 2023-02-13 00:00:00 | 5.15549 |
| 2023-02-14 00:00:00 | 5.22839 |
| 2023-02-15 00:00:00 | 5.20813 |
| 2023-02-16 00:00:00 | 5.20832 |
| 2023-02-17 00:00:00 | 5.2491  |
| 2023-02-19 00:00:00 | 5.2491  |
| 2023-02-20 00:00:00 | 5.2491  |
| 2023-02-21 00:00:00 | 5.32425 |
| 2023-02-22 00:00:00 | 5.32988 |


The two most prominent central bank rates, those of the Federal Reserve and the European Central Bank can be obtained with `openbb.fixedincome.fed` and `openbb.fixedincome.ecb` respectively. For instance `openbb.fixedincome.fed` shows the monthly Federal Funds Rate, showing only the last 10 periods in this example:

|                     |    FED |
|:--------------------|-----:|
| 2022-04-01 00:00:00 | 0.33 |
| 2022-05-01 00:00:00 | 0.77 |
| 2022-06-01 00:00:00 | 1.21 |
| 2022-07-01 00:00:00 | 1.68 |
| 2022-08-01 00:00:00 | 2.33 |
| 2022-09-01 00:00:00 | 2.56 |
| 2022-10-01 00:00:00 | 3.08 |
| 2022-11-01 00:00:00 | 3.78 |
| 2022-12-01 00:00:00 | 4.1  |
| 2023-01-01 00:00:00 | 4.33 |

This can be accompanied with the projections, officially published by the FOMC. Here the long run expectations are plotted, which also backtracks several years, with `openbb.fixedincome.projection(long_run=True)`, showing only the last 5 periods in this example:

|            |   Range High |   Central tendency High |   Median |   Range Midpoint |   Central tendency Midpoint |   Range Low |   Central tendency Low |
|:-----------|-------------:|------------------------:|---------:|-----------------:|----------------------------:|------------:|-----------------------:|
| 2021-12-15 |          3   |                     2.5 |      2.5 |             2.5  |                         2.4 |         2   |                    2.3 |
| 2022-03-16 |          3   |                     2.5 |      2.4 |             2.5  |                         2.4 |         2   |                    2.3 |
| 2022-06-15 |          3   |                     2.5 |      2.5 |             2.5  |                         2.4 |         2   |                    2.3 |
| 2022-09-21 |          3   |                     2.5 |      2.5 |             2.65 |                         2.4 |         2.3 |                    2.3 |
| 2022-12-14 |          3.3 |                     2.5 |      2.5 |             2.8  |                         2.4 |         2.3 |                    2.3 |

The European Central Bank rates can be shown with `openbb.fixedincome.ecb`. The ECB publishes three different rates that can be shown separately with `openbb.fixedincome.ecb('deposit)` for example or plotted together with `openbb.fixedincome.ecb` as shown below, showing only the last 10 periods in this example:

|            |   Deposit |   Lending |   Refinancing |
|:-----------|----------:|----------:|--------------:|
| 2023-02-14 |       2.5 |      3.25 |             3 |
| 2023-02-15 |       2.5 |      3.25 |             3 |
| 2023-02-16 |       2.5 |      3.25 |             3 |
| 2023-02-17 |       2.5 |      3.25 |             3 |
| 2023-02-18 |       2.5 |      3.25 |             3 |
| 2023-02-19 |       2.5 |      3.25 |             3 |
| 2023-02-20 |       2.5 |      3.25 |             3 |
| 2023-02-21 |       2.5 |      3.25 |             3 |
| 2023-02-22 |       2.5 |      3.25 |             3 |
| 2023-02-23 |       2.5 |      3.25 |             3 |

In terms of government bonds, any combination of short term (3 month) and long term (10 year) government bonds for any country can be plotted with `openbb.fixedincome.treasury` for example `openbb.fixedincome.treasury(short_term=['canada', 'united_states'], long_term=['canada', 'united_states'])` as shown below, showing only the last 10 periods in this example:

|            |   canada (3 month) |   united_states (3 month) |   canada (10 year) |   united_states (10 year) |
|:-----------|-------------------:|--------------------------:|-------------------:|--------------------------:|
| 2022-04-01 |            2.704   |                      2.75 |            1.34664 |                      0.91 |
| 2022-05-01 |            2.91857 |                      2.9  |            1.78189 |                      1.33 |
| 2022-06-01 |            3.31545 |                      3.14 |            2.24735 |                      1.87 |
| 2022-07-01 |            3.04316 |                      2.9  |            3.01411 |                      2.5  |
| 2022-08-01 |            2.85909 |                      2.9  |            3.38221 |                      2.76 |
| 2022-09-01 |            3.1479  |                      3.52 |            3.79193 |                      3.21 |
| 2022-10-01 |            3.38053 |                      3.98 |            4.23083 |                      3.85 |
| 2022-11-01 |            3.16619 |                      3.89 |            4.37634 |                      4.46 |
| 2022-12-01 |            2.9415  |                      3.62 |            4.55302 |                      4.51 |
| 2023-01-01 |            2.93762 |                      3.53 |            4.7638  |                      4.61 |


For both the United States and the Eurozone, it is possible to see the current government bond yield curve. For the Eurozone, it is an aggregation of countries that match a specific credit rating, by default AAA, as shown with `openbb.fixedincome.ecbycrv`.

|    |   Maturity |    Rate |
|---:|-----------:|--------:|
|  0 |       0.25 | 2.61446 |
|  1 |       0.5  | 2.86441 |
|  2 |       1    | 2.97514 |
|  3 |       2    | 2.82012 |
|  4 |       3    | 2.68811 |
|  5 |       5    | 2.58939 |
|  6 |       7    | 2.57123 |
|  7 |      10    | 2.57545 |
|  8 |      20    | 2.55717 |
|  9 |      30    | 2.45648 |

When it comes to Corporate Bonds, the major indices are included. These are the ICE BofA indices and the Moody's Aaa and Baa indices. Based on a query, specific benchmarks can be found. For example a collection of indices matching a variety of bond maturities with `openbb.fixedincome.icebofa(category='duration')`, showing only the last 5 periods in this example:

|            |   ICE BofA 1-3 Year US Corporate Index Effective Yield |   ICE BofA 3-5 Year US Corporate Index Effective Yield |   ICE BofA 5-7 Year US Corporate Index Effective Yield |   ICE BofA 7-10 Year US Corporate Index Effective Yield |   ICE BofA 10-15 Year US Corporate Index Effective Yield |   ICE BofA 15+ Year US Corporate Index Effective Yield |
|:-----------|-------------------------------------------------------:|-------------------------------------------------------:|-------------------------------------------------------:|--------------------------------------------------------:|---------------------------------------------------------:|-------------------------------------------------------:|
| 2023-02-09 |                                                   5.22 |                                                   5.04 |                                                   5.12 |                                                    5.2  |                                                     5.34 |                                                   5.32 |
| 2023-02-10 |                                                   5.27 |                                                   5.11 |                                                   5.21 |                                                    5.3  |                                                     5.43 |                                                   5.41 |
| 2023-02-13 |                                                   5.28 |                                                   5.14 |                                                   5.2  |                                                    5.28 |                                                     5.41 |                                                   5.38 |
| 2023-02-14 |                                                   5.36 |                                                   5.23 |                                                   5.28 |                                                    5.32 |                                                     5.44 |                                                   5.39 |
| 2023-02-15 |                                                   5.36 |                                                   5.26 |                                                   5.31 |                                                    5.36 |                                                     5.48 |                                                   5.43 |
| 2023-02-16 |                                                   5.38 |                                                   5.29 |                                                   5.35 |                                                    5.42 |                                                     5.54 |                                                   5.52 |
| 2023-02-17 |                                                   5.37 |                                                   5.26 |                                                   5.33 |                                                    5.42 |                                                     5.53 |                                                   5.5  |
| 2023-02-20 |                                                   5.39 |                                                   5.27 |                                                   5.33 |                                                    5.42 |                                                     5.53 |                                                   5.5  |
| 2023-02-21 |                                                   5.49 |                                                   5.41 |                                                   5.49 |                                                    5.58 |                                                     5.68 |                                                   5.63 |
| 2023-02-22 |                                                   5.49 |                                                   5.4  |                                                   5.48 |                                                    5.56 |                                                     5.65 |                                                   5.59 |

The Moody's Aaa is often referred to as a great alternative to the federal ten-year Treasury bill as an indicator for interest rates and can be plotted with `openbb.fixedincome.moody`, showing only the last 5 periods in this example:

|            |   aaa_index |
|:-----------|------------:|
| 2023-02-15 |        4.59 |
| 2023-02-16 |        4.64 |
| 2023-02-17 |        4.65 |
| 2023-02-21 |        4.76 |
| 2023-02-22 |        4.71 |

Next to that, there are spot rates available for the High Quality Market (HQM) ranging from 1 year to a 100 years through `openbb.fixedincome.spot`. With this, it is also possible to plot the yield curve with `openbb.fixedincome.hqm` for any date in the past. For example `openbb.fixedincome.hqm(date='2020-01-01')` as shown below:

|   Maturity |   spot |
|-----------:|-------:|
|        0.5 |   1.76 |
|        1   |   1.8  |
|        2   |   1.86 |
|        3   |   1.91 |
|        5   |   2.07 |
|        7   |   2.35 |
|       10   |   2.79 |
|       20   |   3.35 |
|       30   |   3.48 |
|       50   |   3.6  |
|       75   |   3.65 |
|      100   |   3.68 |

Furthermore, it is possible to see spreads between a variety of assets. For example the Emerging Markets spread can be shown with `openbb.fixedincome.icespread(category='all', area='emea')`. This is based on the spot treasury curve. Showing only the last 5 periods in this example:

|            |   ICE BofA EMEA Emerging Markets Corporate Plus Index Option-Adjusted Spread |
|:-----------|-----------------------------------------------------------------------------:|
| 2023-02-16 |                                                                         2.66 |
| 2023-02-17 |                                                                         2.75 |
| 2023-02-20 |                                                                         2.75 |
| 2023-02-21 |                                                                         2.74 |
| 2023-02-22 |                                                                         2.77 |

For both `openbb.fixedincome.icebofa` and `openbb.fixedincome.icespread` it is possible to see all the options with `options`. Find an example for `openbb.fixedincome.icespread(options=True)` below.


|     | Type   | Category   | Area          | Grade          | Title                                                                                                 |
|----:|:-------|:-----------|:--------------|:---------------|:------------------------------------------------------------------------------------------------------|
|   2 | spread | duration   | us            | non_sovereign  | ICE BofA 1-3 Year US Corporate Index Option-Adjusted Spread                                           |
|   6 | spread | duration   | us            | non_sovereign  | ICE BofA 3-5 Year US Corporate Index Option-Adjusted Spread                                           |
|  10 | spread | duration   | us            | non_sovereign  | ICE BofA 5-7 Year US Corporate Index Option-Adjusted Spread                                           |
|  14 | spread | duration   | us            | non_sovereign  | ICE BofA 7-10 Year US Corporate Index Option-Adjusted Spread                                          |
|  18 | spread | duration   | us            | non_sovereign  | ICE BofA 10-15 Year US Corporate Index Option-Adjusted Spread                                         |
|  22 | spread | duration   | us            | non_sovereign  | ICE BofA 15+ Year US Corporate Index Option-Adjusted Spread                                           |
|  26 | spread | all        | us            | non_sovereign  | ICE BofA US Corporate Index Option-Adjusted Spread                                                    |
|  30 | spread | usd        | us            | high_yield     | ICE BofA US High Yield Index Option-Adjusted Spread                                                   |
|  34 | spread | eur        | eu            | high_yield     | ICE BofA Euro High Yield Index Option-Adjusted Spread                                                 |
|  38 | spread | all        | ex_g10        | non_sovereign  | ICE BofA Emerging Markets Corporate Plus Index Option-Adjusted Spread                                 |
|  42 | spread | all        | ex_g10        | private_sector | ICE BofA Private Sector Financial Emerging Markets Corporate Plus Index Option-Adjusted Spread        |
|  46 | spread | usd        | ex_g10        | non_sovereign  | ICE BofA US Emerging Markets Corporate Plus Index Option-Adjusted Spread                              |
|  50 | spread | eur        | ex_g10        | non_sovereign  | ICE BofA Euro Emerging Markets Corporate Plus Index Option-Adjusted Spread                            |
|  54 | spread | usd        | ex_g10        | non_sovereign  | ICE BofA US Emerging Markets Liquid Corporate Plus Index Option-Adjusted Spread                       |
|  58 | spread | usd        | ex_g10        | non_financial  | ICE BofA Non-Financial US Emerging Markets Liquid Corporate Plus Index Option-Adjusted Spread         |
|  62 | spread | usd        | ex_g10        | public_sector  | ICE BofA Public Sector Issuers US Emerging Markets Liquid Corporate Plus Index Option-Adjusted Spread |
|  66 | spread | all        | emea          | non_sovereign  | ICE BofA EMEA Emerging Markets Corporate Plus Index Option-Adjusted Spread                            |
|  70 | spread | usd        | emea          | non_sovereign  | ICE BofA EMEA US Emerging Markets Liquid Corporate Plus Index Option-Adjusted Spread                  |
|  74 | spread | all        | asia          | non_sovereign  | ICE BofA Asia Emerging Markets Corporate Plus Index Option-Adjusted Spread                            |
|  78 | spread | usd        | asia          | non_sovereign  | ICE BofA Asia US Emerging Markets Liquid Corporate Plus Index Option-Adjusted Spread                  |
|  82 | spread | all        | latin_america | non_sovereign  | ICE BofA Latin America Emerging Markets Corporate Plus Index Option-Adjusted Spread                   |
|  86 | spread | usd        | latin_america | non_sovereign  | ICE BofA Latin America US Emerging Markets Liquid Corporate Plus Index Option-Adjusted Spread         |
|  90 | spread | all        | ex_g10        | aaa            | ICE BofA AAA-A Emerging Markets Corporate Plus Index Option-Adjusted Spread                           |
|  94 | spread | usd        | ex_g10        | aaa            | ICE BofA AAA-A US Emerging Markets Liquid Corporate Plus Index Option-Adjusted Spread                 |
|  98 | spread | all        | ex_g10        | high_grade     | ICE BofA High Grade Emerging Markets Corporate Plus Index Option-Adjusted Spread                      |
| 102 | spread | all        | ex_g10        | bbb            | ICE BofA BBB Emerging Markets Corporate Plus Index Option-Adjusted Spread                             |
| 106 | spread | usd        | ex_g10        | bbb            | ICE BofA BBB US Emerging Markets Liquid Corporate Plus Index Option-Adjusted Spread                   |
| 110 | spread | all        | ex_g10        | crossover      | ICE BofA Crossover Emerging Markets Corporate Plus Index Option-Adjusted Spread                       |
| 114 | spread | all        | ex_g10        | bb             | ICE BofA BB Emerging Markets Corporate Plus Index Option-Adjusted Spread                              |
| 118 | spread | all        | ex_g10        | high_yield     | ICE BofA High Yield Emerging Markets Corporate Plus Index Option-Adjusted Spread                      |
| 122 | spread | all        | ex_g10        | b              | ICE BofA B & Lower Emerging Markets Corporate Plus Index Option-Adjusted Spread                       |
| 126 | spread | usd        | us            | aaa            | ICE BofA AAA US Corporate Index Option-Adjusted Spread                                                |
| 130 | spread | usd        | us            | aa             | ICE BofA AA US Corporate Index Option-Adjusted Spread                                                 |
| 134 | spread | usd        | us            | a              | ICE BofA Single-A US Corporate Index Option-Adjusted Spread                                           |
| 138 | spread | usd        | us            | bbb            | ICE BofA BBB US Corporate Index Option-Adjusted Spread                                                |
| 142 | spread | usd        | us            | bb             | ICE BofA BB US High Yield Index Option-Adjusted Spread                                                |
| 146 | spread | usd        | us            | b              | ICE BofA Single-B US High Yield Index Option-Adjusted Spread                                          |
| 150 | spread | usd        | us            | ccc            | ICE BofA CCC & Lower US High Yield Index Option-Adjusted Spread                                       |
