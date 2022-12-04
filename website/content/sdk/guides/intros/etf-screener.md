---
title: ETF Screener
---

The ETF screener allows users to screen for ETFs meeting the criteria set by a user-generated preset. The template file is an `.ini` file, and it is attached - [etf_screener_config.zip](https://github.com/OpenBB-finance/OpenBBTerminal/files/10147733/etf_screener_config.zip) - for convenience.

## How to Use

Place the file in the folder, `~/OpenBBUserData/presets/etf/screener/`. Pasted below is the contents of the file.

```console
# Author of preset: OpenBB
# Description: This is the preset used in the Introduction Guides.

[Price]
MIN = None
MAX = None

[Assets]
MIN = None
MAX = None

[NAV]
MIN = None
MAX = None

[Expense]
MIN = None
MAX = None

[PE]
MIN = None
MAX = None

[DivYield]
MIN = None
MAX = None

[Volume]
MIN = None
MAX = None

[Beta]
MIN = None
MAX = None

[N_Hold]
MIN = None
MAX = None

[Open]
MIN = None
MAX = None

[PrevClose]
MIN = None
MAX = None

[YrLow]
MIN = None
MAX = None

[YrHigh]
MIN = None
MAX = None
```

## Examples

The examples below assume that the OpenBB SDK has been imported and the preset file is located in the `OpenBBUserData` folder.

```python
from openbb_terminal.sdk import openbb
```

### Get All ETFs

Setting all parameters as `None` will return every ETF available, which is about 2,500. The empty contents pasted above, `etf_config.ini`, is in the software installation folder and is reachable without declaring a path. User-generated presets stored in the `OpenBBUserData` folder also do not require the full path to be used.

```python
openbb.etf.scr.screen('etf_config.ini')
```

|      |   Assets |   NAV |   Expense |     PE | SharesOut   |    Div |   DivYield |   Volume |   Open |   PrevClose |   YrLow |   YrHigh |   Beta |   N_Hold |
|:-----|---------:|------:|----------:|-------:|:------------|-------:|-----------:|---------:|-------:|------------:|--------:|---------:|-------:|---------:|
| AAA  |     7.35 | 24.51 |      0.25 | nan    | 300,000     |   0.06 |       0.25 |      206 |  24.41 |       24.43 |   24.19 |    25.06 |   0.02 |       27 |
| AAAU |   575.82 | 17.24 |      0.18 | nan    | 33.4        | n/a    |     n/a    |   362817 |  19.11 |       17.45 |   16.73 |    20.57 |   0.13 |        1 |
| AADR |    43.64 | 50.75 |      1.1  |  13.34 | 860,000     |   1.2  |       2.36 |      529 |  51.06 |       51.64 |   46.05 |    68.99 |   1.03 |       37 |
| AAPD |     6.05 | 24.21 |      0.97 | nan    | 250,000     | n/a    |     n/a    |    56693 |  24.1  |       24.22 |   23.4  |    25.1  | n/a    |        9 |
| AAPU |     5.22 | 26.1  |      0.97 | nan    | 200,000     | n/a    |     n/a    |    21584 |  26.14 |       26.13 |   24.61 |    27.56 | n/a    |       10 |
| TRPL |     1.88 | 37.59 |      0.79 |  21.29 | 50,000      |   1.68 |       4.6  |   25           |  37.28 |       36.52 |   33.53 |    43.83 |   0.89 |      508 |
| TRTY |    55.86 | 25.98 |      0.44 |  12.14 | 2.15        |   1.56 |       6.01 | 2236           |  27.76 |       25.98 |   26.08 |    29.24 |   0.45 |       26 |
| TSJA |     9.58 | 25.21 |      0.79 |  26.1  | 380,000     | n/a    |     n/a    |  149           |  27.06 |       25.21 |   25.65 |    29.85 |   0.83 |        9 |
| TSLH |   n/a    | n/a   |    n/a    | n/a    | n/a         | n/a    |     n/a    | 1024           |  25.67 |       25.58 |   24.65 |    26.08 | n/a    |        0 |

Let's adjust one of the parameters to look for ETFs with very low expense ratios.

### Ultra Low Fee

The value for [EXPENSE] is expressed as a percent, and passive investing has driven down the expense ratios industry-wide. Adjusting, `MAX`, to 0.20 will filter for everything below twenty basis points.

This example is included in the `zip` file at the top of the page. To play along with the examples, simply update the preset file to include:

```console
[Expense]
MIN = None
MAX = 0.20
```

This trims the number of results down to 416.

```python
openbb.etf.scr.screen('etf_demo.ini')
```

|      |   Assets |    NAV |   Expense |     PE | SharesOut   |    Div |   DivYield |           Volume |   Open |   PrevClose |   YrLow |   YrHigh |   Beta |   N_Hold |
|:-----|---------:|-------:|----------:|-------:|:------------|-------:|-----------:|-----------------:|-------:|------------:|--------:|---------:|-------:|---------:|
| AAAU |   575.82 |  17.24 |      0.18 | n/a    | 33.4        | n/a    |     n/a    | 362817           |  19.11 |       17.45 |   16.73 |    20.57 |   0.13 |        1 |
| AGG  | 81350    | 101.68 |      0.03 | n/a    | 800.0       |   2.04 |       2.01 |      5.58479e+06 | 101.67 |      101.8  |   98.86 |   116.38 |   0.05 |    10415 |
| AGGY |   957.09 |  44.93 |      0.12 | n/a    | 21.3        |   1.04 |       2.31 | 113291           |  44.86 |       44.89 |   43.47 |    52.86 |   0.13 |     2608 |
| AGIH |     5.15 |  25.75 |      0.13 | n/a    | 200,000     |   0.09 |       0.35 |    nan           |  25.6  |       25.77 |   25.12 |    26.21 | n/a    |       22 |
| AOA  |  1500    |  63.21 |      0.15 |  22.57 | 23.75       |   1.4  |       2.27 |  87097           |  63.22 |       63.17 |   58    |    73.77 |   0.76 |       11 |
| TFLO |     2050 |  50.41 |      0.15 |  n/a |        40.6 |  0.17 |       0.34 |      1.21276e+06 |  50.45 |       50.45 |   50.25 |    50.49 |  -0.01 |        8 |
| TIP  |    30120 | 115.57 |      0.19 |  n/a |       260.6 |  7.91 |       6.87 |      2.1173e+06  | 115.23 |      115.58 |  113.01 |   131.37 |   0.11 |       53 |
| TIPX |     1500 |  19.72 |      0.15 |  n/a |        76   |  1.24 |       6.3  | 170299           |  19.64 |       19.68 |   19.28 |    21.46 |   0.09 |       36 |
| TLH  |     4480 | 118.87 |      0.15 |  n/a |        37.7 |  2.52 |       2.13 | 237452           | 118.88 |      119.32 |  114.39 |   153.04 |  -0.07 |       21 |
| TLT  |    23630 | 113.62 |      0.15 |  n/a |       208   |  2.35 |       2.08 |      1.42783e+07 | 112.94 |      113.62 |  108.12 |   155.12 |  -0.09 |       34 |

### Number of Holdings

Let's narrow down the field some more, this time targeting the number of holdings. Too few holdings might come with volatility swings, while a large number of holdings will track the broad market more closely. How many exist with more than 50, and fewer than 100, holdings? Update the preset file under `[N_Hold]` and run the function again.

```console
[N_Hold]
MIN = 50
MAX = 100
```

```python
openbb.etf.scr.screen('etf_demo.ini')
```

|      |   Assets |    NAV |   Expense |     PE | SharesOut   |   Div |   DivYield |           Volume |   Open |   PrevClose |   YrLow |   YrHigh |   Beta |   N_Hold |
|:-----|---------:|-------:|----------:|-------:|:------------|------:|-----------:|-----------------:|-------:|------------:|--------:|---------:|-------:|---------:|
| BBCA |  6260    |  61.14 |      0.19 |  12.63 | 102.4       |  1.49 |       2.44 |  19426           |  69.59 |       62.53 |   57.96 |    69.95 |   1.05 |       86 |
| BKUI |    26.97 |  49.03 |      0.12 | nan    | 550,000     |  0.37 |       0.76 |    348           |  49.03 |       49.03 |   48.88 |    49.93 |   0.03 |       72 |
| BSCM |  1930    |  21.2  |      0.1  | nan    | 91.2        |  0.39 |       1.83 | 293400           |  21.22 |       21.22 |   21.16 |    21.58 |   0.05 |       86 |
| CLTL |   859.62 | 105.48 |      0.08 | nan    | 8.15        |  0.36 |       0.34 | 163138           | 105.52 |      105.5  |  105.42 |   105.69 |  -0.01 |       67 |
| LQDI |    95.92 |  27.02 |      0.18 | nan    | 3.55        |  0.79 |       2.92 |  14496           |  29.22 |       27.02 |   27.99 |    31.33 |   0.36 |       53 |
| PSET |    42.43 |  49.91 |      0.15 |  17.64 | 850,000     |  0.65 |       1.3  |   1034           |  50.9  |       49.91 |   45.55 |    60.65 |   0.92 |       67 |
| PY   |   175.18 |  41.22 |      0.15 |  10.39 | 4.25        |  1.36 |       3.3  |   3380           |  40.83 |       41.22 |   37.42 |    46.17 |   1.22 |       81 |
| QQQJ |   852.54 |  25.51 |      0.15 |  24.76 | 33.42       |  0.32 |       1.26 | 106733           |  25.18 |       25.51 |   22.14 |    36.24 |   1.11 |       98 |
| QQQN |   105.55 |  25.74 |      0.18 |  26.91 | 4.1         |  0.15 |       0.59 |   7767           |  25.59 |       25.74 |   22.51 |    36.9  |   1.1  |       55 |
| SCHO |  9580    |  48.98 |      0.04 | nan    | 195.65      |  0.29 |       0.58 |      1.05951e+06 |  48.95 |       48.98 |   48.7  |    51.27 |  -0.02 |       94 |
| SCHQ |    94.57 |  41.12 |      0.04 | nan    | 2.3         |  0.95 |       2.41 |  20501           |  39.63 |       39.82 |   38    |    53.37 |  -0.01 |       69 |
| SEIM |    18.45 |  26.36 |      0.15 | nan    | 700,000     |  0.06 |       0.21 |   3459           |  26.36 |       26.36 |   23.03 |    27.24 | nan    |       80 |
| SEIQ |    10.28 |  25.71 |      0.15 | nan    | 400,000     |  0.06 |       0.25 |   1667           |  25.71 |       25.71 |   23.34 |    27.36 | nan    |       56 |
| SEIV |    17.16 |  24.52 |      0.15 | nan    | 700,000     |  0.07 |       0.29 |   2402           |  24.52 |       24.52 |   22.6  |    26.54 | nan    |       95 |
| SELV |    12.4  |  24.8  |      0.15 | nan    | 500,000     |  0.06 |       0.23 |      4           |  24.8  |       24.8  |   23.06 |    25.85 | nan    |       83 |
| SHV  | 20000    | 110.12 |      0.15 | nan    | 181.6       |  0.32 |       0.29 |      3.55702e+06 | 110.11 |      110.12 |  109.95 |   110.48 |   0.02 |       91 |
| SHY  | 26010    |  82.4  |      0.15 | nan    | 315.6       |  0.46 |       0.56 |      3.44994e+06 |  82.38 |       82.4  |   81.94 |    86.27 |  -0.02 |       81 |
| SPMV |    21.61 |  37.91 |      0.1  |  27.77 | 570,000     |  0.62 |       1.66 |     11           |  38.06 |       37.41 |   34.24 |    41.73 |   0.87 |       96 |
| SPTL |  5800    |  32.53 |      0.06 | nan    | 178.4       |  0.74 |       2.29 |      1.2387e+06  |  32.58 |       32.77 |   30.46 |    43.95 |  -0.09 |       70 |
| SPTS |  3350    |  29.33 |      0.06 | nan    | 114.3       |  0.14 |       0.48 | 632190           |  29.32 |       29.34 |   29.15 |    30.68 |  -0.02 |       95 |
| SPYD |  9730    |  42.38 |      0.07 |  11.35 | 229.5       |  1.57 |       3.83 |      1.15948e+06 |  41.03 |       41.25 |   38.09 |    45.83 |   0.99 |       83 |
| TIP  | 30120    | 115.57 |      0.19 | nan    | 260.6       |  7.91 |       6.87 |      2.1173e+06  | 115.23 |      115.58 |  113.01 |   131.37 |   0.11 |       53 |
| EDV  |  1100    |  96.61 |      0.06 | nan    | 11.35       |  2.73 |       2.86 | 166207           |  95.83 |       96.49 |   92.83 |   149.04 |  -0.11 |       82 |
| FLBR |   279.96 |  19.04 |      0.19 |   5.23 | 14.7        |  2.15 |      10.84 |  11907           |  19.76 |       19.84 |   15.46 |    24.52 |   1.09 |       97 |
| FLCA |   323.04 |  31.98 |      0.09 |  12.99 | 10.1        |  0.51 |       1.59 |  15401           |  31.95 |       32.15 |   28.8  |    36.75 |   0.99 |       53 |
| FLFR |     8.67 |  24.77 |      0.09 |  15.11 | 350,000     |  0.97 |       3.89 |  10605           |  24.66 |       24.73 |   23.24 |    35.16 |   1.02 |       78 |
| FLGR |    11.26 |  17.33 |      0.09 |  10.68 | 650,000     |  0.85 |       4.88 |   3353           |  17.22 |       17.24 |   16.47 |    27.53 |   1.07 |       86 |
| FLHK |    12.85 |  21.41 |      0.09 |  14.49 | 600,000     |  0.84 |       3.99 |   1102           |  21.13 |       21.28 |   21.05 |    27.85 |   0.66 |       92 |
| FLSW |    52.66 |  29.25 |      0.09 |  14.77 | 1.8         |  0.55 |       1.91 |  11123           |  28.85 |       28.88 |   27.12 |    36.5  |   0.72 |       52 |
| FLZA |     4.48 |  22.4  |      0.19 |   8.33 | 200,000     |  0.99 |       4.4  |     12           |  22.4  |       22.46 |   20.65 |    30.06 |   1.07 |       61 |
| FUTY |  2250    |  48.99 |      0.08 |  25.27 | 45.9        |  1.21 |       2.46 | 355950           |  49    |       49.01 |   40.91 |    50.25 |   0.48 |       69 |
| HDV  | 12790    | 105.58 |      0.08 |  17.23 | 121.1       |  3.15 |       3.06 | 473603           | 105.63 |      105.63 |   93.48 |   110.91 |   0.82 |       81 |
| IEI  | 12140    | 118.53 |      0.15 | nan    | 102.4       |  1.11 |       0.93 |      1.02374e+06 | 118.58 |      118.72 |  116.05 |   131.43 |  -0.04 |       66 |

### Dividend Yield

A 4% yield isn't too much to ask for, given the current financial conditions. Adding this caveat to the screener brings us down to only four ETFs.

|      |   Assets |    NAV |   Expense |     PE | SharesOut   |   Div |   DivYield |         Volume |   Open |   PrevClose |   YrLow |   YrHigh |   Beta |   N_Hold |
|:-----|---------:|-------:|----------:|-------:|:------------|------:|-----------:|---------------:|-------:|------------:|--------:|---------:|-------:|---------:|
| TIP  | 30120    | 115.57 |      0.19 | nan    | 260.6       |  7.91 |       6.87 |     2.1173e+06 | 115.23 |      115.58 |  113.01 |   131.37 |   0.11 |       53 |
| FLBR |   279.96 |  19.04 |      0.19 |   5.23 | 14.7        |  2.15 |      10.84 | 11907          |  19.76 |       19.84 |   15.46 |    24.52 |   1.09 |       97 |
| FLGR |    11.26 |  17.33 |      0.09 |  10.68 | 650,000     |  0.85 |       4.88 |  3353          |  17.22 |       17.24 |   16.47 |    27.53 |   1.07 |       86 |
| FLZA |     4.48 |  22.4  |      0.19 |   8.33 | 200,000     |  0.99 |       4.4  |    12          |  22.4  |       22.46 |   20.65 |    30.06 |   1.07 |       61 |

