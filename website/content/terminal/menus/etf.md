---
title: ETF
description: This guide introduces the ETF menu, in the OpenBB Terminal. The features provide methods for searching and comparing funds across the ETF universe.
keywords:
- ETF
- overview
- holdings
- weights
- news
- compare companies
- discovery
- technical indicators
- forecasting
- export to Excel
- exchange traded funds
- stock market
- financial tool
- portfolio
- stock chart
- Vanguard Total Stock Market Index Fund
- VTI
- load ETF
- ETF chart
- trendlines
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ETF - Menus | OpenBB Terminal Docs" />

The ETF menu features provide methods for searching and comparing funds across the ETF universe.

## Usage

Enter by typing `etf` from the main menu of the Terminal, or with the absolute path:

```console
/etf
```

![Screenshot 2023-11-02 at 5 43 12 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/f50269a8-8ebc-4ef9-bd37-4c9e15774005)

### Search

Find ETFs by fuzzy query using the `search` command.

```console
/etf search --name SPDR S&P
```

![Screenshot 2023-11-02 at 5 50 19 PM](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/984e0cbb-bced-4610-8a55-3262fdf8ea2a)

### Load

Use the `load` command to place a symbol into memory.

```console
/etf/load xhb
```

### Overview

`overview` shows a table of general statistics.

```console
/etf/load xhb/overview
```

|                  | XHB          |
|:-----------------|:-------------|
| Assets           | $1.21B       |
| Expense Ratio    | 0.35%        |
| PE Ratio         | 11.24        |
| Shares Out       | n/a          |
| Dividend (ttm)   | $0.74        |
| Dividend Yield   | 0.99%        |
| Ex-Dividend Date | Sep 18, 2023 |
| Volume           | 8,880,265    |
| Open             | 75.04        |
| Previous Close   | 73.82        |
| 52-Week Low      | 54.10        |
| 52-Week High     | 85.13        |
| Beta             | n/a          |
| Holdings         | 37           |

### Holdings

The `holdings` command provides a current view of the loaded ETF.

```console
/etf/load xhb/holdings
```

| Symbol   | Name                               | % Of Etf   |    Shares |
|:---------|:-----------------------------------|:-----------|----------:|
| WSM      | Williams-Sonoma, Inc.              | 4.50%      |    321673 |
| CSL      | Carlisle Companies Incorporated    | 4.35%      |    183841 |
| LII      | Lennox International Inc.          | 4.12%      |    119330 |
| MAS      | Masco Corporation                  | 3.99%      |    821783 |
| TT       | Trane Technologies plc             | 3.98%      |    224389 |
| PHM      | PulteGroup, Inc.                   | 3.92%      |    572445 |
| ALLE     | Allegion plc                       | 3.92%      |    427461 |   # cspell: disable-line
| LEN      | Lennar Corporation                 | 3.87%      |    389388 |
| DHI      | D.R. Horton, Inc.                  | 3.83%      |    393696 |
| FND      | Floor & Decor Holdings, Inc.       | 3.78%      |    493049 |
| TOL      | Toll Brothers, Inc.                | 3.76%      |    571043 |
| HD       | The Home Depot, Inc.               | 3.72%      |    140504 |
| NVR      | NVR, Inc.                          | 3.70%      |      7339 |
| JCI      | Johnson Controls International plc | 3.68%      |    805731 |
| LOW      | Lowe's Companies, Inc.             | 3.55%      |    199799 |
| TPX      | Tempur Sealy International, Inc.   | 3.51%      |    942711 |
| WMS      | Advanced Drainage Systems, Inc.    | 3.50%      |    351760 |
| CARR     | Carrier Global Corporation         | 3.50%      |    787745 |
| OC       | Owens Corning                      | 3.41%      |    323306 |
| BLDR     | Builders FirstSource, Inc.         | 3.34%      |    330150 |
| AOS      | A. O. Smith Corporation            | 3.33%      |    511883 |
| FBIN     | Fortune Brands Innovations, Inc.   | 3.17%      |    609787 |
| TREX     | Trex Company, Inc.                 | 2.79%      |    532594 |
| BLD      | TopBuild Corp.                     | 2.64%      |    123797 |
| TMHC     | Taylor Morrison Home Corporation   | 2.07%      |    580878 |
| TPH      | Tri Pointe Homes, Inc.             | 1.39%      |    596693 |
| MHO      | M/I Homes, Inc.                    | 1.39%      |    181673 |
| MDC      | M.D.C. Holdings, Inc.              | 1.26%      |    356746 |
| IBP      | Installed Building Products, Inc.  | 1.21%      |    116492 |
| GRBK     | Green Brick Partners, Inc.         | 1.03%      |    285076 |
| LGIH     | LGI Homes, Inc.                    | 1.02%      |    116166 |
| SKY      | Skyline Champion Corporation       | 1.01%      |    185257 |
| CVCO     | Cavco Industries, Inc.             | 0.76%      |     32610 |
| CCS      | Century Communities, Inc.          | 0.67%      |    117325 |
| DFH      | Dream Finders Homes, Inc.          | 0.27%      |    146550 |
| -        | STATE STREET INSTITUTIONAL LIQ     | 0.09%      |    922512 |
| -        | US DOLLAR                          | -2.36%     | -25351025 |

