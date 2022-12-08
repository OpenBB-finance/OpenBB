---
title: Stocks Screener
---

The Stocks Screener module imports the same screener found in the OpenBB Terminal, and adds advanced scripting capabilities in the SDK layer. The screener utilizes presets (.ini files) to scan for stocks meeting the criteria defined. User-generated files are kept in the `OpenBBUserData` folder under, `~/OpenBBUserData/presets/stocks/screener/`. There are also presets included within the cloned repo folder: 

`path_to_git_clone/OpenBBTerminal/openbb_terminal/stocks/screener/presets`

For convenience, they are supplied here as a ZIP file, [stocks_screener_preset.zip](https://github.com/OpenBB-finance/OpenBBTerminal/files/10127462/stocks_screener_preset.zip).

This screener can find stocks on three exchanges:

- AMEX
- NASDAQ
- NYSE

The data returned is grouped into five categories:

- Overview
- Ownership
- Performance
- Technical
- Valuation

## How to Use

### Template.ini

This file is for seeing all possible arguments and parameters for the screener. Reference this file (included in the ZIP file above) for the master list of settings. There are four categories of parameters to set. Without any parameters, a screener preset file must contain the following at a minimum:

```console
# Author of preset: 
# Description: 

[General]

[Descriptive]

[Fundamental]

[Technical]
```

Parameters should be added as required, and they all have pre-defined values; for example, Price/Free Cash Flow:

```console
# Any, Low (<15), High (>50), Under 5, Under 10, Under 15, Under 20, Under 25, Under 30, Under 35, Under 40, Under 45, Under 50, Under 60, Under 70, Under 80, Under 90, Under 100, Over 5, Over 10, Over 15, Over 20, Over 25, Over 30, Over 35, Over 40, Over 45, Over 50, Over 60, Over 70, Over 80, Over 90, Over 100

Price/Free Cash Flow = Any
```

## Examples

To make a screener with only a few filters, it should look something like this:

```console
# Author of preset: OpenBB
# Description: SDK Demo Screener

[General]
Order = Relative Volume
Signal = Major News

[Descriptive]
Average Volume = Over 500K
Price = Over $5

[Fundamental]
Price/Free Cash Flow = Low (<15)

[Technical]
Beta = Under 1
```

Copy the block above to a new text file in any editor, and save the file to the OpenBBUserData folder, naming it something like, `sdk_guide_preset.ini`. Declaring the path to the preset file, when located in the OpenBBUserData folder, is not required. The kernel must be restarted in order for the file to be recalled this way; however, changes to the preset itself will be reflected without a restart. 

**This preset file has been included in the ZIP file at the top of the page.**

It is a good idea to test choices made before making it too complicated. Start with a handful of filters and modify, or add, them one-at-a-time. Let's pass what we have so far through the screener with `performance` selected as the `data_type`.

### Performance

```python
openbb.stocks.screener.screener_data(preset_loaded='sdk_guide_preset.ini', data_type = 'performance', limit = 100)
```

|    | Ticker   |   Perf Week |   Perf Month |   Perf Quart |   Perf Half |   Perf Year |   Perf YTD |   Volatility W |   Volatility M |   Recom |    Avg Volume |   Rel Volume |   Price |   Change |           Volume |
|---:|:---------|------------:|-------------:|-------------:|------------:|------------:|-----------:|---------------:|---------------:|--------:|--------------:|-------------:|--------:|---------:|-----------------:|
|  0 | GEO      |      0.1389 |       0.4005 |       0.4589 |      0.6723 |      0.3955 |     0.5342 |         0.0574 |         0.0558 |     2.5 |      2.09e+06 |         4.23 |   11.89 |   0.1623 |      8.86013e+06 |
|  1 | EBS      |     -0.0059 |      -0.4513 |      -0.5136 |     -0.6429 |     -0.7204 |    -0.7292 |         0.0452 |         0.0827 |     2.7 | 753610        |         2.91 |   11.77 |   0.0138 |      2.19107e+06 |
|  2 | TME      |      0.1871 |       0.7984 |       0.3721 |      0.5789 |     -0.0531 |    -0.0365 |         0.0681 |         0.0756 |     2.3 |      9.95e+06 |         2.2  |    6.6  |   0.0611 |      2.18486e+07 |
|  3 | QFIN     |      0.0874 |       0.4331 |      -0.0738 |     -0.0744 |     -0.389  |    -0.365  |         0.0472 |         0.0787 |     1.4 | 997070        |         1.62 |   14.56 |   0.0849 |      1.61386e+06 |
|  4 | ATHM     |      0.0229 |       0.0391 |      -0.1772 |     -0.2256 |     -0.1971 |    -0.0455 |         0.0492 |         0.0579 |     2.2 | 577050        |         1.6  |   28.14 |   0.0484 | 922812           |
| 93 | TGNA     |      0.0093 |      -0.0514 |      -0.0882 |     -0.1073 |     -0.0528 |     0.0533 |         0.0133 |         0.0286 |     2.3 |      1.38e+06 |         0.45 |   19.55 |   0.0046 |   620767 |
| 94 | AMN      |      0.0096 |      -0.0365 |       0.1685 |      0.2591 |      0.0558 |    -0.0026 |         0.0243 |         0.0464 |     1.7 | 607420        |         0.43 |  122.01 |  -0.0078 |   264138 |
| 95 | MCY      |     -0.0028 |       0.2416 |       0.1165 |     -0.2619 |     -0.3014 |    -0.3191 |         0.0206 |         0.0386 |     2   | 565130        |         0.43 |   36.13 |   0.0036 |   241950 |
| 96 | FIBK     |     -0.0138 |      -0.0355 |       0.079  |      0.1411 |      0.0616 |     0.0681 |         0.0168 |         0.0206 |     2.2 | 596280        |         0.41 |   43.44 |  -0.0044 |   243947 |
| 97 | BPOP     |      0.0217 |       0.0126 |      -0.0777 |     -0.1245 |     -0.1108 |    -0.128  |         0.0158 |         0.0236 |     2   | 596460        |         0.4  |   71.54 |   0.0007 |   238605 |

It found just under 100 tickers meeting the criteria. Let's dial down the beta value to see how many remain at less than 0.5.

Change the one argument:

```console
[Technical]
Beta = Under 0.5
```

Running the exact same command as before trims down the list to only eleven.

```python
openbb.stocks.screener.screener_data(preset_loaded='sdk_guide_preset.ini', data_type = 'performance', limit = 100)
```

|    | Ticker   |   Perf Week |   Perf Month |   Perf Quart |   Perf Half |   Perf Year |   Perf YTD |   Volatility W |   Volatility M |   Recom |    Avg Volume |   Rel Volume |   Price |   Change |           Volume |
|---:|:---------|------------:|-------------:|-------------:|------------:|------------:|-----------:|---------------:|---------------:|--------:|--------------:|-------------:|--------:|---------:|-----------------:|
|  0 | QFIN     |      0.0874 |       0.4331 |      -0.0738 |     -0.0744 |     -0.389  |    -0.365  |         0.0472 |         0.0787 |     1.4 | 997070        |         1.62 |   14.56 |   0.0849 |      1.61386e+06 |
|  1 | ATHM     |      0.0229 |       0.0391 |      -0.1772 |     -0.2256 |     -0.1971 |    -0.0455 |         0.0492 |         0.0579 |     2.2 | 577050        |         1.6  |   28.14 |   0.0484 | 922812           |
|  2 | JD       |      0.0143 |       0.4065 |      -0.1343 |     -0.0511 |     -0.379  |    -0.2209 |         0.029  |         0.0454 |     1.8 |      9.14e+06 |         1.47 |   53.25 |   0.0669 |      1.34395e+07 |
|  3 | NI       |      0.0256 |       0.0518 |      -0.0844 |     -0.1342 |      0.0784 |    -0.0138 |         0.0151 |         0.0257 |     1.9 |      4.61e+06 |         1.36 |   27.23 |   0.0004 |      6.2667e+06  |
|  4 | ZTO      |      0.1176 |       0.3862 |      -0.0572 |     -0.1073 |     -0.216  |    -0.1393 |         0.0447 |         0.0437 |     1.7 |      3.21e+06 |         0.96 |   24.05 |   0.0217 |      3.06905e+06 |
|  5 | QDEL     |     -0.058  |      -0.0614 |       0.077  |     -0.1232 |     -0.4438 |    -0.3828 |         0.0335 |         0.0408 |     2.3 | 642680        |         0.79 |   83.32 |  -0.018  | 508575           |
|  6 | ED       |      0.0228 |       0.0888 |      -0.0203 |     -0.0298 |      0.1985 |     0.1287 |         0.0149 |         0.0202 |     3.5 |      1.73e+06 |         0.77 |   96.3  |  -0.0025 |      1.3419e+06  |
|  7 | SFM      |      0.027  |       0.1279 |       0.1656 |      0.237  |      0.237  |     0.129  |         0.0249 |         0.034  |     3.2 |      1.54e+06 |         0.74 |   33.51 |  -0.0095 |      1.14442e+06 |
|  8 | PINC     |      0.0244 |      -0.0549 |      -0.0635 |     -0.1125 |     -0.1377 |    -0.1936 |         0.0158 |         0.0217 |     2.6 | 519290        |         0.72 |   33.2  |   0.0097 | 373171           |
|  9 | AEP      |      0.0161 |       0.0587 |      -0.066  |     -0.0723 |      0.1361 |     0.0638 |         0.018  |         0.022  |     2.2 |      3.19e+06 |         0.64 |   94.65 |  -0.006  |      2.04444e+06 |
| 10 | LRN      |     -0.0025 |       0.0796 |      -0.0594 |     -0.0846 |      0.0398 |     0.0741 |         0.0207 |         0.0288 |     1.4 | 587770        |         0.46 |   35.8  |  -0.0047 | 270842           |
| 11 | AMN      |      0.0096 |      -0.0365 |       0.1685 |      0.2591 |      0.0558 |    -0.0026 |         0.0243 |         0.0464 |     1.7 | 607420        |         0.43 |  122.01 |  -0.0078 | 264138           |

### Overview

We know know that these eleven companies have a beta relative to the S&P of under 0.5, and that they all have a price-to-free-cashflow ratio under 15. The `signal` argument has also been set as `Major News`, so we know at least this much about the companies and their relative performance over the last year. Setting the `data_type` to 'overview', will fetch the data which helps us understand who these companies are.

```python
openbb.stocks.screener.screener_data(preset_loaded='sdk_guide_preset.ini', data_type = 'overview', limit = 100)
```

|    | Ticker   | Company                               | Sector                 | Industry                       | Country   |   Market Cap |    P/E |   Price |   Change |           Volume |
|---:|:---------|:--------------------------------------|:-----------------------|:-------------------------------|:----------|-------------:|-------:|--------:|---------:|-----------------:|
|  0 | QFIN     | 360 DigiTech, Inc.                    | Financial              | Credit Services                | China     |    2.19e+09  |   3.73 |   14.56 |   0.0849 |      1.61386e+06 |
|  1 | ATHM     | Autohome Inc.                         | Communication Services | Internet Content & Information | China     |    3.49e+09  |  16.96 |   28.14 |   0.0484 | 922812           |
|  2 | JD       | JD.com, Inc.                          | Consumer Cyclical      | Internet Retail                | China     |    8.152e+10 | 300.85 |   53.25 |   0.0669 |      1.34395e+07 |
|  3 | NI       | NiSource Inc.                         | Utilities              | Utilities - Regulated Gas      | USA       |    1.09e+10  |  17.69 |   27.23 |   0.0004 |      6.2667e+06  |
|  4 | ZTO      | ZTO Express (Cayman) Inc.             | Industrials            | Integrated Freight & Logistics | China     |    1.947e+10 |  24.67 |   24.05 |   0.0217 |      3.06905e+06 |
|  5 | QDEL     | QuidelOrtho Corporation               | Healthcare             | Diagnostics & Research         | USA       |    5.53e+09  |   4.96 |   83.32 |  -0.018  | 508575           |
|  6 | ED       | Consolidated Edison, Inc.             | Utilities              | Utilities - Regulated Electric | USA       |    3.366e+10 |  20.21 |   96.3  |  -0.0025 |      1.3419e+06  |
|  7 | SFM      | Sprouts Farmers Market, Inc.          | Consumer Defensive     | Grocery Stores                 | USA       |    3.57e+09  |  14.67 |   33.51 |  -0.0095 |      1.14442e+06 |
|  8 | PINC     | Premier, Inc.                         | Healthcare             | Health Information Services    | USA       |    3.92e+09  |  21.52 |   33.2  |   0.0097 | 373171           |
|  9 | AEP      | American Electric Power Company, Inc. | Utilities              | Utilities - Regulated Electric | USA       |    4.791e+10 |  19.63 |   94.65 |  -0.006  |      2.04444e+06 |
| 10 | LRN      | Stride, Inc.                          | Consumer Defensive     | Education & Training Services  | USA       |    1.54e+09  |  16.74 |   35.8  |  -0.0047 | 270842           |
| 11 | AMN      | AMN Healthcare Services, Inc.         | Healthcare             | Medical Care Facilities        | USA       |    5.4e+09   |  11.76 |  122.01 |  -0.0078 | 264138           |

### Ownership

When `data_type = 'ownership'`, data presented are statistics for the general float, insider, institutional, and the short ratio.

```python
openbb.stocks.screener.screener_data(preset_loaded='sdk_guide_preset.ini', data_type = 'ownership', limit = 100)
```

|    | Ticker   |   Market Cap |   Outstanding |      Float |   Insider Own |   Insider Trans |   Inst Own |   Inst Trans |   Float Short |   Short Ratio |    Avg Volume |   Price |   Change |           Volume |
|---:|:---------|-------------:|--------------:|-----------:|--------------:|----------------:|-----------:|-------------:|--------------:|--------------:|--------------:|--------:|---------:|-----------------:|
|  0 | QFIN     |    2.19e+09  |    1.5624e+08 | 1.2743e+08 |        0.0654 |          0      |      0.691 |       0.0034 |        0.0226 |          2.89 | 997070        |   14.56 |   0.0849 |      1.61386e+06 |
|  1 | ATHM     |    3.49e+09  |    1.246e+08  | 6.846e+07  |      nan      |        nan      |      0.513 |      -0.0397 |        0.0213 |          2.53 | 577050        |   28.14 |   0.0484 | 922812           |
|  2 | JD       |    8.152e+10 |    1.56e+09   | 1.26e+09   |        0.049  |          0      |      0.161 |      -0.1149 |        0.0136 |          1.88 |      9.14e+06 |   53.25 |   0.0669 |      1.34395e+07 |
|  3 | NI       |    1.09e+10  |    4.065e+08  | 4.0459e+08 |        0.001  |          0      |      0.948 |      -0.0254 |        0.0345 |          3.04 |      4.61e+06 |   27.23 |   0.0004 |      6.2667e+06  |
|  4 | ZTO      |    1.947e+10 |    8.0973e+08 | 6.4491e+08 |        0.0071 |          0      |      0.315 |       0.0345 |        0.0241 |          4.83 |      3.21e+06 |   24.05 |   0.0217 |      3.06905e+06 |
|  5 | QDEL     |    5.53e+09  |    6.69e+07   | 6.092e+07  |        0.011  |          0      |      0.973 |       0.0058 |        0.0515 |          4.88 | 642680        |   83.32 |  -0.018  | 508575           |
|  6 | ED       |    3.366e+10 |    3.546e+08  | 3.5443e+08 |        0.001  |          0.0056 |      0.684 |       0.0082 |        0.0206 |          4.22 |      1.73e+06 |   96.3  |  -0.0025 |      1.3419e+06  |
|  7 | SFM      |    3.57e+09  |    1.0723e+08 | 1.0362e+08 |        0.008  |         -0.1276 |    nan     |      -0.0287 |        0.1386 |          9.31 |      1.54e+06 |   33.51 |  -0.0095 |      1.14442e+06 |
|  8 | PINC     |    3.92e+09  |    1.1835e+08 | 1.1817e+08 |        0.008  |          0      |      0.707 |      -0.0044 |        0.0136 |          3.1  | 519290        |   33.2  |   0.0097 | 373171           |
|  9 | AEP      |    4.791e+10 |    5.1373e+08 | 5.137e+08  |        0.0003 |         -0.0336 |      0.758 |       0.0033 |        0.0129 |          2.07 |      3.19e+06 |   94.65 |  -0.006  |      2.04444e+06 |
| 10 | LRN      |    1.54e+09  |    4.208e+07  | 4.082e+07  |        0.04   |          0      |    nan     |       0.0158 |        0.0808 |          5.61 | 587770        |   35.8  |  -0.0047 | 270842           |
| 11 | AMN      |    5.4e+09   |    4.378e+07  | 4.299e+07  |        0.003  |         -0.0868 |    nan     |       0.0148 |        0.0983 |          6.96 | 607420        |  122.01 |  -0.0078 | 264138           |

### Technical

With `data_type` set to `technical`, aspects of technical analysis is returned.

```python
openbb.stocks.screener.screener_data(preset_loaded='sdk_guide_preset.ini', data_type = 'technical', limit = 100)
```

|    | Ticker   |   Beta |   ATR |   SMA20 |   SMA50 |   SMA200 |   52W High |   52W Low |   RSI |   Price |   Change |   from Open |     Gap |           Volume |
|---:|:---------|-------:|------:|--------:|--------:|---------:|-----------:|----------:|------:|--------:|---------:|------------:|--------:|-----------------:|
|  0 | QFIN     |   0.37 |  1.11 |  0.1061 |  0.1107 |  -0.0206 |    -0.3953 |    0.5375 | 56.6  |   14.56 |   0.0849 |      0.0341 |  0.0492 |      1.61386e+06 |
|  1 | ATHM     |   0.19 |  1.89 | -0.0324 | -0.0405 |  -0.1047 |    -0.3118 |    0.3734 | 47.13 |   28.14 |   0.0484 |      0.0057 |  0.0425 | 922812           |
|  2 | JD       |   0.39 |  3.3  |  0.1141 |  0.1183 |  -0.0584 |    -0.386  |    0.6054 | 58.07 |   53.25 |   0.0669 |     -0.0039 |  0.0711 |      1.34395e+07 |
|  3 | NI       |   0.44 |  0.62 |  0.049  |  0.0498 |  -0.0598 |    -0.1643 |    0.1451 | 61.62 |   27.23 |   0.0004 |      0.0052 | -0.0048 |      6.2667e+06  |
|  4 | ZTO      |  -0.09 |  1.14 |  0.1724 |  0.0968 |  -0.0412 |    -0.2565 |    0.4782 | 65.44 |   24.05 |   0.0217 |      0.0021 |  0.0195 |      3.06905e+06 |
|  5 | QDEL     |   0.29 |  3.46 | -0.0666 |  0.0262 |  -0.1185 |    -0.5373 |    0.2458 | 42.18 |   83.32 |  -0.018  |     -0.018  |  0      | 508575           |
|  6 | ED       |   0.32 |  1.83 |  0.0574 |  0.0843 |   0.0365 |    -0.0578 |    0.2426 | 66.88 |   96.3  |  -0.0025 |      0.002  | -0.0045 |      1.3419e+06  |
|  7 | SFM      |   0.41 |  1.12 |  0.0584 |  0.1446 |   0.1605 |    -0.0518 |    0.4854 | 63.99 |   33.51 |  -0.0095 |     -0.0053 | -0.0041 |      1.14442e+06 |
|  8 | PINC     |   0.36 |  0.7  |  0.0322 | -0.0004 |  -0.0711 |    -0.2042 |    0.0773 | 55.19 |   33.2  |   0.0097 |      0.0125 | -0.0027 | 373171           |
|  9 | AEP      |   0.41 |  2.07 |  0.0456 |  0.0559 |  -0.0117 |    -0.1037 |    0.1799 | 61.62 |   94.65 |  -0.006  |      0.0005 | -0.0065 |      2.04444e+06 |
| 10 | LRN      |   0.25 |  1.36 |  0.0302 | -0.0923 |  -0.0562 |    -0.2439 |    0.3957 | 44.85 |   35.8  |  -0.0047 |     -0.0014 | -0.0033 | 270842           |
| 11 | AMN      |   0.3  |  4.85 |  0.011  |  0.0599 |   0.1431 |    -0.0551 |    0.4744 | 54.13 |  122.01 |  -0.0078 |     -0.0059 | -0.0019 | 264138           |

### Valuation

Lastly, `valuation` gets the basic fundamental ratios.

|    | Ticker   |   Price |   Change |   Volume |   Market Cap |   P/E |   Fwd P/E |   PEG |   P/S |   P/B | P/C   | P/FCF   |   EPS this Y |   EPS next Y |   EPS past 5Y |   EPS next 5Y | Sales past 5Y   |
|---:|:---------|--------:|---------:|---------:|-------------:|------:|----------:|------:|------:|------:|:------|:--------|-------------:|-------------:|--------------:|--------------:|:----------------|
|  0 | AAPL     |  141.17 |  -0.0211 | 83578852 |  2.23252e+12 | 23.14 |     20.74 |  2.6  |  5.66 | 44.67 | 46.22 | 23.11   |        0.089 |       0.0898 |        0.216  |        0.0889 | 0.115           |
|  1 | MSFT     |  240.33 |  -0.0059 | 17929705 |  1.77308e+12 | 25.9  |     21.49 |  1.99 |  8.73 | 10.32 | 16.53 | 39.59   |        0.198 |       0.1709 |        0.243  |        0.1301 | 0.155           |
|  2 | GOOG     |   95.44 |  -0.0084 | 20145081 |  1.23434e+12 | 18.68 |     18.04 |  2.09 |  4.38 |  4.88 |  N/A  |  N/A    |       -0.159 |       0.121  |        0.2848 |        0.0895 |  N/A            |
|  3 | GOOGL    |   95.19 |  -0.009  | 20047848 |  1.21605e+12 | 19.51 |     18.12 |  2.18 |  4.31 |  4.89 | 10.46 | 19.44   |        0.914 |       0.1139 |        0.321  |        0.0895 | 0.233           |
|  4 | AMZN     |   92.42 |  -0.0163 | 65245723 |  9.3352e+11  | 85.26 |     55.08 |  3.28 |  1.86 |  6.85 | 15.91 |  N/A    |        0.549 |       0.8239 |        0.676  |        0.26   | 0.281           |
...continued

Combined, the five DataFrames provide an outline of who they are, which segment of the market they belong to, and how they are currently trading.

### Unconventional Applications

One way to use the screener is to feed it the least amount of variables possible. In this next example, the preset file contains only one filter; requesting data for all constituents of the S&P 500 Index.

```console
# Author of preset: OpenBB
# Description: S&P Index

[General]
Order = Market Cap.

[Descriptive]
Index = S&P 500

[Fundamental]

[Technical]
```

Copy and past the block above into any text editor; then save the file, as `sp500_filter.ini`, to the OpenBBUserData folder. The sample code below combines all five DataFrames for the entire S&P 500 into one, fifty-column, DataFrame. **It will likely take over two-minutes to collect the data.**

```python
from openbb_terminal.sdk import openbb
import pandas as pd

sp500_overview = openbb.stocks.screener.screener_data(preset_loaded='sp500_filter.ini', data_type = 'overview', limit = 500)
sp500_ownership = openbb.stocks.screener.screener_data(preset_loaded='sp500_filter.ini', data_type = 'ownership', limit = 500)
sp500_performance = openbb.stocks.screener.screener_data(preset_loaded='sp500_filter.ini', data_type = 'performance', limit = 500)
sp500_technical = openbb.stocks.screener.screener_data(preset_loaded='sp500_filter.ini', data_type = 'technical', limit = 500)
sp500_valuation = openbb.stocks.screener.screener_data(preset_loaded='sp500_filter.ini', data_type = 'valuation', limit = 500)

sp500_overview = sp500_overview.convert_dtypes()
sp500_ownership = sp500_ownership.convert_dtypes()
sp500_performance = sp500_performance.convert_dtypes()
sp500_technical = sp500_technical.convert_dtypes()
sp500_valuation = sp500_valuation.convert_dtypes()

sp500_overview.drop(columns = ['P/E'], inplace = True)
sp500_overview.set_index(keys = ['Ticker', 'Price', 'Change', 'Volume'], inplace = True)
sp500_performance.drop(columns = ['Avg Volume', 'Price', 'Change', 'Volume'], inplace = True)
sp500_performance.set_index(keys = ['Ticker'], inplace = True)
sp500_ownership.drop(columns = ['Price', 'Change', 'Volume', 'Market Cap'], inplace = True)
sp500_ownership.set_index(keys = ['Ticker'], inplace = True)
sp500_technical.drop(columns = ['Price', 'Change', 'Volume'], inplace = True)
sp500_technical.set_index(keys = ['Ticker'], inplace = True)
sp500_valuation.drop(columns = ['Price', 'Change', 'Volume', 'Market Cap'], inplace = True)
sp500_valuation.set_index(keys = ['Ticker'], inplace = True)

sp500_df = sp500_overview.join(sp500_valuation)
sp500_df = sp500_df.join(sp500_ownership)
sp500_df = sp500_df.join(sp500_performance)
sp500_df = sp500_df.join(sp500_technical)

sp500_df.reset_index(inplace = True)

sp500_df
```

A summary of the output:

```console
    Ticker   Price  Change    Volume  ... 52W Low    RSI from Open     Gap
0     AAPL  141.17 -0.0211  83578852  ...   0.094  42.47   -0.0211     0.0
1     MSFT  240.33 -0.0059  17929705  ...   0.126  50.94   -0.0044 -0.0015
2     GOOG   95.44 -0.0084  20145081  ...  0.1437  48.17   -0.0052 -0.0032
3    GOOGL   95.19  -0.009  20047848  ...  0.1422  48.24   -0.0063 -0.0027
4     AMZN   92.42 -0.0163  65245723  ...  0.0763  38.54   -0.0167  0.0004
..     ...     ...     ...       ...  ...     ...    ...       ...     ...
498   LUMN    5.47 -0.0091  31885469  ...  0.0018  30.19   -0.0036 -0.0054
499   PENN   34.07  0.0119   1689121  ...  0.3366   50.3    0.0068   0.005
500    NWL   12.87 -0.0191   5725896  ...   0.051  40.29     -0.01 -0.0091
501    VNO   25.31  0.0218   2560781  ...  0.2636  59.59    0.0181  0.0036
502    PVH   64.88  0.0399   1100532  ...  0.4918  66.83    0.0328  0.0069

[503 rows x 50 columns]
```