### Compare

The `compare` command accepts a comma-separated list of symbols for comparing overview metrics.

```console
compare -e xhb,pkb,rez,homz
```

|                  | XHB          | PKB          | REZ          | HOMZ         |
|:-----------------|:-------------|:-------------|:-------------|:-------------|
| Assets           | $1.21B       | $208.81M     | $590.71M     | $33.85M      |
| Expense Ratio    | 0.35%        | 0.60%        | 0.48%        | 0.30%        |
| PE Ratio         | 11.24        | 9.23         | 21.51        | 10.42        |
| Shares Out       | n/a          | n/a          | n/a          | n/a          |
| Dividend (ttm)   | $0.74        | $0.23        | $2.20        | $0.80        |
| Dividend Yield   | 0.99%        | 0.45%        | 3.43%        | 2.30%        |
| Ex-Dividend Date | Sep 18, 2023 | Sep 18, 2023 | Sep 26, 2023 | Oct 17, 2023 |
| Volume           | 8,880,265    | 13,224       | 48,825       | 3,926        |
| Open             | 75.04        | 50.59        | 63.05        | 33.90        |
| Previous Close   | 73.82        | 49.83        | 62.31        | 33.47        |
| 52-Week Low      | 54.10        | 37.54        | 60.64        | 29.89        |
| 52-Week High     | 85.13        | 57.25        | 78.33        | 40.68        |
| Beta             | n/a          | n/a          | n/a          | n/a          |
| Holdings         | 37           | 32           | 43           | 102          |


### Disc

The `disc` sub-menu has the movers of the day.

- gainers
- decliners
- active

```console
/etf/disc/gainers
```

|                                                       |   Price |    Chg |   %Chg | Vol    |
|:------------------------------------------------------|--------:|-------:|-------:|:-------|
| Direxion Daily Regional Banks Bull 3X Shares          |   53.11 | 7.74   |  17.06 | 2.4M   |
| AXS 2X Innovation ETF                                 |   51.02 | 7.38   |  16.91 | 165.0K |
| T-Rex 2X Long Tesla Daily Target ETF                  |   19.8  | 2.29   |  13.08 | 177.6K |
| GraniteShares 1.5x Long Coinbase Daily ETF            |   11.94 | 1.38   |  13.07 | 244.7K |
| MicroSectors U.S. Big Banks Index 3X Leveraged ETN    |   13    | 1.44   |  12.46 | 1.4M   |
| AdvisorShares MSOS 2x Daily ETF                       |    2.72 | 0.3    |  12.4  | 371.6K |
| Direxion Daily Homebuilders & Supplies Bull 3X Shares |   53.53 | 5.02   |  10.35 | 716.9K |
| GraniteShares 1.75x Long TSLA Daily ETF               |   21.3  | 1.99   |  10.31 | 78.2K  |
| Direxion Daily South Korea Bull 3X Shares             |    6.45 | 0.57   |   9.69 | 447.4K |
| Direxion Daily TSLA Bull 1.5X Shares                  |   12.41 | 1.06   |   9.34 | 14.7M  |
| Valkyrie Bitcoin Miners ETF                           |   10.59 | 0.9    |   9.29 | 232.1K |
| Direxion Daily S&P 500 High Beta Bull 3X Shares       |   22.96 | 1.91   |   9.07 | 332.5K |
| MicroSectors Oil & Gas Exp. & Prod. 3x Leveraged ETN  |   41.87 | 3.405  |   8.85 | 209.5K |
| Direxion Daily Real Estate Bull 3x Shares             |    6.78 | 0.55   |   8.83 | 1.9M   |
| Direxion Daily Retail Bull 3x Shares                  |    5.53 | 0.44   |   8.64 | 607.1K |
| ARK Innovation ETF                                    |   38.28 | 2.97   |   8.41 | 28.6M  |
| Direxion Daily Small Cap Bull 3x Shares               |   24.94 | 1.86   |   8.06 | 22.6M  |
| GraniteShares 1.25x Long Tesla Daily ETF              |   15.06 | 1.1015 |   7.89 | 66.9K  |
| ProShares UltraPro Russell2000                        |   29.24 | 2.1    |   7.74 | 2.0M   |
| Direxion Daily Consumer Discretionary Bull 3X Shares  |   24.23 | 1.73   |   7.69 | 58.6K  |
| VanEck Digital Transformation ETF                     |    6.13 | 0.43   |   7.54 | 263.3K |
| ARK Next Generation Internet ETF                      |   55.72 | 3.77   |   7.26 | 410.6K |
| Direxion Daily Financial Bull 3x Shares               |   58.32 | 3.86   |   7.09 | 1.0M   |
| Direxion Daily Semiconductor Bull 3X Shares           |   17.08 | 1.13   |   7.08 | 90.0M  |
| Ark Fintech Innovation ETF                            |   19.43 | 1.25   |   6.88 | 561.6K |
